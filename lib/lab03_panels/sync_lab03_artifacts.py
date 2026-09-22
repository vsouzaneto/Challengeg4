"""Copia o pacote para os Labs 03, anexa células e acrescenta tiles gráficos."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent

PACKS = {
    "churn": {
        "dash": ROOT / "notebook-data-001-churn" / "03_LAB_Dashboard",
        "notebook": "lab03_dashboard.ipynb",
        "lvdash": "lab-001-churn-ceo.lvdash.json",
        "builder": "build_churn_panels",
        "page": "paineis",
        "datasets": [
            {
                "name": "panel_ranking",
                "displayName": "Ranking de benchmark",
                "query": """
SELECT
  a.country,
  COUNT(DISTINCT a.account_id) AS accounts,
  COUNT(DISTINCT e.account_id) AS accounts_with_event
FROM workspace.ravenstack.ravenstack_accounts a
LEFT JOIN workspace.ravenstack.ravenstack_churn_events e ON a.account_id = e.account_id
GROUP BY a.country
ORDER BY accounts_with_event DESC
""",
                "x": "country",
                "y": "accounts_with_event",
                "title": "Ranking de benchmark",
            },
            {
                "name": "panel_classification",
                "displayName": "Classificação",
                "query": """
SELECT reason_code, COUNT(*) AS events
FROM workspace.ravenstack.ravenstack_churn_events
GROUP BY reason_code
ORDER BY events DESC
""",
                "x": "reason_code",
                "y": "events",
                "title": "Classificação",
            },
            {
                "name": "panel_segmentation",
                "displayName": "Segmentação",
                "query": """
SELECT
  a.industry,
  COUNT(*) AS accounts,
  ROUND(AVG(CASE WHEN e.account_id IS NOT NULL THEN 1.0 ELSE 0.0 END), 3) AS event_rate
FROM workspace.ravenstack.ravenstack_accounts a
LEFT JOIN (SELECT DISTINCT account_id FROM workspace.ravenstack.ravenstack_churn_events) e
  ON a.account_id = e.account_id
GROUP BY a.industry
HAVING COUNT(*) >= 5
ORDER BY event_rate DESC
""",
                "x": "industry",
                "y": "event_rate",
                "title": "Segmentação",
            },
        ],
    },
    "support": {
        "dash": ROOT / "notebook-process-002-support" / "03_LAB_Dashboard",
        "notebook": "lab03_dashboard.ipynb",
        "lvdash": "lab-002-support-ops.lvdash.json",
        "builder": "build_support_panels",
        "page": "paineis",
        "datasets": [
            {
                "name": "panel_ranking",
                "displayName": "Ranking de benchmark",
                "query": """
SELECT
  `Ticket Channel` AS ticket_channel,
  ROUND(PERCENTILE_APPROX((unix_timestamp(`Time to Resolution`) - unix_timestamp(`First Response Time`)) / 3600.0, 0.95), 2) AS p95_hours
FROM workspace.supportiq.customer_support_tickets
WHERE `Ticket Status` = 'Closed'
  AND `Time to Resolution` IS NOT NULL
  AND `First Response Time` IS NOT NULL
GROUP BY `Ticket Channel`
ORDER BY p95_hours DESC
""",
                "x": "ticket_channel",
                "y": "p95_hours",
                "title": "Ranking de benchmark",
            },
            {
                "name": "panel_classification",
                "displayName": "Classificação",
                "query": """
SELECT `Ticket Type` AS ticket_type, COUNT(*) AS tickets
FROM workspace.supportiq.customer_support_tickets
GROUP BY `Ticket Type`
ORDER BY tickets DESC
""",
                "x": "ticket_type",
                "y": "tickets",
                "title": "Classificação",
            },
            {
                "name": "panel_segmentation",
                "displayName": "Segmentação",
                "query": """
SELECT
  `Ticket Channel` AS ticket_channel,
  ROUND(AVG(`Customer Satisfaction Rating`), 2) AS avg_csat
