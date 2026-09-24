"""
Servidor MCP do G4 Analise: deixa o agente do G4 OS (ou qualquer cliente MCP) usar o sistema como ferramenta.

O agente chama funcoes tipadas (listar sessoes, criar sessao, resumo, listas priorizadas, plano de acao, cruzar
ferramentas, exportar...) e recebe os MESMOS numeros da janela: o motor e as sessoes sao os mesmos.

Seguranca: nada aqui apaga dados, manda mensagem ou executa acao no mundo. As ferramentas so leem as sessoes,
criam sessoes novas e gravam arquivos novos em Downloads/G4 Analise.

Uso no G4 OS (fonte MCP "stdio"): command = python do .venv, args = [este arquivo]. Ver integracao_g4os/.
Teste sem G4 OS:  .venv\\Scripts\\python app\\servidor_mcp.py   (fica esperando um cliente MCP pela entrada padrao)
"""

import json
import os
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")

from mcp.server.fastmcp import FastMCP  # noqa: E402

import servicos  # noqa: E402
from nucleo import cruzamentos, exportar, perfis, sessoes  # noqa: E402
from nucleo.contratos import MODULOS  # noqa: E402

mcp = FastMCP(
    "g4-analise",
    instructions=(
        "G4 Analise: sistema de análise com 4 ferramentas (churn, suporte, leads, mídia) que trabalham sozinhas ou juntas. "
        "Sempre use estas ferramentas para números e listas em vez de calcular por conta própria. Fluxo típico: "
        "listar_sessoes -> (criar_sessao, se precisar) -> obter_resumo -> consultar_lista / obter_plano_de_acao. "
        "Os números vêm com o nível de evidência (teste estatístico): repita essa ressalva ao usuário."
    ),
)

_CACHE = {}
_PRONTO = __import__("threading").Event()   # vira True quando as bibliotecas pesadas terminam de carregar
_PRONTO.set()                               # sem aquecimento (ex.: importado por testes) nao ha o que esperar


# ---------------------------------------------------------------- utilidades

def _sessao(sessao_id):
    s = sessoes.obter(sessao_id)
    if not s:
        raise ValueError(f"sessão '{sessao_id}' não existe. Use listar_sessoes.")
    return s


def _resultado(sessao_id, premissas=None):
    _PRONTO.wait(timeout=180)   # nao importar sklearn ao mesmo tempo que o aquecimento (import circular)
    s = _sessao(sessao_id)
    versoes = tuple(sorted((k, os.path.getmtime(v)) for k, v in s["arquivos"].items() if os.path.exists(v)))
    chave = (sessao_id, json.dumps(premissas or {}, sort_keys=True), versoes)
    if chave not in _CACHE:
        _CACHE[chave] = servicos.analisar_com_cache(s, premissas)
    return s, _CACHE[chave]


def _registros(df, limite=None, colunas=None):
    if df is None:
        return []
    d = df.reset_index() if df.index.name else df
    if colunas:
        d = d[[c for c in colunas if c in d.columns]]
    if limite:
        d = d.head(int(limite))
    d = d.drop(columns=[c for c in d.columns if d[c].map(lambda x: isinstance(x, (list, dict, set))).any()], errors="ignore")
    return json.loads(d.to_json(orient="records", force_ascii=False, date_format="iso", double_precision=4))


def _textos(modulo):
    import importlib
    return importlib.import_module(f"modulos.{modulo}.textos")


def _sem_md(linhas):
    return [x.replace("**", "") for x in linhas]


