/* RFC 8878 Zstandard decompressor.  This file uses no libzstd routines. */
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include <xxhash.h>
#include "zstd_decompress.h"

#define ZSTD_SKIPPABLE_MAGIC 0x184D2A50U
#define ZSTD_SKIPPABLE_MASK  0xFFFFFFF0U
#define ZSTD_DICT_MAGIC      0xEC30A437U
#define FSE_MAX_LOG 12
#define FSE_MAX_SIZE (1U << FSE_MAX_LOG)
#define HUF_MAX_BITS 11
#define HUF_MAX_SIZE (1U << HUF_MAX_BITS)

typedef struct { const u8 *p, *end; int error; } ZReader;
typedef struct { u16 symbol, baseline; u8 nb_bits; } FSECell;
typedef struct {
    FSECell cell[FSE_MAX_SIZE];
    u16 max_symbol;
    u8 table_log, rle_symbol, valid, is_rle;
} FSETable;
typedef struct { u8 symbol, nb_bits; } HUFCell;
typedef struct { HUFCell cell[HUF_MAX_SIZE]; u8 max_bits, valid; } HUFTable;
typedef struct { const u8 *src; size_t bit_count, bit_pos; int error; } RevBits;
typedef struct { const u8 *src; size_t bytes, bit_pos; int error; } FwdBits;

typedef struct {
    const u8 *content;
    size_t content_len;
    u32 id, rep[3];
    HUFTable huf;
    FSETable ll, of, ml;
    int formatted;
} ZDict;

typedef struct {
    u8 *dst, *literals;
    size_t dst_len, out_pos, frame_start, block_start, block_limit;
    u64 window_size;
    const u8 *dict_content;
    size_t dict_len;
    u32 rep[3];
    HUFTable huf;
    FSETable ll, of, ml;
    int error;
} ZDecoder;

static const i16 k_ll_default[36] = {
    4,3,2,2,2,2,2,2,2,2,2,2,2,1,1,1,2,2,2,2,2,2,2,2,
    2,3,2,1,1,1,1,1,-1,-1,-1,-1
};
static const i16 k_ml_default[53] = {
    1,4,3,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,
    -1,-1,-1,-1,-1,-1
};
static const i16 k_of_default[29] = {
    1,1,1,1,1,1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    -1,-1,-1,-1,-1
};

static unsigned highbit32(u32 v) {
    unsigned n = 0;
    while (v > 1) { ++n; v >>= 1; }
    return n;
}

static int need(ZReader *r, size_t n) {
    if (r->error || (size_t)(r->end - r->p) < n) { r->error = 1; return 0; }
    return 1;
}
static u8 rd8(ZReader *r) { if (!need(r, 1)) return 0; return *r->p++; }
static u32 rdle(ZReader *r, unsigned n) {
    u32 v = 0; unsigned i;
    if (!need(r, n)) return 0;
    for (i = 0; i < n; ++i) v |= (u32)r->p[i] << (8U * i);
    r->p += n; return v;
}
static u64 rdle64(ZReader *r, unsigned n) {
    u64 v = 0; unsigned i;
    if (!need(r, n)) return 0;
    for (i = 0; i < n; ++i) v |= (u64)r->p[i] << (8U * i);
    r->p += n; return v;
}

static int fwd_read(FwdBits *b, unsigned n, u32 *out) {
    u32 v = 0; unsigned i;
    if (n > 24 || b->error || b->bit_pos + n > b->bytes * 8U) {
        b->error = 1; return 0;
    }
    for (i = 0; i < n; ++i)
        v |= (u32)((b->src[(b->bit_pos+i)>>3] >> ((b->bit_pos+i)&7)) & 1U) << i;
    b->bit_pos += n; *out = v; return 1;
}

/* A zstd reverse bitstream has an end marker in the highest set bit of its
 * last byte.  Bits are encountered backwards, but the first encountered bit
 * is the high bit of an RFC bit-field. */
static int rev_init(RevBits *b, const u8 *src, size_t bytes) {
    unsigned marker;
    if (bytes == 0 || src[bytes-1] == 0) return 0;
    marker = highbit32(src[bytes-1]);
    b->src = src; b->bit_count = (bytes-1U)*8U + marker;
    b->bit_pos = 0; b->error = 0;
    return 1;
}
static size_t rev_left(const RevBits *b) {
    return b->bit_pos <= b->bit_count ? b->bit_count - b->bit_pos : 0;
}
static int rev_read(RevBits *b, unsigned n, u32 *out) {
    u32 v = 0; unsigned i;
    if (n > 32 || b->error || b->bit_pos + n > b->bit_count) {
        b->error = 1; return 0;
    }
    for (i = 0; i < n; ++i) {
        size_t q = b->bit_count - 1U - b->bit_pos - i;
        v |= (u32)((b->src[q>>3] >> (q&7)) & 1U) << (n-1U-i);
    }
    b->bit_pos += n; *out = v; return 1;
}
static u32 rev_peek_padded(const RevBits *b, unsigned n) {
    u32 v = 0; unsigned i;
    for (i = 0; i < n; ++i) if (b->bit_pos+i < b->bit_count) {
        size_t q = b->bit_count - 1U - b->bit_pos - i;
        v |= (u32)((b->src[q>>3] >> (q&7)) & 1U) << (n-1U-i);
    }
    return v;
}

