# Submissão — Fernando William — Challenge 002

## Sobre mim

- **Nome:** Fernando William Santos
- **LinkedIn:** linkedin.com/in/fernandowilliam
- **Challenge escolhido:** 002 — Redesign de Suporte

---

## Executive Summary

A pergunta "onde perdemos tempo" não tem resposta na extração que recebi: as datas de resposta e resolução estão todas dentro de cerca de 27 horas e metade das resoluções vem antes da primeira resposta, o que indica arquivo gerado ou extração errada; o primeiro passo é conferir com quem gerou o arquivo. O que dá para responder, e provei rodando, é quanto da triagem (ler, classificar e encaminhar), que hoje é 100% manual, uma máquina faz com segurança: um classificador treinado em 34 mil tickets de suporte de TI de outra organização, o único dado rotulado disponível, decide sozinho 6 em cada 10 tickets e acerta 96 de cada 100 desses; os outros 4 em 10 continuam com uma pessoa. Isso libera o equivalente a 0,45 a 1,29 pessoa por ano, ou R$ 20 mil a R$ 114 mil, a depender do custo por hora, que é a premissa mais frágil; é capacidade liberada para atendimento, não corte, e ainda não foi validada na nossa operação. Medi o modelo de linguagem que se esperaria usar aqui e ele perdeu para o classificador simples em todos os cortes, então ficou de fora. Peço um piloto de 30 dias na categoria de acesso a sistemas, que custa 15 minutos por dia de uma pessoa revisando e exige três campos novos no sistema de tickets (hora de abertura, trocas de fila, espera pelo cliente), a cargo de quem administra o sistema; sem esses campos, a pergunta sobre tempo perdido continua sem resposta com ou sem automação.

---

## Solução

### Abordagem

Antes de abrir qualquer arquivo nesta rodada escrevi o que esperava encontrar, com número (`process-log/diario.md`, primeira entrada); eu já tinha visto os dados numa preparação anterior, declarada no topo do diário, e descartei tudo dela. Depois auditei os dois datasets com 18 testes antes de qualquer análise, porque o enunciado descreve 30 mil tickets e o arquivo tem 8.469. A sequência foi: auditoria, diagnóstico com o que sobreviveu, fronteira entre máquina e pessoa lida em tickets reais, protótipo medido em dados de teste, piloto com regra de decisão.

Usei IA em duas camadas com requisitos opostos. Na autoria, um agente de código escreveu os scripts a partir dos meus pedidos, e o que importa é a rastreabilidade das decisões, registrada no diário. No produto, o modelo que roda dentro do protótipo, e o que importa é custo, acurácia e comportamento quando não sabe. O protótipo roda ponta a ponta sem chave de API.

### Resultados / Findings

#### O arquivo de métricas não serve para medir tempo

O gargalo por canal, prioridade e tipo foi calculado (item 5 de `solution/01_auditoria_dados.txt`): as medianas são indistinguíveis entre canais, prioridades e tipos, e em dois cortes a mediana é negativa, porque os tempos são sorteio. Os testes que provam isso estão no mesmo arquivo.

| Teste | Resultado |
|---|---|
| Linhas | 8.469, contra ~30.000 no enunciado |
| Amplitude das datas de resposta e resolução | 27 h 02 min, em 3 dias de 2023, para compras de 2020 e 2021 |
| Resolução antes da primeira resposta | 49,3% dos tickets fechados |
| Nota de satisfação | uniforme (χ² p = 0,80); sem relação com canal, prioridade, tipo ou tempo (ANOVA p > 0,27; r = 0,02) |
| Descrição do ticket prevê o tipo? | 19,8%, contra 20,7% chutando a classe majoritária |
| Categóricas | todas uniformes (Bonferroni p ≥ 0,157); e-mails 100% em example.com/org/net |

Tempos, nota e os dois campos de texto ficaram fora do diagnóstico. O que sobrevive é o volume como referência.

#### O que os dados respondem

O segundo arquivo tem 47.837 tickets de suporte de TI de uma organização, rotulados em 8 categorias, conforme a documentação do dataset público, com Hardware em 28%, HR Support em 23% e Access em 15%. Um modelo de custo parametrizado (`solution/02_modelo_custo.py`, 8 premissas nomeadas com a fonte ao lado) estima a triagem manual de 30 mil tickets em 1.500 a 4.000 horas por ano. Com a triagem automática decidindo 60% dos tickets a 96% de acerto, a economia líquida fica entre 784 e 2.276 horas por ano, ou 0,45 a 1,29 FTE. O valor em reais depende do custo por hora, que é premissa, e por isso aparece uma linha só por cenário no arquivo de saída.

