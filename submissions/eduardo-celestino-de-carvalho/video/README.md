# Vídeo tutorial do Lead Kanban

Vídeo de 2 minutos, em motion design e com narração, para quem vai usar a ferramenta sem conhecer a área comercial. Ele abre como primeira seção do procedimento do app (botão **?**) e também pelo botão "Assistir tutorial", no guia rápido do Pipeline.

O vídeo pronto fica em [`solution/web/media/`](../solution/web/media/), junto com a capa e as legendas. Esta pasta guarda o código que o gera.

## Como é feito

| Etapa | Arquivo | O que faz |
|---|---|---|
| Roteiro | [roteiro.json](roteiro.json) | Texto das 10 cenas, voz e ajustes de pronúncia ("Lead" → "Líd") |
| Narração | [scripts/narracao.py](scripts/narracao.py) | Voz neural pt-BR (Microsoft Edge TTS), apara silêncios e gera a linha do tempo e as legendas WebVTT |
| Capturas | [scripts/capturas.mjs](scripts/capturas.mjs) | Telas reais do app em 2× e a posição de cada elemento destacado |
| Cenas | [src/cenas.tsx](src/cenas.tsx) | Motion design em [Remotion](https://www.remotion.dev/) (React): câmera sobre as telas reais, spotlight, rótulos e números animados, sincronizados a cada frase |
| Render | [scripts/renderizar.mjs](scripts/renderizar.mjs) + [scripts/codificar.py](scripts/codificar.py) | O Chrome do Remotion exporta os quadros e o PyAV mixa a narração e codifica em H.264 + AAC |

As cenas usam capturas do app, não telas desenhadas. Se a interface mudar, basta rodar as capturas de novo, e os destaques acompanham as novas posições.

## Reproduzir

Requisitos: Node 20+, Python 3.11+, Microsoft Edge (para as capturas) e internet (voz e fontes).

```powershell
# 1. Em solution/: python server.py
# 2. Nesta pasta:
npm install
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/narracao.py   # voz, linha do tempo e legendas
npm run capturas                                 # telas do app em http://localhost:8000
npm run video -- --conferir                      # quadros de conferência em out/conferencia/
npm run video                                    # out/tutorial.mp4 + capa
```

As capturas (`public/capturas/`) e os áudios (`public/audio/`) não são versionados: os dois comandos acima os recriam, e `src/capturas.json` e `src/narracao.json` guardam as posições e os tempos usados no vídeo publicado.

Para publicar no app, copie `out/tutorial.mp4`, `out/tutorial-capa.jpg` e `out/tutorial.vtt` para `solution/web/media/`. `npm run studio` abre a prévia interativa do Remotion.

**Por que o MP4 não sai direto do Remotion:** nesta máquina, o Controle de Aplicativo do Windows bloqueia o ffmpeg que acompanha o Remotion. O Remotion exporta apenas os quadros, e o PyAV faz a codificação.

## Limitações

- A voz é sintética (Microsoft Edge TTS). Para uma versão final, basta trocar os WAV em `public/audio/` por uma gravação humana ou outra voz, e a linha do tempo se ajusta ao novo áudio.
- O texto do roteiro é enviado ao serviço online de voz da Microsoft. Ele não contém dados de clientes.
- O Remotion tem licença gratuita para uso individual e empresas pequenas; uso corporativo maior exige licença paga.