static int fse_build(FSETable *t, const i16 *norm, unsigned max_symbol,
                     unsigned table_log) {
    u16 symbols[FSE_MAX_SIZE], next[256];
    unsigned size, mask, step, pos, high, s, i, nonzero = 0;
    if (table_log < 5 || table_log > FSE_MAX_LOG || max_symbol > 255) return 0;
    size = 1U << table_log; mask = size-1U; high = size-1U;
    memset(symbols, 0xFF, sizeof(symbols)); memset(next, 0, sizeof(next));
    for (s = 0; s <= max_symbol; ++s) {
        if (norm[s] < -1) return 0;
        if (norm[s] == -1) {
            symbols[high--] = (u16)s; next[s] = 1; ++nonzero;
        } else if (norm[s] > 0) { next[s] = (u16)norm[s]; ++nonzero; }
    }
    if (nonzero < 2) return 0;
    step = (size >> 1) + (size >> 3) + 3U; pos = 0;
    for (s = 0; s <= max_symbol; ++s) for (i = 0; i < (unsigned)(norm[s] > 0 ? norm[s] : 0); ++i) {
        if (pos > high || symbols[pos] != 0xFFFFU) return 0;
        symbols[pos] = (u16)s;
        pos = (pos + step) & mask;
        while (pos > high) pos = (pos + step) & mask;
    }
    if (pos != 0) return 0;
    for (i = 0; i < size; ++i) {
        u16 sym = symbols[i]; unsigned n, nb;
        if (sym == 0xFFFFU || sym > max_symbol) return 0;
        n = next[sym]++; if (n == 0) return 0;
        nb = table_log - highbit32(n);
        t->cell[i].symbol = sym; t->cell[i].nb_bits = (u8)nb;
        t->cell[i].baseline = (u16)((n << nb) - size);
    }
    t->table_log = (u8)table_log; t->max_symbol = (u16)max_symbol;
    t->valid = 1; t->is_rle = 0; return 1;
}

/* RFC 8878 4.1.1, read forward with variable-width normalized counts. */
static int fse_read_table(const u8 **pp, const u8 *end, FSETable *t,
                          unsigned max_symbol, unsigned max_log) {
    FwdBits b; i16 norm[256]; unsigned log, remain, sym = 0, nonzero = 0;
    u32 x;
    if (*pp >= end || max_symbol > 255 || max_log > FSE_MAX_LOG) return 0;
    memset(norm, 0, sizeof(norm));
    b.src = *pp; b.bytes = (size_t)(end-*pp); b.bit_pos = 0; b.error = 0;
    if (!fwd_read(&b, 4, &x)) return 0;
    log = x + 5U; if (log > max_log || log > FSE_MAX_LOG) return 0;
    remain = 1U << log;
    while (remain != 0) {
        unsigned maxval, bits = 0, short_count, low, value, zeros;
        i16 count;
        if (sym > max_symbol) return 0;
        maxval = remain + 1U;
        while ((1U << bits) <= maxval) ++bits;
        if (bits == 0 || bits > 20 || !fwd_read(&b, bits-1U, &x)) return 0;
        low = x; short_count = (1U << bits) - (maxval + 1U);
        if (low < short_count) value = low;
        else {
            if (!fwd_read(&b, 1, &x)) return 0;
            value = low + (x << (bits-1U));
            if (x) value -= short_count;
        }
        if (value > maxval) return 0;
        count = (i16)value - 1;
        if (count > 0 && (unsigned)count > remain) return 0;
        if (count == -1) { --remain; ++nonzero; }
        else if (count > 0) { remain -= (unsigned)count; ++nonzero; }
        norm[sym++] = count;
        if (count == 0) {
            zeros = 0;
            do { if (!fwd_read(&b, 2, &x)) return 0; zeros += x; } while (x == 3U);
            if (zeros > max_symbol + 1U - sym) return 0;
            while (zeros--) norm[sym++] = 0;
        }
    }
    if (nonzero < 2 || sym == 0 || !fse_build(t, norm, sym-1U, log)) return 0;
    if ((b.bit_pos+7U)/8U > b.bytes) return 0;
    *pp += (b.bit_pos+7U)/8U; return 1;
}

