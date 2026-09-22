"""Painéis gráficos do Lab 03, um módulo por challenge."""

from .common import REQUIRED_SECTIONS, DashboardPanels
from .churn import build_churn_panels
from .crm import build_crm_panels
from .social import build_social_panels
from .support import build_support_panels

BUILDERS = {
    "churn": build_churn_panels,
    "support": build_support_panels,
    "crm": build_crm_panels,
    "social": build_social_panels,
}

__all__ = [
    "BUILDERS",
    "REQUIRED_SECTIONS",
    "DashboardPanels",
    "build_churn_panels",
    "build_crm_panels",
    "build_social_panels",
    "build_support_panels",
]
