// Avalia o roteamento COMPLETO que a API executa (predict + decideRoute) nas partições de validação e teste.
// Uso: npm run eval:routing   (requer analysis/03_classifier.py rodado antes)
// Saída: data/routing_eval.json. Falha se a política TS divergir da réplica Python usada na seleção.
import { writeFileSync } from "node:fs";
import { dataPath, loadModel, loadPythonPredictions, loadRules, loadSplit } from "../lib/eval-data";
import { evaluatePartition } from "../lib/routing-eval";
import type { RoutingEval } from "../lib/types";

function main() {
  const model = loadModel();
  const rules = loadRules();
  const python = loadPythonPredictions();
  const validation = evaluatePartition(loadSplit("val"), model, rules, python.validation);
  const test = evaluatePartition(loadSplit("test"), model, rules, python.test);

  const report: RoutingEval = {
    generatedAt: new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00"),
    note:
      "Medido com predict() e decideRoute(), as mesmas funções da API, com a política completa (escalação, guarda de domínio, " +
      "confiança, categoria sempre-humana e risco de privilégio). Limiares escolhidos só na validação; o teste é a fonte dos números publicados.",
    thresholds: model.thresholds,
    validation,
    test,
  };
  writeFileSync(dataPath("routing_eval.json"), JSON.stringify(report, null, 2), "utf-8");

  for (const [name, p] of [["validação", validation], ["teste", test]] as const) {
    console.log(`[${name}] n=${p.n} acurácia do modelo=${p.modelAccuracy}`);
    console.log(`  rotas: ${p.routes.map((x) => `${x.route}=${x.n} (${(x.share * 100).toFixed(1)}%)`).join(" | ")}`);
    console.log(`  motivos: ${p.reasons.map((x) => `${x.reasonCode}=${x.n}`).join(" | ")}`);
    console.log(`  auto: acerto=${p.auto.accuracy} IC=[${p.auto.accuracyCI.low}, ${p.auto.accuracyCI.high}] erros=${p.auto.errors}`);
    console.log(
      `  vazamento de privilégio: ${p.adminRightsLeak.autoRoutedElsewhere}/${p.adminRightsLeak.trueAdminRights} ` +
        `(${(p.adminRightsLeak.share * 100).toFixed(1)}%) → ${JSON.stringify(p.adminRightsLeak.toQueues)}`,
    );
    console.log(
      `  concordância com Python: rota=${p.pythonAgreement.route} rótulo=${p.pythonAgreement.label} ` +
        `Δconf=${p.pythonAgreement.maxConfidenceDiff.toExponential(2)}`,
    );
  }
  const diverged = [validation, test].some(
    (p) => p.pythonAgreement.route < 1 || p.pythonAgreement.label < 1 || p.pythonAgreement.maxConfidenceDiff > 1e-3,
  );
  if (diverged) {
    console.error("FALHOU: política/inferência TS diverge da réplica Python usada na seleção");
    process.exit(1);
  }
  console.log("OK →", dataPath("routing_eval.json"));
}

main();