static void fse_set_rle(FSETable *t, u8 symbol) {
    memset(t, 0, sizeof(*t)); t->rle_symbol = symbol; t->max_symbol = symbol;
    t->valid = 1; t->is_rle = 1;
}
static int fse_predefined(FSETable *t, int kind) {
    if (kind == 0) return fse_build(t, k_ll_default, 35, 6);
    if (kind == 1) return fse_build(t, k_of_default, 28, 5);
    return fse_build(t, k_ml_default, 52, 6);
}
static int fse_init(const FSETable *t, RevBits *b, u32 *state) {
    if (!t->valid) return 0;
    if (t->is_rle) { *state = 0; return 1; }
    return rev_read(b, t->table_log, state) && *state < (1U << t->table_log);
}
static u16 fse_sym(const FSETable *t, u32 state) {
    if (t->is_rle) return t->rle_symbol;
    return state < (1U << t->table_log) ? t->cell[state].symbol : 0xFFFFU;
}
static int fse_update(const FSETable *t, RevBits *b, u32 *state) {
    const FSECell *c; u32 v;
    if (t->is_rle) return 1;
    if (*state >= (1U << t->table_log)) return 0;
    c = &t->cell[*state];
    if (!rev_read(b, c->nb_bits, &v)) return 0;
    *state = c->baseline + v;
    return *state < (1U << t->table_log);
}

/* Weights omit their final nonzero entry.  Complete the Kraft sum and make
 * a max-bit lookup table whose high bits match the reverse bit reader. */
static int huf_make(HUFTable *h, u8 *weights, unsigned explicit_count) {
    unsigned s, w, max_bits; u32 total = 0, rest, next = 0;
    if (explicit_count == 0 || explicit_count >= 256) return 0;
    for (s = 0; s < explicit_count; ++s) {
        if (weights[s] > HUF_MAX_BITS) return 0;
        if (weights[s]) total += 1U << (weights[s]-1U);
    }
    if (total == 0) return 0;
    max_bits = highbit32(total) + 1U;
    if (max_bits > HUF_MAX_BITS) return 0;
    rest = (1U << max_bits) - total;
    if (rest == 0 || (rest & (rest-1U)) != 0) return 0;
    weights[explicit_count++] = (u8)(highbit32(rest)+1U);
    if (weights[explicit_count-1U] > HUF_MAX_BITS) return 0;
    memset(h, 0, sizeof(*h));
    for (w = 1; w <= max_bits; ++w) {
        unsigned len = max_bits + 1U - w, scale = 1U << (max_bits-len);
        for (s = 0; s < explicit_count; ++s) if (weights[s] == w) {
            unsigned code = next >> (max_bits-len), fill = 1U << (max_bits-len);
            unsigned i, first = code << (max_bits-len);
            for (i = 0; i < fill; ++i) {
                unsigned index = first+i;
                if (h->cell[index].nb_bits) return 0;
                h->cell[index].symbol = (u8)s; h->cell[index].nb_bits = (u8)len;
            }
            next += scale;
        }
    }
    if (next != (1U << max_bits)) return 0;
    h->max_bits = (u8)max_bits; h->valid = 1; return 1;
}

/* Huffman weights use two interleaved FSE states.  A state whose transition
 * needs zero bits remains decodable after the bitstream has no bits left;
 * only a transition needing unavailable bits ends the stream.  RFC 8878
 * then decodes the two final states, in the current interleaving order. */
static int huf_fse_weights(const u8 *src, size_t bytes, const FSETable *t,
                           u8 *weights, unsigned *count) {
    RevBits b;
    u32 state[2];
    u8 tmp[256];
    unsigned n = 0, turn = 0;
    HUFTable trial;
    if (!t->valid || t->is_rle) return 0;
    if (!rev_init(&b, src, bytes) || !fse_init(t, &b, &state[0]) ||
        !fse_init(t, &b, &state[1])) return 0;
    while (n < 255) {
        const FSECell *c;
        if (state[turn] >= (1U << t->table_log)) return 0;
        c = &t->cell[state[turn]];
        if (c->symbol > HUF_MAX_BITS || rev_left(&b) < c->nb_bits) break;
        tmp[n++] = (u8)c->symbol;
        if (!fse_update(t, &b, &state[turn])) return 0;
        turn ^= 1U;
    }
    if (n > 253U || state[turn] >= (1U << t->table_log) ||
        t->cell[state[turn]].symbol > HUF_MAX_BITS) return 0;
    tmp[n++] = (u8)t->cell[state[turn]].symbol;
    turn ^= 1U;
    if (state[turn] >= (1U << t->table_log) || t->cell[state[turn]].symbol > HUF_MAX_BITS)
        return 0;
    tmp[n++] = (u8)t->cell[state[turn]].symbol;
    memcpy(weights, tmp, n);
    if (!huf_make(&trial, weights, n)) return 0;
    *count = n;
    return 1;
}

