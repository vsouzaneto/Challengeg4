import { redirect } from "next/navigation";
import { agentSlug, getPipeline } from "@/lib/pipeline";

export default function GerenteHome() {
  const { managers } = getPipeline();
  redirect(`/gerente/${agentSlug(managers[0])}`);
}
