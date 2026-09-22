# Process log — como a IA foi usada

Este diretório é a evidência auditável do processo. Tudo aqui foi produzido durante o trabalho, na ordem em que aconteceu.

| Arquivo | O que contém |
|---|---|
| `hypotheses.md` | 27 hipóteses formuladas pela IA sob a regra do Marcus (hipótese antes de fator, auditoria antes de análise), cada uma com veredito, número e se entra no score |
| `decisions.md` | Ledger de decisões com origem: decisão do Marcus / consenso / sugestão da IA |
| `ai-errors.md` | Erros cometidos pela IA, como foram detectados, causa raiz e correção |
| `workflow.md` | Narrativa cronológica, iteração por iteração |
| `baselines/` | O que a IA produz sozinha quando recebe o brief colado (3 variantes + síntese) |
| `differentiation-rubric.md` | O que esta entrega precisa fazer a mais que os baselines, escrito antes de codar, com o status final de cada item |
| `critique-synthesis.md` | Auditoria adversarial por agentes independentes: achados verificados e o que foi corrigido |
| `screenshots/app/` | Capturas do app rodando (geradas por `solution/04_screenshots.py`) |
| `screenshots/sessoes/` | Capturas da janela do Claude Code durante o trabalho (barra lateral com outras sessões recortada) |
| `chat-exports/` | Transcript da sessão de Claude Code em texto, com o token de API colado por engano removido |

Ferramenta principal: Claude Code (Claude Fable 5.1), com edição automática desligada e revisão humana de cada mudança.