# listas que o agente pode consultar, por modulo: nome -> (descricao, funcao(r) -> DataFrame)
LISTAS = {
    "churn": {
        "contas_priorizadas": ("Contas ativas por prioridade (risco × valor), com score e motivos", lambda r: r["ativos"]),
        "precisa_suporte": ("Contas em risco com problema de suporte", lambda r: r["precisa_suporte"]),
        "sinais": ("Sinais de comportamento testados (churn com × sem o sinal, p-valor)", lambda r: r["sinais"]),
        "motivos": ("Motivos declarados de cancelamento", lambda r: r["motivos"]),
        "segmentos": ("Taxa de churn por segmento/canal/país/plano, com intervalo de confiança",
                      lambda r: _juntar_segmentos(r["segmentos"])),
    },
    "suporte": {
        "chamados": ("Chamados com duração calculada", lambda r: r["chamados"]),
        "gargalos": ("Tempo e acúmulo por canal, prioridade e tipo", lambda r: _juntar_segmentos(r["gargalos"]["por_dimensao"])),
        "satisfacao": ("O que impacta a satisfação (teste por variável)", lambda r: r["satisfacao"]["tabela"] if r["satisfacao"] else None),
        "desperdicio": ("Horas acima da meta por prioridade", lambda r: r["desperdicio"]["por_prioridade"] if r["desperdicio"] else None),
        "automacao": ("Faixas de confiança do classificador (automático / sugere / humano)",
                      lambda r: r["automacao"]["faixas"] if r["automacao"] else None),
    },
    "leads": {
        "foco": ("Deals vivos por valor esperado (lista da segunda-feira)", lambda r: r["abertos"][r["abertos"].lista == "Foco"]),
        "requalificar": ("Deals parados além do maior ciclo já fechado", lambda r: r["abertos"][r["abertos"].lista == "Requalificar"]),
        "prospeccao": ("Deals em prospecção", lambda r: r["abertos"][r["abertos"].lista == "Prospecção"]),
        "vendedores": ("Pipeline por vendedor (parados, valor esperado, ganho histórico)", lambda r: r["vendedores"]),
        "fatores": ("Taxa de ganho por vendedor/produto/setor/porte", lambda r: _juntar_segmentos(r["fatores"])),
    },
    "midia": {
        "dimensoes": ("Engajamento por dimensão com veredito", lambda r: _juntar_segmentos(r["drivers"])),
        "combinacoes": ("Combinações plataforma × formato × categoria × tamanho", lambda r: r["combinacoes"]["tabela"] if r["combinacoes"] else None),
        "patrocinio_por_faixa": ("Patrocinado − orgânico por faixa de criador", lambda r: r["patrocinio"]["por_faixa"] if r["patrocinio"] else None),
        "custo_por_faixa": ("Custo por interação por faixa de criador (premissa de custo)",
                            lambda r: r["patrocinio"].get("custo") if r["patrocinio"] else None),
        "audiencia": ("Qual audiência engaja mais, por plataforma", lambda r: r["audiencia"]),
        "painel_semanal": ("Engajamento semanal por plataforma", lambda r: r["painel"]),
    },
}


def _juntar_segmentos(d):
    import pandas as pd
    partes = []
    for chave, v in d.items():
        t = v["tabela"].copy()
        t.insert(0, "dimensao", v.get("rotulo", chave))
        t = t.rename(columns={t.columns[1]: "grupo"}) if "grupo" not in t.columns else t
        t["p_valor_dimensao"] = v.get("p_valor", v.get("p_tempo"))
        partes.append(t)
    return pd.concat(partes, ignore_index=True) if partes else None


# ---------------------------------------------------------------- ferramentas de leitura

@mcp.tool()
def listar_ferramentas() -> dict:
    """Lista as 4 ferramentas de análise (módulos), o que cada uma resolve, as listas consultáveis e os cruzamentos."""
    return {"modulos": [{"chave": m.chave, "nome": m.nome, "desafio": m.desafio, "descricao": m.descricao,
                         "tabelas": [{"nome": t.nome, "obrigatoria": t.obrigatoria, "campos_obrigatorios": [c.nome for c in t.obrigatorios()]}
                                     for t in m.tabelas],
                         "listas": {k: v[0] for k, v in LISTAS[m.chave].items()}} for m in MODULOS.values()],
            "cruzamentos": [{"origem": o, "destino": d, "selo": cruzamentos.SELOS[x[0]][1], "tipo": x[1], "descricao": x[2],
                             "disponivel": (o, d) in servicos.PONTES} for (o, d), x in cruzamentos.MATRIZ.items()]}


@mcp.tool()
def listar_sessoes() -> list:
    """Lista as sessões de análise salvas (as mesmas da janela do G4 Analise), das mais novas para as mais antigas."""
    return [{"id": s["id"], "nome": s["nome"], "modulo": s["modulo"], "fonte": s["fonte"], "criada_em": s["criada_em"],
             "origem_id": s["origem_id"], "origem": s["origem_descricao"],
             "selo": cruzamentos.SELOS.get(s["selo"], ("", ""))[1] if s["selo"] else None} for s in sessoes.listar()]