static int huf_read_table(const u8 **pp, const u8 *end, HUFTable *h) {
    const u8 *p = *pp;
    u8 header, weights[256];
    unsigned count;
    if (p >= end) return 0;
    header = *p++; memset(weights, 0, sizeof(weights));
    if (header >= 128) {
        unsigned i; size_t packed;
        count = (unsigned)header - 127U;
        packed = (count + 1U) / 2U;
        if (count >= 256 || (size_t)(end-p) < packed) return 0;
        for (i = 0; i < count; ++i) {
            u8 x = p[i >> 1];
            weights[i] = (i & 1U) ? (x & 15U) : (x >> 4);
        }
        p += packed;
        if (!huf_make(h, weights, count)) return 0;
    } else {
        const u8 *section_end;
        FSETable table;
        if (header == 0 || (size_t)(end-p) < header) return 0;
        section_end = p + header;
        if (!fse_read_table(&p, section_end, &table, HUF_MAX_BITS, 6) ||
            p >= section_end ||
            !huf_fse_weights(p, (size_t)(section_end-p), &table, weights, &count) ||
            !huf_make(h, weights, count)) return 0;
        p = section_end;
    }
    *pp = p; return 1;
}

static int huf_decode_stream(const HUFTable *h, const u8 *src, size_t bytes,
                             u8 *out, size_t count) {
    RevBits b; size_t i;
    if (!h->valid || !rev_init(&b, src, bytes)) return 0;
    for (i = 0; i < count; ++i) {
        HUFCell c = h->cell[rev_peek_padded(&b, h->max_bits)];
        u32 ignored;
        if (c.nb_bits == 0 || c.nb_bits > rev_left(&b) ||
            !rev_read(&b, c.nb_bits, &ignored)) return 0;
        out[i] = c.symbol;
    }
    return rev_left(&b) == 0;
}

static int emit_byte(ZDecoder *d, u8 value) {
    if (d->error || d->out_pos >= d->dst_len || d->out_pos >= d->block_limit) {
        d->error = 1; return 0;
    }
    d->dst[d->out_pos++] = value; return 1;
}
static int emit_bytes(ZDecoder *d, const u8 *src, size_t count) {
    if (d->out_pos > d->dst_len || d->out_pos > d->block_limit ||
        count > d->dst_len-d->out_pos || count > d->block_limit-d->out_pos) {
        d->error = 1; return 0;
    }
    memcpy(d->dst+d->out_pos, src, count); d->out_pos += count; return 1;
}

static int copy_match(ZDecoder *d, u64 offset, size_t count) {
    size_t i;
    if (offset == 0 || offset > (u64)SIZE_MAX || d->out_pos > d->dst_len ||
        d->out_pos > d->block_limit || count > d->dst_len-d->out_pos ||
        count > d->block_limit-d->out_pos) { d->error = 1; return 0; }
    for (i = 0; i < count; ++i) {
        size_t frame_pos = d->out_pos-d->frame_start;
        u8 value;
        if (offset <= frame_pos) {
            if (offset > d->window_size) { d->error = 1; return 0; }
            value = d->dst[d->out_pos-(size_t)offset];
        } else {
            u64 behind = offset-frame_pos;
            if (frame_pos > d->window_size || behind > d->dict_len) {
                d->error = 1; return 0;
            }
            value = d->dict_content[d->dict_len-(size_t)behind];
        }
        if (!emit_byte(d, value)) return 0;
    }
    return 1;
}

static int ll_value(u16 code, RevBits *b, size_t *out) {
    static const u32 base[20] = {
        16,18,20,22,24,28,32,40,48,64,128,256,512,1024,2048,4096,
        8192,16384,32768,65536
    };
    static const u8 bits[20] = {
        1,1,1,1,2,2,3,3,4,6,7,8,9,10,11,12,13,14,15,16
    };
    u32 x;
    if (code <= 15) { *out = code; return 1; }
    if (code > 35 || !rev_read(b, bits[code-16U], &x)) return 0;
    *out = (size_t)base[code-16U]+x; return 1;
}
static int ml_value(u16 code, RevBits *b, size_t *out) {
    static const u32 base[21] = {
        35,37,39,41,43,47,51,59,67,83,99,131,259,515,1027,2051,
        4099,8195,16387,32771,65539
    };
    static const u8 bits[21] = {
        1,1,1,1,2,2,3,3,4,4,5,7,8,9,10,11,12,13,14,15,16
    };
    u32 x;
    if (code <= 31) { *out = (size_t)code+3U; return 1; }
    if (code > 52 || !rev_read(b, bits[code-32U], &x)) return 0;
    *out = (size_t)base[code-32U]+x; return 1;
}

