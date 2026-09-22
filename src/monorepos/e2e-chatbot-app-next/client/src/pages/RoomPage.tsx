import { FormEvent, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getLabRoom } from '@chat-template/core/lab-rooms';
import { ChatHeader } from '@/components/chat-header';
import { Suggestion } from '@/components/elements/suggestion';
import { LightbulbIcon } from '@/components/icons';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

type RoomMessage = {
  role: 'user' | 'assistant';
  text: string;
  sql?: string | null;
};

export default function RoomPage() {
  const { alias = '' } = useParams<{ alias: string }>();
  const room = useMemo(() => getLabRoom(alias), [alias]);
  const [input, setInput] = useState('');
  const [pending, setPending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<RoomMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function send(content: string) {
    const text = content.trim();
    if (!text || !room || pending) {
      return;
    }
    setError(null);
    setPending(true);
    setMessages((current) => [...current, { role: 'user', text }]);
    setInput('');
    try {
      const response = await fetch(`/api/genie/${room.alias}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: text,
          conversationId,
        }),
      });
      const payload = (await response.json()) as {
        conversationId?: string;
        text?: string;
        sql?: string | null;
        error?: string;
      };
      if (!response.ok) {
        throw new Error(payload.error || 'A consulta ao Genie falhou');
      }
      setConversationId(payload.conversationId ?? null);
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: payload.text || '',
          sql: payload.sql,
        },
      ]);
    } catch (sendError) {
      const message =
        sendError instanceof Error ? sendError.message : 'A consulta ao Genie falhou';
      setError(message);
    } finally {
      setPending(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void send(input);
  }

  if (!room) {
    return (
      <div className="flex h-full flex-col">
        <ChatHeader title="Sala não encontrada" />
        <div className="flex flex-1 items-center justify-center text-muted-foreground">
          Sala Genie desconhecida.
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col" data-testid={`room-page-${room.alias}`}>
      <ChatHeader title={room.title} />
      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-4 overflow-y-auto px-4 py-6">
        {messages.length === 0 && (
          <div className="flex flex-col gap-3">
            <p className="text-sm text-muted-foreground">
              Genie sobre `{room.schema}`. Histórico desta sala não é salvo.
            </p>
            {room.suggestions.map((suggestion) => (
              <Suggestion
                key={suggestion}
                suggestion={suggestion}
                variant="tertiary"
                onClick={(value) => {
                  void send(value);
                }}
                className="h-auto w-full justify-start gap-2 rounded-none border-0 bg-transparent py-2 pl-0 text-left text-sm font-normal text-muted-foreground hover:bg-transparent hover:text-foreground"
              >
                <LightbulbIcon
                  size={16}
                  className="shrink-0 text-muted-foreground"
                  aria-hidden
                />
                {suggestion}
              </Suggestion>
            ))}
          </div>
        )}
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className="whitespace-pre-wrap rounded-lg border border-border px-3 py-2 text-sm"
            data-role={message.role}
          >
            <div className="mb-1 text-xs uppercase text-muted-foreground">
              {message.role === 'user' ? 'Você' : 'Genie'}
            </div>
            <div>{message.text}</div>
            {message.sql ? (
              <pre className="mt-2 overflow-x-auto rounded bg-muted p-2 text-xs">
                {message.sql}
              </pre>
            ) : null}
          </div>
        ))}
        {pending ? (
          <div className="text-sm text-muted-foreground">Genie está consultando…</div>
        ) : null}
        {error ? (
          <div className="text-sm text-red-600" role="alert">
            {error}
          </div>
        ) : null}
      </div>
      <form
        onSubmit={onSubmit}
        className="mx-auto flex w-full max-w-3xl gap-2 px-4 pb-6"
      >
        <Textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder={`Pergunte sobre ${room.title}`}
          className="min-h-12"
          disabled={pending}
        />
        <Button type="submit" disabled={pending || !input.trim()}>
          Enviar
        </Button>
      </form>
    </div>
  );
}
