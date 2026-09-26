import { redirect } from "next/navigation";

// Server component that calls redirect() — should produce 307
export default function Page() {
  redirect("/nextjs-compat/nav-redirect-result");
}
