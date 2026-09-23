# Manifesto da entrega — Challenge 004

Verificação local: **22/09/2026**. Este manifesto separa artefatos versionados de links externos e registra o estado real de publicação.

## Percurso do avaliador

1. Ler no [README da submissão](../../README.md) as quatro respostas e decisões executivas em um minuto.
2. Abrir o tour Arcade de sete etapas: `https://app.arcade.software/share/VHx5b51f94IAFSr6pmds`. O percurso executivo termina aqui, dentro de cinco minutos.
3. Assistir ao [vídeo obrigatório de arquitetura](./assets/architecture-walkthrough-captioned.mp4), artefato da construção fora do percurso executivo.
4. Consultar a síntese do NotebookLM: [vídeo](./assets/notebooklm-video.mp4), [mapa mental](./assets/notebooklm-mind-map.png) e [infográfico](./assets/notebooklm-infographic.png).
5. Aprofundar somente se necessário pelo [estudo de caso](./CONSTRUCTION-STORY.md) e [diário](../../process-log/004-social.md).

## Estado dos links externos

| Entrega | Estado em 22/09/2026 | Verificação |
|---|---|---|
| Arcade | Público | HTTP 200 sem sessão; título `Cockpit de Social Media — decisões em 3 minutos | Arcade` |
| NotebookLM | Privado por decisão do autor | Vídeo, mapa e infográfico foram baixados e versionados; o avaliador não precisa acessar a conta proprietária |

O notebook-fonte não integra o percurso externo. Os cinco projetos antigos do Arcade foram excluídos com confirmação de Luis e movidos para `Recently deleted`; o Cockpit foi preservado e publicado.

## Artefatos versionados

| Arquivo | Propriedade verificada | Bytes | SHA-256 |
|---|---:|---:|---|
| `assets/architecture-walkthrough-captioned.mp4` | H.264/AAC, 1.280 × 720 px, 6min05,55s; sem cortes | 46.065.676 | `3bd2642074715c082212388c9672aa3afcd8a1037351f071736661e33125f907` |
| `CONSTRUCTION-STORY.docx` | 7 páginas; abre sem reparo | 45.991 | `fef288a03791f9f99b918f877a22396c816369215b95cde22100306487c076f4` |
| `assets/methodology-evolution.png` | 2.000 × 2.800 px | 579.992 | `818408330d0aa37b35d59d0515f6a6090130de35c871606a36267300e2f4042f` |
| `assets/notebooklm-mind-map.png` | 2.375 × 5.138 px | 675.511 | `88a3d2f7a7c414b204d0d65f695383851128fa28a9fb9a02341e50bc4f0defce` |
| `assets/notebooklm-infographic.png` | 1.536 × 2.752 px | 5.389.693 | `c3b8064089ac2314e7382c5003ef35a2e02f9c99b6b8986dbfc860cc1107fb53` |
| `assets/notebooklm-video.mp4` | H.264/AAC, 1.280 × 720 px, 5min57,54s | 11.686.713 | `27edddf577a02bfbb0b172db77829ada78fa55c2a3ced10846e70e65da3de0ee` |

## QA aplicada

- O vídeo de arquitetura é a gravação aprovada por Luis, com hash-fonte `a968a524dbe45443a066717e5d63523e5336f958fb3a6dcd50d0d0887dbbea4a`. A cópia de 232.879.349 bytes foi otimizada para 46.065.676 bytes, sem cortes, para permanecer abaixo do limite de 100 MB do GitHub.
- O vídeo otimizado decodifica integralmente; duração, áudio, legendas e cinco pares de quadros distribuídos foram confrontados com a fonte.
- O primeiro infográfico foi rejeitado por dois números imprecisos e regenerado.
- O primeiro vídeo foi rejeitado por duração e frase ambígua; a segunda geração corrigiu o contrato factual.
- A versão final foi acelerada uniformemente em `1,1×`, sem corte, para cumprir o intervalo de 4–6 minutos.
- O MP4 decodifica integralmente; seis quadros distribuídos e o encerramento foram inspecionados.
- O Arcade abriu em uma segunda sessão do Chrome e percorreu as sete etapas até o encerramento.
- Duas passadas finais consecutivas terminaram sem correção relevante; HR-01 humano permanece pendente.
- O primeiro preflight remoto confirmou dependências íntegras e **146/146 testes** em 68,762 segundos; como o shell não devolveu status terminal inequívoco após a suíte, o gate completo será repetido no SHA documental final antes da atualização do PR aberto.
