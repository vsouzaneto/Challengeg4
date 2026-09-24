"""
Servicos do G4 Analise sem tela: criar sessoes, rodar analises, cruzar ferramentas e exportar.

Usado pela janela (app/tela.py) e pelo servidor MCP do agente do G4 OS (app/servidor_mcp.py), para que os dois
enxerguem exatamente as mesmas sessoes e os mesmos numeros.
"""

import hashlib
import importlib
import json
import os
import shutil

import joblib

from nucleo import cruzamentos, depara, leitura, sessoes
from nucleo.carregar import tabelas_da_sessao
from nucleo.contratos import MODULOS, mapeamento_desafio
from modulos.churn import pontes as pontes_churn
from modulos.leads import pontes as pontes_leads
from modulos.midia import pontes as pontes_midia
from modulos.suporte import pontes as pontes_suporte

# Pontes prontas (cooperativo): (origem, destino) -> funcao(sessao, resultado[, base]) que monta a sub-sessao
PONTES = {
    ("churn", "suporte"): pontes_churn.para_suporte, ("churn", "leads"): pontes_churn.para_leads,
    ("churn", "midia"): pontes_churn.para_midia,
    ("suporte", "churn"): pontes_suporte.para_churn, ("suporte", "leads"): pontes_suporte.para_leads,
    ("suporte", "midia"): pontes_suporte.para_midia,
    ("leads", "midia"): pontes_leads.para_midia,
    ("midia", "leads"): pontes_midia.para_leads,
}


def modulo_de_analise(chave):
    return importlib.import_module(f"modulos.{chave}.analise")


def analisar_sessao(sessao, premissas=None):
    """Roda a analise do modulo da sessao. premissas = dict com os campos de Premissas do modulo (opcional)."""
    mod = modulo_de_analise(sessao["modulo"])
    tabs = tabelas_da_sessao(sessao, leitura.ler)
    return mod.analisar(tabs, mod.Premissas(**(premissas or {})))


_RAIZ_APP = os.path.dirname(os.path.abspath(__file__))


def _assinatura(sessao, premissas):
    """Muda quando mudam os arquivos, o De/Para, as premissas ou o codigo da analise: so ai a analise e refeita."""
    arquivos = {t: [c, os.path.getmtime(c), os.path.getsize(c)] for t, c in sorted(sessao["arquivos"].items()) if os.path.exists(c)}
    base = json.dumps([sessao["modulo"], arquivos, sessao["mapeamento"], premissas or {}], sort_keys=True, default=str).encode()
    h = hashlib.sha256(base)
    for rel in (f"modulos/{sessao['modulo']}/analise.py", "nucleo/carregar.py", "nucleo/depara.py", "nucleo/leitura.py"):
        with open(os.path.join(_RAIZ_APP, rel), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:24]


def analisar_com_cache(sessao, premissas=None):
    """Como analisar_sessao, mas guarda o resultado no disco (pasta da sessao). Fechar e abrir o sistema NAO refaz
    a analise; ela so e refeita se os dados, o De/Para, as premissas ou o codigo mudarem."""
    if not sessao.get("id"):
        return analisar_sessao(sessao, premissas)
    pasta = os.path.join(sessoes.pasta_da_sessao(sessao["id"]), "analises")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, _assinatura(sessao, premissas) + ".joblib")
    if os.path.exists(caminho):
        try:
            return joblib.load(caminho)
        except Exception:  # noqa: BLE001  (arquivo corrompido ou de outra versao: refaz)
            pass
    r = analisar_sessao(sessao, premissas)
    temp = caminho + ".tmp"
    joblib.dump(r, temp, compress=1)
    os.replace(temp, caminho)
    antigos = sorted((os.path.join(pasta, x) for x in os.listdir(pasta) if x.endswith(".joblib")), key=os.path.getmtime)
    for velho in antigos[:-6]:   # guarda as 6 combinacoes de premissas mais recentes
        try:
            os.remove(velho)
        except OSError:
            pass
    return r


# ---------------------------------------------------------------- sessoes

def arquivos_do_desafio(chave):
    """{tabela: caminho} dos dados do desafio e a lista de obrigatorios que faltam."""
    pasta = leitura.pasta_dados_desafio()
    if not pasta:
        return {}, ["pasta de dados do desafio não encontrada"]
    arquivos, faltam = {}, []
    for t in MODULOS[chave].tabelas:
        caminho = os.path.join(pasta, t.arquivo_desafio)
        if os.path.exists(caminho):
            arquivos[t.nome] = caminho
        elif t.obrigatoria:
            faltam.append(t.arquivo_desafio)
    return arquivos, faltam