@mcp.tool()
def obter_resumo(sessao_id: str, premissas: dict | None = None) -> dict:
    """Resumo executivo da sessão (texto com os números), métricas principais e limitações dos dados.
    premissas: opcional, muda as premissas do módulo (ex.: {"taxa_recuperacao_pct": 30} no churn)."""
    s, r = _resultado(sessao_id, premissas)
    t = _textos(s["modulo"])
    return {"sessao": s["nome"], "modulo": s["modulo"], "resumo_executivo": _sem_md(t.resumo_executivo(r)),
            "qualidade_dos_dados": r["qualidade"], "premissas_usadas": {k: v for k, v in vars(r["premissas"]).items()},
            "origem": s["origem_descricao"]}


@mcp.tool()
def obter_plano_de_acao(sessao_id: str, premissas: dict | None = None) -> list:
    """Plano de ação / estratégia priorizada da sessão: o que fazer, para quem, impacto e força da evidência."""
    s, r = _resultado(sessao_id, premissas)
    if s["modulo"] == "suporte":
        return _plano_suporte(r)
    tabela = r["estrategia"] if s["modulo"] == "midia" else r.get("acoes")
    return _registros(tabela.drop(columns=["ids"], errors="ignore") if tabela is not None else None)


def _plano_suporte(r):
    """O Suporte entrega o plano em blocos (acúmulo, prioridade, automação, não automatizar, satisfação)."""
    L, v, g = [], r["volume"], r["gargalos"]["por_dimensao"]
    if v.get("em_aberto_%", 0) > 30:
        L.append({"acao": "Atacar o acúmulo (é capacidade, não canal)", "evidencia": "fato nos dados",
                  "por_que": f"{v['em_aberto_%']:.0f}% dos chamados sem resolução, igual em todos os grupos"})
    if "prioridade" in g and g["prioridade"]["p_tempo"] >= 0.05:
        L.append({"acao": "Fazer a prioridade valer (fila por urgência e meta por prioridade)", "evidencia": "fato nos dados",
                  "por_que": f"o tempo de atendimento não muda com a prioridade (p = {g['prioridade']['p_tempo']:.2f})".replace(".", ",")})
    a = r["automacao"]
    if a:
        f = a["faixas"].set_index("faixa")
        L.append({"acao": f"Automatizar a triagem com confiança ≥ {r['premissas'].confianca_auto:.0%}", "evidencia": "testado em tickets nunca vistos",
                  "por_que": f"{f.loc['Automático', 'tickets_%']:.0f}% dos tickets com {f.loc['Automático', 'acerto_%']:.1f}".replace(".", ",") + "% de acerto; "
                             f"~{a['horas_mes']:.0f} h/mês de triagem economizadas (premissas editáveis)"})
        L.append({"acao": "Nunca automatizar", "evidencia": "regra de negócio",
                  "por_que": "cancelamento, reembolso, prioridade crítica, permissão de acesso e confiança baixa ficam com humano"})
    sat = r["satisfacao"]
    if sat and (sat["tabela"].p_valor >= 0.05).all():
        L.append({"acao": "Medir satisfação de outro jeito", "evidencia": "fato nos dados",
                  "por_que": "nenhuma variável (nem o tempo) muda a nota: ela não serve como termômetro"})
    return L


