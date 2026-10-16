"""Narração neural do tutorial (Microsoft Edge TTS) e linha do tempo das cenas.

    python scripts/narracao.py

Lê roteiro.json e grava:
- public/audio/<cena>.wav            voz de cada cena (24 kHz, mono, silêncio das pontas aparado)
- src/narracao.json                  início, duração e legendas de cada cena, em segundos e quadros
- out/tutorial.vtt                   legendas WebVTT para o player do app

O texto do roteiro é enviado ao serviço online de leitura em voz alta da Microsoft.
As legendas usam o texto do roteiro; a pronúncia ajustada vale só para a voz.
"""
from __future__ import annotations

import asyncio
import json
import math
import re
import wave
from pathlib import Path

import edge_tts
import miniaudio
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
TAXA = 24000
FPS = 30
ENTRADA = 1.2      # respiro antes da primeira fala (s)
INTERVALO = 0.7    # pausa entre cenas (s)
SAIDA = 2.0        # tempo de tela após a última fala (s)
MARGEM = 0.05      # silêncio mantido em cada ponta da fala (s)


def sentencas(texto: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto) if s.strip()]


async def sintetizar(texto: str, voz: str, velocidade: str) -> tuple[np.ndarray, list[tuple[float, float]]]:
    fala = edge_tts.Communicate(texto, voz, rate=velocidade, boundary="SentenceBoundary")
    mp3, marcas = bytearray(), []
    async for parte in fala.stream():
        if parte["type"] == "audio":
            mp3.extend(parte["data"])
        elif parte["type"] == "SentenceBoundary":
            marcas.append((parte["offset"] / 1e7, (parte["offset"] + parte["duration"]) / 1e7))
    pcm = miniaudio.decode(bytes(mp3), output_format=miniaudio.SampleFormat.SIGNED16, nchannels=1, sample_rate=TAXA)
    return np.frombuffer(pcm.samples, dtype="<i2").copy(), marcas


def aparar(x: np.ndarray) -> tuple[np.ndarray, float]:
    ativo = np.flatnonzero(np.abs(x) > 400)
    if not len(ativo):
        return x, 0.0
    ini = max(0, ativo[0] - int(MARGEM * TAXA))
    fim = min(len(x), ativo[-1] + int(MARGEM * TAXA))
    return x[ini:fim], ini / TAXA


def gravar(caminho: Path, x: np.ndarray) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(x.astype("<i2").tobytes())


def legendas(texto: str, marcas: list[tuple[float, float]], desloc: float, duracao: float) -> list[dict]:
    frases = sentencas(texto)
    if len(marcas) == len(frases):
        tempos = [(max(0.0, a - desloc), min(duracao, b - desloc)) for a, b in marcas]
    else:  # serviço agrupou as frases de outro jeito: distribui pelo tamanho do texto
        total, acc, tempos = sum(len(f) for f in frases), 0, []
        for f in frases:
            tempos.append((duracao * acc / total, duracao * (acc + len(f)) / total))
            acc += len(f)
    return [{"inicio": round(a, 3), "fim": round(b, 3), "texto": f} for f, (a, b) in zip(frases, tempos)]


def vtt_tempo(s: float) -> str:
    h, resto = divmod(s, 3600)
    m, seg = divmod(resto, 60)
    return f"{int(h):02d}:{int(m):02d}:{seg:06.3f}"


async def main() -> None:
    roteiro = json.loads((RAIZ / "roteiro.json").read_text(encoding="utf-8"))
    cenas, cursor = [], ENTRADA
    for cena in roteiro["cenas"]:
        fala = cena["texto"]
        for escrito, dito in roteiro["pronuncia"].items():
            fala = fala.replace(escrito, dito)
        bruto, marcas = await sintetizar(fala, roteiro["voz"], roteiro["velocidade"])
        audio, desloc = aparar(bruto)
        duracao = len(audio) / TAXA
        gravar(RAIZ / "public" / "audio" / f"{cena['id']}.wav", audio)
        inicio_cena = cursor - (ENTRADA if not cenas else INTERVALO / 2)
        cenas.append({
            "id": cena["id"], "texto": cena["texto"], "audio": f"audio/{cena['id']}.wav",
            "fala": round(cursor, 3), "duracaoFala": round(duracao, 3), "inicio": round(inicio_cena, 3),
            "legendas": [{**l, "inicio": round(l["inicio"] + cursor, 3), "fim": round(l["fim"] + cursor, 3)}
                         for l in legendas(cena["texto"], marcas, desloc, duracao)],
        })
        print(f"{cena['id']:<10} {duracao:5.1f} s")
        cursor += duracao + INTERVALO
    total = cursor - INTERVALO + SAIDA
    for atual, seguinte in zip(cenas, cenas[1:] + [None]):
        fim = seguinte["inicio"] if seguinte else total
        atual["duracao"] = round(fim - atual["inicio"], 3)
        atual["deQuadro"] = round(atual["inicio"] * FPS)
        atual["quadros"] = round(fim * FPS) - atual["deQuadro"]
    linha = {"fps": FPS, "total": round(total, 3), "quadros": math.ceil(total * FPS), "cenas": cenas}
    (RAIZ / "src" / "narracao.json").write_text(json.dumps(linha, ensure_ascii=False, indent=1), encoding="utf-8")

    cues = [l for c in cenas for l in c["legendas"]]
    for atual, seguinte in zip(cues, cues[1:]):  # sem sobreposição entre legendas vizinhas
        atual["fim"] = min(atual["fim"], seguinte["inicio"] - 0.001)
    vtt = ["WEBVTT", ""]
    for i, l in enumerate(cues, 1):
        vtt += [str(i), f"{vtt_tempo(l['inicio'])} --> {vtt_tempo(l['fim'])}", l["texto"], ""]
    (RAIZ / "out").mkdir(exist_ok=True)
    (RAIZ / "out" / "tutorial.vtt").write_text("\n".join(vtt), encoding="utf-8")
    print(f"total {total:.1f} s · {len(cues)} legendas")


if __name__ == "__main__":
    asyncio.run(main())
