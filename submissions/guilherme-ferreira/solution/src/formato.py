"""Números no formato brasileiro: ponto no milhar, vírgula no decimal."""
import math

SEM_NUMERO = "—"


def _vazio(valor):
    try:
        return valor is None or math.isnan(valor)
    except TypeError:
        return False


def _trocar_separadores(texto):
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def numero_br(valor, casas=0) -> str:
    if _vazio(valor):
        return SEM_NUMERO
    return _trocar_separadores(f"{valor:,.{casas}f}")


def resumo_selecao(marcados, total) -> str:
    """Texto curto de um filtro: "Todas", "Nenhuma", o único item marcado ou "k de n"."""
    if len(marcados) == total:
        return "Todas"
    if not marcados:
        return "Nenhuma"
    if len(marcados) == 1:
        return str(marcados[0])
    return f"{len(marcados)} de {total}"


def percentual_br(fracao, casas=1, sinal=False) -> str:
    """0,1234 vira "12,3%". Com sinal=True, positivos ganham "+". Sem número, vira "—"."""
    if _vazio(fracao):
        return SEM_NUMERO
    mais = "+" if sinal else ""
    return _trocar_separadores(f"{fracao * 100:{mais},.{casas}f}") + "%"