@mcp.tool()
def consultar_lista(sessao_id: str, lista: str | None = None, filtros: dict | None = None, ordenar_por: str | None = None,
                    decrescente: bool = True, limite: int = 20, colunas: list | None = None) -> dict:
    """Consulta uma lista/tabela da análise. Sem 'lista', usa a principal do módulo (churn: contas_priorizadas,
    suporte: chamados, leads: foco, mídia: dimensoes). Nomes em listar_ferramentas.
    filtros: {coluna: valor ou [valores]} (igualdade). ordenar_por: nome de coluna. limite: máximo de linhas."""
    s, r = _resultado(sessao_id)
    opcoes = LISTAS[s["modulo"]]
    lista = lista or next(iter(opcoes))
    if lista not in opcoes:
        raise ValueError(f"lista '{lista}' não existe para {s['modulo']}. Opções: {', '.join(opcoes)}")
    df = opcoes[lista][1](r)
    if df is None:
        return {"lista": lista, "linhas": [], "aviso": "a base desta sessão não tem os dados para esta lista"}
    df = df.reset_index() if df.index.name else df
    for col, val in (filtros or {}).items():
        if col not in df.columns:
            raise ValueError(f"coluna '{col}' não existe. Colunas: {', '.join(map(str, df.columns))}")
        vals = val if isinstance(val, list) else [val]
        df = df[df[col].astype(str).isin([str(v) for v in vals])]
    if ordenar_por:
        df = df.sort_values(ordenar_por, ascending=not decrescente)
    return {"lista": lista, "descricao": opcoes[lista][0], "total_linhas": int(len(df)), "colunas": [str(c) for c in df.columns],
            "linhas": _registros(df, limite, colunas)}


@mcp.tool()
def obter_metodo(sessao_id: str) -> dict:
    """Como cada número da sessão foi calculado (método, testes, premissas) — para explicar ao usuário."""
    s, r = _resultado(sessao_id)
    t = _textos(s["modulo"])
    return {"metodo": _sem_md(t.explicacao_metodo(r)), "qualidade_dos_dados": r["qualidade"]}


@mcp.tool()
def sugerir_depara(modulo: str, arquivos: dict) -> dict:
    """Para arquivos PRÓPRIOS (não os do desafio): sugere a ligação coluna do arquivo -> campo do sistema.
    arquivos: {tabela: caminho completo do CSV/Excel/JSON}. Mostre a sugestão ao usuário antes de criar a sessão."""
    sugestao, faltando = servicos.sugerir_depara(modulo, arquivos)
    return {"sugestao": sugestao, "campos_obrigatorios_sem_coluna": faltando}


@mcp.tool()
def classificar_ticket(sessao_id: str, texto: str, tipo: str | None = None, prioridade: str | None = None) -> dict:
    """(Suporte) Classifica um ticket novo: categoria, confiança e decisão (automático / IA sugere / humano),
    com tickets parecidos já vistos. Precisa de uma sessão de Suporte com os textos classificados (Dataset 2)."""
    from modulos.suporte.analise import decidir, similares
    s, r = _resultado(sessao_id)
    if s["modulo"] != "suporte" or not r["classificador"]:
        raise ValueError("use uma sessão de Suporte que tenha os textos classificados (Dataset 2)")
    d = decidir(texto, r["classificador"], r["premissas"], tipo=tipo, prioridade=prioridade)
    d["alternativas"] = [{"categoria": c, "confianca": round(p, 3)} for c, p in d["alternativas"]]
    return {**d, "parecidos": _registros(similares(texto, r["classificador"]))}


@mcp.tool()
def recomendar_post(sessao_id: str, plataforma: str | None = None, tipo: str | None = None, categoria: str | None = None,
                    faixa_seguidores: str | None = None, patrocinado: bool | None = None) -> dict:
    """(Mídia) Para um post que o time quer publicar: engajamento esperado (posts parecidos do histórico) e se trocar
    formato/plataforma renderia mais. faixa_seguidores: '<10K', '10K–50K', '50K–100K', '100K–500K' ou '500K+'."""
    from modulos.midia.analise import recomendar_post as rec
    s, r = _resultado(sessao_id)
    if s["modulo"] != "midia":
        raise ValueError("use uma sessão de Mídia")
    pat = None if patrocinado is None else ("patrocinado" if patrocinado else "orgânico")
    return rec(r["posts"], r["premissas"], plataforma=plataforma, tipo=tipo, categoria=categoria,
               faixa_seguidores=faixa_seguidores, patrocinado_txt=pat)


# ---------------------------------------------------------------- ferramentas que criam coisas (nada é apagado)

