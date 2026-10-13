"""pt-BR number formatting for the generated reports."""


def n(x: float) -> str:
    """Integer with pt-BR thousands separator."""
    return f"{round(x):,}".replace(",", ".")


def d(x: float, places: int = 2) -> str:
    """Decimal with pt-BR separators and a true minus sign: 1.234,56 / −0,04."""
    s = f"{x:,.{places}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return s.replace("-", "−")


def seg(label: str) -> str:
    """Segment label safe inside a Markdown table: 'Phone | Low' becomes 'Phone · Low'."""
    return label.replace(" | ", " · ")


def pct(x: float, places: int = 1) -> str:
    return d(x * 100, places) + "%"


def pp(x: float, places: int = 1) -> str:
    """A difference in percentage points, with its sign."""
    return ("+" if x >= 0 else "−") + d(abs(x) * 100, places) + " p.p."


def pv(x: float) -> str:
    """p-value with its comparison sign: '= 0,11', or '< 0,01' when smaller."""
    return "< 0,01" if x < 0.01 else "= " + d(x, 2)


def brl(x: float) -> str:
    return "R$ " + n(x)
