"""Dump the OpenAPI document to stdout: ``python -m api.export_openapi > openapi.json``."""

import json
import sys

from api.main import app


def main() -> None:
    json.dump(app.openapi(), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
