"""
Cálculo de ROI da triagem com IA: fonte única usada pelo app e pelo relatório.

Premissas de mercado com fonte; desempenho da IA medido no conjunto de teste do Dataset 2.
Ver solution/01-diagnostico/outputs/modelo_desperdicio.md para a discussão das fontes.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

CUSTO_MES_ANALISTA = 6959          # R$: salário + encargos, salario.com.br, CBO 2124-20, out/2026 (n = 64.048)
HORAS_MES = 42 * 52 / 12           # jornada de 42 h/semana
HORAS_FTE_ANO = 42 * 52 * 0.80     # 80% do tempo é produtivo


@dataclass
class Premissas:
    volume_ano: int = 30_000            # enunciado do case
    triagem_min: float = 3.0            # min para ler e classificar um ticket manualmente
    erro_roteamento: float = 0.05       # fração triada errado hoje (NÃO medida; só usada se incluir_reroteamento)
    min_por_erro: float = 3.9           # tempo de agente extra por ticket mal roteado
    revisao_auto_min: float = 0.17      # ~10 s para conferir um ticket roteado pela IA
    escolha_top2_min: float = 0.50      # ~30 s para escolher entre 2 sugestões
    custo_hora: float = CUSTO_MES_ANALISTA / HORAS_MES


CENARIOS = {
    "Conservador": Premissas(triagem_min=1.5),
    "Base": Premissas(triagem_min=3.0),
    "Otimista": Premissas(triagem_min=5.0),
}


def calcular(p: Premissas, cob_auto: float, cob_sugere: float, cob_humano: float, precisao_auto: float,
             precisao_sugere_top1: float = 0.62, incluir_reroteamento: bool = False) -> dict:
    """Tempo de agente por ano: hoje × com IA.

    Por padrão conta SÓ o tempo de triagem, que é o ganho que conseguimos sustentar com medição
    (cobertura das faixas) + premissa explícita (minutos por ticket).

    A redução do roteamento errado fica DESLIGADA por padrão (parecer do juiz, fase 3): o erro da IA
    foi medido contra o rótulo humano, e o erro humano atual é premissa de mercado sobre
    "transferências", que incluem escalonamentos legítimos. A queda não está demonstrada.
    Se ligada, usa o pior caso de ancoragem na faixa "sugere": o humano aceita a 1ª sugestão.
    """
    atual_triagem = p.volume_ano * p.triagem_min / 60
    ia_triagem = p.volume_ano * (cob_auto * p.revisao_auto_min + cob_sugere * p.escolha_top2_min
                                 + cob_humano * p.triagem_min) / 60
    erro_ia = (cob_auto * (1 - precisao_auto) + cob_sugere * max(p.erro_roteamento, 1 - precisao_sugere_top1)
               + cob_humano * p.erro_roteamento)
    atual_retrab = p.volume_ano * p.erro_roteamento * p.min_por_erro / 60 if incluir_reroteamento else 0.0
    ia_retrab = p.volume_ano * erro_ia * p.min_por_erro / 60 if incluir_reroteamento else 0.0
    atual, com_ia = atual_triagem + atual_retrab, ia_triagem + ia_retrab
    rec = atual - com_ia
    return {"horas_atual": atual, "horas_com_ia": com_ia, "horas_recuperaveis": rec,
            "horas_triagem_recuperaveis": atual_triagem - ia_triagem,
            "fte": rec / HORAS_FTE_ANO, "reais_ano": rec * p.custo_hora,
            "erro_atual": p.erro_roteamento, "erro_ia": erro_ia}


def faixas_de(av) -> tuple[float, float, float, float, float]:
    cob = av["faixa"].value_counts(normalize=True)
    return (cob.get("auto", 0.0), cob.get("sugere", 0.0), cob.get("humano", 0.0),
            float(av.loc[av["faixa"] == "auto", "acertou"].mean()),
            float(av.loc[av["faixa"] == "sugere", "acertou"].mean()))


def renderizar(st, av) -> None:
    import pandas as pd

    auto, sug, hum, prec, prec_sug = faixas_de(av)
    br = lambda x: f"{100 * x:.1f}%".replace(".", ",")
    st.markdown(f"Desempenho da IA **medido** no teste: {br(auto)} automático (precisão {br(prec)}) · "
                f"{br(sug)} sugestão · {br(hum)} humano. As **premissas** abaixo são de mercado: troque pelos números reais da operação.")
    c = st.columns(3)
    p = Premissas(
        volume_ano=c[0].number_input("Tickets por ano", 1000, 1_000_000, 30_000, step=1000),
        triagem_min=c[1].slider("Minutos para triar 1 ticket hoje", 0.5, 10.0, 3.0, 0.5,
                                help="A premissa que mais pesa no resultado. Fonte fraca (blogs de fornecedores: 3–8 min; boa prática: < 2 min)."),
    )
    incluir = c[2].toggle("Incluir hipótese: menos roteamento errado", value=False,
                          help="Não demonstrada: o erro atual da equipe não foi medido. Valide no piloto antes de usar.")
    if incluir:
        d = st.columns(2)
        p.erro_roteamento = d[0].slider("% de tickets triados errado hoje", 0, 40, 5,
                                        help="Não use a taxa de transferência de mercado (15–25%) inteira: ela inclui escalonamentos legítimos.") / 100
        p.min_por_erro = d[1].slider("Minutos extras por ticket mal roteado", 1.0, 15.0, 3.9, 0.1)
    r = calcular(p, auto, sug, hum, prec, prec_sug, incluir)
    k = st.columns(4)
    k[0].metric("Horas de triagem hoje", f"{r['horas_atual']:,.0f} h/ano".replace(",", "."))
    k[1].metric("Tempo liberado (bruto)", f"{r['horas_recuperaveis']:,.0f} h/ano".replace(",", "."))
    k[2].metric("Equivale a", f"{r['fte']:.1f} pessoa(s)".replace(".", ","))
    k[3].metric("Valor do tempo liberado", f"R$ {r['reais_ano']:,.0f}/ano".replace(",", "."))
    st.caption(f"Custo/hora: R$ {p.custo_hora:.2f}".replace(".", ",") + " (salário + encargos de analista de suporte, salario.com.br, out/2026). "
               "É **tempo liberado**, não economia de caixa; ainda não desconta implantação e manutenção.")

    linhas = []
    for nome, cen in CENARIOS.items():
        cen = replace(cen, volume_ano=p.volume_ano)  # cópia: não altera CENARIOS (compartilhado entre sessões)
        x = calcular(cen, auto, sug, hum, prec, prec_sug, False)
        linhas.append({"Cenário": nome, "Minutos de triagem hoje": f"{cen.triagem_min:.1f}".replace(".", ","),
                       "Tempo liberado (h/ano)": f"{x['horas_recuperaveis']:,.0f}".replace(",", "."),
                       "Pessoas": f"{x['fte']:.1f}".replace(".", ","),
                       "R$/ano": f"R$ {x['reais_ano']:,.0f}".replace(",", ".")})
    st.markdown("**Cenários (só tempo de triagem)**")
    st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")
    st.info("**Antes de qualquer decisão financeira, o piloto mede:** (1) minutos de triagem por ticket, (2) % de reatribuições "
            "e (3) tempo de espera em fila errada. Ficam fora do número, de propósito, o tempo de espera do cliente "
            "(provavelmente o maior ganho) e os ganhos de rascunho e autoatendimento: somar números sem base seria vender o projeto, não avaliá-lo.")
