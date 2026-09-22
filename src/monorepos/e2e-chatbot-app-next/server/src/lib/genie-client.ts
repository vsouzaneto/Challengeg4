import { getDatabricksToken } from '@chat-template/auth';
import {
  getLabRoom,
  isLabRoomAlias,
  listConfiguredLabRooms,
  type LabRoomAlias,
} from '@chat-template/core';

type GenieAttachment = {
  attachment_id?: string;
  text?: { content?: string };
  query?: { query?: string; description?: string };
};

type GenieMessage = {
  conversation_id?: string;
  message_id?: string;
  id?: string;
  status?: string;
  content?: string;
  attachments?: GenieAttachment[] | null;
  error?: { error?: string; type?: string } | null;
  message?: GenieMessage;
};

export type GenieReply = {
  conversationId: string;
  text: string;
  sql: string | null;
  status: string;
};

function workspaceHost(): string {
  const fromEnv = process.env.DATABRICKS_HOST?.replace(/\/$/, '');
  if (!fromEnv) {
    throw new Error('DATABRICKS_HOST is not configured');
  }
  return fromEnv;
}

async function bearerToken(): Promise<string> {
  const pat = process.env.DATABRICKS_TOKEN?.trim();
  if (pat) {
    return pat;
  }
  return getDatabricksToken();
}

async function genieFetch(path: string, init?: RequestInit): Promise<GenieMessage> {
  const token = await bearerToken();
  const response = await fetch(`${workspaceHost()}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });
  const body = (await response.json()) as GenieMessage;
  if (!response.ok) {
    const detail = body.error?.error || JSON.stringify(body).slice(0, 400);
    throw new Error(`Genie HTTP ${response.status}: ${detail}`);
  }
  return body;
}

function unwrapMessage(payload: GenieMessage): GenieMessage {
  return payload.message ?? payload;
}

function messageIdOf(message: GenieMessage): string {
  return message.message_id || message.id || '';
}

function textFrom(message: GenieMessage): string {
  const attachments = message.attachments ?? [];
  const texts = attachments
    .map((item) => item.text?.content?.trim())
    .filter((item): item is string => Boolean(item));
  if (texts.length > 0) {
    return texts.join('\n\n');
  }
  if (message.error?.error) {
    return message.error.error;
  }
  return message.content?.trim() || '';
}

function sqlFrom(message: GenieMessage): string | null {
  const query = (message.attachments ?? []).find((item) => item.query?.query);
  return query?.query?.query ?? null;
}

async function waitForMessage(
  spaceId: string,
  conversationId: string,
  messageId: string,
): Promise<GenieMessage> {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    const raw = await genieFetch(
      `/api/2.0/genie/spaces/${spaceId}/conversations/${conversationId}/messages/${messageId}`,
    );
    const message = unwrapMessage(raw);
    const status = message.status || '';
    if (status === 'COMPLETED' || status === 'FAILED' || status === 'CANCELLED') {
      return message;
    }
    await new Promise((resolve) => setTimeout(resolve, 1500));
  }
  throw new Error('Genie timed out waiting for the answer');
}

export function resolveRoomSpace(alias: string): {
  alias: LabRoomAlias;
  spaceId: string;
} {
  if (!isLabRoomAlias(alias)) {
    throw new Error(`Unknown room: ${alias}`);
  }
  const room = getLabRoom(alias);
  if (!room) {
    throw new Error(`Unknown room: ${alias}`);
  }
  const spaceId = process.env[room.envKey]?.trim();
  if (!spaceId) {
    throw new Error(`${room.envKey} is not configured`);
  }
  return { alias, spaceId };
}

export function publicRooms() {
  return listConfiguredLabRooms().map((room) => ({
    alias: room.alias,
    title: room.title,
    pack: room.pack,
    schema: room.schema,
    suggestions: [...room.suggestions],
    configured: Boolean(room.spaceId),
  }));
}

export async function askGenie(options: {
  alias: string;
  content: string;
  conversationId?: string;
}): Promise<GenieReply> {
  const { spaceId } = resolveRoomSpace(options.alias);
  const content = options.content.trim();
  if (!content) {
    throw new Error('Message is empty');
  }

  let conversationId = options.conversationId?.trim();
  let started: GenieMessage;
  if (conversationId) {
    started = unwrapMessage(
      await genieFetch(
        `/api/2.0/genie/spaces/${spaceId}/conversations/${conversationId}/messages`,
        { method: 'POST', body: JSON.stringify({ content }) },
      ),
    );
    conversationId = started.conversation_id || conversationId;
  } else {
    started = unwrapMessage(
      await genieFetch(`/api/2.0/genie/spaces/${spaceId}/start-conversation`, {
        method: 'POST',
        body: JSON.stringify({ content }),
      }),
    );
    conversationId = started.conversation_id || '';
  }

  const startedId = messageIdOf(started);
  if (!conversationId || !startedId) {
    throw new Error('Genie did not return conversation or message id');
  }

  const finished = await waitForMessage(spaceId, conversationId, startedId);
  return {
    conversationId,
    text: textFrom(finished) || 'Genie finished without text.',
    sql: sqlFrom(finished),
    status: finished.status || 'COMPLETED',
  };
}