static int resolve_offset(ZDecoder *d, u64 value, size_t ll, u64 *offset) {
    u32 used;
    if (value > 3) {
        if (value-3U > UINT_MAX) return 0;
        used = (u32)(value-3U);
        d->rep[2] = d->rep[1]; d->rep[1] = d->rep[0]; d->rep[0] = used;
    } else if (ll == 0 && value == 3) {
        if (d->rep[0] <= 1) return 0;
        used = d->rep[0]-1U;
        d->rep[2] = d->rep[1]; d->rep[1] = d->rep[0]; d->rep[0] = used;
    } else {
        unsigned index = ll == 0 ? (unsigned)value : (unsigned)(value-1U);
        if (index > 2 || d->rep[index] == 0) return 0;
        used = d->rep[index];
        while (index) { d->rep[index] = d->rep[index-1U]; --index; }
        d->rep[0] = used;
    }
    *offset = used; return 1;
}

static int decode_sequences(ZDecoder *d, const u8 *src, const u8 *end,
                            size_t literal_count) {
    ZReader r;
    u32 first, count, n, ll_state, of_state, ml_state;
    u8 modes;
    unsigned ll_mode, of_mode, ml_mode;
    RevBits bits;
    size_t literal_pos = 0;
    r.p = src; r.end = end; r.error = 0;
    if (!need(&r, 1)) return 0;
    first = rd8(&r);
    if (first == 0) {
        if (r.p != end) return 0;
        return emit_bytes(d, d->literals, literal_count);
    }
    if (first < 128) count = first;
    else if (first < 255) count = ((first-128U) << 8) + rd8(&r);
    else count = (u32)rd8(&r) + ((u32)rd8(&r) << 8) + 0x7F00U;
    if (r.error || count == 0 || !need(&r, 1)) return 0;
    modes = rd8(&r); if (modes & 3U) return 0;
    ll_mode = modes >> 6; of_mode = (modes >> 4) & 3U; ml_mode = (modes >> 2) & 3U;

    if (ll_mode == SEQ_MODE_PREDEFINED) { if (!fse_predefined(&d->ll, 0)) return 0; }
    else if (ll_mode == SEQ_MODE_RLE) {
        if (!need(&r, 1)) return 0; fse_set_rle(&d->ll, rd8(&r));
        if (d->ll.rle_symbol > 35) return 0;
    } else if (ll_mode == SEQ_MODE_FSE) {
        if (!fse_read_table(&r.p, r.end, &d->ll, 35, 9)) return 0;
    } else if (!d->ll.valid) return 0;
    if (of_mode == SEQ_MODE_PREDEFINED) { if (!fse_predefined(&d->of, 1)) return 0; }
    else if (of_mode == SEQ_MODE_RLE) {
        if (!need(&r, 1)) return 0; fse_set_rle(&d->of, rd8(&r));
        if (d->of.rle_symbol > 31) return 0;
    } else if (of_mode == SEQ_MODE_FSE) {
        if (!fse_read_table(&r.p, r.end, &d->of, 31, 8)) return 0;
    } else if (!d->of.valid) return 0;
    if (ml_mode == SEQ_MODE_PREDEFINED) { if (!fse_predefined(&d->ml, 2)) return 0; }
    else if (ml_mode == SEQ_MODE_RLE) {
        if (!need(&r, 1)) return 0; fse_set_rle(&d->ml, rd8(&r));
        if (d->ml.rle_symbol > 52) return 0;
    } else if (ml_mode == SEQ_MODE_FSE) {
        if (!fse_read_table(&r.p, r.end, &d->ml, 52, 9)) return 0;
    } else if (!d->ml.valid) return 0;
    if (r.error || r.p >= r.end || !rev_init(&bits, r.p, (size_t)(r.end-r.p)) ||
        !fse_init(&d->ll, &bits, &ll_state) || !fse_init(&d->of, &bits, &of_state) ||
        !fse_init(&d->ml, &bits, &ml_state)) return 0;

    for (n = 0; n < count; ++n) {
        u16 ll_code = fse_sym(&d->ll, ll_state), of_code = fse_sym(&d->of, of_state);
        u16 ml_code = fse_sym(&d->ml, ml_state);
        u32 extra; u64 offset_value, offset; size_t ll, ml;
        if (ll_code > 35 || of_code > 31 || ml_code > 52 ||
            !rev_read(&bits, of_code, &extra)) return 0;
        offset_value = ((u64)1 << of_code) + extra;
        if (!ml_value(ml_code, &bits, &ml) || !ll_value(ll_code, &bits, &ll) ||
            ll > literal_count-literal_pos || !emit_bytes(d, d->literals+literal_pos, ll)) return 0;
        literal_pos += ll;
        if (!resolve_offset(d, offset_value, ll, &offset) || !copy_match(d, offset, ml)) return 0;
        if (n+1U != count && (!fse_update(&d->ll, &bits, &ll_state) ||
            !fse_update(&d->ml, &bits, &ml_state) || !fse_update(&d->of, &bits, &of_state))) return 0;
    }
    if (rev_left(&bits) != 0) return 0;
    return emit_bytes(d, d->literals+literal_pos, literal_count-literal_pos);
}

