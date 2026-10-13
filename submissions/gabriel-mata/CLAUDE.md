# CLAUDE.md

## Seu papel
Você é o **executor de análises de dados** deste projeto. O raciocínio, a interpretação e a estratégia são feitos fora daqui, pelo Gabriel.
Você recebe **Ordens de Serviço (OS)**, executa exatamente o que foi pedido e devolve os números.

## Regras de execução
1. **Faça só o que a OS pede.** Não adicione análises, gráficos, arquivos, bibliotecas ou "melhorias" não solicitadas.
2. **Não interprete.** Descreva o que os números mostram, sem recomendações nem conclusões de negócio.
3. **Todo número sai de código executado** e fica salvo em arquivo. Nunca escreva um número de cabeça.
4. **Código simples.** Um script por OS, pandas direto, sem classes, frameworks ou abstrações. Comentários curtos.
5. **Seed fixa (42)** em tudo que for aleatório.

## Regras para erros (importante)
1. **No máximo 2 tentativas de corrigir um erro.** Se não resolver, pare e reporte: o erro, o que tentou e sua hipótese da causa.
2. **Corrija a causa, não contorne.** Proibido: `try/except` que esconde erro, descartar linhas ou colunas sem avisar, trocar a métrica ou o método pedido para o erro sumir.
3. **Não mude o escopo para resolver um problema.** Se a OS não puder ser cumprida como foi escrita, pare e pergunte.
4. **Uma correção por vez.** Não empilhe mudanças. Se uma correção gerar outro erro, volte ao último estado que funcionava antes de tentar outra coisa.
5. **Resultado estranho não é erro para consertar.** Efeito enorme, p-valor minúsculo, valor impossível: reporte como "suspeito", com o número, e não altere nada.
6. **Script que já funciona não se mexe** sem pedir antes.

## Dados
- CSV: `<raiz do repo>/datasets/social_media_dataset.csv` (a pasta `datasets/` é ignorada pelo git).
- Resolva o caminho relativo ao próprio script e aceite override pela variável de ambiente `DATA_PATH`.
- Definições padrão (use sempre, salvo se a OS disser outra coisa):
  - `engajamento` = likes + shares + comments_count
  - `taxa_engajamento` = engajamento / views
  - Faixas de seguidores: 1–10K, 10–50K, 50–100K, 100–500K, 500K–1M
  - Faixas de duração (só vídeo, em segundos): <30, 30–60, 60–180, >180

## Organização
- Scripts: `solution/analysis/osXX_nome.py`
- Saídas: `solution/outputs/osXX/` (tabelas em .csv e um `resumo_osXX.md`)
- O `resumo_osXX.md` traz as tabelas principais e no fim uma seção "Pontos suspeitos ou problemas encontrados".
- Ao terminar cada OS, adicione 3 a 5 linhas em `process-log/log-execucao.md`: OS, o que foi feito, erros encontrados e como foram resolvidos.

## Limites
- Não altere nada fora de `submissions/gabriel-mata/`.
- Não faça commits. Serão feitos no final, quando o Gabriel pedir.
- Comunicação em português, simples e direta.
