import { notFound } from "next/navigation";

// Server component that calls notFound() — should produce 404
export default function Page() {
  notFound();
}