FROM workspace.supportiq.customer_support_tickets
WHERE `Ticket Status` = 'Closed'
GROUP BY `Ticket Channel`
ORDER BY avg_csat ASC
""",
                "x": "ticket_channel",
                "y": "avg_csat",
                "title": "Segmentação",
            },
        ],
    },
    "crm": {
        "dash": ROOT / "notebook-build-003-lead-scorer" / "03_LAB_Dashboard",
        "notebook": "lab03_dashboard.ipynb",
        "lvdash": "lab-003-crm-seller.lvdash.json",
        "builder": "build_crm_panels",
        "page": "paineis",
        "datasets": [
            {
                "name": "panel_ranking",
                "displayName": "Ranking de benchmark",
                "query": """
SELECT
  sales_agent,
  ROUND(AVG(CASE WHEN deal_stage = 'Won' THEN 1.0 ELSE 0.0 END), 3) AS win_rate
FROM workspace.crm.sales_pipeline
WHERE deal_stage IN ('Won', 'Lost')
GROUP BY sales_agent
ORDER BY win_rate DESC
""",
                "x": "sales_agent",
                "y": "win_rate",
                "title": "Ranking de benchmark",
            },
            {
                "name": "panel_classification",
                "displayName": "Classificação",
                "query": """
SELECT deal_stage, COUNT(*) AS opportunities
FROM workspace.crm.sales_pipeline
GROUP BY deal_stage
ORDER BY opportunities DESC
""",
                "x": "deal_stage",
                "y": "opportunities",
                "title": "Classificação",
            },
            {
                "name": "panel_segmentation",
                "displayName": "Segmentação",
                "query": """
SELECT
  a.sector,
  ROUND(AVG(CASE WHEN p.deal_stage = 'Won' THEN 1.0 ELSE 0.0 END), 3) AS win_rate
FROM workspace.crm.sales_pipeline p
LEFT JOIN workspace.crm.accounts a ON p.account = a.account
WHERE p.deal_stage IN ('Won', 'Lost')
  AND a.sector IS NOT NULL
GROUP BY a.sector
ORDER BY win_rate DESC
""",
                "x": "sector",
                "y": "win_rate",
                "title": "Segmentação",
            },
        ],
    },
    "social": {
        "dash": ROOT / "notebook-marketing-004-social" / "03_LAB_Dashboard",
        "notebook": "lab03_dashboard.ipynb",
        "lvdash": "lab-004-social-media.lvdash.json",
        "builder": "build_social_panels",
        "page": "paineis",
        "datasets": [
            {
                "name": "panel_ranking",
                "displayName": "Ranking de benchmark",
                "query": """
SELECT
  platform,
  ROUND(AVG((likes + shares + comments_count) / NULLIF(views, 0)), 4) AS eng_per_view
FROM workspace.social.social_media_dataset
GROUP BY platform
ORDER BY eng_per_view DESC
""",
                "x": "platform",
                "y": "eng_per_view",
                "title": "Ranking de benchmark",
            },
            {
                "name": "panel_classification",
                "displayName": "Classificação",
                "query": """
SELECT content_type, COUNT(*) AS posts
FROM workspace.social.social_media_dataset
GROUP BY content_type
ORDER BY posts DESC
""",
                "x": "content_type",
                "y": "posts",
                "title": "Classificação",
            },
            {
                "name": "panel_image",
                "displayName": "Segmentação de imagem",
                "query": """
