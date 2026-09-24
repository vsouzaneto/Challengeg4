"""De/Para: sugere qual coluna do arquivo corresponde a cada campo do contrato."""

import difflib
import re
import unicodedata


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def sugerir(tabela, colunas):
    """Devolve {campo: coluna ou None}. Uma coluna nao e usada duas vezes."""
    livres = list(colunas)
    norm = {c: normalizar(c) for c in colunas}
    resultado = {}
    for campo in tabela.campos:
        alvos = [campo.nome, campo.rotulo] + list(campo.sinonimos)
        if campo.coluna_desafio:
            alvos.insert(0, campo.coluna_desafio)
        alvos_n = [normalizar(a) for a in alvos]
        # Respeita a ordem de preferencia dos nomes (ex.: "content_id" antes de "id").
        escolhida = next((c for a in alvos_n for c in livres if norm[c] == a), None)
        if escolhida is None:
            melhor, nota = None, 0.0
            for c in livres:
                for a in alvos_n:
                    r = difflib.SequenceMatcher(None, norm[c], a).ratio()
                    if r > nota:
                        melhor, nota = c, r
            escolhida = melhor if nota >= 0.85 else None
        resultado[campo.nome] = escolhida
        if escolhida:
            livres.remove(escolhida)
    return resultado


def faltando(tabela, mapa):
    """Campos obrigatorios sem coluna."""
    return [c.rotulo for c in tabela.obrigatorios() if not mapa.get(c.nome)]


def aplicar(df, mapa):
    """Renomeia as colunas para os nomes do contrato e descarta o que nao foi mapeado."""
    usados = {col: campo for campo, col in mapa.items() if col}
    return df[list(usados)].rename(columns=usados)
