# G8: crítica adversarial, síntese

A entrega passou por crítica **antes** do PR, com dois tipos de revisor:

| Rodada | Revisor | Como foi feita | Veredito |
|---|---|---|---|
| 1 | Agente `g4-reviewer` (Claude Code), baseado nos critérios públicos do repositório | Checkout limpo da branch, `uv sync`, rodou os 4 scripts e os testes, comparou os CSVs regerados com os versionados, conferiu mais de 30 números contra os dados | **9/10, sem bloqueadores** · [`../../reports/review-verdict-round1.md`](../../reports/review-verdict-round1.md) |
| 2 | ChatGPT e Gemini, operados pelo Douglas | Link do fork com o pedido de apontar fraquezas, números sem fonte, o que não roda na segunda-feira e o que falta do brief | ChatGPT: "não aprovaria sem corrigir", 24 apontamentos · Gemini: não conseguiu ler o GitHub e não avaliou |

## Rodada 1: o que foi apontado e o que fiz

| # | Apontamento | Decisão | Status | Verificação |
|---|---|---|---|---|
| 1 | Process log incompleto: `chat-exports/` e `critique/` vazias; linha do tempo por gate só com o G0 | Preencher | Linha do tempo G0–G8 e esta síntese: **feito**. Transcript da sessão: **feito** (`chat-exports/sessao-claude-code-g0-a-g8.md`) | `process-log/README.md` |
| 2 | `app/assets/posts.parquet` tinha as 52.214 linhas do dataset (dataset bruto versionado é motivo de reprovação por higiene) | Remover do repositório | **Feito**: o app carrega os dados por `src/app_data.py` (local ou Kaggle na 1ª abertura, 4,8 s a frio); conteúdo idêntico ao anterior | `git ls-files \| grep parquet` → vazio; commit `c976a8e` |
| 3 | Único número sem tabela: "≤ 0,012 p.p." (real: 0,0126) | Corrigir e gerar a tabela | **Feito** | `outputs/tables/dq-segment-amplitude.csv`; commit `8cd775c` |
| 4 | Data do PR em branco no README | Preencher no dia do PR | _no G9_ | `README.md` |
| 5 | `curl` sem cookie entra em loop de redirecionamento no domínio `streamlit.app` | Documentar; é o login do próprio Streamlit Cloud | `/healthz` responde `200 {"status":"ok"}` com cookie; o app abre no navegador | `curl -c ck -b ck -L https://decision-social-doug.streamlit.app/healthz` |

### O risco que não se resolve editando arquivo
> "A silhueta é a do #91; as 8 diferenças vivem dentro das camadas."

O revisor mostrou que, por fora, a entrega se parece com o PR #91 (mesmo arquivo, mesma conclusão, mesmo tipo de app), e que o resumo executivo abria justamente pelo achado estatístico, onde as duas empatam. **Decisão do Douglas:** o README passa a abrir pelo processo; a estatística vira o motivo, não a manchete.

## Rodada 2: ChatGPT e Gemini

Prints: `../screenshots/g8-chatgpt-01` a `09` e `g8-gemini-01`. **Gemini** respondeu que o GitHub bloqueou a leitura e pediu o conteúdo colado; não houve avaliação. **ChatGPT** ("Pensou por 3m 14s") leu o repositório e fez 24 apontamentos. Conferi cada um contra os arquivos antes de aceitar.