def criar_sessao_desafio(nome, chave):
    arquivos, faltam = arquivos_do_desafio(chave)
    if faltam:
        raise ValueError("faltam arquivos obrigatórios: " + ", ".join(faltam))
    mapa = {t: m for t, m in mapeamento_desafio(MODULOS[chave]).items() if t in arquivos}
    return sessoes.criar(nome, chave, "desafio", mapa, arquivos)


def sugerir_depara(chave, caminhos):
    """Para arquivos proprios: {tabela: {campo: coluna sugerida}} e os obrigatorios que ficaram sem coluna."""
    m = MODULOS[chave]
    sugestao, faltando = {}, {}
    for t in m.tabelas:
        if t.nome not in caminhos:
            if t.obrigatoria:
                faltando[t.nome] = ["(arquivo da tabela)"]
            continue
        df = leitura.ler(caminhos[t.nome])
        sugestao[t.nome] = depara.sugerir(t, df.columns)
        f = depara.faltando(t, sugestao[t.nome])
        if f:
            faltando[t.nome] = f
    return sugestao, faltando


def criar_sessao_arquivos(nome, chave, caminhos, mapeamento=None):
    """Cria sessao com arquivos do computador. Copia os arquivos para a pasta da sessao (o original fica intacto)."""
    sugestao, faltando = sugerir_depara(chave, caminhos)
    mapa = mapeamento or sugestao
    falta_final = {t: depara.faltando(MODULOS[chave].tabela(t), mapa.get(t, {})) for t in caminhos}
    falta_final = {t: f for t, f in falta_final.items() if f}
    obrig = [t.nome for t in MODULOS[chave].tabelas if t.obrigatoria and t.nome not in caminhos]
    if falta_final or obrig:
        raise ValueError(f"De/Para incompleto: {falta_final or ''} {('tabelas obrigatórias sem arquivo: ' + ', '.join(obrig)) if obrig else ''}")
    novo = sessoes.criar(nome, chave, "arquivos", mapa, {})
    pasta = os.path.join(sessoes.pasta_da_sessao(novo), "entrada")
    os.makedirs(pasta, exist_ok=True)
    copiados = {}
    for t, c in caminhos.items():
        destino = os.path.join(pasta, t + os.path.splitext(c)[1].lower())
        shutil.copyfile(c, destino)
        copiados[t] = destino
    sessoes.atualizar_arquivos(novo, copiados)
    return novo


# ---------------------------------------------------------------- cruzamentos

def criar_sub_sessao(s, destino, resultado, base=None):
    """Roda a ponte, grava as tabelas na pasta da nova sessao e devolve o id da sub-sessao.

    Tipo A: a ponte devolve 'tabelas' ja com os nomes do sistema (De/Para identidade).
    Tipo B: devolve 'brutas' (tabela original filtrada) e usa o De/Para da base escolhida; as outras tabelas
    da base sao reaproveitadas como estao.
    """
    ponte = PONTES[(s["modulo"], destino)]
    saida = ponte(s, resultado, base) if base is not None else ponte(s, resultado)
    selo = cruzamentos.MATRIZ[(s["modulo"], destino)][0]
    if "brutas" in saida:
        tabelas, mapa = saida["brutas"], saida["base"]["mapeamento"]
        caminhos = {t: c for t, c in saida["base"]["arquivos"].items() if t not in tabelas}
    else:
        tabelas = saida["tabelas"]
        mapa = {t: {col: col for col in df.columns} for t, df in tabelas.items()}
        caminhos = {}
    novo = sessoes.criar(saida["nome"], destino, "cruzamento", mapa, {}, origem_id=s["id"],
                         origem_descricao=saida["descricao"], selo=selo)
    pasta = os.path.join(sessoes.pasta_da_sessao(novo), "entrada")
    os.makedirs(pasta, exist_ok=True)
    for t, df in tabelas.items():
        caminhos[t] = os.path.join(pasta, f"{t}.csv")
        df.to_csv(caminhos[t], index=False)
    sessoes.atualizar_arquivos(novo, caminhos)
    return novo
