"""Publica cópias estáticas dos documentos para o servidor local sem dependências."""
import argparse
from pathlib import Path

ROOT = Path(__file__).parent
SOURCES = {
    "business-spec.md": ROOT / "docs" / "business-spec.md",
    "functional-spec.md": ROOT / "docs" / "functional-spec.md",
    "technical-spec.md": ROOT / "docs" / "technical-spec.md",
    "test-plan.md": ROOT / "docs" / "test-plan.md",
    "operations.md": ROOT / "docs" / "operations.md",
    "product-roadmap.md": ROOT / "docs" / "product-roadmap.md",
    "data-audit.md": ROOT / "docs" / "data-audit.md",
    "case-development.md": ROOT / "docs" / "case-development.md",
    "process-log.md": ROOT / "PROCESS_LOG.md",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Falha se uma cópia estiver ausente ou desatualizada")
    args = parser.parse_args()
    output = ROOT / "static" / "source"
    if not args.check:
        output.mkdir(parents=True, exist_ok=True)
    stale = []
    for name, source in SOURCES.items():
        target = output / name
        content = source.read_bytes()
        if not target.exists() or target.read_bytes() != content:
            stale.append(name)
            if not args.check:
                target.write_bytes(content)
    if args.check and stale:
        parser.exit(1, "Cópias desatualizadas: " + ", ".join(stale) + "\n")
    print(f"Documentos {'conferidos' if args.check else 'publicados'}: {len(SOURCES)}")


if __name__ == "__main__":
    main()
