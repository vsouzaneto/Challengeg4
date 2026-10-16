"""Serve Command Center React (dist). Apenas localhost."""
from __future__ import annotations

import functools
import os
import socket
import subprocess
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from analytics.paths import COMMAND_CENTER_DIST, DASH_PUBLIC, SOLUTION

PORT = 8765
COMMAND_CENTER = SOLUTION / "command-center"


class DashboardHandler(SimpleHTTPRequestHandler):
    """SPA estática."""

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("", "/"):
            self.path = "/index.html"
        super().do_GET()

    def list_directory(self, path):  # noqa: ARG002
        self.send_error(404, "Arquivo não encontrado. Rode start.bat ou npm run build em command-center.")
        return None


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            return True
    return False


def _ensure_build() -> None:
    index = COMMAND_CENTER_DIST / "index.html"
    if index.is_file():
        return
    print("Build ausente. Rodando npm run build em command-center/ ...", file=sys.stderr)
    npm = "npm.cmd" if os.name == "nt" else "npm"
    node_modules = COMMAND_CENTER / "node_modules"
    if not node_modules.is_dir():
        subprocess.run([npm, "install"], cwd=COMMAND_CENTER, check=True, shell=os.name == "nt")
    result = subprocess.run(
        [npm, "run", "build"],
        cwd=COMMAND_CENTER,
        shell=os.name == "nt",
    )
    if result.returncode != 0 or not index.is_file():
        raise SystemExit(
            "Falha no build. Manual:\n"
            f"  cd {COMMAND_CENTER}\n"
            "  npm install && npm run build"
        )


def main() -> None:
    if not (DASH_PUBLIC / "bundle.json").exists():
        raise SystemExit(f"Execute: cd {SOLUTION} && python run_analysis.py")

    _ensure_build()

    if _port_in_use(PORT):
        print(
            f"ERRO: porta {PORT} já em uso.\n"
            "Windows: netstat -aon | findstr :8765\n"
            "Depois: taskkill /F /PID <PID>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    root = str(COMMAND_CENTER_DIST.resolve())
    os.chdir(root)
    handler = functools.partial(DashboardHandler, directory=root)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"RavenStack Intelligence: {url}")
    print(f"Servindo: {root}")
    webbrowser.open(url)
    with ThreadingHTTPServer(("127.0.0.1", PORT), handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
