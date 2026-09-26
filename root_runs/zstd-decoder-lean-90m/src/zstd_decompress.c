/* RFC 8878 Zstandard decoder.  This implementation is self-contained. */
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <xxhash.h>
#include "zstd_decompress.h"

#define ERR 0
#define FSE_MAX 512
typedef struct { const u8 *p,*end; } In;
typedef struct { const u8 *p; size_t bits,pos; } FwdBits;
typedef struct { const u8 *p; size_t pos; } RevBits;
typedef struct { u8 sym,nb; u16 base; } FSEEnt;
typedef struct { int log,size,valid,rle; u8 r; FSEEnt e[FSE_MAX]; } FSE;
typedef struct { u8 sym,nb; } HEnt;
typedef struct { HEnt e[1<<11]; int maxbits,valid; } Huff;
typedef struct { u8 *out; size_t cap,n,frame_start,window; const u8 *dict; size_t dlen; u32 rep[3]; Huff huff; FSE ll,ml,of; } DCtx;

static u32 rd32(const u8*p){return (u32)p[0]|((u32)p[1]<<8)|((u32)p[2]<<16)|((u32)p[3]<<24);}
static u64 rdle(const u8*p,unsigned n){u64 v=0;unsigned i;for(i=0;i<n;i++)v|=(u64)p[i]<<(8*i);return v;}
static int get(In*i,const u8**p,size_t n){if((size_t)(i->end-i->p)<n)return 0;*p=i->p;i->p+=n;return 1;}
static int lg2u(unsigned x){int n=-1;while(x){x>>=1;n++;}return n;}
static unsigned fb_peek(FwdBits*b,unsigned n){unsigned v=0,i;for(i=0;i<n;i++)if(b->pos+i<b->bits)v|=((b->p[(b->pos+i)>>3]>>((b->pos+i)&7))&1u)<<i;return v;}
static int fb_read(FwdBits*b,unsigned n,unsigned*v){if(b->pos+n>b->bits)return 0;*v=fb_peek(b,n);b->pos+=n;return 1;}
/* Reverse Zstd bitstream.  Bits nearest the end form high-to-low result. */
static int rb_init(RevBits*b,const u8*p,size_t n){unsigned x,k;if(!n||!p[n-1])return 0;x=p[n-1];k=7;while(k&&!(x&(1u<<k)))k--;b->p=p;b->pos=(n-1)*8+k;return 1;}
static int rb_read(RevBits*b,unsigned n,unsigned*v){unsigned x=0;if(n>b->pos)return 0;while(n--){--b->pos;x=(x<<1)|((b->p[b->pos>>3]>>(b->pos&7))&1u);}*v=x;return 1;}
static int rb_empty(const RevBits*b){return b->pos==0;}