static int decode_literals(ZDecoder *d, const u8 **pp, const u8 *end,
                           size_t *literal_count) {
    const u8 *p = *pp;
    u8 first, type, format;
    size_t regen, compressed = 0, header_size;
    unsigned streams = 1;
    if (p >= end) return 0;
    first = p[0]; type = first & 3U; format = (first >> 2) & 3U;
    if (type == LITERALS_TYPE_RAW || type == LITERALS_TYPE_RLE) {
        if (format == 0 || format == 2) { regen = first >> 3; header_size = 1; }
        else if (format == 1) {
            if ((size_t)(end-p) < 2) return 0;
            regen = (first >> 4) | ((size_t)p[1] << 4); header_size = 2;
        } else {
            if ((size_t)(end-p) < 3) return 0;
            regen = (first >> 4) | ((size_t)p[1] << 4) | ((size_t)p[2] << 12);
            header_size = 3;
        }
        if (regen > BLOCK_SIZE_MAX || (size_t)(end-p) < header_size) return 0;
        p += header_size;
        if (type == LITERALS_TYPE_RAW) {
            if ((size_t)(end-p) < regen) return 0;
            memcpy(d->literals, p, regen); p += regen;
        } else {
            if (p >= end) return 0;
            memset(d->literals, *p++, regen);
        }
    } else {
        if (format == 0 || format == 1) {
            if ((size_t)(end-p) < 3) return 0;
            regen = (first >> 4) | ((size_t)(p[1] & 0x3FU) << 4);
            compressed = ((size_t)p[1] >> 6) | ((size_t)p[2] << 2);
            header_size = 3; streams = format == 0 ? 1U : 4U;
        } else if (format == 2) {
            if ((size_t)(end-p) < 4) return 0;
            regen = (first >> 4) | ((size_t)p[1] << 4) | ((size_t)(p[2] & 3U) << 12);
            compressed = ((size_t)p[2] >> 2) | ((size_t)p[3] << 6);
            header_size = 4; streams = 4;
        } else {
            if ((size_t)(end-p) < 5) return 0;
            regen = (first >> 4) | ((size_t)p[1] << 4) | ((size_t)(p[2] & 0x3FU) << 12);
            compressed = ((size_t)p[2] >> 6) | ((size_t)p[3] << 2) | ((size_t)p[4] << 10);
            header_size = 5; streams = 4;
        }
        if (regen > BLOCK_SIZE_MAX || compressed > (size_t)(end-p)-header_size) return 0;
        {
            const u8 *payload, *stream_data;
            size_t tree_size = 0;
            p += header_size; payload = p;
            if (type == LITERALS_TYPE_COMPRESSED) {
                if (!huf_read_table(&p, payload+compressed, &d->huf)) return 0;
                tree_size = (size_t)(p-payload);
            } else if (!d->huf.valid) return 0;
            if (tree_size > compressed) return 0;
            stream_data = p;
            if (streams == 1) {
                if (!huf_decode_stream(&d->huf, stream_data, compressed-tree_size,
                                       d->literals, regen)) return 0;
            } else {
                size_t total = compressed-tree_size, sizes[4], per, i, at = 0;
                if (total < 6) return 0;
                sizes[0] = (size_t)stream_data[0] | ((size_t)stream_data[1] << 8);
                sizes[1] = (size_t)stream_data[2] | ((size_t)stream_data[3] << 8);
                sizes[2] = (size_t)stream_data[4] | ((size_t)stream_data[5] << 8);
                if (sizes[0]+sizes[1] > total-6 || sizes[2] > total-6-sizes[0]-sizes[1]) return 0;
                sizes[3] = total-6-sizes[0]-sizes[1]-sizes[2];
                per = (regen+3U)/4U;
                if (regen < 3U*per) return 0;
                stream_data += 6;
                for (i = 0; i < 4; ++i) {
                    size_t wanted = i == 3 ? regen-3U*per : per;
                    if (!huf_decode_stream(&d->huf, stream_data+at, sizes[i],
                                           d->literals+i*per, wanted)) return 0;
                    at += sizes[i];
                }
            }
            p = payload+compressed;
        }
    }
    *literal_count = regen; *pp = p; return 1;
}

