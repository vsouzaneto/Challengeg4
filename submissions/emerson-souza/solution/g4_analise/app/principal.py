"""
Abre o G4 Analise.

1. Sobe as telas (Streamlit) numa porta livre do proprio computador.
2. Abre essas telas numa JANELA PROPRIA (pywebview), como um programa.
3. Se a janela nao puder abrir (ex.: Linux sem componentes graficos), abre no navegador, com aviso.

    python app/principal.py              -> janela propria
    python app/principal.py --navegador  -> forca abrir no navegador
"""

import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TELA = os.path.join(PASTA, "app", "tela.py")


def aviso(texto):
    print(f"[G4 Analise] {texto}", flush=True)


def porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def subir_telas(porta):
    comando = [
        sys.executable, "-m", "streamlit", "run", TELA,
        "--server.port", str(porta), "--server.address", "127.0.0.1",
        "--server.headless", "true", "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false",
    ]
    return subprocess.Popen(comando, cwd=PASTA)


def esperar(url, processo, limite=90):
    inicio = time.time()
    while time.time() - inicio < limite:
        if processo.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url + "/_stcore/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except OSError:
            time.sleep(0.5)
    return False


def abrir_janela(url):
    import logging
    import webview
    logging.getLogger("pywebview").setLevel(logging.CRITICAL)  # sem traceback no fallback
    webview.settings["ALLOW_DOWNLOADS"] = True   # botoes "Baixar PDF/CSV" funcionarem dentro da janela
    webview.create_window("G4 Analise", url, width=1400, height=900, min_size=(1000, 650))
    webview.start()


def main():
    porta = porta_livre()
    url = f"http://127.0.0.1:{porta}"
    aviso("Iniciando...")
    processo = subir_telas(porta)
    try:
        if not esperar(url, processo):
            aviso("As telas nao subiram. Veja a mensagem acima.")
            sys.exit(1)
        if "--navegador" not in sys.argv:
            try:
                abrir_janela(url)
                return  # fechou a janela -> encerra
            except Exception as erro:
                aviso(f"Nao foi possivel abrir a janela propria ({erro.__class__.__name__}). Abrindo no navegador.")
        webbrowser.open(url)
        aviso(f"Aberto no navegador: {url}  (feche esta janela ou aperte Ctrl+C para encerrar)")
        processo.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if processo.poll() is None:
            processo.terminate()


if __name__ == "__main__":
    main()
