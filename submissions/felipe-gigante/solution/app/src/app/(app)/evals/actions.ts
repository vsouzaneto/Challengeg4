"use server";
import { revalidatePath } from "next/cache";
import { requireUser } from "@/lib/auth";
import { runEvals } from "@/lib/evals";
import { llmEnabled } from "@/lib/ai/llm";

export async function runEvalsAction() {
  await requireUser();
  await runEvals({ useLlm: llmEnabled() });
  revalidatePath("/evals");
}
