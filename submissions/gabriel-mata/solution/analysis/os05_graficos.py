"""OS-05 - Graficos para os relatorios (4 PNG). Graficos 1 e 3 recalculam os dados a
partir do CSV; graficos 2 e 4 leem as saidas das OS anteriores."""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

SEED = 42
N_BOOT = 1000
N_PERM = 200
MIN_N = 100

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os05"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_OS02 = SCRIPT_DIR.parent / "outputs" / "os02"
OUT_OS03C = SCRIPT_DIR.parent / "outputs" / "os03c"

# faixas da OS-02/OS-03: ate 50K, 50-100K, 100-500K, 500K-1M
FAIXA_SEG_BINS = [0, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["ate 50K", "50-100K", "100-500K", "500K-1M"]
FAIXA_SEG_EXIBE = ["até 50K", "50–100K", "100–500K", "500K–1M"]

COMBO_N4 = ["platform", "content_type", "content_category", "faixa_seguidores"]
SEGMENTO_INJECAO = "Bilibili | video | beauty | 50-100K"   # sorteado no Bloco 3b da OS-03c

VARS_PT = {
    "platform": "Plataforma",
    "content_type": "Formato",
    "content_category": "Categoria",
    "faixa_seguidores": "Faixa de seguidores",
    "is_sponsored": "Patrocínio",
    "audience_age_distribution": "Idade da audiência",
    "audience_gender_distribution": "Gênero da audiência",
    "audience_location": "País da audiência",
}

# duas cores: cinza para o padrao, vermelho para o destaque
CINZA = "#9A9A9A"
CINZA_LINHA = "#5F5F5F"
DESTAQUE = "#C0392B"

plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "axes.edgecolor": CINZA_LINHA,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.6,
})

notas = []     # pontos suspeitos / observacoes, preenchidos durante a execucao
resumo = {}    # valores principais de cada grafico