static int decode_compressed_block(ZDecoder *d, const u8 *src, size_t size) {
    const u8 *p = src, *end = src+size; size_t literals;
    return decode_literals(d, &p, end, &literals) && p <= end &&
           decode_sequences(d, p, end, literals) && d->out_pos <= d->block_limit;
}

static u32 read32le(const u8 *p) {
    return (u32)p[0] | ((u32)p[1] << 8) | ((u32)p[2] << 16) | ((u32)p[3] << 24);
}

static int parse_dict(const void *dict_data, size_t dict_len, ZDict *dict) {
    const u8 *buf = (const u8 *)dict_data, *p, *end;
    ZReader r;
    memset(dict, 0, sizeof(*dict));
    if (dict_data == NULL || dict_len == 0) return 1;
    if (dict_len < 8) return 0;
    if (read32le(buf) != ZSTD_DICT_MAGIC) {
        dict->content = buf; dict->content_len = dict_len;
        dict->rep[0] = 1; dict->rep[1] = 4; dict->rep[2] = 8;
        return 1;
    }
    r.p = buf+4; r.end = buf+dict_len; r.error = 0;
    dict->id = rdle(&r, 4);
    if (r.error || dict->id == 0) return 0;
    p = r.p; end = r.end;
    if (!huf_read_table(&p, end, &dict->huf) ||
        !fse_read_table(&p, end, &dict->of, 31, 8) ||
        !fse_read_table(&p, end, &dict->ml, 52, 9) ||
        !fse_read_table(&p, end, &dict->ll, 35, 9)) return 0;
    r.p = p;
    dict->rep[0] = rdle(&r, 4); dict->rep[1] = rdle(&r, 4); dict->rep[2] = rdle(&r, 4);
    if (r.error || dict->rep[0] == 0 || dict->rep[1] == 0 || dict->rep[2] == 0) return 0;
    dict->content = r.p; dict->content_len = (size_t)(r.end-r.p);
    if (dict->rep[0] >= dict->content_len || dict->rep[1] >= dict->content_len ||
        dict->rep[2] >= dict->content_len) return 0;
    dict->formatted = 1;
    return 1;
}

static void begin_frame(ZDecoder *d, const ZDict *dict, u64 window) {
    d->frame_start = d->out_pos; d->window_size = window;
    d->dict_content = dict->content; d->dict_len = dict->content_len;
    d->rep[0] = dict->rep[0] ? dict->rep[0] : 1;
    d->rep[1] = dict->rep[1] ? dict->rep[1] : 4;
    d->rep[2] = dict->rep[2] ? dict->rep[2] : 8;
    memset(&d->huf, 0, sizeof(d->huf));
    memset(&d->ll, 0, sizeof(d->ll)); memset(&d->of, 0, sizeof(d->of));
    memset(&d->ml, 0, sizeof(d->ml));
    if (dict->formatted) { d->huf = dict->huf; d->ll = dict->ll; d->of = dict->of; d->ml = dict->ml; }
}

static int decode_frame(ZDecoder *d, ZReader *r, const ZDict *dict) {
    u8 descriptor;
    unsigned fcs_flag, did_flag, did_size, fcs_size;
    int single, checksum, last = 0;
    u64 window, fcs = 0;
    u32 did = 0;
    unsigned blocks = 0;
    if (!need(r, 1)) return 0;
    descriptor = rd8(r); fcs_flag = descriptor >> 6; single = (descriptor & 0x20U) != 0;
    checksum = (descriptor & 0x04U) != 0; did_flag = descriptor & 3U;
    if (descriptor & 0x08U) return 0;
    if (single) window = 0;
    else {
        u8 wd; u64 base;
        if (!need(r, 1)) return 0;
        wd = rd8(r); base = (u64)1 << (10U + (wd >> 3));
        window = base + (base >> 3) * (wd & 7U);
    }
    did_size = did_flag == 0 ? 0 : (did_flag == 3 ? 4 : did_flag);
    if (did_size) did = rdle(r, did_size);
    fcs_size = fcs_flag == 0 ? (single ? 1U : 0U) :
               (fcs_flag == 1 ? 2U : (fcs_flag == 2 ? 4U : 8U));
    if (fcs_size) { fcs = rdle64(r, fcs_size); if (fcs_size == 2) fcs += 256; }
    if (r->error || (!single && window == 0)) return 0;
    if (single) window = fcs;
    if (did != 0 && (!dict->formatted || dict->id != did)) return 0;
    begin_frame(d, dict, window);
    do {
        u32 header, bsize; unsigned type;
        d->block_start = d->out_pos;
        d->block_limit = d->out_pos + BLOCK_SIZE_MAX;
        if (d->block_limit < d->out_pos || d->block_limit > d->dst_len) d->block_limit = d->dst_len;
        if (!need(r, 3)) return 0;
        header = rdle(r, 3); last = header & 1U; type = (header >> 1) & 3U; bsize = header >> 3;
        if (++blocks > 1000000U || type == BLOCK_TYPE_RESERVED || bsize > BLOCK_SIZE_MAX || bsize > window)
            return 0;
        if (type == BLOCK_TYPE_RAW) {
            if (!need(r, bsize) || !emit_bytes(d, r->p, bsize)) return 0;
            r->p += bsize;
        } else if (type == BLOCK_TYPE_RLE) {
            u8 value; size_t i;
            if (!need(r, 1)) return 0; value = rd8(r);
            for (i = 0; i < bsize; ++i) if (!emit_byte(d, value)) return 0;
        } else {
            if (!need(r, bsize) || !decode_compressed_block(d, r->p, bsize)) return 0;
            r->p += bsize;
        }
        if (d->out_pos-d->block_start > BLOCK_SIZE_MAX) return 0;
    } while (!last);
    if (checksum) {
        u32 stored, actual;
        if (!need(r, 4)) return 0;
        stored = rdle(r, 4);
        actual = (u32)XXH64(d->dst+d->frame_start, d->out_pos-d->frame_start, 0);
        if (stored != actual) return 0;
    }
    return !d->error && (!fcs_size || (u64)(d->out_pos-d->frame_start) == fcs);
}

