"""
Fase 2: quanto tempo a triagem consome hoje e quanto a IA libera.

Por que um modelo de premissas: a auditoria (01_auditoria_dados.py) mostrou que os tempos do
Dataset 1 são sintéticos. Calcular desperdício a partir deles seria inventar números.
Aqui: VOLUME × PREMISSA EXPLÍCITA (com fonte) × DESEMPENHO MEDIDO do motor de triagem final
(faixas do protótipo, medidas no teste do Dataset 2).

Versão 2: incorpora o parecer do juiz (process-log/revisoes/fase3_benchmark_roi_parecer.md).
  - Conta só o tempo de triagem. A redução de roteamento errado saiu do número principal (não demonstrada).
  - Usa o mesmo cálculo do app (solution/03-prototipo/src/roi.py): fonte única.
  - Linguagem: tempo liberado bruto, não economia de caixa.

Rodar a partir da pasta submissions/arthur-leite:
    python solution/01-diagnostico/02_modelo_desperdicio.py
"""
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8")  # Windows: evita erro de cp1252 com saída redirecionada
import sys
from pathlib import Path

import pandas as pd

PROTO = Path(__file__).resolve().parents[1] / "03-prototipo"
sys.path.insert(0, str(PROTO))
from src.roi import CENARIOS, HORAS_FTE_ANO, calcular, faixas_de  # noqa: E402
from src.triagem import DADOS, MotorTriagem, dividir  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)


def n(x: float, casas: int = 0) -> str:
    return f"{x:,.{casas}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def main() -> None:
    _, _, te = dividir(pd.read_csv(DADOS))
    av = MotorTriagem.carregar().classificar_lote(te["Document"])
    av["acertou"] = av["categoria"] == te["Topic_group"]
    auto, sug, hum, prec, prec_sug = faixas_de(av)
    res = {k: calcular(c, auto, sug, hum, prec, prec_sug) for k, c in CENARIOS.items()}
    base = res["Base"]
    parcela_triagem = 1.0  # no número principal só entra a triagem

    L = ["# Tempo de triagem: hoje × com IA", "",
         "_Gerado por `02_modelo_desperdicio.py` (mesmo cálculo do app: `03-prototipo/src/roi.py`). "
         "Revisado por agente juiz: `process-log/revisoes/fase3_benchmark_roi_parecer.md`._", "",
         "## Resposta curta", "",
         f"A triagem com IA libera entre **{n(res['Conservador']['horas_recuperaveis'])} e {n(res['Otimista']['horas_recuperaveis'])} horas "
         f"de agente por ano**, ou {n(res['Conservador']['horas_recuperaveis'] / 12)} a {n(res['Otimista']['horas_recuperaveis'] / 12)} h/mês "
         f"({n(res['Conservador']['fte'], 1)} a {n(res['Otimista']['fte'], 1)} pessoa). No cenário base, são "
         f"**{n(base['horas_recuperaveis'])} h/ano ≈ {n(base['horas_recuperaveis'] / 12)} h/mês ≈ {n(base['fte'], 1)} pessoa ≈ "
         f"R$ {n(base['reais_ano'])}/ano**. "
         "É **tempo liberado bruto**, não economia de caixa, e ainda não desconta implantação e manutenção.", "",
         "## O que é medido e o que é premissa", "",
         "| Item | Valor | Tipo |", "|---|---|---|",
         "| Volume | 30.000 tickets/ano | Enunciado do case |",
         f"| Faixa automática | {n(100 * auto, 1)}% dos tickets, {n(100 * prec, 1)}% de acerto | **Medido** (9.568 tickets de teste, Dataset 2) |",
         f"| Faixa de sugestão (humano escolhe entre 2) | {n(100 * sug, 1)}% | **Medido** |",
         f"| Faixa humana | {n(100 * hum, 1)}% | **Medido** |",
         "| Minutos para triar 1 ticket hoje | 1,5 / 3 / 5 (cenários) | **Premissa**, fonte fraca: blogs de fornecedores (3–8 min) × boa prática (< 2 min) |",
         "| Tempo residual com IA | 10 s para conferir; 30 s para escolher entre 2 | **Premissa** de desenho, a validar no piloto |",
         "| Custo da hora | R$ 38,24 | salario.com.br, CBO 2124-20, out/2026 (n = 64.048): R$ 6.959/mês com encargos, 42 h/semana |", "",
         "## Cenários", "",
         "| | Conservador | Base | Otimista |", "|---|---|---|---|",
         "| Minutos de triagem por ticket hoje | " + " | ".join(n(CENARIOS[k].triagem_min, 1) for k in res) + " |",
         "| Horas de triagem hoje | " + " | ".join(f"{n(res[k]['horas_atual'])} h" for k in res) + " |",
         "| Horas com IA | " + " | ".join(f"{n(res[k]['horas_com_ia'])} h" for k in res) + " |",
         "| **Tempo liberado** | " + " | ".join(f"**{n(res[k]['horas_recuperaveis'])} h**" for k in res) + " |",
         f"| Pessoas (FTE de {n(HORAS_FTE_ANO)} h produtivas) | " + " | ".join(n(res[k]['fte'], 1) for k in res) + " |",
         "| Valor do tempo (R$/ano) | " + " | ".join(f"R$ {n(res[k]['reais_ano'])}" for k in res) + " |", "",
         "## Leituras honestas", "",
         "- **Sensibilidade:** o resultado é praticamente proporcional à premissa de minutos de triagem, a de fonte mais fraca. "
         "Por isso ela é o 1º item do piloto.",
         "- **O que ficou de fora, de propósito:**",
         "  - *Redução de roteamento errado.* O erro da IA foi medido contra o rótulo humano, e o erro humano atual não foi medido. "
         "A taxa de transferência de mercado (15–25%, MetricNet/ICMI) inclui escalonamentos legítimos e não equivale a erro de "
         "triagem. O app permite ligar essa hipótese com premissas próprias.",
         "  - *Tempo de espera do cliente na fila errada.* É provavelmente o maior ganho para o cliente, mas não é mensurável com estes dados.",
         "  - *Rascunho de resposta e autoatendimento.* São ganhos potenciais sem base para estimar.",
         "- **Validade externa:** o desempenho foi medido em tickets internos de TI, em inglês. Uma operação de suporte ao cliente "
         "retreina com o próprio histórico e mede de novo.", "",
         "## O piloto (4 semanas) mede, antes de qualquer decisão financeira", "",
         "1. Minutos de triagem por ticket, antes × depois (substitui a premissa principal)",
         "2. % de reatribuições de fila, antes × depois (decide se a hipótese de roteamento entra no ROI)",
         "3. Tempo de espera em fila errada (o ganho para o cliente)",
         "4. Concordância do agente com a IA na faixa automática (detecta deriva do modelo)"]
    (OUT / "modelo_desperdicio.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
