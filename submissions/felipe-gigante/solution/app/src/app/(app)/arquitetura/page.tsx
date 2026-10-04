import { PageHeader, Section, Pill } from "@/components/ui";
import Link from "next/link";
import { getGateConfig } from "@/lib/ai/gate-store";
import { FAST_MODEL, STRONG_MODEL, llmEnabled } from "@/lib/ai/llm";

const STEPS = [
  ["Input Guardrail", "Prompt injection, jailbreak, payload de código/SQL, pedido de dados de terceiros, fora de escopo. PII (cartão, CPF, e-mail, telefone, senha) é mascarada antes de qualquer LLM ou log.", "src/lib/ai/guardrails.ts"],
  ["Classificação", "TF-IDF + Logistic Regression treinado no Dataset 2 (48k tickets), exportado para JSON e executado em TypeScript. 8 categorias → time de roteamento. Abaixo de 60% de confiança, cascata para LLM.", "src/lib/ai/classifier.ts"],
  ["Sentimento", "Léxico bilíngue + sinais operacionais (contato repetido, dias esperando, CAIXA ALTA). Tendência na conversa: queda ≥15 pontos ou nota < 22 dispara “Customer frustration detected”.", "src/lib/ai/sentiment.ts"],
  ["Risco & intenção", "Regras explícitas do que NÃO automatizar: reembolso, chargeback, cancelamento, ameaça jurídica, fraude, perda de dados, LGPD, emoção severa. Campos estruturados (tipo do formulário) também contam.", "src/lib/ai/risk.ts"],
  ["Prioridade", "Severidade + Urgência + Sentimento + Risco do tópico — cada componente visível no trace.", "src/lib/ai/priority.ts"],
  ["Knowledge Base", "Busca por similaridade × cobertura dos termos raros da pergunta (evita o falso positivo “fala de cobrança, então é o artigo de pagamento”). Perguntas-exemplo por artigo, padrão Botpress.", "src/lib/ai/kb.ts"],
  ["Confidence Gate", "score = peso·classificador + (1−peso)·KB − penalidade de frustração. Acima do threshold máximo e risco baixo → AUTO; entre mínimo e máximo → SUGESTÃO; abaixo, ou risco alto → HUMANO. Pesos e thresholds são ajustáveis em “Confiança da IA”.", "src/lib/ai/gate.ts"],
  ["Output Guardrail", "Groundedness (termos da resposta suportados pelo artigo), promessas não autorizadas (reembolso aprovado, valores, garantias), vazamento de PII, disclaimer em temas sensíveis. Reprovou → fallback seguro.", "src/lib/ai/guardrails.ts"],
] as const;