#### Onde a pessoa é insubstituível, lido nos tickets

Sorteei 90 tickets de HR Support, Administrative rights e Access e li os 40 erros do modelo nas duas primeiras (`solution/03_leitura_fronteira.txt`). Três casos que a máquina classifica bem e mesmo assim não pode decidir: a linha 42710, uma auditoria interna que descobriu contas de desligados reativadas e pede desligamento imediato e investigação; a linha 15296, um formulário de licença-maternidade; a linha 30478, um aprovador de férias que saiu da empresa e deixou pedidos pendentes. A regra de escalonamento saiu dessa leitura e vale acima de qualquer confiança do modelo: pessoa entrando ou saindo, conta e privilégio, auditoria e incidente, segurança física, urgência marcada, custo com aprovação.

A leitura revelou um problema no dado de treino: boa parte dos erros em Administrative rights (impressora, som de TV, Safari, portas de emergência) tem rótulo errado na origem. O recall de 0,61 dessa classe subestima o modelo; quanto, só uma reanotação independente diz, e ela é a primeira ação do piloto. A deduplicação confirmou: 201 grupos de tickets quase idênticos têm rótulos diferentes.

#### Protótipo

`solution/04_classificador.py` deduplica por similaridade antes do split (4.955 linhas, 10,4%, saíram; sem isso a acurácia é 1,8 ponto maior, diferença compatível com vazamento de quase-duplicatas entre treino e teste, embora a dedup também mude o tamanho e a dificuldade do conjunto), treina TF-IDF com regressão logística e mede a abstenção. Acurácia global de 84,0% no teste de 8.577 tickets, macro-F1 0,83. Com limiar de confiança 0,70:

| Limiar | Máquina decide | Acerto nos decididos | Vai para pessoa |
|---|---|---|---|
| 0,65 | 64,6% | 95,4% | 35,4% |
| 0,70 | 59,7% | 96,3% | 40,3% |
| 0,80 | 48,7% | 97,8% | 51,3% |

Escolhi 0,70 porque cruza 95% com folga e ainda cobre 60%. A curva foi medida no próprio conjunto de teste, então os 96,3% carregam viés de seleção do limiar; o número que vale é o que o piloto medir. Administrative rights fica com 76% de acerto mesmo entre os decididos, e é por isso que a regra de conteúdo vale acima da confiança. Esse é o cruzamento entre os dois arquivos: o modelo treinado no segundo aplicado ao texto do primeiro. Rodei o modelo sobre as 8.469 descrições sem sentido do primeiro arquivo: 78% ficam abaixo do limiar, mas 7.645 delas caem em Hardware, 22% com confiança alta. Hardware é o ralo do modelo para texto que não fala de nada, e o piloto mede isso.

Testei o protótipo como um usuário faria (`solution/07_avaliacao_prototipo.py`): mil tickets do teste sorteados com outra semente e seis tickets escritos à mão. Nos mil, 48,5% foram para pessoa (13,5 pontos pela regra de conteúdo, 35 pela confiança) e a máquina acertou 95,7% dos 515 que decidiu, o mesmo patamar da curva do script 04 num sorteio diferente. Dos seis à mão, cinco caíram no caminho esperado; o sexto, um reset de senha do sistema de ponto, foi para pessoa por confiança baixa porque "timecard" é vocabulário de HR Support nesta operação. A regra de urgência é a que mais manda para pessoa, 80 dos 135 disparos, e leva junto tickets que o modelo classificaria bem; é a primeira regra a rever no piloto.

#### O LLM medido, e retirado

Classifiquei 320 tickets do conjunto de teste (40 por classe) com o gemini-3.1-flash-lite, o modelo mais barato disponível na conta em 16/09/2026, por REST, com cache de todas as respostas em `solution/cache/` (`solution/05_llm_amostra.py`).

| Opção | Acurácia balanceada | Ponderada pela demanda | Custo por mil tickets |
|---|---|---|---|
| TF-IDF, decide 100% | 75,6% | 78,7% | R$ 0 |
| LLM zero-shot, 100% | 55,0% | 46,8% | R$ 0,32 |
| LLM com 3 exemplos por classe, 100% | 58,8% | 45,5% | R$ 2,06 |
| TF-IDF decide, LLM só onde abstém | 67,8% | 62,5% | R$ 0,15 |
| Pessoa, 5 min a R$ 35/h | não medida | não medida | R$ 2.917 |

