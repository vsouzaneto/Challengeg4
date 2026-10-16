"""Mixa a narração e codifica os quadros em MP4 (H.264 + AAC) com PyAV.

    python scripts/codificar.py <pasta_quadros> <saida.mp4> [--crf 31]

- Áudio: cada cena de src/narracao.json entra no instante da sua fala.
- Volume: fala normalizada para ~-19 dBFS RMS (≈ -16 LUFS em voz), pico limitado a -1 dBFS.
- Vídeo: CRF 31 por padrão (~10 MB para 2 min em 1080p, texto das telas legível); também grava a capa.
"""
from __future__ import annotations

import json
import sys
import wave
from fractions import Fraction
from pathlib import Path

import av
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
TAXA = 48000


def ler_wav(caminho: Path) -> np.ndarray:
    with wave.open(str(caminho), "rb") as w:
        taxa, bruto = w.getframerate(), w.readframes(w.getnframes())
    x = np.frombuffer(bruto, dtype="<i2").astype(np.float32) / 32768
    t_novo = np.arange(int(len(x) * TAXA / taxa)) * (taxa / TAXA)
    return np.interp(t_novo, np.arange(len(x)), x).astype(np.float32)


def mixar(linha: dict, duracao: float) -> np.ndarray:
    mix = np.zeros(int(duracao * TAXA) + TAXA, dtype=np.float32)
    for cena in linha["cenas"]:
        x = ler_wav(RAIZ / "public" / cena["audio"])
        i = int(round(cena["fala"] * TAXA))
        fim = min(len(mix), i + len(x))
        mix[i:fim] += x[: fim - i]
    ativo = np.abs(mix) > 10 ** (-45 / 20)
    if ativo.any():
        mix *= 10 ** (-19 / 20) / max(float(np.sqrt(np.mean(mix[ativo] ** 2))), 1e-6)
    pico = 10 ** (-1 / 20)
    return np.clip(mix, -pico, pico)[: int(duracao * TAXA)]


def main() -> None:
    quadros_dir, saida = Path(sys.argv[1]), Path(sys.argv[2])
    crf = sys.argv[sys.argv.index("--crf") + 1] if "--crf" in sys.argv else "31"
    linha = json.loads((RAIZ / "src" / "narracao.json").read_text(encoding="utf-8"))
    fps = int(linha["fps"])
    quadros = sorted(quadros_dir.glob("*.jpeg")) or sorted(quadros_dir.glob("*.jpg"))
    if not quadros:
        raise SystemExit("sem quadros para codificar")
    w, h = Image.open(quadros[0]).size
    duracao = len(quadros) / fps
    audio = mixar(linha, duracao)

    container = av.open(str(saida), "w", options={"movflags": "+faststart"})
    v = container.add_stream("libx264", rate=fps)
    v.width, v.height, v.pix_fmt = w, h, "yuv420p"
    v.options = {"crf": crf, "preset": "slow", "tune": "stillimage"}
    a = container.add_stream("aac", rate=TAXA)
    a.layout = "stereo"
    a.bit_rate = 128000
    a.time_base = Fraction(1, TAXA)

    bloco, pos = 1024, 0
    for k, q in enumerate(quadros):
        for pkt in v.encode(av.VideoFrame.from_image(Image.open(q).convert("RGB"))):
            container.mux(pkt)
        alvo = int((k + 1) / fps * TAXA)
        while pos < min(alvo, len(audio)):
            trecho = audio[pos: pos + bloco]
            if len(trecho) < bloco:
                trecho = np.pad(trecho, (0, bloco - len(trecho)))
            fa = av.AudioFrame.from_ndarray(np.stack([trecho, trecho]).astype(np.float32), format="fltp", layout="stereo")
            fa.sample_rate, fa.pts = TAXA, pos
            for pkt in a.encode(fa):
                container.mux(pkt)
            pos += bloco
    for stream in (v, a):
        for pkt in stream.encode():
            container.mux(pkt)
    container.close()

    capa = quadros[min(len(quadros) - 1, int(3.2 * fps))]  # abertura já montada
    Image.open(capa).convert("RGB").resize((1280, 720)).save(saida.with_name("tutorial-capa.jpg"), quality=85)
    print(f"MP4: {saida} · {w}×{h} · {duracao:.1f} s · {saida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