| # | Apontamento do ChatGPT | Conferência | Destino |
|---|---|---|---|
| 1 | O processo atual (contrato no e-mail e no CRM) foi inventado a partir da vivência e apresentado como fato | Procede: o brief não descreve a operação | **Aceito** (decisão do Douglas): marcado como premissa a validar na semana 1 |
| 2 | "Foi gerado por Poisson" é vendido como prova; o teste só mostra compatibilidade | Procede | **Aceito**: "se comporta como um sorteio", "inferência pela assinatura estatística" |
| 3 | São 332 comparações com veredito, não 335 | Procede: 3 desfechos secundários do patrocínio não têm veredito | **Aceito**: texto corrigido em todos os documentos |
| 4 | `compare()` supõe posts independentes; creators se repetem | ICC por creator = −0,001; efeito de desenho 0,99 | **Respondido com análise**: veredito inalterado (`inf-robustness.csv`) |
| 5 | TOST com IC 90% individual, sem correção para múltiplos testes | Com Bonferroni para 332, maior limite 0,78 p.p. | **Respondido com análise**: todas seguem equivalentes |
| 6 | "Dados não permitem decidir" e a 1ª recomendação é suspender patrocínios; faltam exceções | Procede como incoerência de enquadramento | **Aceito** (decisão do Douglas): STR-01 vira regra de entrada, com política de exceção |
| 7 | "Gera 0,77 interação" é o limite superior do IC, não o efeito | Procede: o efeito estimado é −0,003 p.p. | **Aceito**: descrito como limite do IC 95% |
| 8 | R$ 5 por interação é arbitrário e sustenta o "menos de 1%" | Procede | **Aceito**: nova métrica sem parâmetro (cada interação precisaria valer R$ 646) |
| 9 | O CSV enviado na aba 1 não chega ao painel | Procede, confirmado no código | **Aceito**: o painel aceita o arquivo checado; novo teste |
| 10 | O app não integra CRM, redes ou vendas | Escopo definido no G6 (4 telas, sem integrações) | **Mantido**: decisão de escopo do Douglas |
| 11 | Preços de mercado sem fonte na tabela | Procede: as fontes estavam só no texto | **Aceito**: coluna `fonte` em `str-market-fees.csv` |
| 12 | ±1 p.p. foi escolhido pelo autor | É uma régua pré-registrada (decisão do Douglas) | **Respondido com análise**: o veredito vale para qualquer régua a partir de 0,45 p.p. |
| 13 | "Reprovado em todas" vs. "9 de 11" | Procede | **Aceito** |
| 14 | "6 contra 8 esperados" supõe testes independentes | Procede em parte (grupos se sobrepõem) | **Aceito**: "compatível com o acaso" |
| 15 | "Variância/média entre 0,99 e 1,00", mas likes = 1,003 | 1,003 arredonda para 1,00 | **Mantido** |
| 16 | "Manter a cadência atual" sem dizer qual é | Procede | **Aceito**: medir a cadência real por canal no Gate 0 |
| 17 | Não identifica o CRM real, campos e API | A empresa do brief não tem sistemas descritos | **Mantido**: inventário no roadmap (semana 1) |
| 18 | Testes de 393–1.570 posts por braço em 15 dias, sem prova de volume | Procede | **Aceito**: o teste fecha ao atingir o n, não numa data |
| 19 | Sem estratégia concreta de conteúdo ("faça X sobre Y") | O arquivo não sustenta nenhuma; inventar seria o erro do baseline | **Mantido**: EXP-02 testa formato por canal |
| 20 | Sem concentração de esforço | A recomendação é não mudar o mix enquanto não há evidência | **Mantido** |
| 21 | Threshold de seguidores sem número | Não existe threshold nos dados | **Mantido**: o threshold é financeiro e numérico (fee ≤ vendas × margem; R$ 646 por interação) |
| 22 | ROI trocado por cenários hipotéticos | O arquivo não tem custo nem venda (DQ-12) | **Mantido** |
| 23 | Quick wins são de governança, não de conteúdo | Intencional: sem medição, quick win de conteúdo seria palpite | **Mantido** |
| 24 | Brief pede 4–6 h; a entrega não mostra o tempo gasto | — | **Sem mudança** no README |

**Balanço:** 12 aceitos, 3 respondidos com análise nova (o veredito não mudou), 9 mantidos com justificativa.

### O ataque central do ChatGPT
> "Você concluiu que meu dataset não permite tomar decisão. Então por que sua primeira recomendação é eu tomar a decisão de suspender meus novos contratos de influenciadores?"

**Depois do G8:** a recomendação deixou de ser "suspender". É: *nenhum contrato novo entra sem custo, cupom/UTM e grupo de comparação*. Não decide se patrocínio funciona; garante que o próximo contrato responda essa pergunta.