/* FSE normalized count header (forward, LSB-first). */
static int fse_counts(const u8*p,size_t n,int maxsym,short*norm,int*logp,size_t*used){
 FwdBits b;int log,remaining,threshold,nb,s=0,prev0=0;unsigned v,low,max,z;
 memset(norm,0,(maxsym+1)*sizeof(*norm));if(!n)return 0;log=(p[0]&15)+5;if(log<5||log>9)return 0;
 b.p=p;b.bits=n*8;b.pos=4;remaining=(1<<log)+1;threshold=1<<log;nb=log+1;
 while(remaining>1&&s<=maxsym){
  if(prev0){z=0;do{if(!fb_read(&b,2,&v))return 0;z+=v;}while(v==3);while(z--){if(++s>maxsym)return 0;norm[s]=0;}}
  max=(unsigned)(2*threshold-1-remaining);if(!fb_read(&b,(unsigned)nb,&v))return 0;low=v&(unsigned)(threshold-1);
  if(low<max){v=low;b.pos--;}else{v&=(unsigned)(2*threshold-1);if(v>=(unsigned)threshold)v-=max;}
  norm[s]=(short)((int)v-1);remaining-=norm[s]<0?-norm[s]:norm[s];prev0=(norm[s]==0);s++;
  while(remaining<threshold){threshold>>=1;if(--nb<1)return 0;}
 }
 if(remaining!=1||s<1)return 0;*used=(b.pos+7)/8;*logp=log;return 1;
}
static int fse_build(FSE*f,const short*norm,int maxsym,int log){
 int size=1<<log,high=size-1,pos=0,step=(size>>1)+(size>>3)+3,next[256],i,s,total=0;
 if(log<5||log>9||size>FSE_MAX)return 0;for(s=0;s<=maxsym;s++){next[s]=norm[s]<0?1:norm[s];total+=norm[s]<0?1:norm[s];}if(total!=size)return 0;
 for(i=0;i<size;i++)f->e[i].sym=255;for(s=0;s<=maxsym;s++)if(norm[s]<0)f->e[high--].sym=(u8)s;
 for(s=0;s<=maxsym;s++)for(i=0;i<norm[s];i++){while(f->e[pos].sym!=255)pos=(pos+step)&(size-1);f->e[pos].sym=(u8)s;pos=(pos+step)&(size-1);}
 for(i=0;i<size;i++){int ns=next[f->e[i].sym]++,hb=lg2u((unsigned)ns),nb=log-hb;f->e[i].nb=(u8)nb;f->e[i].base=(u16)((ns<<nb)-size);}
 f->log=log;f->size=size;f->valid=1;f->rle=0;return 1;
}
static int fse_custom(In*in,FSE*f,int max){short n[256];int l;size_t u;const u8*p;if(!fse_counts(in->p,(size_t)(in->end-in->p),max,n,&l,&u)||!get(in,&p,u))return 0;return fse_build(f,n,max,l);}
static int fse_rle(In*in,FSE*f){const u8*p;if(!get(in,&p,1))return 0;memset(f,0,sizeof(*f));f->valid=f->rle=1;f->r=p[0];return 1;}
static int fse_state(const FSE*f,RevBits*b,unsigned*st){return f->rle?((*st=0),1):rb_read(b,(unsigned)f->log,st);}
static int fse_sym(const FSE*f,unsigned st,unsigned*s){if(f->rle){*s=f->r;return 1;}if(st>=(unsigned)f->size)return 0;*s=f->e[st].sym;return 1;}
static int fse_next(const FSE*f,RevBits*b,unsigned*st){unsigned x;if(f->rle)return 1;if(!rb_read(b,f->e[*st].nb,&x))return 0;*st=f->e[*st].base+x;return 1;}
static int fse_predef(FSE*ll,FSE*ml,FSE*of){
 static const short L[36]={4,3,2,2,2,2,2,2,2,2,2,2,2,1,1,1,2,2,2,2,2,2,2,2,2,3,2,1,1,1,1,1,-1,-1,-1,-1};
 static const short M[53]={1,4,3,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1};
 static const short O[29]={1,1,1,1,1,1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1};
 return fse_build(ll,L,35,6)&&fse_build(ml,M,52,6)&&fse_build(of,O,28,5);
}

static int huff_from_weights(Huff*h,const u8*w,int n){
 int sum=0,maxw=0,i,maxbits,lastw,full=1,code=0,weight;
 for(i=0;i<n;i++) if(w[i]) { sum+=1<<(w[i]-1); if(w[i]>maxw)maxw=w[i]; }
 if(!sum) return 0;
 while(full<=sum) full<<=1;
 maxbits=lg2u((unsigned)full); lastw=lg2u((unsigned)(full-sum))+1;
 if(lastw<=0||n>255||maxbits>11||lastw>maxbits) return 0;
 memset(h->e,0,sizeof(h->e));
 /* RFC codes are canonical in reverse-bit order: allocate longest first,
    then shift the running code right as code length decreases. */
 for(weight=1;weight<=maxbits;weight++) {
   int len=maxbits+1-weight;
   for(i=0;i<=n;i++) {
     int iw=(i==n)?lastw:w[i];
     if(iw==weight) { int fill=1<<(maxbits-len),k;
       if(code >= (1<<len)) return 0;
       for(k=0;k<fill;k++) { int x=(code<<(maxbits-len))+k; h->e[x].sym=(u8)i; h->e[x].nb=(u8)len; }
       code++;
     }
   }
   code>>=1;
 }
 h->maxbits=maxbits;h->valid=1;return 1;
}
static int huff_tree(In*in,Huff*h){
 const u8*p,*q;u8 w[256];int n=0,i;if(!get(in,&p,1))return 0;
 if(p[0]>=128){n=p[0]-127;if(!get(in,&p,(size_t)((n+1)/2)))return 0;for(i=0;i<n;i++)w[i]=(i&1)?(p[i/2]&15):(p[i/2]>>4);return huff_from_weights(h,w,n);}
 else {size_t hs=p[0],used;FSE f;short norm[256];int log,wi=0;RevBits b;unsigned s1,s2,x;if(!get(in,&q,hs)||!fse_counts(q,hs,255,norm,&log,&used)||!fse_build(&f,norm,255,log)||used>=hs||!rb_init(&b,q+used,hs-used))return 0;if(!fse_state(&f,&b,&s1)||!fse_state(&f,&b,&s2))return 0;while(!rb_empty(&b)&&wi<254){if(!fse_sym(&f,s1,&x))return 0;w[wi++]=(u8)x;if(!rb_empty(&b)&&!fse_next(&f,&b,&s1))break;if(wi>=254)break;if(!fse_sym(&f,s2,&x))return 0;w[wi++]=(u8)x;if(!rb_empty(&b)&&!fse_next(&f,&b,&s2))break;}if(wi==254){if(!fse_sym(&f,s1,&x))return 0;w[wi++]=(u8)x;}else{if(wi>253)return 0;if(!fse_sym(&f,s1,&x))return 0;w[wi++]=(u8)x;if(!fse_sym(&f,s2,&x))return 0;w[wi++]=(u8)x;}return huff_from_weights(h,w,wi);}
}
static int huff_stream(const Huff*h,const u8*p,size_t n,u8*out,size_t want){RevBits b;size_t i;unsigned x,j;if(!h->valid||!rb_init(&b,p,n))return 0;for(i=0;i<want;i++){if(b.pos<(size_t)h->maxbits)return 0;x=0;for(j=0;j<(unsigned)h->maxbits;j++)x=(x<<1)|((b.p[(b.pos-1-j)>>3]>>((b.pos-1-j)&7))&1u);if(!h->e[x].nb||b.pos<h->e[x].nb)return 0;b.pos-=h->e[x].nb;out[i]=h->e[x].sym;}return rb_empty(&b);}

