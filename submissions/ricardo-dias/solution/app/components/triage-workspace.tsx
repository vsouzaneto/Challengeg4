"use client";

import { useEffect, useRef, useState } from "react";
import type { ClassifyResponse, SampleResponse } from "@/lib/types";
import { MAX_TEXT_CHARS, validateText } from "@/lib/validation";
import {
  categoryLabels,
  number,
  percent,
  routeLabels,
  routeTone,
} from "./format";
import { Icon } from "./icons";
import { Badge, Notice, Stat } from "./ui";

type Sample = SampleResponse["items"][number];
type BatchRow = { sample: Sample; result: ClassifyResponse };

async function responseError(response: Response): Promise<string> {
  const body = await response.json().catch(() => null);
  return typeof body?.error === "string"
    ? body.error
    : `Não foi possível concluir a operação (${response.status}). Tente novamente.`;
}
async function requestJson<T>(
  url: string,
  signal: AbortSignal,
  body?: unknown,
): Promise<T> {
  const response = await fetch(url, {
    signal,
    cache: "no-store",
    ...(body
      ? {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      : {}),
  });
  if (!response.ok) throw new Error(await responseError(response));
  return response.json() as Promise<T>;
}
function ErrorMessage({ message }: { message: string }) {
  return (
    <p className="inline-error" role="alert">
      <Icon name="alert" />
      {message}
    </p>
  );
}

export function TriageWorkspace() {
  const [view, setView] = useState<"single" | "batch">("single");
  const [text, setText] = useState("");
  const [sample, setSample] = useState<Sample | null>(null);
  const [result, setResult] = useState<ClassifyResponse | null>(null);
  const [busy, setBusy] = useState<"sample" | "classify" | "draft" | null>(
    null,
  );
  const [error, setError] = useState("");
  const [draft, setDraft] = useState("");
  const [draftError, setDraftError] = useState("");
  const [copied, setCopied] = useState(false);
  const [batch, setBatch] = useState<BatchRow[]>([]);
  const [batchStatus, setBatchStatus] = useState("");
  const [batchBusy, setBatchBusy] = useState(false);
  const [batchError, setBatchError] = useState("");
  const [onlyErrors, setOnlyErrors] = useState(false);
  const singleController = useRef<AbortController | null>(null);
  const batchController = useRef<AbortController | null>(null);
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(
    () => () => {
      singleController.current?.abort();
      batchController.current?.abort();
      if (copyTimer.current) clearTimeout(copyTimer.current);
    },
    [],
  );

  function updateText(value: string, origin: Sample | null = null) {
    singleController.current?.abort();
    singleController.current = null;
    setBusy(null);
    setText(value);
    setSample(origin);
    setResult(null);
    setError("");
    setDraft("");
    setDraftError("");
    setCopied(false);
  }

  async function loadSample() {
    singleController.current?.abort();
    const controller = new AbortController();
    singleController.current = controller;
    setBusy("sample");
    setError("");
    const timer = setTimeout(() => controller.abort("timeout"), 30_000);
    try {
      const data = await requestJson<SampleResponse>(
        "/api/sample?n=1",
        controller.signal,
      );
      if (!data.items?.length)
        throw new Error("Nenhuma amostra disponível no momento.");
      if (!controller.signal.aborted)
        updateText(data.items[0].text, data.items[0]);
    } catch (err) {
      if (singleController.current === controller)
        setError(
          controller.signal.aborted
            ? "A busca demorou mais que o esperado. Tente novamente."
            : err instanceof Error
              ? err.message
              : "Falha ao buscar amostra.",
        );
    } finally {
      clearTimeout(timer);
      if (singleController.current === controller) setBusy(null);
    }
  }

  async function classifyTicket() {
    const input = validateText(text);
    if (!input.ok) {
      setError(input.error);
      return;
    }
    singleController.current?.abort();
    const controller = new AbortController();
    singleController.current = controller;
    setBusy("classify");
    setError("");
    setResult(null);
    setDraft("");
    setDraftError("");
    setCopied(false);
    const timer = setTimeout(() => controller.abort("timeout"), 45_000);
    try {
      const data = await requestJson<ClassifyResponse>(
        "/api/classify",
        controller.signal,
        { text: input.text },
      );
      if (!controller.signal.aborted) setResult(data);
    } catch (err) {
      if (singleController.current === controller)
        setError(
          controller.signal.aborted
            ? "A classificação demorou mais que o esperado. Tente novamente."
            : err instanceof Error
              ? err.message
              : "Falha na classificação.",
        );
    } finally {
      clearTimeout(timer);
      if (singleController.current === controller) setBusy(null);
    }
  }

  async function generateDraft() {
    if (!result?.draftAllowed) return;
    singleController.current?.abort();
    const controller = new AbortController();
    singleController.current = controller;
    setBusy("draft");
    setDraft("");
    setDraftError("");
    setCopied(false);
    const timer = setTimeout(() => controller.abort("timeout"), 65_000);
    try {
      const response = await fetch("/api/draft", {
        method: "POST",
        signal: controller.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) throw new Error(await responseError(response));
      if (!response.body)
        throw new Error("O serviço não retornou um rascunho.");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let received = "";
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          received += decoder.decode(value, { stream: true });
          if (!controller.signal.aborted) setDraft(received);
        }
        received += decoder.decode();
        if (!received.trim())
          throw new Error(
            "O serviço retornou um rascunho vazio. Tente novamente.",
          );
        if (!controller.signal.aborted) setDraft(received);
      } finally {
        reader.releaseLock();
      }
    } catch (err) {
      if (singleController.current === controller) {
        setDraft("");
        setDraftError(
          controller.signal.aborted
            ? "A geração foi interrompida por tempo limite. Tente novamente."
            : err instanceof Error
              ? err.message
              : "Não foi possível gerar o rascunho.",
        );
      }
    } finally {
      clearTimeout(timer);
      if (singleController.current === controller) setBusy(null);
    }
  }

  async function copyDraft() {
    try {
      await navigator.clipboard.writeText(draft);
      setCopied(true);
      if (copyTimer.current) clearTimeout(copyTimer.current);
      copyTimer.current = setTimeout(() => setCopied(false), 2500);
    } catch {
      setDraftError(
        "Não foi possível copiar automaticamente. Selecione o texto do rascunho para copiá-lo.",
      );
    }
  }

  async function runBatch() {
    batchController.current?.abort();
    const controller = new AbortController();
    batchController.current = controller;
    setBatchBusy(true);
    setBatch([]);
    setBatchError("");
    setOnlyErrors(false);
    setBatchStatus("Buscando amostra aleatória do conjunto de teste…");
    const timer = setTimeout(() => controller.abort("timeout"), 90_000);
    try {
      const data = await requestJson<SampleResponse>(
        "/api/sample?n=200",
        controller.signal,
      );
      if (!data.items?.length)
        throw new Error("Não há tickets disponíveis para avaliar.");
      if (controller.signal.aborted) return;
      setBatchStatus(
        `Classificando ${number(data.items.length)} tickets em uma única requisição…`,
      );
      const response = await requestJson<{ results: ClassifyResponse[] }>(
        "/api/classify",
        controller.signal,
        { texts: data.items.map((item) => item.text) },
      );
      if (response.results?.length !== data.items.length)
        throw new Error(
          "O lote retornou uma quantidade inesperada de resultados. A avaliação não foi publicada.",
        );
      if (controller.signal.aborted) return;
      setBatch(
        data.items.map((item, index) => ({
          sample: item,
          result: response.results[index],
        })),
      );
      setBatchStatus(
        `Avaliação concluída: ${number(data.items.length)} tickets classificados.`,
      );
    } catch (err) {
      if (batchController.current === controller) {
        setBatchStatus("");
        setBatchError(
          controller.signal.aborted
            ? "A avaliação excedeu o tempo limite. Tente novamente."
            : err instanceof Error
              ? err.message
              : "Falha ao avaliar a amostra.",
        );
      }
    } finally {
      clearTimeout(timer);
      if (batchController.current === controller) setBatchBusy(false);
    }
  }

  const correct = batch.filter(
    (row) => row.result.category === row.sample.label,
  ).length;
  const auto = batch.filter((row) => row.result.route === "auto");
  const escalated = batch.filter(
    (row) => row.result.route === "escalar",
  ).length;
  const batchRows = onlyErrors
    ? batch.filter((row) => row.result.category !== row.sample.label)
    : batch;

  return (
    <>
      <div className="tabs" role="group" aria-label="Modo da triagem">
        <button
          type="button"
          aria-pressed={view === "single"}
          onClick={() => setView("single")}
        >
          <Icon name="ticket" width={16} />
          Ticket individual
        </button>
        <button
          type="button"
          aria-pressed={view === "batch"}
          onClick={() => setView("batch")}
        >
          <Icon name="chart" width={16} />
          Avaliar uma amostra
        </button>
      </div>
      {view === "single" ? (
        <div className="triage-grid">
          <section className="panel" aria-labelledby="ticket-input-heading">
            <div className="panel-header">
              <div>
                <h2 id="ticket-input-heading">Comece com um ticket</h2>
                <p>Cole uma solicitação ou explore uma amostra real.</p>
              </div>
              <Badge tone="gold">TI interno</Badge>
            </div>
            <form
              className="panel-body"
              onSubmit={(event) => {
                event.preventDefault();
                void classifyTicket();
              }}
            >
              <label htmlFor="ticket-text" className="field-label">
                Descrição do atendimento
              </label>
              <textarea
                id="ticket-text"
                value={text}
                onChange={(event) => updateText(event.target.value)}
                placeholder="Cole aqui o texto do ticket em inglês ou carregue uma amostra abaixo…"
                aria-describedby="ticket-help ticket-count"
                aria-invalid={
                  Boolean(error) || text.trim().length > MAX_TEXT_CHARS
                }
                spellCheck={false}
              />
              <div className="input-meta">
                <span id="ticket-help">
                  Avaliado em tickets de TI em inglês.
                </span>
                <span
                  id="ticket-count"
                  className={
                    text.trim().length > MAX_TEXT_CHARS ? "over-limit" : ""
                  }
                >
                  {number(text.trim().length)} / {number(MAX_TEXT_CHARS)}
                </span>
              </div>
              {sample && (
                <p className="field-hint" style={{ marginBottom: 14 }}>
                  Amostra #{sample.id} · selecionada aleatoriamente do conjunto
                  de teste.
                </p>
              )}
              <div className="button-row">
                <button
                  className="button"
                  type="submit"
                  disabled={Boolean(busy) || !text.trim()}
                >
                  {busy === "classify" ? (
                    <span className="spinner" />
                  ) : (
                    <Icon name="sparkle" width={16} />
                  )}
                  {busy === "classify"
                    ? "Classificando…"
                    : "Classificar ticket"}
                </button>
                <button
                  className="button secondary"
                  type="button"
                  disabled={Boolean(busy)}
                  onClick={() => void loadSample()}
                >
                  {busy === "sample" ? (
                    <span className="spinner" />
                  ) : (
                    <Icon name="refresh" width={16} />
                  )}
                  {busy === "sample" ? "Buscando…" : "Amostra aleatória"}
                </button>
              </div>
              {error && <ErrorMessage message={error} />}
            </form>
            <div className="help-strip">
              <Icon name="shield" />
              <span>
                A triagem sugere uma categoria e uma fila. A resolução e o envio
                de respostas continuam sob responsabilidade humana.
              </span>
            </div>
          </section>
          <div
            className="stack"
            aria-live="polite"
            aria-busy={busy === "classify"}
          >
            {!result ? (
              <div className="panel empty-state">
                <span className="empty-icon">
                  {busy === "classify" ? (
                    <span className="spinner" />
                  ) : (
                    <Icon name="flow" width={30} height={30} />
                  )}
                </span>
                <h2>
                  {busy === "classify"
                    ? "Analisando a solicitação"
                    : "Cada ticket, um próximo passo."}
                </h2>
                <p>
                  {busy === "classify"
                    ? "O classificador está avaliando a categoria e as regras de encaminhamento."
                    : "A categoria, a confiança e o motivo do encaminhamento aparecerão aqui."}
                </p>
                <div className="empty-steps">
                  <span>Classificar</span>
                  <Icon name="arrow" />
                  <span>Verificar</span>
                  <Icon name="arrow" />
                  <span>Encaminhar</span>
                </div>
              </div>
            ) : (
              <>
                <section
                  className="panel"
                  aria-label="Resultado da classificação"
                >
                  <div className="panel-header">
                    <h3>Resultado da triagem</h3>
                    <Badge>Classificador local</Badge>
                  </div>
                  <div className="result-main">
                    <div className="result-category">
                      <div>
                        <p className="eyebrow">Categoria prevista</p>
                        <h2>{categoryLabels[result.category]}</h2>
                        <small>{result.category}</small>
                      </div>
                      <div className="confidence">
                        {percent(result.confidence)}
                        <span className="confidence-caption">
                          Confiança do modelo
                        </span>
                      </div>
                    </div>
                    <div className="progress-track" aria-hidden="true">
                      <span
                        className="progress-fill"
                        style={{
                          width: `${result.confidence * 100}%`,
                        }}
                      />
                    </div>
                    <div className={`result-route ${routeTone[result.route]}`}>
                      <Badge tone={routeTone[result.route]}>
                        <Icon
                          name={
                            result.route === "auto"
                              ? "check"
                              : result.route === "escalar"
                                ? "alert"
                                : "people"
                          }
                          width={13}
                          height={13}
                        />
                        {routeLabels[result.route]}
                      </Badge>
                      <p>{result.routeReason}</p>
                    </div>
                    {sample && (
                      <p className="source-note">
                        Rótulo de referência: {categoryLabels[sample.label]} ·{" "}
                        {sample.label === result.category
                          ? "A previsão corresponde ao rótulo."
                          : "A previsão diverge do rótulo."}
                      </p>
                    )}
                  </div>
                  <details className="detail-section">
                    <summary>
                      Entender a classificação
                      <Icon name="chevron" width={15} />
                    </summary>
                    <div className="detail-content">
                      <p className="small-copy muted">
                        Vocabulário de conteúdo reconhecido:{" "}
                        <strong>{percent(result.knownShare)}</strong>. A
                        confiança é um score do modelo; não é garantia de
                        acerto.
                      </p>
                      <div className="term-list">
                        {result.topTerms.map((term) => (
                          <span
                            className="term"
                            key={term.term}
                            title={`Contribuição: ${number(term.weight, 3)}`}
                          >
                            {term.term}
                          </span>
                        ))}
                      </div>
                      {result.topTerms.length === 0 && (
                        <p className="field-hint">
                          Nenhum termo com contribuição positiva disponível.
                        </p>
                      )}
                      <p className="field-hint" style={{ marginBottom: 18 }}>
                        Termos que contribuíram para a categoria prevista.
                      </p>
                      {result.probabilities.map((item) => (
                        <div className="mix-row" key={item.label}>
                          <div className="mix-label">
                            <span>{categoryLabels[item.label]}</span>
                            <strong>{percent(item.p)}</strong>
                          </div>
                          <div className="progress-track" aria-hidden="true">
                            <span
                              className="progress-fill"
                              style={{ width: `${item.p * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                  <details className="detail-section">
                    <summary>
                      Tickets semelhantes
                      <Icon name="chevron" width={15} />
                    </summary>
                    <div className="detail-content">
                      {result.similar.length ? (
                        result.similar.map((ticket, index) => (
                          <div className="similar-ticket" key={index}>
                            <Badge>{categoryLabels[ticket.label]}</Badge>
                            <span className="field-hint">
                              {" "}
                              · Similaridade {number(ticket.score, 2)}
                            </span>
                            <p>{ticket.text}</p>
                          </div>
                        ))
                      ) : (
                        <p className="field-hint">
                          Nenhum ticket semelhante encontrado.
                        </p>
                      )}
                      <p className="source-note">
                        A similaridade mede a proximidade do vocabulário entre
                        os textos. Exemplos do treino; sem respostas de
                        resolução associadas.
                      </p>
                    </div>
                  </details>
                </section>
                <section className="panel">
                  <div className="panel-header">
                    <div>
                      <h3>Uma primeira versão da resposta</h3>
                      <p>Rascunho: o agente revisa antes de enviar.</p>
                    </div>
                    <Icon name="sparkle" />
                  </div>
                  <div className="panel-body">
                    {result.draftAllowed ? (
                      <>
                        <p className="small-copy muted">
                          Gere uma sugestão em português e confira o conteúdo
                          antes de utilizá-la.
                        </p>
                        {draft && <div className="draft-content">{draft}</div>}
                        <div className="button-row" style={{ marginTop: 16 }}>
                          <button
                            className="button secondary"
                            disabled={Boolean(busy)}
                            onClick={() => void generateDraft()}
                          >
                            {busy === "draft" ? (
                              <span className="spinner" />
                            ) : (
                              <Icon name="sparkle" width={16} />
                            )}
                            {busy === "draft"
                              ? "Gerando rascunho…"
                              : draft
                                ? "Gerar novamente"
                                : "Gerar rascunho"}
                          </button>
                          {draft && busy !== "draft" && (
                            <button
                              className="button secondary"
                              onClick={() => void copyDraft()}
                            >
                              <Icon
                                name={copied ? "check" : "copy"}
                                width={16}
                              />
                              {copied ? "Copiado" : "Copiar rascunho"}
                            </button>
                          )}
                        </div>
                        {draftError && <ErrorMessage message={draftError} />}
                      </>
                    ) : (
                      <Notice
                        title="Este atendimento exige uma resposta humana."
                        tone="warning"
                      >
                        A política de encaminhamento bloqueou a geração de
                        rascunho para este ticket.
                      </Notice>
                    )}
                  </div>
                </section>
              </>
            )}
          </div>
        </div>
      ) : (
        <>
          <div className="panel">
            <div className="batch-intro">
              <div>
                <p className="eyebrow">Uma demonstração com dados reais</p>
                <h2>Veja o desempenho além de um exemplo.</h2>
                <p>
                  Selecione tickets aleatórios do conjunto de teste e compare as
                  previsões com seus rótulos. O resultado desta amostra pode
                  variar e não substitui a avaliação completa da página Modelo.
                </p>
              </div>
              <button
                className="button"
                disabled={batchBusy}
                onClick={() => void runBatch()}
              >
                {batchBusy ? (
                  <span className="spinner" />
                ) : (
                  <Icon name="chart" width={17} />
                )}
                {batchBusy ? "Avaliando…" : "Testar em 200 tickets"}
              </button>
            </div>
          </div>
          <p className="batch-status" role="status">
            {batchStatus}
          </p>
          {batchError && <ErrorMessage message={batchError} />}
          {batch.length > 0 && (
            <>
              <div className="stats-grid">
                <Stat
                  label="Acerto na amostra"
                  value={percent(correct / batch.length)}
                  detail={`${number(correct)} de ${number(batch.length)} categorias corretas`}
                  icon="check"
                />
                <Stat
                  label="Roteamento automático"
                  value={percent(auto.length / batch.length)}
                  detail={`${number(auto.length)} tickets passaram por todas as regras`}
                  icon="flow"
                />
                <Stat
                  label="Acerto nos automáticos"
                  value={
                    auto.length
                      ? percent(
                          auto.filter(
                            (row) => row.result.category === row.sample.label,
                          ).length / auto.length,
                        )
                      : "—"
                  }
                  detail={
                    auto.length
                      ? "Acurácia apenas dos tickets na rota automática"
                      : "Nenhum ticket encaminhado automaticamente"
                  }
                  icon="shield"
                />
                <Stat
                  label="Intervenção humana"
                  value={number(batch.length - auto.length)}
                  detail={`${number(escalated)} escalações · ${number(batch.length - auto.length - escalated)} revisões`}
                  icon="people"
                  tone="gold"
                />
              </div>
              <section className="section panel">
                <div className="panel-header">
                  <h2>Previsões e encaminhamentos</h2>
                  <button
                    className="button secondary small"
                    aria-pressed={onlyErrors}
                    onClick={() => setOnlyErrors(!onlyErrors)}
                  >
                    {onlyErrors ? "Mostrar todos" : "Mostrar erros"}
                  </button>
                </div>
                <div
                  className="table-scroll"
                  tabIndex={0}
                  role="region"
                  aria-label="Resultados dos tickets da amostra"
                >
                  <table>
                    <thead>
                      <tr>
                        <th>Ticket</th>
                        <th>Referência</th>
                        <th>Previsão</th>
                        <th>Confiança</th>
                        <th>Destino</th>
                      </tr>
                    </thead>
                    <tbody>
                      {batchRows.map(({ sample: item, result: prediction }) => (
                        <tr key={item.id}>
                          <td className="batch-text">
                            <strong>#{item.id}</strong>
                            <p>{item.text}</p>
                            <details>
                              <summary>Ler ticket completo</summary>
                              <p>{item.text}</p>
                            </details>
                          </td>
                          <td>{categoryLabels[item.label]}</td>
                          <td>
                            <Badge
                              tone={
                                item.label === prediction.category
                                  ? "success"
                                  : "danger"
                              }
                            >
                              {categoryLabels[prediction.category]}
                            </Badge>
                          </td>
                          <td className="numeric">
                            {percent(prediction.confidence)}
                          </td>
                          <td>
                            <Badge tone={routeTone[prediction.route]}>
                              {routeLabels[prediction.route]}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {batchRows.length === 0 && (
                    <p className="panel-body small-copy">
                      Nenhuma divergência nesta amostra.
                    </p>
                  )}
                </div>
              </section>
            </>
          )}
        </>
      )}
    </>
  );
}
