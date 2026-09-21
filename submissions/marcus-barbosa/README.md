# Submissão — Marcus Barbosa — Challenge 003

## Sobre mim

- **Nome:** Marcus Barbosa
- **LinkedIn:** [[a confirmar pelo Marcus antes do PR]]
- **Challenge escolhido:** 003 — Lead Scorer (Vendas / RevOps)

---

## Executive Summary

Construí um Lead Scorer em Python e Streamlit que o vendedor abre na segunda-feira e vê o que fazer com cada deal, com o motivo e o número por trás. Antes de qualquer fator, testei 27 hipóteses nos 8.800 deals do CRM: vendedor, vendedor × produto, produto, setor e porte da conta não separam ganho de perda além do acaso, e a base tem duas bordas que enganam (só há fechamentos a partir de março de 2017 e nenhum deal fechou depois de 138 dias). O que sobrevive é a idade do deal (metade das derrotas acontece em até 14 dias) e o valor. A chance de ganhar em 90 dias é calibrada por um painel de 7 snapshots de 2017 só com o passado, e o backtest walk-forward confirma o achado mais caro para a Head de RevOps: 1.291 deals em Engaging, 64% do valor nominal do pipeline, estão além de qualquer ciclo já concluído e nenhum deles fechou depois, em nenhuma das datas testadas. A recomendação principal é limpar esse pipeline e cadastrar as contas dos 1.425 deals sem conta antes de cobrar priorização de alguém.

---

## Solução

### Abordagem

Comecei pelo processo, não pelos dados: li as 176 reviews públicas que o avaliador do G4 deixou nos 100 PRs anteriores e extraí a rubrica real e as armadilhas (pasta gitignored, data de referência, `GTXPro`, leakage, higiene). Gerei três baselines colando o brief em agentes cegos, para saber o que a IA produz sozinha, e escrevi uma rubrica de 16 diferenciadores antes de abrir os CSVs (`process-log/differentiation-rubric.md`).

Com os dados: auditoria de saúde com número (`solution/01_audit.py`), 27 hipóteses testadas com veredito automático e revisão humana (`solution/02_explore.py`, `process-log/hypotheses.md`), calibração por painel de snapshots (`solution/leadscorer/calibration.py`), score por valor esperado com categorias de ação (`scoring.py`), backtest walk-forward (`03_backtest.py`), 21 testes de invariantes, app com a identidade visual do G4 extraída do CSS público do site (`docs/design-system.md`). Cada número do README tem o script que o gerou em `docs/methodology.md`.

### Resultados / Findings

1. O pipeline aberto está, em sua maior parte, fora do suporte histórico. Em 2017-12-31, 1.291 dos 1.589 deals em Engaging (81%) têm mais de 138 dias, e nenhum deal, ganho ou perdido, teve ciclo maior que isso em 6.711 fechamentos. No backtest, dos 149, 275, 408 e 530 deals nessa situação em 30/06, 31/07, 31/08 e 30/09, zero fecharam depois.
2. Quem morre, morre cedo. Ciclo mediano dos Lost é 14 dias; dos Won, 57 (p=10⁻²⁶). Entre deals com conta, a chance de ganhar em 90 dias é 47% até 14 dias, 55% de 15 a 90, 44% de 91 a 120 e 13% de 121 a 138 (n=8.456 linhas deal × data, IC 95% em `docs/methodology.md`).
3. Vendedor não é sinal. Spread de 15 pp entre vendedores, mas χ² p=0,26; e o gap vendedor × produto (8,7 pp) é igual ao que a sorte produz com esses tamanhos de amostra (nulo binomial 9,9 pp, p=0,89). O que outros candidatos aprovados chamaram de fit vendedor × produto é ruído.
4. Conta ausente é processo. 1.425 deals abertos (68%) não têm conta, em Engaging e em Prospecting na mesma proporção; nenhum deal fechado fica sem conta. Não dá para saber se a conta é preenchida no fechamento, então ela vira ação de higiene, não fator.
5. Valor concentrado. 20% dos deals abertos carregam 50% do valor de lista; o valor fechado é 0,998 do preço de lista, então o preço de lista é o ticket.
6. Toda a prospecção sem data (500 deals) está na região Central, e um vendedor tem 194 deals abertos sem nenhum acionável.

