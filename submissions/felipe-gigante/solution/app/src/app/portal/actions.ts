"use server";
import { redirect } from "next/navigation";
import { z } from "zod";
import { createPortalTicket, customerReply, getTicketByToken, submitCsat } from "@/lib/tickets";

const NewTicket = z.object({
  name: z.string().trim().min(2).max(80),
  email: z.email().max(120),
  message: z.string().trim().min(5).max(4000),
  channel: z.enum(["Chat", "Email", "Social media", "Phone"]).default("Chat"),
});

export async function openTicketAction(_: { error?: string } | undefined, form: FormData) {
  const parsed = NewTicket.safeParse(Object.fromEntries(form));
  if (!parsed.success) return { error: "Preencha nome, e-mail válido e uma mensagem com pelo menos 5 caracteres." };
  const { token } = await createPortalTicket(parsed.data);
  redirect(`/portal/t/${token}`);
}

export async function sendCustomerMessage(token: string, body: string) {
  const t = await getTicketByToken(token);
  if (!t || !body.trim() || ["closed"].includes(t.status)) return;
  await customerReply(t.id, body.trim().slice(0, 4000));
}

export async function sendCsat(token: string, score: number, comment: string) {
  const t = await getTicketByToken(token);
  if (!t || t.csat || score < 1 || score > 5) return;
  await submitCsat(t.id, Math.round(score), comment.slice(0, 1000));
}
