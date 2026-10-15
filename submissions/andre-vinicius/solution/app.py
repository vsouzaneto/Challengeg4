"""Servidor local do Lead Scorer. Python 3, biblioteca padrão, só 127.0.0.1."""
import argparse
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from scoring import load_data, rank_open

ROOT = Path(__file__).parent


def summarize_sales(rows):
    """Contexto historico por vendedor, independente do ranking de abertas."""
    sellers = {}
    for row in rows:
        if row["deal_stage"] not in {"Won", "Lost"}:
            continue
        name = row["sales_agent"] or "Não informado"
        summary = sellers.setdefault(name, {"won": 0, "lost": 0, "won_value": Decimal(0)})
        if row["deal_stage"] == "Lost":
            summary["lost"] += 1
        else:
            summary["won"] += 1
            try:
                summary["won_value"] += Decimal(row.get("close_value") or "0")
            except InvalidOperation:
                pass
    return {name: {**summary, "won_value": float(summary["won_value"])} for name, summary in sellers.items()}


def build_payload(data_dir: Path):
    rows = load_data(data_dir)
    as_of, deals = rank_open(rows)
    return {"as_of": as_of.isoformat(), "deals": deals, "counts": dict(Counter(d["queue"] for d in deals)),
            "sales_by_agent": summarize_sales(rows)}


def handler_factory(payload):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT / "static"), **kwargs)

        def do_GET(self):
            if urlsplit(self.path).path == "/api/deals":
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            super().do_GET()

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data", help="Pasta dos CSVs originais")
    parser.add_argument("--port", type=int, default=8843)
    parser.add_argument("--host", default="127.0.0.1", help="Endereço de escuta; padrão só nesta máquina")
    args = parser.parse_args()
    payload = build_payload(args.data)
    server = ThreadingHTTPServer((args.host, args.port), handler_factory(payload))
    print(f"Lead Scorer: http://{args.host}:{server.server_port} | {len(payload['deals'])} oportunidades abertas | referência {payload['as_of']}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
