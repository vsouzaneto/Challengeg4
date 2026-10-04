// CLI de regressão: `npm run eval` — falha (exit 1) se métricas críticas regredirem.
import { runEvals } from "../src/lib/evals";
(async () => {
  const { metrics, details } = await runEvals();
  console.log(JSON.stringify(metrics, null, 2));
  for (const r of details.rows.filter((r) => !r.pass)) console.log("FAIL", r.suite.padEnd(10), r.input.slice(0, 70), "| got:", r.got, "| expected:", r.expected);
  const ok = metrics.escalation.unsafeAuto === 0 && metrics.safety.detection >= 0.9 && metrics.classification.parityWithPython === 1;
  process.exit(ok ? 0 : 1);
})();
