import { all, one } from "@/lib/db";
import { PageHeader, Section, Stat, fmt } from "@/components/ui";
import { GapCard, NewArticle, TestQuestion, DeleteArticle } from "@/components/kb/KbClient";

export const dynamic = "force-dynamic";

export default async function KnowledgePage() {
  const gaps = await all<{ id: number; question: string; topic: string; category: string; occurrences: number; best_score: number; examples: string; updated_at: number }>(
    "SELECT * FROM kb_gaps WHERE status='pending' ORDER BY occurrences DESC, updated_at DESC");
  const resolved = await all<{ id: number; question: string; occurrences: number; title: string }>(
    "SELECT g.id, g.question, g.occurrences, a.title FROM kb_gaps g LEFT JOIN kb_articles a ON a.id=g.article_id WHERE g.status='resolved' ORDER BY g.updated_at DESC LIMIT 10");
  const articles = await all<{ id: number; title: string; topic: string; uses: number; source: string; questions: string; body: string }>(
    "SELECT a.*, (SELECT COUNT(*) FROM tickets t WHERE t.kb_article_id=a.id) uses FROM kb_articles a ORDER BY uses DESC");
  const cov = await one<{ covered: number; total: number }>("SELECT SUM(kb_score >= 0.27) covered, COUNT(*) total FROM tickets");
  const pendingOcc = gaps.reduce((s, g) => s + g.occurrences, 0);

  return (
    <>
      <PageHeader kicker="Knowledge Manager" title="Knowledge Base & Knowledge Gaps">
        Cada pergunta que a IA não consegue responder com segurança vira um <b>Pending Knowledge</b>, agrupado com perguntas similares.
        Ao aprovar uma resposta, a próxima pergunta parecida é respondida automaticamente — o sistema aprende com a própria operação.
      </PageHeader>
      <div className="space-y-5 p-8">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat label="Artigos publicados" value={articles.length} />
          <Stat label="Gaps pendentes" value={gaps.length} sub={`${pendingOcc} perguntas sem resposta`} tone="gold" />
          <Stat label="Gaps resolvidos" value={resolved.length} />
          <Stat label="KB Coverage" value={fmt.pct(((cov?.covered ?? 0) / (cov?.total || 1)) * 100)} sub="tickets com artigo relevante" />
        </div>

        <div className="grid gap-5 xl:grid-cols-[1.3fr_1fr]">
          <Section kicker="Pending Knowledge" title="Perguntas sem resposta (ordenadas por ocorrências)">
            <div className="space-y-3">
              {gaps.map((g) => <GapCard key={g.id} g={g} />)}
              {!gaps.length && <p className="text-sm text-muted">Nenhum gap pendente. 🎉</p>}
            </div>
          </Section>
          <div className="space-y-5">
            <Section kicker="Demo: o sistema aprendendo" title="Testar uma pergunta no pipeline">
              <p className="mb-3 text-xs text-muted">1) Teste a pergunta abaixo → HUMANO + gap. 2) Responda o gap ao lado. 3) Teste de novo → a IA responde com o novo artigo.</p>
              <TestQuestion />
            </Section>
            {resolved.length > 0 && (
              <Section title="Gaps resolvidos recentemente">
                <ul className="space-y-1.5 text-sm">{resolved.map((r) => <li key={r.id}>✅ “{r.question}” <span className="text-xs text-muted">→ {r.title} ({r.occurrences} ocorrências)</span></li>)}</ul>
              </Section>
            )}
          </div>
        </div>

        <Section kicker="Base de conhecimento" title="Artigos" right={<NewArticle />}>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {articles.map((a) => (
              <details key={a.id} className="rounded-lg border border-line p-3">
                <summary className="cursor-pointer list-none">
                  <div className="flex items-start justify-between gap-2">
                    <b className="text-sm text-navy">{a.title}</b>
                    <span className="shrink-0 rounded-full bg-offwhite px-2 text-[11px] font-semibold">{fmt.n(a.uses)} tickets</span>
                  </div>
                  <div className="mt-1 text-xs text-muted">{a.topic ?? "—"} · origem: {a.source === "gap" ? <span className="font-semibold text-gold">Knowledge Gap</span> : a.source}</div>
                </summary>
                <div className="mt-2 whitespace-pre-wrap border-t border-line pt-2 text-xs">{a.body}</div>
                <div className="mt-2 text-[11px] text-muted">Perguntas-exemplo: {a.questions.split("\n").filter(Boolean).length} · <DeleteArticle id={a.id} /></div>
              </details>
            ))}
          </div>
        </Section>
      </div>
    </>
  );
}