@mcp.tool()
def criar_sessao(nome: str, modulo: str, usar_dados_do_desafio: bool = True, arquivos: dict | None = None,
                 mapeamento: dict | None = None) -> dict:
    """Cria uma sessão de análise (aparece também na janela). modulo: churn, suporte, leads ou midia.
    Com usar_dados_do_desafio=True usa os dados do desafio G4. Para arquivos próprios: arquivos={tabela: caminho} e,
    opcionalmente, mapeamento={tabela: {campo: coluna}} (sem ele, usa a sugestão automática de sugerir_depara)."""
    if modulo not in MODULOS:
        raise ValueError(f"módulo inválido. Opções: {', '.join(MODULOS)}")
    if usar_dados_do_desafio:
        novo = servicos.criar_sessao_desafio(nome, modulo)
    else:
        if not arquivos:
            raise ValueError("informe arquivos={tabela: caminho}")
        novo = servicos.criar_sessao_arquivos(nome, modulo, arquivos, mapeamento)
    return {"sessao_id": novo, "nome": nome, "modulo": modulo}


@mcp.tool()
def enviar_para_outra_ferramenta(sessao_id: str, destino: str, base_sessao_id: str | None = None) -> dict:
    """Cooperativo: usa o resultado desta sessão em outra ferramenta (cria uma sub-sessão; veja 'cruzamentos' em
    listar_ferramentas). Nos cruzamentos Tipo B, base_sessao_id escolhe a base de destino (padrão: dados do desafio)."""
    s, r = _resultado(sessao_id)
    chave = (s["modulo"], destino)
    if chave not in servicos.PONTES:
        raise ValueError(f"não há cruzamento disponível de {s['modulo']} para {destino}")
    selo, tipo, desc = cruzamentos.MATRIZ[chave]
    if tipo == "lista":
        saida = servicos.PONTES[chave](s, r)
        caminho = exportar.salvar(saida["df"].to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), saida["arquivo"])
        return {"tipo": "lista", "resumo": saida["resumo"], "arquivo_salvo": caminho}
    base = None
    if tipo == "B":
        opcoes = perfis.bases_de_destino(destino)
        if base_sessao_id:
            base = next((b for _, b in opcoes if b.get("id") == base_sessao_id), None)
        else:
            base = next((b for _, b in opcoes if b.get("id") is None), opcoes[0][1] if opcoes else None)
        if base is None:
            raise ValueError("não achei a base de destino; crie uma sessão do módulo de destino ou use os dados do desafio")
    novo = servicos.criar_sub_sessao(s, destino, r, base)
    return {"sub_sessao_id": novo, "selo": cruzamentos.SELOS[selo][1], "o_que_foi_feito": sessoes.obter(novo)["origem_descricao"]}


@mcp.tool()
def exportar_sessao(sessao_id: str, formato: str = "pdf") -> dict:
    """Grava um arquivo da sessão em Downloads/G4 Analise e devolve o caminho.
    formato: 'pdf' (relatório), 'md' (relatório em Markdown), 'csv' (dados analisados) ou 'xlsx' (tudo, uma aba por tabela)."""
    import importlib
    s, r = _resultado(sessao_id)
    rel = importlib.import_module(f"modulos.{s['modulo']}.relatorio")
    base = f"{s['modulo']}_{s['nome']}".replace(" ", "_")[:60]
    if formato == "pdf":
        caminho = exportar.salvar(rel.pdf(r, s["nome"]), base + ".pdf")
    elif formato == "md":
        caminho = exportar.salvar(rel.markdown(r, s["nome"]), base + ".md")
    elif formato == "csv":
        caminho = exportar.salvar(exportar.csv_principal(s["modulo"], r), base + "_dados_analisados.csv")
    elif formato == "xlsx":
        caminho = exportar.salvar(exportar.excel_completo(s["modulo"], r), base + "_analise_completa.xlsx")
    else:
        raise ValueError("formato: pdf, md, csv ou xlsx")
    return {"arquivo_salvo": caminho}


def _aquecer():
    """Carrega as bibliotecas pesadas em segundo plano, logo ao abrir: a 1a pergunta do agente nao estoura o tempo."""
    import importlib
    try:
        for m in ("churn", "suporte", "leads", "midia"):
            for parte in ("analise", "textos", "relatorio"):
                try:
                    importlib.import_module(f"modulos.{m}.{parte}")
                except Exception:  # noqa: BLE001
                    pass
    finally:
        _PRONTO.set()


if __name__ == "__main__":
    import threading
    _PRONTO.clear()
    threading.Thread(target=_aquecer, daemon=True).start()
    mcp.run()
