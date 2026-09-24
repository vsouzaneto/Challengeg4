import { pool } from "./database/pool.js";
import { hashPassword } from "./security.js";

export interface ApplicationUser {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface UserRow {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  created_at: Date;
  updated_at: Date;
}

function mapUser(row: UserRow): ApplicationUser {
  return {
    id: row.id,
    name: row.name,
    email: row.email,
    isActive: row.is_active,
    createdAt: row.created_at.toISOString(),
    updatedAt: row.updated_at.toISOString(),
  };
}

export class UserConflictError extends Error {}
export class SelfDeactivationError extends Error {}

function emailAddress(email: string): string {
  return email.trim().toLocaleLowerCase("pt-BR");
}

export async function listUsers(): Promise<ApplicationUser[]> {
  const { rows } = await pool.query<UserRow>(
    "SELECT id, name, email, is_active, created_at, updated_at FROM users ORDER BY name, email",
  );
  return rows.map(mapUser);
}

export async function createUser(input: { name: string; email: string; password: string }): Promise<ApplicationUser> {
  const email = emailAddress(input.email);
  const passwordHash = await hashPassword(input.password);

  try {
    const { rows } = await pool.query<UserRow>(
      `INSERT INTO users (name, email, password_hash)
       VALUES ($1, $2, $3)
       RETURNING id, name, email, is_active, created_at, updated_at`,
      [input.name, email, passwordHash],
    );
    const user = rows[0];
    if (!user) {
      throw new Error("User creation did not return a record");
    }
    return mapUser(user);
  } catch (error) {
    if (typeof error === "object" && error !== null && "code" in error && error.code === "23505") {
      throw new UserConflictError("Já existe um usuário com este e-mail.");
    }
    throw error;
  }
}

export async function updateUser(
  actorId: number,
  userId: number,
  input: { name: string; email: string; isActive: boolean },
): Promise<ApplicationUser | null> {
  if (actorId === userId && !input.isActive) {
    throw new SelfDeactivationError("Você não pode desativar a própria conta.");
  }

  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rows } = await client.query<UserRow>(
      `UPDATE users
       SET name = $1, email = $2, is_active = $3, updated_at = NOW()
       WHERE id = $4
       RETURNING id, name, email, is_active, created_at, updated_at`,
      [input.name, emailAddress(input.email), input.isActive, userId],
    );
    const user = rows[0];
    if (!user) {
      await client.query("ROLLBACK");
      return null;
    }
    if (!input.isActive) {
      await client.query("DELETE FROM sessions WHERE user_id = $1", [userId]);
    }
    await client.query("COMMIT");
    return mapUser(user);
  } catch (error) {
    await client.query("ROLLBACK");
    if (typeof error === "object" && error !== null && "code" in error && error.code === "23505") {
      throw new UserConflictError("Já existe um usuário com este e-mail.");
    }
    throw error;
  } finally {
    client.release();
  }
}

export async function resetUserPassword(userId: number, password: string): Promise<boolean> {
  const passwordHash = await hashPassword(password);
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rowCount } = await client.query(
      "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
      [passwordHash, userId],
    );
    if (!rowCount) {
      await client.query("ROLLBACK");
      return false;
    }
    await client.query("DELETE FROM sessions WHERE user_id = $1", [userId]);
    await client.query("COMMIT");
    return true;
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}