McNemar entre LLM e TF-IDF nos mesmos tickets: p < 10⁻⁹ no zero-shot e p < 10⁻⁷ com exemplos. Na zona em que o modelo barato abstém, o LLM acerta 39% (43% com exemplos), pior do que o modelo barato forçado a decidir, 56%. A taxonomia é da casa (Hardware inclui sala de reunião, Storage é pasta compartilhada) e o LLM não a aprende com 3 exemplos. O LLM custa quase nada e mesmo assim não vale: a segunda camada é uma pessoa.

#### Fluxo proposto

O ticket entra e passa pela regra de conteúdo; se bater em um dos cinco grupos implementados (pessoa entrando ou saindo, conta e privilégio, auditoria e incidente, segurança física, urgência marcada), vai direto para fila humana com a categoria sugerida. O sexto grupo da fronteira, custo com aprovação, ficou fora da regra por termo: "approval" é o termo de maior peso de Miscellaneous e mandaria a categoria inteira para pessoa; fica para o piloto decidir por valor. As regras de conteúdo não foram avaliadas em cobertura nem falsos positivos. Se não, o classificador dá categoria e confiança; acima de 0,70 segue para a fila da categoria, abaixo vai para fila humana com a sugestão. Toda reversão da pessoa vira rótulo novo, e isso tem preço medido: a curva de aprendizado (`solution/08_curva_aprendizado.py`) mostra o modelo perto do teto no geral (F1 médio sobe 0,8 ponto entre 80% e 100% do treino) e Administrative rights ainda subindo, a cerca de 162 exemplos novos por ponto de recall, o que a operação inteira geraria em 7 a 8 semanas se toda reversão virasse rótulo; é piso, porque exemplo sorteado vale menos do que correção de erro. `solution/06_triagem.py` implementa o fluxo: recebe um texto e devolve categoria, confiança, destino e qual regra decidiu.

#### Piloto

`docs/piloto.md`, uma página: 30 dias em Access, metade sorteada com triagem automática e metade como hoje, três registros novos (hora de abertura, trocas de fila, espera pelo cliente) e regra de decisão fixada antes: expandir abaixo de 5% de reversão humana, manter entre 5% e 10%, desligar acima de 10% ou se a espera não cair.

### Recomendações

1. Registrar hora de abertura, cada troca de fila e tempo esperando o cliente. Sem isso, "onde perdemos tempo" não tem resposta com nenhuma automação.
2. Rodar o piloto de 30 dias em Access com a regra de decisão de `docs/piloto.md`.
3. Reclassificar Administrative rights antes de qualquer modelo maior; o dado de treino está errado na origem.
4. Não usar este LLM nesta triagem: um modelo, dois prompts, 320 tickets e uma taxonomia sustentam retirá-lo desta arquitetura, não uma regra geral. Reavaliar se o piloto mostrar erro concentrado em texto longo.

### Limitações

O primeiro dataset não sustenta nenhuma conclusão sobre tempo ou satisfação, e por isso o diagnóstico de gargalo não existe aqui; existe o caminho para medi-lo. As anomalias são assinatura de dado gerado, não prova de origem. O modelo de custo aplica a composição de um dataset de suporte de TI ao volume de uma operação multicanal de consumo; é a única composição real disponível, e não há teste de que represente a operação descrita. O modelo de custo depende de 8 premissas, listadas no topo do script; as mais frágeis são minutos por triagem e custo por hora. A medição do LLM usa 320 tickets, com intervalo de confiança em torno de ±5 pontos pela binomial; é estimativa amostral. O gemini-3.1-flash-lite tem desligamento anunciado para maio de 2027, e o substituto custa mais. Hardware absorve texto fora de domínio com confiança; o protótipo só tem palavras-chave e confiança, a trava de fora de domínio não foi implementada e fica como métrica do piloto. O limiar de abstenção foi escolhido e medido no mesmo conjunto de teste; faltou um conjunto de validação separado. A estimativa de correções por semana vem de uma curva de aprendizado com exemplos sorteados, não de correções reais; vale como piso. A acurácia da pessoa não foi medida, e os 201 grupos com rótulo inconsistente sugerem que ela não é 100%. Ficaram fora por decisão: dashboard, fine-tuning, análise de sentimento e previsão de nota, os dois últimos porque os dados não sustentam.

Tempo de trabalho, somado a partir das horas do diário: cerca de 5 horas, da primeira entrada às 15:21 ao commit final por volta das 20:50 (horário de Brasília), mais a preparação anterior, não cronometrada e descartada.

---

## Process Log — Como usei IA

