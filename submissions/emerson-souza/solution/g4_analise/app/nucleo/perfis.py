"""
Cruzamentos Tipo B (hipotese, selo azul): um PERFIL tirado de uma analise filtra a base de outra ferramenta.

Ex.: "paises das contas que mais cancelam" -> so os posts cuja audiencia e desses paises -> a ferramenta de
Midia diz que conteudo usar com esse publico. O filtro e aplicado no arquivo original da base de destino
(colunas originais), entao a sub-sessao usa o mesmo De/Para da base escolhida.
"""

import os

from . import leitura, sessoes
from .contratos import MODULOS, mapeamento_desafio

PAISES = {
    "us": "USA", "usa": "USA", "united states": "USA", "estados unidos": "USA", "uk": "UK", "gb": "UK",
    "united kingdom": "UK", "reino unido": "UK", "in": "India", "india": "India", "índia": "India",
    "de": "Germany", "germany": "Germany", "alemanha": "Germany", "br": "Brazil", "brazil": "Brazil", "brasil": "Brazil",
    "cn": "China", "china": "China", "jp": "Japan", "japan": "Japan", "japão": "Japan", "ru": "Russia", "russia": "Russia",
    "rússia": "Russia", "fr": "France", "france": "France", "frança": "France", "au": "Australia", "australia": "Australia",
    "ca": "Canada", "canada": "Canada", "canadá": "Canada",
}


def pais(x):
    """Nome canonico do pais (codigo, ingles ou portugues)."""
    return PAISES.get(str(x).strip().lower(), str(x).strip())


def bases_de_destino(destino):
    """Opcoes de base para o destino: dados do desafio (se existirem) + sessoes 'raiz' do destino."""
    opcoes = []
    pasta = leitura.pasta_dados_desafio()
    m = MODULOS[destino]
    if pasta:
        arq = {t.nome: os.path.join(pasta, t.arquivo_desafio) for t in m.tabelas
               if os.path.exists(os.path.join(pasta, t.arquivo_desafio))}
        if any(t.obrigatoria and t.nome in arq for t in m.tabelas):
            opcoes.append(("Dados do desafio", {"id": None, "nome": "dados do desafio", "modulo": destino,
                                                "arquivos": arq, "mapeamento": mapeamento_desafio(m)}))
    for s in sessoes.listar():
        if s["modulo"] == destino and not s["origem_id"]:
            opcoes.append((f"Sessão '{s['nome']}'", s))
    return opcoes


def coluna_bruta(base, tabela, campo):
    col = base["mapeamento"].get(tabela, {}).get(campo)
    if not col:
        raise ValueError(f"a base escolhida não tem o campo '{campo}' ligado no De/Para")
    return col


def ler_tabela(base, tabela):
    return leitura.ler(base["arquivos"][tabela])


def filtrar(df, base, tabela, filtros):
    """Linhas da tabela ORIGINAL cujos campos (nomes do sistema) estao nos valores pedidos.
    filtros = {campo: (valores, funcao_de_normalizacao_ou_None)}."""
    for campo, (valores, norm) in filtros.items():
        col = coluna_bruta(base, tabela, campo)
        chave = df[col].map(norm) if norm else df[col].astype(str)
        df = df[chave.isin(set(valores))]
    return df