static int literals(DCtx*d,In*in,u8**lit,size_t*ln){
 const u8*h,*p;unsigned t,fmt;size_t regen,comp,streams=1,i;u8*z;if(!get(in,&h,1))return 0;t=h[0]&3;fmt=(h[0]>>2)&3;
 if(t<2){if(fmt==0||fmt==2)regen=h[0]>>3;else if(fmt==1){if(!get(in,&p,1))return 0;regen=(h[0]>>4)|((size_t)p[0]<<4);}else{if(!get(in,&p,2))return 0;regen=(h[0]>>4)|((size_t)p[0]<<4)|((size_t)p[1]<<12);}z=(u8*)malloc(regen?regen:1);if(!z)return 0;if(t==0){if(!get(in,&p,regen)){free(z);return 0;}memcpy(z,p,regen);}else{if(!get(in,&p,1)){free(z);return 0;}memset(z,p[0],regen);}*lit=z;*ln=regen;return 1;}
 if(fmt<2){u32 v;if(!get(in,&p,2))return 0;v=(u32)h[0]|((u32)p[0]<<8)|((u32)p[1]<<16);regen=(v>>4)&1023;comp=(v>>14)&1023;streams=fmt?4:1;}else if(fmt==2){u32 v;if(!get(in,&p,3))return 0;v=(u32)h[0]|((u32)p[0]<<8)|((u32)p[1]<<16)|((u32)p[2]<<24);regen=(v>>4)&16383;comp=(v>>18)&16383;streams=4;}else{u64 v;if(!get(in,&p,4))return 0;v=(u64)h[0]|((u64)p[0]<<8)|((u64)p[1]<<16)|((u64)p[2]<<24)|((u64)p[3]<<32);regen=(v>>4)&262143;comp=(v>>22)&262143;streams=4;}
 if((size_t)(in->end-in->p)<comp)return 0;{In q={in->p,in->p+comp};in->p+=comp;if(t==2&&!huff_tree(&q,&d->huff))return 0;if(!d->huff.valid)return 0;z=(u8*)malloc(regen?regen:1);if(!z)return 0;if(streams==1){if(!huff_stream(&d->huff,q.p,(size_t)(q.end-q.p),z,regen)){free(z);return 0;}}else{const u8*j;size_t sz[4],off=0,each=(regen+3)/4;if(!get(&q,&j,6)){free(z);return 0;}sz[0]=j[0]|((size_t)j[1]<<8);sz[1]=j[2]|((size_t)j[3]<<8);sz[2]=j[4]|((size_t)j[5]<<8);if(sz[0]+sz[1]+sz[2]>(size_t)(q.end-q.p)){free(z);return 0;}sz[3]=(size_t)(q.end-q.p)-sz[0]-sz[1]-sz[2];for(i=0;i<4;i++){size_t w=i==3?regen-off:each;if(!huff_stream(&d->huff,q.p+off,sz[i],z+off,w)){free(z);return 0;}off+=w;}}}
 *lit=z;*ln=regen;return 1;
}
static unsigned llbase(unsigned c,unsigned*b){if(c<16){*b=0;return c;}if(c<20){*b=1;return 16+2*(c-16);}if(c<22){*b=2;return 24+4*(c-20);}if(c<24){*b=3;return 32+8*(c-22);}if(c==24){*b=4;return 48;}if(c==25){*b=6;return 64;}*b=c-19;return 1u<<(c-19);}
static unsigned mlbase(unsigned c,unsigned*b){if(c<32){*b=0;return c+3;}if(c<36){*b=1;return 35+2*(c-32);}if(c<38){*b=2;return 43+4*(c-36);}if(c<40){*b=3;return 51+8*(c-38);}if(c<42){*b=4;return 67+16*(c-40);}if(c==42){*b=5;return 99;}if(c==43){*b=7;return 131;}*b=c-36;return (1u<<(c-36))+3;}
static int put(DCtx*d,u8 x){if(d->n>=d->cap)return 0;d->out[d->n++]=x;return 1;}
static int match(DCtx*d,size_t off,size_t n){size_t i;for(i=0;i<n;i++){if(!off)return 0;if(off<=d->n-d->frame_start){if(!put(d,d->out[d->n-off]))return 0;}else{size_t back=off-(d->n-d->frame_start);if(back>d->dlen||!put(d,d->dict[d->dlen-back]))return 0;}}return 1;}
static int sequences(DCtx*d,In*in,u8*lit,size_t ln){
 const u8*p;unsigned ns,mode,ls,os,ms,a,b,c,x;size_t li=0,i;RevBits rb;FSE oldl=d->ll,oldm=d->ml,oldo=d->of;if(!get(in,&p,1))return 0;if(!p[0]){for(i=0;i<ln;i++)if(!put(d,lit[i]))return 0;return 1;}if(p[0]<128)ns=p[0];else if(p[0]<255){unsigned q=p[0];if(!get(in,&p,1))return 0;ns=((q-128)<<8)|p[0];}else{if(!get(in,&p,2))return 0;ns=p[0]|((unsigned)p[1]<<8)|0x7f00;}if(!get(in,&p,1)||(p[0]&3))return 0;mode=p[0];ls=mode>>6;os=(mode>>4)&3;ms=(mode>>2)&3;
 if(ls==0||os==0||ms==0){FSE L,M,O;if(!fse_predef(&L,&M,&O))return 0;if(ls==0)d->ll=L;if(os==0)d->of=O;if(ms==0)d->ml=M;}if(ls==1&&!fse_rle(in,&d->ll))return 0;if(os==1&&!fse_rle(in,&d->of))return 0;if(ms==1&&!fse_rle(in,&d->ml))return 0;if(ls==2&&!fse_custom(in,&d->ll,35))return 0;if(os==2&&!fse_custom(in,&d->of,31))return 0;if(ms==2&&!fse_custom(in,&d->ml,52))return 0;if((ls==3&&!oldl.valid)||(os==3&&!oldo.valid)||(ms==3&&!oldm.valid))return 0;if(!rb_init(&rb,in->p,(size_t)(in->end-in->p)))return 0;in->p=in->end;if(!fse_state(&d->ll,&rb,&ls)||!fse_state(&d->of,&rb,&os)||!fse_state(&d->ml,&rb,&ms))return 0;
 for(i=0;i<ns;i++){unsigned lb,mb,ob,ll,ml,oval,off,origll;if(!fse_sym(&d->ll,ls,&a)||!fse_sym(&d->of,os,&b)||!fse_sym(&d->ml,ms,&c))return 0;ll=llbase(a,&lb);ml=mlbase(c,&mb);ob=b;if(!rb_read(&rb,ob,&x))return 0;oval=(1u<<ob)+x;if(!rb_read(&rb,mb,&x))return 0;ml+=x;if(!rb_read(&rb,lb,&x))return 0;ll+=x;origll=ll;if(li+ll>ln)return 0;while(ll--)if(!put(d,lit[li++]))return 0;if(oval<=3){if(oval==3&&origll==0){if(!d->rep[0])return 0;off=d->rep[0]-1;d->rep[2]=d->rep[1];d->rep[1]=d->rep[0];d->rep[0]=off;}else{unsigned k=oval-1+(origll==0);if(k>2)return 0;off=d->rep[k];while(k){d->rep[k]=d->rep[k-1];k--;}d->rep[0]=off;}}else{off=oval-3;d->rep[2]=d->rep[1];d->rep[1]=d->rep[0];d->rep[0]=off;}if(!match(d,off,ml))return 0;if(i+1<ns&&(!fse_next(&d->ll,&rb,&ls)||!fse_next(&d->ml,&rb,&ms)||!fse_next(&d->of,&rb,&os)))return 0;}
 if(!rb_empty(&rb))return 0;while(li<ln)if(!put(d,lit[li++]))return 0;return 1;
}
static int compressed(DCtx*d,const u8*p,size_t n){In in={p,p+n};u8*lit=NULL;size_t ln;int ok=literals(d,&in,&lit,&ln)&&sequences(d,&in,lit,ln);free(lit);return ok;}
static int frame(DCtx*d,In*in){
 const u8*p;u8 hd;unsigned fcs,did,ss,ck;u64 size=UINT64_MAX;int last=0;d->frame_start=d->n;d->rep[0]=1;d->rep[1]=4;d->rep[2]=8;d->huff.valid=0;d->ll.valid=d->ml.valid=d->of.valid=0;if(!get(in,&p,1))return 0;hd=p[0];if(hd&8)return 0;fcs=hd>>6;ss=(hd>>5)&1;ck=(hd>>2)&1;did=hd&3;if(!ss){if(!get(in,&p,1))return 0;d->window=(size_t)((1ULL<<(10+(p[0]>>3)))+((1ULL<<(10+(p[0]>>3)))/8)*(p[0]&7));}if(did&&!get(in,&p,did==3?4:did))return 0;{unsigned z=fcs==0?(ss?1:0):fcs==1?2:fcs==2?4:8;if(z){if(!get(in,&p,z))return 0;size=rdle(p,z)+(z==2?256:0);if(ss)d->window=(size_t)size;}}
 while(!last){u32 bh;unsigned typ,bs;if(!get(in,&p,3))return 0;bh=(u32)p[0]|((u32)p[1]<<8)|((u32)p[2]<<16);last=bh&1;typ=(bh>>1)&3;bs=bh>>3;if(typ==3||bs>BLOCK_SIZE_MAX)return 0;if(typ==0){if(!get(in,&p,bs))return 0;while(bs--)if(!put(d,*p++))return 0;}else if(typ==1){if(!get(in,&p,1))return 0;while(bs--)if(!put(d,p[0]))return 0;}else{if(!get(in,&p,bs)||!compressed(d,p,bs))return 0;}}
 if(ck){u32 want;if(!get(in,&p,4))return 0;want=rd32(p);if((u32)XXH64(d->out+d->frame_start,d->n-d->frame_start,0)!=want)return 0;}return size==UINT64_MAX||size==d->n-d->frame_start;
}
size_t ZSTD_get_decompressed_size(const void*src,size_t n){const u8*p=(const u8*)src;u8 h;unsigned f,ss,d;if(n<5||rd32(p)!=ZSTD_MAGIC)return(size_t)-1;p+=4;h=*p++;f=h>>6;ss=(h>>5)&1;d=h&3;if(h&8)return(size_t)-1;if(!ss){if(p>=(const u8*)src+n)return(size_t)-1;p++;}if((size_t)((const u8*)src+n-p)<(d==3?4:d))return(size_t)-1;p+=d==3?4:d;if(f==0){if(!ss)return(size_t)-1;if(p>=(const u8*)src+n)return(size_t)-1;return*p;}if(f==1){if((size_t)((const u8*)src+n-p)<2)return(size_t)-1;return 256+rdle(p,2);}if(f==2){if((size_t)((const u8*)src+n-p)<4)return(size_t)-1;return rdle(p,4);}if((size_t)((const u8*)src+n-p)<8)return(size_t)-1;return(size_t)rdle(p,8);}
size_t ZSTD_decompress(void*dst,size_t cap,const void*src,size_t n,const void*dict,size_t dn){In in={(const u8*)src,(const u8*)src+n};DCtx d;const u8*p;memset(&d,0,sizeof(d));d.out=(u8*)dst;d.cap=cap;d.dict=(const u8*)dict;d.dlen=dn;while(in.p<in.end){if(!get(&in,&p,4))return ERR;if((rd32(p)&0xfffffff0U)==0x184d2a50U){u32 z;if(!get(&in,&p,4))return ERR;z=rd32(p);if(!get(&in,&p,z))return ERR;continue;}if(rd32(p)!=ZSTD_MAGIC||!frame(&d,&in))return ERR;}return d.n;}
