import { redirect } from "next/navigation";
import { getPipeline } from "@/lib/pipeline";

export default function Home() {
  const { agents } = getPipeline();
  redirect(`/vendedor/${agents[0].slug}`);
}
