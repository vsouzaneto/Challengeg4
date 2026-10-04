import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import crypto from "node:crypto";
export { hashPassword, verifyPassword } from "./password";

// Sessão stateless: cookie assinado (HMAC-SHA256). Não depende do banco — necessário porque, na
// Vercel sem Turso, cada instância serverless tem sua própria cópia do SQLite em /tmp.
export type User = { id: number; name: string; email: string; role: string };
const COOKIE = "sos_session";
const TTL = 1000 * 60 * 60 * 24 * 7;
const SECRET = process.env.SESSION_SECRET ?? "dev-only-secret-change-me";

const sign = (payload: string) => crypto.createHmac("sha256", SECRET).update(payload).digest("base64url");

export async function createSession(user: User) {
  const payload = Buffer.from(JSON.stringify({ ...user, exp: Date.now() + TTL })).toString("base64url");
  (await cookies()).set(COOKIE, `${payload}.${sign(payload)}`, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: TTL / 1000 });
}

export async function destroySession() {
  (await cookies()).delete(COOKIE);
}

export async function currentUser(): Promise<User | null> {
  const raw = (await cookies()).get(COOKIE)?.value;
  if (!raw) return null;
  const [payload, sig] = raw.split(".");
  if (!payload || !sig) return null;
  const expected = sign(payload);
  if (sig.length !== expected.length || !crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) return null;
  try {
    const data = JSON.parse(Buffer.from(payload, "base64url").toString()) as User & { exp: number };
    if (data.exp < Date.now()) return null;
    return { id: data.id, name: data.name, email: data.email, role: data.role };
  } catch {
    return null;
  }
}

export async function requireUser(): Promise<User> {
  const u = await currentUser();
  if (!u) redirect("/login");
  return u;
}
