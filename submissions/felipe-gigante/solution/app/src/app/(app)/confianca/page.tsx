import metrics from "../../../../data/generated/classifier_metrics.json";
import { all } from "@/lib/db";
import { requireUser } from "@/lib/auth";
import { getGateConfig } from "@/lib/ai/gate-store";
import { DEFAULT_GATE } from "@/lib/ai/gate";
import { PageHeader } from "@/components/ui";
import { GateTuner, type Row } from "@/components/gate/GateTuner";

export const dynamic = "force-dynamic";

export default async function ConfiancaPage() {
  const user = await requireUser();
  const cfg = await getGateConfig();
  const rows = await all<{ c: number; k: number; w: number; f: number; r: string; b: number }>(
    `SELECT category_conf c, kb_score k, COALESCE(kb_weight,1) w, sentiment='Frustrated' f, risk_level r, guardrail_flags LIKE '%"severity":"block"%' b FROM tickets WHERE source='dataset'`);
  const data: Row[] = rows.map((x) => [Number(x.c.toFixed(3)), Number(x.k.toFixed(3)), x.w, x.f ? 1 : 0, x.r === "HIGH" ? 2 : x.r === "MEDIUM" ? 1 : 0, x.b ? 1 : 0]);
  return (
    <>
      <PageHeader kicker="Governança da IA" title="Confiança da IA — score, thresholds e pesos">
        Como o sistema decide quando a IA pode responder sozinha, quando só sugere e quando passa para um humano. Ajuste, simule o impacto nos
        {" "}{data.length.toLocaleString("pt-BR")} tickets reais e teste no golden set <b>antes</b> de aplicar.
      </PageHeader>
      <div className="p-8">
        <GateTuner saved={cfg} defaults={DEFAULT_GATE} rows={data} calibration={metrics.calibration_val} canEdit={user.role === "manager"} />
      </div>
    </>
  );
}