O que o backtest diz contra a solução, sem rodeio: na captura de valor ganho pelo top-N, o score empata com ordenar por preço de lista, porque a chance é quase plana entre 15 e 120 dias. O que o método faz que ordenar por preço não faz é tirar do topo o que a história diz que não fecha, dizer o que fazer com cada bloco e não inventar chance onde não há histórico (`docs/backtest.md`).

### Recomendações

Para a Head de RevOps, em ordem:

1. Limpar o pipeline nesta semana: confirmar cliente a cliente os 1.291 deals além de 138 dias e encerrar como Lost o que não responder. Isso tira US$ 3,2 milhões de valor fictício do forecast.
2. Tornar a conta obrigatória para sair de Prospecting. 68% dos deals abertos não têm conta; nos dados, nenhum deal fechou sem.
3. Colocar a regra dos 14 dias na rotina: todo deal engajado recebe contato com próximo passo e data na primeira semana. Metade das derrotas acontece nessa janela.
4. Rever a carteira de quem tem mais de 100 deals abertos (7 vendedores acima do P75 do time; correlação de −0,45 entre carga e conversão).
5. Instrumentar antes de sofisticar: registrar atividade e transições de estágio no CRM. Sem isso, nenhum modelo, este incluído, sai de uma chance quase plana.

Como saber se funcionou: piloto de 8 semanas com metade dos vendedores de cada gerente usando a pauta; métricas antecedentes (valor além de 138 dias, share de deals sem conta, contato em até 7 dias nos engajados) e primária (win rate em 90 dias do grupo com a ferramenta contra o grupo sem), com gate de continuar só se a diferença for maior que o intervalo de confiança.

### Limitações

- A base é sintética na origem e tem bordas artificiais (teto de 138 dias, fechamentos só a partir de março de 2017). As taxas valem para esta base.
- Não há atividade, transições de estágio nem a data em que a conta foi preenchida. Por isso a conta não pode ser fator e a prospecção não recebe chance.
- A chance com conta é um limite otimista e a chance incluindo deals sem conta é o pessimista; a verdade está entre os dois.
- O score não bate ordenar por preço na captura de valor em 2017.
- Sem deploy público nesta versão; o app roda local com um comando e sem chave de API.

### Como rodar

```bash
cd submissions/marcus-barbosa/solution
py -3.12 -m pip install -r requirements.txt
py -3.12 download_data.py            # ou: py -3.12 download_data.py --zip archive.zip (zip baixado do Kaggle)
py -3.12 -m pytest -q tests           # 21 testes
py -3.12 01_audit.py && py -3.12 02_explore.py && py -3.12 03_backtest.py
py -3.12 -m streamlit run app.py
```

Presets por URL para navegar sem clicar: `?papel=Gerente&regiao=Central`, `?papel=RevOps&data=2017-09-30`, `?papel=Vendedor&vendedor=Vicki%20Laflamme`. `99_clean_env_check.ps1` repete tudo em um venv novo.

### Lógica do score

| Passo | Regra | Sustentação |
|---|---|---|
| Chance de ganhar em 90 d | taxa por faixa de idade (0-14, 15-90, 91-120, 121-138 dias) calibrada em painel de snapshots de fim de mês, só com deals com conta e só com o passado | H8b, H10b, H11; `calibration.py` |
| Valor esperado | chance × preço de lista | H7 (valor fechado = 0,998 do preço) |
| Score 0-100 | percentil do valor esperado entre os deals acionáveis (Engaging até 138 d) | "score 88" = vale mais que 88% do pipeline acionável |
| Sem chance e sem score | Engaging além de 138 d (nenhum deal fechou depois) e Prospecting (sem histórico de prospecção → engajamento) | H9, H11, decisão 15 |
| Categorias | Focar agora (score ≥ 70), Primeiras duas semanas (≤ 14 d), Manter follow-up, Confirmar se está vivo (> 138 d), Qualificar ou descartar (Prospecting); Cadastrar conta como ação a mais | decisões 9, 13, 16 |
| Fora do score | vendedor, vendedor × produto, produto, setor, porte, subsidiária, desconto | H1, H2b, H4, H14, H15, H16, H7 |

---

## Process Log — Como usei IA