SELECT content_type, COUNT(*) AS posts
FROM workspace.social.social_media_dataset
GROUP BY content_type
ORDER BY posts DESC
""",
                "x": "content_type",
                "y": "posts",
                "title": "Segmentação de imagem",
            },
        ],
    },
}


def copy_package(dest: Path) -> None:
    target = dest / "lab03_panels"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(
        SRC,
        target,
        ignore=shutil.ignore_patterns("sync_lab03_artifacts.py", "__pycache__"),
    )


def append_notebook(dest: Path, builder: str) -> None:
    nb_path = dest / PACKS_NOTEBOOK_NAME(dest)
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    joined = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])
    if "build_" in joined and "lab03_panels" in joined:
        return
    nb["cells"].extend(
        [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Painéis gráficos\n",
                    "\n",
                    "Ranking, galeria, classificação, segmentação, segmentação de imagem, estatísticas do modelo, matriz de confusão, curva de aprendizado e viés/variância. Calculados só com colunas reais do dump.\n",
                ],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [
                    "import sys\n",
                    "from pathlib import Path\n",
                    "\n",
                    "HERE = Path.cwd()\n",
                    "for candidate in (HERE, HERE / '03_LAB_Dashboard', HERE.parent / 'lib', HERE.parent.parent / 'lib'):\n",
                    "    if (candidate / 'lab03_panels' / '__init__.py').exists():\n",
                    "        sys.path.insert(0, str(candidate))\n",
                    "        break\n",
                    "else:\n",
                    "    raise FileNotFoundError('lab03_panels não encontrado')\n",
                    "\n",
                    f"from lab03_panels import {builder}\n",
                    "from lab03_panels.render import render_panels\n",
                    "\n",
                    "try:\n",
                    "    show = display\n",
                    "except NameError:\n",
                    "    show = print\n",
                    "\n",
                    f"panels = {builder}()\n",
                    "render_panels(panels, show)\n",
                    "print('secoes', list(panels.panels))\n",
                ],
            },
        ]
    )
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def PACKS_NOTEBOOK_NAME(dest: Path) -> str:
    for spec in PACKS.values():
        if spec["dash"] == dest:
            return spec["notebook"]
    raise KeyError(dest)


def bar_widget(dataset: dict, index: int) -> dict:
    x_name = dataset["x"]
    y_name = dataset["y"]
    return {
        "widget": {
            "name": f"w-{dataset['name']}",
            "queries": [
                {
                    "name": "main_query",
                    "query": {
                        "datasetName": dataset["name"],
                        "fields": [
                            {"name": x_name, "expression": f"`{x_name}`"},
                            {"name": y_name, "expression": f"`{y_name}`"},
                        ],
                        "disaggregated": True,
                    },
                }
            ],
            "spec": {
                "version": 2,
                "widgetType": "bar",
                "encodings": {
                    "x": {"fieldName": x_name, "displayName": x_name},
                    "y": {"fieldName": y_name, "displayName": y_name},
                },
                "frame": {"showTitle": True, "title": dataset["title"]},
            },
        },
        "position": {"x": (index % 2) * 6, "y": 1 + (index // 2) * 6, "width": 6, "height": 6},
    }


def update_lvdash(spec: dict) -> None:
    path = spec["dash"] / spec["lvdash"]
    data = json.loads(path.read_text(encoding="utf-8"))
    existing = {item["name"] for item in data["datasets"]}
    for dataset in spec["datasets"]:
        if dataset["name"] in existing:
            continue
        data["datasets"].append(
            {
                "name": dataset["name"],
                "displayName": dataset["displayName"],
                "query": dataset["query"],
            }
        )
    pages = data["pages"]
    if any(page.get("name") == spec["page"] for page in pages):
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return
    layout = [
        {
            "widget": {
                "name": "paineis-title",
                "multilineTextboxSpec": {
                    "lines": [
                        "## Paineis graficos",
                        "Ranking, classificacao e segmentacao com colunas reais. Modelo, matriz, curva e vies no notebook Lab 03.",
                    ]
                },
            },
            "position": {"x": 0, "y": 0, "width": 12, "height": 1},
        }
    ]
    for index, dataset in enumerate(spec["datasets"]):
        layout.append(bar_widget(dataset, index))
    pages.append(
        {
            "name": spec["page"],
            "displayName": "Paineis",
            "pageType": "PAGE_TYPE_CANVAS",
            "layoutVersion": "GRID_V1",
            "layout": layout,
        }
    )
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    for spec in PACKS.values():
        copy_package(spec["dash"])
        append_notebook(spec["dash"], spec["builder"])
        update_lvdash(spec)
        print("updated", spec["dash"].name)


if __name__ == "__main__":
    main()
