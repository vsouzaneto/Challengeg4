import { config } from "./config.js";
import { pool } from "./database/pool.js";
import { createSessionToken, hashPassword, hashSessionToken, verifyPassword } from "./security.js";

export interface SessionUser {
  id: number;
  name: string;
  email: string;
}

interface UserRow {
  id: number;
  name: string;
  email: string;
  password_hash: string;
  is_active: boolean;
}

interface LoginAttempt {
  count: number;
  resetAt: number;
}

const loginAttempts = new Map<string, LoginAttempt>();
const maximumAttempts = 5;
const attemptWindowMs = 15 * 60 * 1000;
const dummyHash = hashPassword("lead-scorer-dummy-password");
const maximumConcurrentKdf = 4;
const kdfQueue: Array<() => void> = [];
let activeKdf = 0;

export class LoginRateLimitError extends Error {}

function normalizedEmail(email: string): string {
  return email.trim().toLocaleLowerCase("pt-BR");
}

function attemptKey(email: string, source: string): string {
  return `${source}\u0000${normalizedEmail(email)}`;
}

export function reserveLoginAttempt(email: string, source: string): void {
  const key = attemptKey(email, source);
  const now = Date.now();
  const current = loginAttempts.get(key);
  if (!current || current.resetAt <= now) {
    loginAttempts.set(key, { count: 1, resetAt: now + attemptWindowMs });
    return;
  }
  if (current.count >= maximumAttempts) {
    throw new LoginRateLimitError("Muitas tentativas de login. Aguarde antes de tentar novamente.");
  }
  loginAttempts.set(key, { ...current, count: current.count + 1 });
}

export function clearLoginAttempts(email: string, source: string): void {
  loginAttempts.delete(attemptKey(email, source));
}

async function withKdfLimit<T>(operation: () => Promise<T>): Promise<T> {
  if (activeKdf >= maximumConcurrentKdf) {
    await new Promise<void>((resolve) => kdfQueue.push(resolve));
  }
  activeKdf += 1;
  try {
    return await operation();
  } finally {
    activeKdf -= 1;
    kdfQueue.shift()?.();
  }
}

export async function authenticateUser(email: string, password: string): Promise<SessionUser | null> {
  const { rows } = await pool.query<UserRow>(
    "SELECT id, name, email, password_hash, is_active FROM users WHERE email = $1",
    [normalizedEmail(email)],
  );
  const user = rows[0];

  return withKdfLimit(async () => {
    if (!user || !user.is_active) {
      await verifyPassword(password, await dummyHash);
      return null;
    }
    if (!(await verifyPassword(password, user.password_hash))) {
      return null;
    }
    return { id: user.id, name: user.name, email: user.email };
  });
}

export async function createSession(userId: number, currentToken?: string): Promise<{ token: string; maxAge: number }> {
  const token = createSessionToken();
  const expiresAt = new Date(Date.now() + config.sessionMaxAgeSeconds * 1000);
  const client = await pool.connect();

  try {
    await client.query("BEGIN");
    await client.query("DELETE FROM sessions WHERE expires_at <= NOW()");
    if (currentToken) {
      const currentHash = hashSessionToken(currentToken);
      const rotated = await client.query(
        "UPDATE sessions SET token_hash = $1, expires_at = $2, created_at = NOW() WHERE token_hash = $3 AND user_id = $4",
        [hashSessionToken(token), expiresAt, currentHash, userId],
      );
      if (rotated.rowCount) {
        await client.query("COMMIT");
        return { token, maxAge: config.sessionMaxAgeSeconds };
      }
      await client.query("DELETE FROM sessions WHERE token_hash = $1", [currentHash]);
    }
    await client.query(
      "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES ($1, $2, $3)",
      [hashSessionToken(token), userId, expiresAt],
    );
    await client.query("COMMIT");
    return { token, maxAge: config.sessionMaxAgeSeconds };
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

export async function getSessionUser(token: string): Promise<SessionUser | null> {
  const { rows } = await pool.query<SessionUser>(
    `SELECT u.id, u.name, u.email
     FROM sessions s
     JOIN users u ON u.id = s.user_id
     WHERE s.token_hash = $1 AND s.expires_at > NOW() AND u.is_active = TRUE`,
    [hashSessionToken(token)],
  );
  return rows[0] ?? null;
}

export async function deleteSession(token: string): Promise<void> {
  await pool.query("DELETE FROM sessions WHERE token_hash = $1", [hashSessionToken(token)]);
}
