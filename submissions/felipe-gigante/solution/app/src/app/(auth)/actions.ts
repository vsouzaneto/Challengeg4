"use server";
import { redirect } from "next/navigation";
import { z } from "zod";
import { one, run } from "@/lib/db";
import { createSession, destroySession, hashPassword, verifyPassword } from "@/lib/auth";

export type AuthState = { error?: string } | undefined;

export async function login(_: AuthState, form: FormData): Promise<AuthState> {
  const email = String(form.get("email") ?? "").trim().toLowerCase();
  const password = String(form.get("password") ?? "");
  const u = await one<{ id: number; name: string; email: string; role: string; password_hash: string }>("SELECT id, name, email, role, password_hash FROM users WHERE email=?", [email]);
  if (!u || !verifyPassword(password, u.password_hash)) return { error: "E-mail ou senha inválidos." };
  await createSession({ id: u.id, name: u.name, email: u.email, role: u.role });
  redirect("/dashboard");
}

const SignupSchema = z.object({
  name: z.string().trim().min(2, "Informe seu nome."),
  email: z.email("E-mail inválido.").transform((e) => e.toLowerCase()),
  password: z.string().min(8, "A senha precisa de pelo menos 8 caracteres."),
  role: z.enum(["agent", "manager", "knowledge"]),
});

export async function signup(_: AuthState, form: FormData): Promise<AuthState> {
  const parsed = SignupSchema.safeParse(Object.fromEntries(form));
  if (!parsed.success) return { error: parsed.error.issues[0].message };
  const { name, email, password, role } = parsed.data;
  if (await one("SELECT id FROM users WHERE email=?", [email])) return { error: "Já existe uma conta com esse e-mail." };
  const r = await run("INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?,?,?,?,?)", [name, email, hashPassword(password), role, Date.now()]);
  await createSession({ id: Number(r.lastInsertRowid), name, email, role });
  redirect("/dashboard");
}

export async function logout() {
  await destroySession();
  redirect("/login");
}
