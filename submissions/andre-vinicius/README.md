# Submissão — Andre Vinicius — Challenge 003

## Sobre mim

- **Nome:** Andre Vinicius
- **LinkedIn:** https://www.linkedin.com/in/andre-paulino-nascimento/
- **Challenge escolhido:** Build 003 — Lead Scorer

---

## Executive Summary

Construí o **Foco**, uma aplicação local que ajuda vendedores a decidir qual oportunidade trabalhar em seguida. Ela organiza 2.089 negócios abertos do conjunto fornecido pelo desafio em três filas, explica cada prioridade e sugere a próxima ação. Testei uma hipótese de pontuação baseada no histórico, mas sua AUC de 0,4854 não sustentou uma promessa preditiva; por isso entreguei uma regra operacional transparente. O próximo passo recomendado é testar o fluxo com vendedores e medir o tempo até a próxima ação em dados atuais.

---

## Solução

### Abordagem

Comecei pela pergunta da pessoa de vendas: “em qual oportunidade devo agir agora, e por quê?”. Dividi o trabalho em auditoria dos dados, regra de prioridade, interface, testes e documentação. Usei o **Demiurgo**, meu ambiente de desenvolvimento, para organizar tarefas com critérios de aceite, agentes, revisões e evidências. O Foco é independente: o avaliador pode executá-lo apenas com os arquivos desta submissão.

### Resultados / Findings

- Os quatro CSVs reúnem 8.800 oportunidades; 2.089 estavam abertas na referência histórica usada pelo protótipo.
- As filas **Avançar**, **Revisar** e **Qualificar** aparecem em três formas de leitura, com busca, filtros, razões e próxima ação por negócio.
- Uma hipótese de afinidade histórica por produto e setor foi avaliada com corte cronológico e rejeitada após AUC de **0,4854**. O índice entregue é uma heurística de atenção, não probabilidade de fechamento.
- A auditoria encontrou `GTXPro` no pipeline e `GTX Pro` no catálogo. A ligação foi normalizada. Oportunidades sem conta permanecem visíveis e indicam a necessidade de completar o cadastro.
- A aplicação foi verificada por auditoria, avaliação, 21 testes Python, 7 testes Node e acesso HTTP. Veja [a tela final do Foco](process-log/screenshots/foco-atual.png), [a documentação no produto](process-log/screenshots/construcao-atual.png) e [o Kanban do G4](process-log/screenshots/demiurgo-kanban-g4.png).

### Como executar

Requer **Python 3.10 ou superior**. Na pasta `solution/`, execute `python iniciar.py` — ou dê dois cliques em `iniciar-foco.cmd` no Windows. Na primeira execução, o comando baixa os CSVs públicos; depois funciona sem internet. Ele usa uma porta local livre, informa a URL e tenta abrir o navegador. Não há instalação de pacotes Python nem conta de serviço. Mais detalhes em [solution/README.md](solution/README.md).

### Recomendações

1. Experimentar a ordem e as próximas ações com vendedores e gerentes; medir tempo até ação e negócios parados.
2. Ajustar prazo e pesos com feedback real antes de integrar ao CRM.
3. Para uso compartilhado, acrescentar autenticação, permissões por carteira e persistência no servidor.

### Limitações

O dataset é fictício e histórico. Não contém sequência de atividades de venda suficiente para provar efeito da regra sobre conversão. O mapa de regiões é ilustrativo. Anotações e status ficam apenas no navegador local. Não houve piloto comercial ou medição de ganho de tempo. O índice não prevê fechamento.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usei |
| --- | --- |
| Demiurgo, desenvolvido por mim | Organizar objetivo, tarefas, agentes, critérios de aceite, revisão e evidências do case. |
| OpenAI Codex | Auditar dados, implementar aplicação, escrever testes e documentação. |
| Claude Code | Levantar os desafios, revisar painéis e redesign e apoiar a documentação. |
| Modelo local | Apoiar uma primeira frente de documentação, depois conferida contra o código. |
| Replit | Exploração visual de uma interface antes da implementação final. |

### Workflow

1. Li o desafio e escolhi o problema de decisão comercial. No Demiurgo, transformei esse objetivo em tarefas e critérios verificáveis.
2. Com apoio de IA, auditei o conjunto e testei uma hipótese histórica. Revisei a avaliação antes de decidir que a solução não deveria prometer previsão.
3. Construí e usei a primeira versão do Foco. Meu feedback pediu comparação mais rápida, filtros, visões alternativas e contexto por pessoa e região.
4. Testei dados, regras, interface e resposta HTTP; revisei o que a documentação afirma e preparei a execução em um comando.

### Onde a IA errou e como corrigi

A hipótese inicial de score parecia plausível, mas o teste cronológico não a sustentou. Rejeitei a interpretação preditiva e mantive uma regra operacional explicável. Também verificamos a grafia divergente de produto entre tabelas e preservamos oportunidades sem conta, para que o sistema não omitisse trabalho real da carteira. Na interface, precisei orientar a organização da informação depois de experimentar o primeiro protótipo.

### O que eu adicionei que a IA sozinha não faria

Defini o problema que valia resolver, os critérios para confiar na pontuação e a experiência que ajudaria a pessoa de vendas. Usei o Demiurgo para fazer agentes trabalharem com escopo, testes, revisão e documentação. Escolhi o que entraria no produto depois de examinar resultados e limitações, em vez de aceitar a primeira resposta gerada. O relato completo está em [solution/PROCESS_LOG.md](solution/PROCESS_LOG.md) e [como desenvolvi o Foco](solution/docs/case-development.md).

### Tempo e custo

O desafio propõe uma referência de 4 a 6 horas. Horas ativas e custo monetário por ferramenta não foram medidos de modo confiável. A divisão de horas em [como desenvolvi o Foco](solution/docs/case-development.md) é uma estimativa para um case semelhante, não uma medição deste trabalho. O histórico Git local de desenvolvimento não acompanha este PR; o registro escrito, os testes e as capturas documentam o processo sem expor arquivos internos de versões antigas.

---

## Evidências

- [x] [Captura do produto](process-log/screenshots/foco-atual.png)
- [x] [Captura da documentação e construção](process-log/screenshots/construcao-atual.png)
- [x] [Kanban do Demiurgo filtrado no G4](process-log/screenshots/demiurgo-kanban-g4.png)
- [x] Código, testes, auditoria e avaliação em `solution/`
- [x] [Process log completo](solution/PROCESS_LOG.md)

---

_Submissão preparada em: 14/10/2026._
