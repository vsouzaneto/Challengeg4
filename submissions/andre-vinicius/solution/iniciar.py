"""Prepara os dados públicos e abre o Foco com um único comando."""

import argparse
import subprocess
import sys
import threading
import webbrowser
from http.server import ThreadingHTTPServer

from app import ROOT, build_payload, handler_factory


REQUIRED = ("accounts.csv", "products.csv", "sales_teams.csv", "sales_pipeline.csv")


def ensure_data():
    missing = [name for name in REQUIRED if not (ROOT / "data" / name).is_file()]
    if missing:
        print("Baixando os CSVs públicos do desafio G4...", flush=True)
        subprocess.run([sys.executable, str(ROOT / "download_data.py")], cwd=ROOT, check=True)
    return build_payload(ROOT / "data")


def main():
    parser = argparse.ArgumentParser(description="Baixa os dados, inicia o Foco e abre o navegador.")
    parser.add_argument("--check", action="store_true", help="confere os dados sem abrir o servidor")
    parser.add_argument("--no-browser", action="store_true", help="não abre o navegador automaticamente")
    args = parser.parse_args()

    if sys.version_info < (3, 10):
        parser.error("O Foco requer Python 3.10 ou superior.")
    try:
        payload = ensure_data()
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        parser.exit(1, f"Não foi possível preparar os dados: {exc}\n")
    print(f"Dados prontos: {len(payload['deals'])} oportunidades abertas.", flush=True)
    if args.check:
        return

    try:
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(payload))
    except OSError as exc:
        parser.exit(1, f"Não foi possível abrir a aplicação local: {exc}\n")
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Abra {url} | Para encerrar: Ctrl+C", flush=True)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