> **Este bloco é obrigatório.** Sem ele, a submissão é desclassificada.

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Claude Code (Claude Fable 5.1), sessão única, edição automática desligada | Auditoria do repositório e das reviews públicas, análise dos dados, código, testes, app, documentação |
| Subagentes do Claude Code em painéis (juízes, céticos, arquitetos, auditores) | Escolha do challenge (4 juízes + 3 céticos), baselines cegos do brief (3), painel de arquitetura (3 designs + 3 juízes), pesquisa sobre o G4 (5 varreduras), auditoria adversarial da entrega |
| Claude in Chrome | Download do dataset no Kaggle com a minha sessão logada |
| Playwright (Chromium headless) | Capturas de tela reproduzíveis do app |
| GitHub CLI | Coleta das 176 reviews públicas do avaliador nos 100 PRs anteriores |

### Workflow

1. Clonei o repositório, li os 11 arquivos e pedi uma auditoria de segurança (unicode invisível, injeção de prompt, hooks, histórico): nada malicioso.
2. Mandei coletar todas as reviews públicas do avaliador; delas saíram a rubrica real e 13 armadilhas (`docs/marcos.md`, `_auditoria/` fora da pasta).
3. Painel de agentes para escolher o challenge: empate 002 × 003 (33 × 32). Escolhi o 003 pelo alinhamento com o negócio do G4, contra o consenso numérico.
4. Defini o pronto: 100% dos marcos, banca de revisores com 100/100, tudo explicável e verdadeiro.
5. Baselines cegos e rubrica de diferenciação antes dos dados.
6. Download dos dados pela minha sessão; auditoria de saúde; 27 hipóteses com veredito.
7. Três decisões de produto delegadas à análise com exigência de justificativa (deals além de 138 dias, vendedor fora do score, origem das hipóteses), registradas no ledger.
8. Motor v1, backtest, descoberta de que a taxa condicional superestimava; motor v2 por painel de snapshots; backtest walk-forward.
9. App com a identidade do G4, capturas, validação em ambiente limpo, auditoria adversarial por agentes, banca final.

Detalhes iteração a iteração em `process-log/workflow.md`; decisões com origem em `process-log/decisions.md`.

### Onde a IA errou e como corrigi

Quatro erros registrados em `process-log/ai-errors.md`, cada um com detecção, causa raiz e correção:

1. `git add -f` arrastou caches do pytest para um commit; corrigido e regra de add alterada.
2. O veredito automático marcou sazonalidade como confirmada (p=10⁻¹⁹) ignorando que a base não tem fechamentos antes de março de 2017; criada a janela limpa.
3. A primeira rodada aceitou vendedor × produto como sinal comparando gaps entre quartis; o teste nulo binomial mostrou que era acaso.
4. A primeira calibração usou Won/(Won+Lost), que ignora quem nunca fecha; o backtest mostrou ganho observado de 32% a 50% contra 61% a 67% calibrados; trocada por painel de snapshots.

### O que eu adicionei que a IA sozinha não faria

Meu papel foi de direção, e o ledger registra exatamente isso, sem atribuir a mim hipóteses que não formulei. O que veio de mim: começar pela auditoria do processo e das reviews públicas, em vez de pelos dados; a regra de que nenhum fator entra sem hipótese testada e nenhum número sem denominador; a definição de pronto com banca de revisores e nota 100; a escolha do 003 contra o consenso do painel; a exigência de que o produto tivesse a cara do G4 e o texto não tivesse cara de IA; e a recusa a qualquer atribuição falsa no process log. As hipóteses, o código e os textos são da IA sob essa direção; as decisões 9 a 17 foram delegadas à análise com a condição de vir com o porquê, e endossadas.

---

## Evidências

- [x] Screenshots do app rodando: `process-log/screenshots/app/`
- [x] Screenshots das sessões com IA: `process-log/screenshots/sessoes/`
- [x] Chat export: `process-log/chat-exports/` (transcript da sessão, com o token de API que colei por engano removido)
- [x] Git history: commits incrementais nesta branch, autoria Marcus Barbosa
- [x] Outro: baselines cegos (`process-log/baselines/`), painel de arquitetura (`docs/design-panel.md`), auditoria adversarial (`process-log/critique-synthesis.md`), banca final (`docs/banca-final.md`)

---

_Submissão enviada em: 2026-09-21_