size_t ZSTD_decompress(void *dst, size_t dst_len, const void *src, size_t src_len,
                       const void *dict_data, size_t dict_len) {
    ZReader r; ZDecoder d; ZDict dict; size_t result = 0;
    if (dst == NULL || src == NULL || src_len == 0 || !parse_dict(dict_data, dict_len, &dict)) return 0;
    memset(&d, 0, sizeof(d)); d.dst = (u8 *)dst; d.dst_len = dst_len;
    d.literals = (u8 *)malloc(BLOCK_SIZE_MAX);
    if (!d.literals) return 0;
    r.p = (const u8 *)src; r.end = r.p+src_len; r.error = 0;
    while (r.p < r.end) {
        u32 magic, skip;
        if (!need(&r, 4)) goto finish;
        magic = rdle(&r, 4);
        if ((magic & ZSTD_SKIPPABLE_MASK) == ZSTD_SKIPPABLE_MAGIC) {
            skip = rdle(&r, 4);
            if (r.error || !need(&r, skip)) goto finish;
            r.p += skip; continue;
        }
        if (magic != ZSTD_MAGIC || !decode_frame(&d, &r, &dict)) goto finish;
    }
    result = d.out_pos;
finish:
    free(d.literals); return result;
}

size_t ZSTD_get_decompressed_size(const void *src, size_t src_len) {
    const u8 *p = (const u8 *)src, *end;
    u32 magic; u8 descriptor; unsigned fcs_flag, fcs_size, did_flag, did_size, i;
    int single; u64 size = 0;
    if (!src || src_len < 4) return (size_t)-1;
    end = p+src_len;
    for (;;) {
        if ((size_t)(end-p) < 4) return (size_t)-1;
        magic = read32le(p); p += 4;
        if ((magic & ZSTD_SKIPPABLE_MASK) != ZSTD_SKIPPABLE_MAGIC) break;
        if ((size_t)(end-p) < 4) return (size_t)-1;
        size = read32le(p); p += 4;
        if (size > (u64)(end-p)) return (size_t)-1;
        p += (size_t)size;
    }
    if (magic != ZSTD_MAGIC || p >= end) return (size_t)-1;
    descriptor = *p++; if (descriptor & 0x08U) return (size_t)-1;
    fcs_flag = descriptor >> 6; single = (descriptor & 0x20U) != 0;
    if (!single) { if (p >= end) return (size_t)-1; ++p; }
    did_flag = descriptor & 3U; did_size = did_flag == 0 ? 0 : (did_flag == 3 ? 4 : did_flag);
    if ((size_t)(end-p) < did_size) return (size_t)-1;
    p += did_size;
    fcs_size = fcs_flag == 0 ? (single ? 1U : 0U) :
               (fcs_flag == 1 ? 2U : (fcs_flag == 2 ? 4U : 8U));
    if (fcs_size == 0 || (size_t)(end-p) < fcs_size) return (size_t)-1;
    size = 0;
    for (i = 0; i < fcs_size; ++i) size |= (u64)p[i] << (8U*i);
    if (fcs_size == 2) size += 256;
    return size > (u64)SIZE_MAX ? (size_t)-1 : (size_t)size;
}