O diário completo, escrito durante o trabalho, está em `process-log/diario.md`. O transcript integral da sessão com o agente está em `process-log/chat-exports/`. Como auditar em três comandos: ler o diário, rodar `solution/01_auditoria_dados.py` e comparar a saída com `solution/01_auditoria_dados.txt`, rodar `solution/06_triagem.py` com um ticket qualquer.

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Claude Code (agente na pasta do trabalho) | escrever e rodar os scripts a partir dos meus pedidos; toda saída conferida por mim |
| Codex | revisão independente da submissão antes do PR; 27 achados, tratados em `process-log/revisao-independente.md`; scrollback da sessão em `process-log/capturas/` |
| Gemini 3.1 Flash-Lite (dentro do produto) | camada de classificação medida e descartada |

### Workflow

1. Escrevi hipóteses com número antes de abrir os arquivos.
2. Pedi ao agente uma olhada crua nos dois CSVs, sem análise, e anotei o que vi.
3. Pedi a auditoria com 18 testes e comparei cada aposta com o resultado.
4. Escrevi a hipótese do custo, pedi o modelo parametrizado e comparei.
5. Pedi 90 tickets sorteados e 40 erros do modelo, li todos e escolhi os que citaria.
6. Escrevi a hipótese do protótipo, pedi dedup, split, classificador e curva de abstenção; escolhi o limiar.
7. Pedi a medição do LLM em 320 tickets do teste, com cache e custo; pedi uma segunda rodada com exemplos; retirei o LLM.
8. Escrevi o piloto e a regra de decisão.
9. Pedi o protótipo ponta a ponta com a regra de conteúdo e testei com três tickets.
10. Pedi a revisão independente ao Codex, tratei os 27 achados, e fechei com o teste do protótipo como usuário e a curva de aprendizado.

Foram 16 iterações registradas no diário, entrada a entrada.

### Onde a IA errou e como corrigi

| O que aconteceu | Como percebi | O que mudou |
|---|---|---|
| O modelo mais barato retornou 404 e o agente pulou para o que a mensagem de erro sugeria, sem consultar preço | a tabela pública tinha um intermediário mais barato | testei o 3.1-flash-lite, que respondeu; custo por mil 17% menor na entrada e 40% menor na saída que o sugerido |
| A saída do classificador apresentava Administrative rights como "classe fraca do modelo" | li os 20 erros: impressora, som de TV, Safari, portas de emergência | o problema é rótulo na origem; entrou como primeira ação do piloto, antes de qualquer modelo maior |
| Minha própria hipótese de que o LLM venceria o modelo barato na cauda | medi: 39% contra 56% | o LLM saiu da arquitetura com o número que prova |

### O que eu adicionei que a IA sozinha não faria

Decidir que os tempos do primeiro arquivo não entram no diagnóstico, em vez de produzir a tabela de gargalo por canal que o enunciado pede e que o dado não sustenta. Ler os tickets e descobrir que a classe fraca tem rótulo errado na origem. Reconhecer que a taxonomia é da casa e que isso explica por que o LLM perde. Apresentar o resultado em horas e FTE e não em reais, porque custo por hora é a premissa mais frágil. A regra de escalonamento por conteúdo acima da confiança. A regra de decisão do piloto escrita antes de começar, e os três registros novos sem os quais a pergunta do Diretor continua sem resposta.

---

## Evidências

- [x] Diário de processo com hora, hipótese antes de cada teste e decisão: `process-log/diario.md`
- [x] Chat export integral da sessão com o agente: `process-log/chat-exports/`; scrollback do terminal em `process-log/capturas/`
- [x] Git history: um commit por bloco de trabalho, nesta branch
- [x] Saída de cada script ao lado do código: `solution/*.txt`
- [x] Cache de todas as chamadas ao LLM: `solution/cache/` (o cache guarda o hash do prompt; o texto do prompt está na função `montar_prompt` de `solution/05_llm_amostra.py`)
- [x] Teste do protótipo como usuário e curva de aprendizado: `solution/07_avaliacao_prototipo.txt`, `solution/08_curva_aprendizado.txt`
- [x] Revisão independente: `process-log/revisao-independente.md`

### Como reproduzir

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Python 3.12. Baixar os dois CSVs do Kaggle (Customer Support Ticket Dataset e IT Service Ticket Classification Dataset, ambos CC0) para `solution/data/`, com os nomes `customer_support_tickets.csv` e `all_tickets_processed_improved_v3.csv`. Depois, na ordem: `01_auditoria_dados.py`, `02_modelo_custo.py`, `03_leitura_fronteira.py`, `04_classificador.py --limiar 0.70`, `05_llm_amostra.py` e `05_llm_amostra.py --exemplos 3` (usam o cache; a chave só é necessária para chamadas novas), `06_triagem.py "texto do ticket"`, `07_avaliacao_prototipo.py`, `08_curva_aprendizado.py`.

---

_Submissão enviada em: 16 de setembro de 2026_