export default async function ArquiteturaPage() {
  const g = await getGateConfig();
  return (
    <>
      <PageHeader kicker="Para quem vai manter isso" title="Como funciona">
        Ticket entra → IA entende → classifica → prioriza → consulta conhecimento → responde ou sugere → decide se precisa de humano → registra → coleta CSAT → transforma gaps em conhecimento.
      </PageHeader>
      <div className="space-y-5 p-8">
        <Section kicker="Pipeline" title="8 etapas, todas visíveis no trace de cada ticket">
          <ol className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {STEPS.map(([name, desc, file], i) => (
              <li key={name} className="relative rounded-xl border border-line p-4">
                <div className="h-display absolute -top-3 left-4 rounded-full bg-navy px-2 text-xs font-bold text-gold">{i + 1}</div>
                <div className="font-semibold text-navy">{name}</div>
                <p className="mt-1 text-xs text-muted">{desc}</p>
                <code className="mt-2 block text-[10px] text-gold">{file}</code>
              </li>
            ))}
          </ol>
        </Section>

        <div className="grid gap-5 xl:grid-cols-3">
          <Section kicker="Human in the loop" title="Upstream e downstream">
            <div className="space-y-3 text-sm">
              <div className="rounded-lg bg-rose-50 p-3"><b className="text-rose-800">Upstream (IA → humano)</b><p className="text-xs text-rose-900/80">Automático pelo gate (risco, baixa confiança, frustração crescente, guardrail) ou manual (“Assumir”). O humano recebe resumo, categoria, artigo e motivo — o cliente não repete nada.</p></div>
              <div className="rounded-lg bg-emerald-50 p-3"><b className="text-emerald-800">Downstream (humano → IA)</b><p className="text-xs text-emerald-900/80">O humano decide o que é dele (ex.: aprova o estorno) e devolve. A IA confirma ao cliente, encerra e pede CSAT. Humano decide, IA conclui.</p></div>
              <div className="rounded-lg bg-amber-50 p-3"><b className="text-amber-800">Feedback loop</b><p className="text-xs text-amber-900/80">Cada sugestão aceita / editada / rejeitada vira o AI Acceptance Rate e alimenta evals e a re-calibração.</p></div>
            </div>
          </Section>
          <Section kicker="Model routing" title="Escalonamento de inteligência">
            <ol className="space-y-2 text-sm">
              <li><Pill v="auto">Tier 0 · local</Pill> classificador + regras + KB. Custo zero, ~1 ms. Atende a maior parte.</li>
              <li><Pill v="suggest">Tier 1 · {FAST_MODEL}</Pill> confiança &lt; 60%: classificação estruturada (JSON) + sentimento + resumo; redige resposta ancorada no artigo.</li>
              <li><Pill v="MEDIUM">Tier 2 · {STRONG_MODEL}</Pill> confiança &lt; 40% ou casos que vão para sugestão.</li>
              <li><Pill v="human">Humano</Pill> ainda incerto ou alto risco.</li>
            </ol>
            <p className="mt-3 text-xs text-muted">Status neste deploy: <b>{llmEnabled() ? "LLM ativo (Groq/OpenAI-compatible)" : "sem chave de LLM — rodando 100% no tier local"}</b>. Configure <code>GROQ_API_KEY</code> para ativar a cascata.</p>
          </Section>
          <Section kicker="MCP" title="Tools desacopladas do app">
            <p className="text-sm text-muted">O servidor <code>mcp/server.ts</code> expõe as capacidades do Support OS via Model Context Protocol, para que outros agentes (vendas, onboarding, assistente interno) reutilizem as mesmas tools com governança própria.</p>
            <ul className="mt-3 space-y-1 font-mono text-xs">
              {["knowledge.search_articles", "knowledge.list_gaps", "knowledge.create_gap", "support.triage_ticket", "support.classify_text", "support.get_ticket", "support.ops_metrics"].map((t) => <li key={t} className="rounded bg-offwhite px-2 py-1">{t}</li>)}
            </ul>
            <p className="mt-3 text-xs text-muted"><code>npm run mcp</code> (stdio) — configuração para Claude Desktop/Code no README.</p>
          </Section>
        </div>

        <Section kicker="O que NÃO automatizar" title="A maturidade é saber quando parar">
          <div className="grid gap-3 text-sm md:grid-cols-3 xl:grid-cols-6">
            {[["Financeiro", "reembolso, chargeback, cobrança duplicada"], ["Churn", "cancelamento, troca para concorrente"], ["Jurídico", "Procon, advogado, processo, LGPD"], ["Segurança", "fraude, conta invadida, compra não reconhecida"], ["Irreversível", "perda de dados"], ["Emocional", "raiva / frustração crescente"]].map(([k, v]) => (
              <div key={k} className="rounded-lg border-l-4 border-rose-600 bg-white p-3 shadow-sm"><b className="text-navy">{k}</b><p className="text-xs text-muted">{v}</p></div>
            ))}
          </div>
          <p className="mt-3 text-xs text-muted">Nesses casos a IA ainda trabalha — classifica, resume, puxa o artigo de política e redige um rascunho — mas quem decide e envia é um humano. Configuração atual do gate: AUTO ≥ {g.autoThreshold} · SUGESTÃO ≥ {g.suggestThreshold} · peso do classificador {g.wClassifier} — <Link href="/confianca" className="font-semibold text-gold hover:underline">ajustar</Link>.</p>
        </Section>
      </div>
    </>
  );
}