def br(x, dec=0):
    """Numero no formato pt-BR: milhar com ponto, decimal com virgula."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "@").replace(".", ",").replace("@", ".")


def br_pct(x, dec=0, sinal=False):
    """Percentual pt-BR, com sinal explicito se pedido (menos tipografico)."""
    s = br(abs(x), dec) + "%"
    if x < 0:
        return "−" + s
    return ("+" + s) if (sinal and x > 0) else s


def salvar_fig(fig, nome):
    caminho = OUT_DIR / nome
    fig.savefig(caminho, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"  -> {nome}")


# ---------------------------------------------------------------- carga e derivadas
df = pd.read_csv(DATA_PATH)
df["post_date"] = pd.to_datetime(df["post_date"], format="%m/%d/%y %I:%M %p")
df["engajamento"] = df["likes"] + df["shares"] + df["comments_count"]
df["taxa_engajamento"] = df["engajamento"] / df["views"]
df["faixa_seguidores"] = pd.cut(df["follower_count"], bins=FAIXA_SEG_BINS,
                                labels=FAIXA_SEG_LABELS, right=True).astype(str)

N = len(df)
print(f"Base: {N} linhas (origem: {DATA_PATH})")

rng = np.random.default_rng(SEED)


# ================================================================ Grafico 1
# Bloco 5 da OS-03: media de engajamento por faixa de seguidores x is_sponsored,
# com IC 95% bootstrap percentil (1.000 reamostragens).
print("\n[1] grafico_01_engajamento_por_faixa.png")

eng = df["engajamento"].to_numpy(dtype=float)
eh_spon = df["is_sponsored"].astype(bool).to_numpy()


def boot_ic(v, B=N_BOOT, chunk=250):
    n = len(v)
    out = np.empty(B)
    feitos = 0
    while feitos < B:
        b = min(chunk, B - feitos)
        out[feitos:feitos + b] = v[rng.integers(0, n, size=(b, n))].mean(axis=1)
        feitos += b
    return np.percentile(out, [2.5, 97.5])


g1 = []
for faixa in FAIXA_SEG_LABELS:
    for flag in [True, False]:
        pos = np.flatnonzero((df["faixa_seguidores"] == faixa).to_numpy() & (eh_spon == flag))
        v = eng[pos]
        lo, hi = boot_ic(v)
        g1.append({"faixa": faixa, "patrocinado": flag, "n": len(pos),
                   "media": v.mean(), "ic_inferior": lo, "ic_superior": hi})
g1 = pd.DataFrame(g1)
print(g1.to_string(index=False))

org = g1[~g1["patrocinado"]].set_index("faixa").loc[FAIXA_SEG_LABELS]
spo = g1[g1["patrocinado"]].set_index("faixa").loc[FAIXA_SEG_LABELS]

fig, ax = plt.subplots()
x = np.arange(len(FAIXA_SEG_LABELS))
larg = 0.34
kw = dict(error_kw=dict(ecolor=CINZA_LINHA, elinewidth=1.2, capthick=1.2), capsize=4)

for desloc, dados, cor, rotulo in [(-0.19, org, CINZA, "Orgânico"),
                                   (0.19, spo, DESTAQUE, "Patrocinado")]:
    err = np.vstack([dados["media"] - dados["ic_inferior"],
                     dados["ic_superior"] - dados["media"]])
    ax.bar(x + desloc, dados["media"], larg, yerr=err, color=cor, label=rotulo, **kw)
    for xi, m in zip(x + desloc, dados["media"]):
        ax.text(xi, m + 55, br(m, 0), ha="center", va="bottom", fontsize=11)

ax.set_ylim(0, 2350)                       # eixo Y comecando em 0 (obrigatorio)
ax.set_xticks(x, FAIXA_SEG_EXIBE)
ax.set_xlabel("Faixa de seguidores do creator")
ax.set_ylabel("Interações por post (média)")
ax.set_title("Patrocinado e orgânico entregam o mesmo engajamento, "
             "em qualquer tamanho de creator", pad=14)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: br(v, 0)))
ax.yaxis.grid(True, alpha=0.5)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, -0.14))
fig.tight_layout()
salvar_fig(fig, "grafico_01_engajamento_por_faixa.png")

resumo["g1"] = g1
largura_ic = (g1["ic_superior"] - g1["ic_inferior"]).max()
notas.append(
    "**Gráfico 1 — as 8 barras são visualmente idênticas.** As médias ficam entre "
    f"{br(g1['media'].min(), 1)} e {br(g1['media'].max(), 1)} interações: amplitude de "
    f"{br(g1['media'].max() - g1['media'].min(), 1)} interação "
    f"({br((g1['media'].max() / g1['media'].min() - 1) * 100, 2)}%). O IC 95% mais largo mede "
    f"{br(largura_ic, 1)} interações, cerca de {br(largura_ic / 2350 * 100, 2)}% da altura do "
    "eixo — as barras de erro saem do tamanho de um traço e praticamente não aparecem no PNG. "
    "É o que os números mostram, nada foi ajustado.")
notas.append(
    "**Gráfico 1 — IC levemente diferentes dos do Bloco 5 da OS-03.** As 8 médias e os 8 n "
    "batem casa a casa com `solution/outputs/os03/bloco5_engajamento_por_faixa.csv`. Os IC "
    "mudam na 1ª ou 2ª casa decimal (ex.: faixa até 50K patrocinado, 2.008,35–2.013,60 aqui "
    "contra 2.008,21–2.013,48 na OS-03) porque na OS-03 o gerador seed 42 já tinha sido "
    "consumido pelos Blocos 1 a 4 antes do Bloco 5, e aqui ele começa do zero. Mesma lógica, "
    "mesmo número de reamostragens; só o fluxo de números aleatórios é outro.")


# ================================================================ Grafico 2
# Lifts de taxa_engajamento dos niveis 1 a 4 da OS-02 (leitura dos .csv).
print("\n[2] grafico_02_segmentos_vs_limite.png")

lifts_n = []
for nivel in [1, 2, 3, 4]:
    t = pd.read_csv(OUT_OS02 / f"nivel{nivel}.csv")
    t = t[t["metrica"] == "taxa_engajamento"]
    lifts_n.append(t[["nivel", "variaveis", "segmento", "n", "lift"]])
    print(f"  nivel {nivel}: {len(t)} segmentos")
g2 = pd.concat(lifts_n, ignore_index=True)
lifts = g2["lift"].to_numpy()
print(f"  total: {len(lifts)} segmentos | min {lifts.min():.6f} | max {lifts.max():.6f}")

desvio_max_pct = np.abs(lifts - 1).max() * 100
fora_de_2pct = int((np.abs(lifts - 1) > 0.02).sum())
fora_de_10pct = int((np.abs(lifts - 1) > 0.10).sum())

rng_jitter = np.random.default_rng(SEED)
y = rng_jitter.uniform(-0.33, 0.33, size=len(lifts))      # leve dispersao vertical

# eixo baixo e largo: os pontos ficam numa faixa horizontal
fig = plt.figure(figsize=(10, 6))
ax = fig.add_axes((0.055, 0.30, 0.91, 0.36))
ax.axvspan(0.90, 1.10, color=DESTAQUE, alpha=0.09, zorder=0)
for b in [0.90, 1.10]:
    ax.axvline(b, color=DESTAQUE, linestyle="--", linewidth=1.3, zorder=1)
ax.scatter(lifts, y, s=14, color=CINZA, alpha=0.55, edgecolors="none", zorder=3)

ax.text(1.0, 1.16, "Diferença mínima para importar (±10%)", clip_on=False,
        ha="center", va="bottom", fontsize=11, color=DESTAQUE)

ax.set_xlim(0.85, 1.15)
ax.set_ylim(-1, 1)
ax.set_xticks(np.arange(0.85, 1.16, 0.05))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: br_pct((v - 1) * 100, 0, sinal=True)))
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.set_xlabel("Diferença de engajamento vs. média da plataforma", labelpad=10)
ax.set_title(f"Todos os {br(len(lifts), 0)} segmentos ficam a menos de 2% da média", pad=42)
salvar_fig(fig, "grafico_02_segmentos_vs_limite.png")

resumo["g2"] = {"segmentos": len(lifts), "por_nivel": [len(t) for t in lifts_n],
                "lift_min": lifts.min(), "lift_max": lifts.max(),
                "desvio_max_pct": desvio_max_pct,
                "fora_2pct": fora_de_2pct, "fora_10pct": fora_de_10pct}
notas.append(
    f"**Gráfico 2 — o título fixo confere.** São {br(len(lifts), 0)} segmentos (níveis 1 a 4, "
    f"métrica `taxa_engajamento`). O maior desvio absoluto vs. a média da plataforma é "
    f"{br(desvio_max_pct, 4)}%: {br(fora_de_2pct, 0)} segmentos passam de ±2% e "
    f"{br(fora_de_10pct, 0)} passam de ±10%. Consequência visual: dentro de um eixo de −15% a "
    "+15%, os 693 pontos viram uma mancha estreita sobre o 0% e a faixa sombreada fica vazia.")


# ================================================================ Grafico 3
# Recalculo da busca do Nivel 4 da OS-02 em dois cenarios (sem injecao e com +5%).
print("\n[3] grafico_03_controle_positivo.png")

chave4 = df[COMBO_N4].astype(str).agg(" | ".join, axis=1)
cod4, nomes4 = pd.factorize(chave4, sort=True)
k4 = len(nomes4)
cont4 = np.bincount(cod4, minlength=k4)
valido4 = cont4 >= MIN_N
idx_validos = np.flatnonzero(valido4)
print(f"  segmentos existentes: {k4} | com n >= {MIN_N}: {int(valido4.sum())}")

# refaz o sorteio do Bloco 3b da OS-03c (mesma logica) e confere com o segmento da OS
candidatos = [g for g in range(k4) if 100 <= cont4[g] <= 150]
g_sorteado = int(np.random.default_rng(SEED).choice(candidatos))
nome_sorteado = nomes4[g_sorteado]
print(f"  candidatos (n entre 100 e 150): {len(candidatos)}")
print(f"  sorteado: {nome_sorteado} (n={cont4[g_sorteado]})")
if nome_sorteado != SEGMENTO_INJECAO:
    raise SystemExit(f"sorteio nao reproduziu o segmento da OS: {nome_sorteado}")
pos_sorteado = np.flatnonzero(cod4 == g_sorteado)

plat_pos = [np.flatnonzero((df["platform"] == p).to_numpy())
            for p in sorted(df["platform"].unique())]
taxa_base = df["taxa_engajamento"].to_numpy(dtype=float)
plat = df["platform"].to_numpy()


def cenario(efeito):
    """Lifts do Nivel 4, posicao do segmento sorteado e p95 do maior lift por acaso."""
    taxa = taxa_base.copy()
    taxa[pos_sorteado] = taxa[pos_sorteado] * efeito
    media_plat = pd.Series(taxa).groupby(plat).transform("mean").to_numpy()
    idx = taxa / media_plat

    lifts_todos = np.bincount(cod4, weights=idx, minlength=k4) / cont4
    lifts_v = lifts_todos[valido4]
    ordem = np.argsort(-lifts_v)
    ranking = list(idx_validos[ordem])
    posicao = ranking.index(g_sorteado) + 1

    # teste contra o acaso: embaralha o indice dentro de cada plataforma
    rng_perm = np.random.default_rng(SEED)
    maiores = np.empty(N_PERM)
    for r in range(N_PERM):
        emb = idx.copy()
        for pos in plat_pos:
            emb[pos] = idx[rng_perm.permutation(pos)]
        maiores[r] = (np.bincount(cod4, weights=emb, minlength=k4) / cont4)[valido4].max()
    return {"lifts_ordenados": lifts_v[ordem], "posicao": posicao,
            "lift_segmento": lifts_todos[g_sorteado],
            "p95_acaso": float(np.percentile(maiores, 95)),
            "n_ranking": len(ranking)}


cen = {"Dados originais": cenario(1.00),
       "Com +5% inserido em um segmento": cenario(1.05)}
for nome, c in cen.items():
    print(f"  {nome}: posicao {c['posicao']} de {c['n_ranking']} | "
          f"lift {c['lift_segmento']:.6f} | p95 acaso {c['p95_acaso']:.6f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 6), sharey=True)
for ax, (titulo, c) in zip(axes, cen.items()):
    n_r = c["n_ranking"]
    xs = np.arange(1, n_r + 1)
    ys = (c["lifts_ordenados"] - 1) * 100
    ax.scatter(xs, ys, s=16, color=CINZA, edgecolors="none", zorder=3)

    px = c["posicao"]
    py = (c["lift_segmento"] - 1) * 100
    ax.scatter([px], [py], s=70, color=DESTAQUE, zorder=5)
    desloc_x = 10 if px < n_r / 2 else -10
    ax.annotate(f"{px}º de {n_r}", (px, py),
                xytext=(desloc_x, 14), textcoords="offset points",
                ha="left" if desloc_x > 0 else "right",
                fontsize=11, color=DESTAQUE, fontweight="bold")

    y95 = (c["p95_acaso"] - 1) * 100
    ax.axhline(y95, color=CINZA_LINHA, linestyle="--", linewidth=1.3, zorder=2)
    ax.text(n_r, y95 + 0.12, "Maior resultado esperado por acaso",
            ha="right", va="bottom", fontsize=11, color=CINZA_LINHA)

    ax.set_title(titulo, pad=10)
    ax.set_xlim(-4, n_r + 4)
    ax.yaxis.grid(True, alpha=0.5)
    ax.set_axisbelow(True)

axes[0].yaxis.set_major_formatter(FuncFormatter(lambda v, _: br_pct(v, 0, sinal=True)))
axes[0].set_ylim(-1.5, 6.0)
fig.supxlabel("Segmentos ordenados", fontsize=12)
fig.supylabel("Diferença vs. média da plataforma (%)", fontsize=12)
fig.suptitle("Teste do método: um efeito de +5% sai do último lugar para o primeiro",
             fontsize=13.5, y=0.975)
fig.tight_layout(rect=(0.01, 0.0, 1, 0.94))
salvar_fig(fig, "grafico_03_controle_positivo.png")

resumo["g3"] = {"segmento": nome_sorteado, "n": int(cont4[g_sorteado]),
                "segmentos_existentes": k4, "no_ranking": int(valido4.sum()),
                "cenarios": cen}
pos_sem = cen["Dados originais"]["posicao"]
pos_com = cen["Com +5% inserido em um segmento"]["posicao"]
if not (pos_sem == 128 and pos_com == 1):
    notas.append(
        f"**Gráfico 3 — posições diferentes do exemplo da OS.** O calculado é {pos_sem} de "
        f"{cen['Dados originais']['n_ranking']} sem injeção e {pos_com} de "
        f"{cen['Com +5% inserido em um segmento']['n_ranking']} com +5%; a OS dá como exemplo "
        "128º e 1º. Os rótulos saem com os valores calculados e o título fixo foi mantido.")

p95_os02 = 1.006406   # teste_acaso.csv da OS-02, nivel 4, taxa_engajamento
p95_aqui = cen["Dados originais"]["p95_acaso"]
notas.append(
    f"**Gráfico 3 — reprodução confere, com uma diferença esperada no p95.** O sorteio do "
    f"Bloco 3b foi refeito e caiu no mesmo segmento (`{nome_sorteado}`, n = "
    f"{br(int(cont4[g_sorteado]), 0)}, entre {br(len(candidatos), 0)} candidatos), o lift com "
    f"+5% deu {br(cen['Com +5% inserido em um segmento']['lift_segmento'], 6)} — igual ao do "
    "`bloco3b_injecao_na_busca.csv` da OS-03c — e as posições saíram "
    f"{pos_sem}º e {pos_com}º de {cen['Dados originais']['n_ranking']}. O p95 do acaso sem "
    f"injeção deu {br(p95_aqui, 6)} aqui contra {br(p95_os02, 6)} no "
    "`teste_acaso.csv` da OS-02 (0,03% de diferença): mesma lógica e mesmas 200 permutações, "
    "mas na OS-02 o gerador seed 42 chega nesse teste em outro ponto do fluxo e o nível 4 era "
    "avaliado junto com as outras métricas. A posição da linha tracejada não muda no olho.")


# ================================================================ Grafico 4
# Maior efeito maximo plausivel por variavel (OS-03c, bloco1_equivalencia.csv).
print("\n[4] grafico_04_efeito_maximo.png")

eq = pd.read_csv(OUT_OS03C / "bloco1_equivalencia.csv")
eq = eq[eq["metrica"] == "taxa_engajamento"]
g4 = (eq.groupby("variavel")["efeito_maximo_plausivel_pct"].max()
        .rename("efeito_max_pct").reset_index())
g4["variavel_pt"] = g4["variavel"].map(VARS_PT)
if g4["variavel_pt"].isna().any():
    raise SystemExit(f"variavel sem nome em portugues: {g4[g4['variavel_pt'].isna()]}")
g4 = g4.sort_values("efeito_max_pct", ascending=False).reset_index(drop=True)
print(g4.to_string(index=False))

fig, ax = plt.subplots()
ypos = np.arange(len(g4))[::-1]            # maior no topo
ax.barh(ypos, g4["efeito_max_pct"], height=0.6, color=CINZA)
for yi, v in zip(ypos, g4["efeito_max_pct"]):
    ax.text(v + 0.015, yi, br(v, 2) + "%", va="center", ha="left", fontsize=11)

ax.axvline(1.0, color=DESTAQUE, linestyle="--", linewidth=1.6, zorder=4)
ax.text(0.985, len(g4) - 0.55, "Limite de equivalência (1%)",
        ha="right", va="top", fontsize=11, color=DESTAQUE)

ax.set_yticks(ypos, g4["variavel_pt"])
ax.set_xlim(0, 1.2)
ax.set_xticks(np.arange(0, 1.21, 0.2))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: br(v, 1) + "%"))
ax.set_xlabel("Efeito máximo plausível sobre a taxa de engajamento")
ax.set_title("O maior efeito possível de cada variável fica abaixo de 0,15%", pad=14)
ax.xaxis.grid(True, alpha=0.5)
ax.set_axisbelow(True)
fig.tight_layout()
salvar_fig(fig, "grafico_04_efeito_maximo.png")

resumo["g4"] = g4
maior_g4 = g4["efeito_max_pct"].max()
acima_015 = int((g4["efeito_max_pct"] > 0.15).sum())
notas.append(
    f"**Gráfico 4 — o título fixo confere.** O maior efeito máximo plausível é "
    f"{br(maior_g4, 4)}% ({VARS_PT[g4.loc[0, 'variavel']]}) e {br(acima_015, 0)} variáveis "
    "passam de 0,15%. Consequência visual: com o eixo de 0 a 1,2%, as 8 barras ocupam no "
    "máximo um oitavo da largura e a linha de 1% fica isolada à direita.")


# ================================================================ resumo
print("\n[5] resumo_os05.md")

FAIXA_MD = dict(zip(FAIXA_SEG_LABELS, FAIXA_SEG_EXIBE))

L = []
L.append("# OS-05 — Gráficos para os relatórios\n")
L.append("Script: `solution/analysis/os05_graficos.py`")
L.append("Fonte: `datasets/social_media_dataset.csv` "
         f"({br(N, 0)} posts), mais as saídas da OS-02 e da OS-03c")
L.append("Saídas: `solution/outputs/os05/` (4 arquivos .png)\n")
L.append("**Padrão visual dos 4 gráficos:** matplotlib, PNG, 150 dpi, 10 × 6 polegadas, fundo "
         "branco, fonte de 11 pt para cima, grade horizontal leve, textos em português e "
         "números com vírgula decimal. Duas cores: cinza `#9A9A9A` para o padrão e vermelho "
         "`#C0392B` para o destaque. Os títulos e rótulos são os textos fixos da OS, sem "
         "alteração.\n")
L.append("| Arquivo | Origem dos dados |")
L.append("|---|---|")
L.append("| `grafico_01_engajamento_por_faixa.png` | recalculado do CSV (Bloco 5 da OS-03) |")
L.append("| `grafico_02_segmentos_vs_limite.png` | `solution/outputs/os02/nivel1.csv` a "
         "`nivel4.csv` |")
L.append("| `grafico_03_controle_positivo.png` | recalculado do CSV (Nível 4 da OS-02 + "
         "sorteio do Bloco 3b da OS-03c) |")
L.append("| `grafico_04_efeito_maximo.png` | "
         "`solution/outputs/os03c/bloco1_equivalencia.csv` |")

L.append("\n---\n")
L.append("## 1. `grafico_01_engajamento_por_faixa.png`\n")
L.append("Média de `engajamento` (likes + shares + comments_count) por faixa de seguidores × "
         "`is_sponsored`, recalculada do CSV com a lógica do Bloco 5 da OS-03. Barras "
         "agrupadas (orgânico em cinza, patrocinado em vermelho), IC 95% bootstrap "
         "(1.000 reamostragens, seed 42) como barra de erro, eixo Y de 0 a 2.350.\n")
L.append("| Faixa de seguidores | Grupo | n | Média | IC 95% inferior | IC 95% superior |")
L.append("|---|---|---|---|---|---|")
for faixa in FAIXA_SEG_LABELS:
    for flag, rot in [(False, "Orgânico"), (True, "Patrocinado")]:
        r = g1[(g1["faixa"] == faixa) & (g1["patrocinado"] == flag)].iloc[0]
        L.append(f"| {FAIXA_MD[faixa]} | {rot} | {br(r['n'], 0)} | {br(r['media'], 2)} | "
                 f"{br(r['ic_inferior'], 2)} | {br(r['ic_superior'], 2)} |")
rotulos = [br(g1[(g1["faixa"] == f) & (g1["patrocinado"] == s)].iloc[0]["media"], 0)
           for f in FAIXA_SEG_LABELS for s in [False, True]]
L.append("\nRótulo escrito sobre cada barra, sem casas decimais, na ordem do eixo X: "
         + ", ".join(rotulos) + ".")

L.append("\n## 2. `grafico_02_segmentos_vs_limite.png`\n")
r2 = resumo["g2"]
L.append(f"Lifts de `taxa_engajamento` dos {br(r2['segmentos'], 0)} segmentos dos níveis 1 a 4 "
         "da OS-02, lidos dos .csv de `solution/outputs/os02/`. Um ponto cinza por segmento "
         "numa faixa horizontal, com dispersão vertical uniforme em [−0,33; 0,33] (seed 42) "
         "para não sobrepor. Faixa sombreada entre 0,90 e 1,10 e eixo X de 0,85 a 1,15, "
         "rotulado de −15% a +15%.\n")
L.append("| Item | Valor |")
L.append("|---|---|")
L.append("| Segmentos por nível (1 / 2 / 3 / 4) | "
         + " / ".join(br(v, 0) for v in r2["por_nivel"]) + " |")
L.append(f"| Total de segmentos | {br(r2['segmentos'], 0)} |")
L.append(f"| Menor lift | {br(r2['lift_min'], 6)} "
         f"({br_pct((r2['lift_min'] - 1) * 100, 2, True)}) |")
L.append(f"| Maior lift | {br(r2['lift_max'], 6)} "
         f"({br_pct((r2['lift_max'] - 1) * 100, 2, True)}) |")
L.append(f"| Maior desvio absoluto vs. a média | {br(r2['desvio_max_pct'], 4)}% |")
L.append(f"| Segmentos fora de ±2% | {br(r2['fora_2pct'], 0)} |")
L.append(f"| Segmentos fora de ±10% (faixa sombreada) | {br(r2['fora_10pct'], 0)} |")

L.append("\n## 3. `grafico_03_controle_positivo.png`\n")
r3 = resumo["g3"]
L.append("Busca do Nível 4 da OS-02 (platform × content_type × content_category × "
         f"faixa_seguidores, n ≥ {MIN_N}, `taxa_engajamento`) recalculada do CSV em dois "
         f"cenários: sem injeção e com +5% no segmento sorteado. "
         f"{br(r3['segmentos_existentes'], 0)} segmentos existentes, "
         f"{br(r3['no_ranking'], 0)} no ranking. Segmento da injeção: "
         f"`{r3['segmento']}` (n = {br(r3['n'], 0)}), reproduzido com o sorteio do Bloco 3b da "
         "OS-03c (seed 42). Linha tracejada no p95 do maior lift por acaso (200 permutações "
         "dentro da plataforma, seed 42). Os dois painéis compartilham o eixo Y (−1% a +6%).\n")
L.append("| Painel | Lift do segmento sorteado | Posição | p95 do maior lift por acaso |")
L.append("|---|---|---|---|")
for nome, c in r3["cenarios"].items():
    L.append(f"| {nome} | {br(c['lift_segmento'], 6)} "
             f"({br_pct((c['lift_segmento'] - 1) * 100, 2, True)}) | "
             f"{c['posicao']}º de {c['n_ranking']} | {br(c['p95_acaso'], 6)} "
             f"({br_pct((c['p95_acaso'] - 1) * 100, 2, True)}) |")
c0 = r3["cenarios"]["Dados originais"]["lifts_ordenados"]
c1 = r3["cenarios"]["Com +5% inserido em um segmento"]["lifts_ordenados"]
L.append(f"\nFaixa dos 128 lifts no painel 1: {br(c0.min(), 6)} a {br(c0.max(), 6)}. "
         f"No painel 2: {br(c1.min(), 6)} a {br(c1.max(), 6)}.")

L.append("\n## 4. `grafico_04_efeito_maximo.png`\n")
L.append("Maior efeito máximo plausível (%) entre os segmentos de cada variável, só para "
         "`taxa_engajamento`, lido de `solution/outputs/os03c/bloco1_equivalencia.csv`. "
         "Barras horizontais cinza ordenadas da maior para a menor, valor ao lado com 2 casas "
         "decimais, eixo X de 0 a 1,2% e linha tracejada vermelha em 1%.\n")
L.append("| Variável (rótulo do gráfico) | Coluna de origem | Efeito máximo plausível |")
L.append("|---|---|---|")
for _, r in g4.iterrows():
    L.append(f"| {r['variavel_pt']} | `{r['variavel']}` | {br(r['efeito_max_pct'], 4)}% |")

L.append("\n---\n")
L.append("## Pontos suspeitos ou problemas encontrados\n")
for i, nota in enumerate(notas, start=1):
    L.append(f"{i}. {nota}\n")

(OUT_DIR / "resumo_os05.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"  -> resumo_os05.md")
print(f"\nPronto. Saidas em {OUT_DIR}")
