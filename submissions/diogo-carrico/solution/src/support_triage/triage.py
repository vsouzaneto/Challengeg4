"""Triage a ticket: never-automate policy, domain guard, classifier, per-class threshold and enabled classes.

Command line (from the solution folder, after scripts/train_classifier.py):
    uv run python -m support_triage.triage "texto do ticket"
    uv run python -m support_triage.triage --csv tickets.csv --column texto
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import pandas as pd

from support_triage.classifier import normalize_text, vocabulary_coverage
from support_triage.paths import OUTPUTS_DIR
from support_triage.policy import NEVER_AUTOMATED_CLASSES, matching_rule

MODEL_PATH = OUTPUTS_DIR / "model" / "triage.joblib"


@dataclass
class Decision:
    decision: str  # "rotear" or "humano"
    queue: str  # the class queue, or who handles it
    reason: str
    predicted_class: str | None = None
    confidence: float | None = None
    threshold: float | None = None
    vocabulary_coverage: float | None = None


def load_model(path: Path = MODEL_PATH) -> dict:
    if not path.exists():
        sys.exit(
            f"Modelo não encontrado em {path}. Rode antes: uv run python scripts/train_classifier.py"
        )
    return joblib.load(path)


def triage(text: str, artifact: dict) -> Decision:
    rule = matching_rule(text)
    if rule:
        return Decision("humano", rule.goes_to, f"Política: {rule.name}")

    clean = normalize_text(text)
    coverage = vocabulary_coverage(clean, artifact["vocabulary"])
    if coverage < artifact["guard"]:
        return Decision(
            "humano",
            "Triagem humana",
            f"Fora do domínio: só {coverage:.0%} das palavras de conteúdo são conhecidas pelo modelo (mínimo {artifact['guard']:.0%})",
            vocabulary_coverage=coverage,
        )

    model = artifact["model"]
    proba = model.predict_proba([clean])[0]
    best = int(proba.argmax())
    cls, conf = str(model.classes_[best]), float(proba[best])
    threshold = artifact["thresholds"][cls]
    base = {
        "predicted_class": cls,
        "confidence": conf,
        "threshold": threshold,
        "vocabulary_coverage": coverage,
    }
    if cls in NEVER_AUTOMATED_CLASSES:
        return Decision(
            "humano",
            "Triagem humana",
            f"Classe nunca roteada sozinha: {NEVER_AUTOMATED_CLASSES[cls]}",
            **base,
        )
    if conf < threshold:
        return Decision(
            "humano",
            "Triagem humana",
            f"Confiança {conf:.0%} abaixo do limiar da classe ({threshold:.0%})",
            **base,
        )
    if cls not in artifact["enabled_classes"]:
        return Decision(
            "humano",
            "Triagem humana",
            f"Confiança {conf:.0%} acima do limiar, mas a classe está em piloto: não provou {artifact['target_precision']:.0%} de precisão no teste",
            **base,
        )
    return Decision(
        "rotear",
        cls,
        f"Confiança {conf:.0%} acima do limiar da classe ({threshold:.0%})",
        **base,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Triagem de tickets: rotear ou mandar para humano"
    )
    parser.add_argument("text", nargs="?", help="texto do ticket")
    parser.add_argument("--csv", help="arquivo CSV com vários tickets")
    parser.add_argument("--column", default="texto", help="coluna do CSV com o texto")
    args = parser.parse_args()
    artifact = load_model()
    if args.csv:
        df = pd.read_csv(args.csv)
        out = pd.DataFrame(
            [asdict(triage(t, artifact)) for t in df[args.column].fillna("")]
        )
        print(pd.concat([df, out], axis=1).to_string(index=False))
    elif args.text:
        for k, v in asdict(triage(args.text, artifact)).items():
            if v is not None:
                print(f"{k:20} {v:.3f}" if isinstance(v, float) else f"{k:20} {v}")
    else:
        parser.error("informe o texto do ticket ou --csv")


if __name__ == "__main__":
    main()
