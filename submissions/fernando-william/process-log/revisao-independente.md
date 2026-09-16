# Revisão independente antes do PR

Abri o Codex nesta pasta, com o mesmo `AGENTS.md`, e pedi uma revisão como avaliador cético que clona o repositório sem credencial: números do README contra as saídas, afirmações sem teste, setup que não funcionaria, caminhos pessoais, arquivos indevidos, inconsistências entre diário e scripts, e o que um Diretor não entenderia no sumário. Ele devolveu 27 achados em cerca de 5 minutos. A tabela abaixo diz o que fiz com cada um. Os achados que apontavam arquivos "ausentes no clone" eram efeito do momento: a revisão rodou antes do commit final, que leva README, exports, capturas e este arquivo.

| Achado do Codex | O que fiz | Onde |
|---|---|---|
| O script do LLM exige a chave antes de ler o cache; sem credencial, não roda mesmo com tudo cacheado | Corrigido: a chave só é carregada se houver chamada nova; testado sem a variável | `solution/05_llm_amostra.py` |
| README, chat-exports e revisão não estavam versionados | Timing: entram no commit final | commit final |
| "Saídas de todos os scripts" não valia para os scripts 00 e 06 | Gerei as duas saídas e ajustei a frase | `solution/00_teste_chave_gemini.txt`, `solution/06_triagem.txt` |
| Placeholders de tempo e data no README | Preenchidos no fechamento | `README.md` |
| "Treinado nos 48 mil tickets" não descreve a execução: 47.837 → 42.882 após dedup → 34.305 no treino | Reescrito no sumário: "34 mil, depois de remover repetições" | `README.md`, sumário |
| "27 horas" apresentado como limite exato; a amplitude é 27 h 02 min em 3 dias | Corrigido na tabela da auditoria e "cerca de" no sumário | `README.md` |
| p < 10⁻⁹ do McNemar vale para o zero-shot; com exemplos é 1,9 × 10⁻⁷ | Os dois valores agora aparecem | `README.md`, protótipo |
| Queda de 1,8 ponto atribuída a "vazamento" sem isolar a causa | Reescrito: diferença compatível com vazamento, mas a dedup também muda o conjunto | `README.md`, protótipo |
| Limiar 0,70 escolhido e medido no mesmo conjunto de teste; viés de seleção | Procede. Declarado no texto e em Limitações; o número que vale é o do piloto. Não refiz com conjunto de validação por tempo | `README.md` |
| "47.837 tickets reais" sem prova de procedência | Reescrito: tickets de uma organização, conforme a documentação do dataset público | `README.md` |
| Custo combina 30 mil tickets de uma operação multicanal com composição de um dataset de TI | Procede. Declarado em Limitações como a única composição real disponível, sem teste de representatividade | `README.md`, Limitações |
| "Recall de 0,61 é teto do rótulo" exigiria reanotação | Reescrito: subestima o modelo; quanto, só a reanotação diz, e ela é a primeira ação do piloto. No diário mantive a frase original, porque foi o que pensei na hora | `README.md` |
| "O arquivo é gerado" é mais forte do que as anomalias provam | Reescrito como assinatura de dado gerado, não prova de origem | `README.md` |
| README promete seis grupos na regra de conteúdo, o código implementa cinco | Procede. Explicado por que "custo com aprovação" ficou fora: "approval" é o termo de maior peso de Miscellaneous. Declarado que as regras não foram avaliadas em cobertura nem falsos positivos | `README.md`, fluxo |
| "Não contratar LLM" generaliza além do experimento | Reescrito para o escopo medido: este modelo, esta triagem | `README.md`, recomendação 4 |
| "15 minutos por dia" sem fonte | Marcado como premissa; o piloto registra o tempo real | `docs/piloto.md` |
| Piloto não diz como selecionar Access antes de classificar, nem unidade de sorteio nem tamanho | Acrescentado: o classificador roda em tudo, o piloto vale para o que ele aponta como acesso, sorteio ticket a ticket, cerca de 185 por metade, efeito mínimo a calcular na primeira semana | `docs/piloto.md` |
| "O sistema guarda nada mais" afirma sobre o sistema o que só sei da extração | Reescrito: a extração que recebi | `docs/piloto.md` |
| README diz "antes de abrir qualquer arquivo" e o diário declara uma preparação anterior | Reescrito: "nesta rodada", com referência à entrada de preparação | `README.md`, abordagem |
| Diário diz que todas as datas caem em 2023-06-01; a saída mostra três dias | Mantido: é a entrada da primeira olhada, em cinco linhas sorteadas; a auditoria, na entrada seguinte, corrigiu para 27 h em 3 dias | `process-log/diario.md` |
| Diário diz que o fluxo ganhou trava de fora de domínio; o protótipo não implementa | Mantido no diário como decisão da hora; o README declara em Limitações que não foi implementada | `README.md`, Limitações |
| Diário diz que o piloto mede reversão em Hardware; o plano é só em Access | Mantido: a decisão posterior, ao escrever o piloto, prevaleceu; Hardware fica como métrica quando a expansão chegar lá | `docs/piloto.md` |
| Saída do script 06 não versionada | Gerada | `solution/06_triagem.txt` |
| `triagem_lote.csv` sem origem documentada | Removido do repositório | commit final |
| Sumário com jargão (FTE, LLM, "decide 60%") e "pessoa por ano" lido como corte de quadro | Sumário reescrito: capacidade liberada, não redução; 96% só sobre o que a máquina aceita; limitação principal na primeira frase | `README.md`, sumário |
| Sem baseline operacional nem responsável pela instrumentação | Parcial: o piloto nomeia os campos e o critério; responsável e baseline dependem da operação e ficam como pergunta | `docs/piloto.md` |
| `.venv` contém caminhos absolutos | Informativo: ignorada pelo git, não vai no clone | `.gitignore` |

Os três pontos mais fracos que ele apontou (clone incompleto, validação insuficiente do limiar e do custo, controles prometidos e não implementados) estão, nesta ordem, resolvido pelo commit final, declarado em Limitações, e declarado em Limitações com a parte implementada descrita corretamente.
