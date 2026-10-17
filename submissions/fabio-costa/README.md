# Submissão — Fabio Costa — Challenge 002

## Demonstração online — login obrigatório

**[ACESSAR O PROTÓTIPO AI MASTER](https://aimaster.yeff.com.br/)**

**IMPORTANTE:** para visualizar e avaliar o protótipo operacional, é necessário fazer login.

- **Acesso automático:** clique em **Access Demo** ou **Acessar demonstração** na tela de login.
- **Acesso manual:** usuário `admin` / senha `aimaster123`.
- **Cadastro:** não é necessário.

Após a autenticação, o avaliador terá acesso à aplicação do challenge.

## Sobre mim

- **Nome:** Fabio Costa
- **LinkedIn:** https://www.linkedin.com/in/fabioycosta/
- **Challenge:** 002 — Redesign de Suporte
- **Demonstração:** https://aimaster.yeff.com.br/
- **Acesso de avaliação:** clique em **Access Demo** (ou **Acessar demonstração**, em português). Para acesso manual, use usuário `admin` e senha `aimaster123`.

## Executive Summary

Desenvolvi o **AI Master — Support Operations Intelligence**, uma aplicação que reúne diagnóstico de atendimento, análises operacionais, proposta de automação seletiva com IA e um protótipo funcional para operadores de suporte. No Dataset 1, foram examinados 8.469 tickets, dos quais 5.700 (67,30%) permaneciam Open ou Pending Customer Response no snapshot. O Dataset 2, independente, forneceu 47.837 textos rotulados para avaliação de classificação supervisionada; o LinearSVC alcançou 86,43% de Macro-F1 no teste desse corpus. A solução prioriza primeiro a capacidade operacional do atendente, incorporando NLP, LLM/RAG e regras determinísticas onde apresentam utilidade, com autorização humana para decisões sensíveis.

## Solução

A aplicação apresenta os quatro entregáveis do desafio e uma camada transversal de Data Quality & Audit.

### Abordagem

O trabalho começou com a auditoria dos datasets e a verificação das limitações de seus campos. O Dataset 1 foi utilizado no diagnóstico operacional; o Dataset 2, por não possuir chave comum com o primeiro, foi reservado ao treinamento e à avaliação do classificador.

O diagnóstico examina status, canais, prioridades, tipos, satisfação, produtos, assuntos, cobertura temporal e combinações operacionais. As métricas são diferenciadas entre **observadas**, **derivadas** e **estimadas**.

A proposta de automação foi construída sobre um fluxo operacional completo: entrada do ticket, primeiro contato, classificação, decisão de roteamento, execução, acompanhamento e revisão humana. O protótipo inclui workspaces de atendimento, consulta ao histórico, priorização, acompanhamento e mecanismos de apoio ao operador.

### Resultados / Findings

**Dataset 1 — Diagnóstico operacional**

| Indicador | Resultado |
|---|---:|
| Tickets observados | 8.469 |
| Open | 2.819 |
| Pending Customer Response | 2.881 |
| Open + Pending | 5.700 (67,30%) |
| Closed | 2.769 |
| Refund requests | 1.752 |
| Cancellation requests | 1.695 |

Os aproximadamente 30 mil tickets anuais mencionados no briefing representam a escala contextual da operação, não o tamanho do CSV fornecido.

O diagnóstico identifica gargalos por volume e taxa de não encerramento, avaliando canal, prioridade e tipo. Na amostra com CSAT, os testes realizados não encontraram associação estatisticamente significativa a 5% para essas três dimensões isoladas. Produto e assunto são explorados como sinais descritivos, sem alegações causais.

**Dataset 2 — Classificação supervisionada**

- Corpus: 47.837 documentos, oito categorias.
- Modelo selecionado: LinearSVC.
- Resultado: **86,43% de Macro-F1 no conjunto de teste do Dataset 2**.
- Transferência para o domínio do Dataset 1: não validada.

**Protótipo**

Interface operacional com histórico, workspaces por canal, tickets, suporte à priorização, primeiro contato, follow-up, orientação ao operador, análises e arquitetura de automação. Funcionalidades dependentes de serviços externos ou eventos ainda inexistentes são identificadas como propostas ou integrações pendentes.

**Arquitetura e ROI projetado**

Foram modeladas duas alternativas com o mesmo volume planejado de 2.500 tickets/mês e hipótese de três minutos de capacidade operacional poupada por ticket.

| Cenário | Custo recorrente estimado/mês | Break-even | ROI projetado |
|---|---:|---:|---:|
| A — External API LLM | US$ 684,67 | 0,82 min/ticket | **265,14%** |
| B — Private Open-weight, CPU-first | US$ 776,67 | 0,93 min/ticket | **221,89%** |

Os percentuais representam **retorno estimado sobre capacidade equivalente**, nas premissas exibidas no Architecture Map. Não representam economia financeira realizada. Custos únicos de implantação, desempenho em produção e economia efetiva ainda precisam ser validados.

### Recomendações

1. Registrar eventos reais de criação, primeiro contato, atendimento, follow-up, resolução e encerramento para permitir medição confiável de SLAs.
2. Priorizar os fluxos de primeiro contato e acompanhamento de clientes, usando filas e regras de escalonamento.
3. Validar o classificador no domínio operacional antes do uso automático de suas previsões.
4. Utilizar NLP local para classificação e LLM/RAG seletivo para contexto, conhecimento e respostas sugeridas.
5. Exigir autorização humana para reembolsos, cancelamentos, negociações, casos técnicos sensíveis e previsões incertas.
6. Comparar as duas arquiteturas em piloto com qualidade, latência, custos completos, esforço humano e retorno efetivamente medidos.

### Limitações

O Dataset 1 não possui timestamp histórico de abertura do ticket. Os campos temporais existentes exigem tratamento cuidadoso e não permitem reconstruir integralmente SLAs históricos. A redução estimada de horas decorridas não equivale automaticamente à redução de trabalho humano.

Os datasets são independentes, sem join relacional confiável. O resultado de classificação no Dataset 2 não demonstra eficácia operacional no Dataset 1.

O ROI apresentado é estimado por cenário. Taxas reais de automação, esforço humano, despesas finais, implantação e benefícios financeiros precisam ser medidos em operação.

## Execução local

Dentro de `solution/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir `http://127.0.0.1:5000`. A demonstração hospedada oferece autenticação automática por meio do botão **Access Demo**, sem necessidade de cadastro.

Antes da execução, obter os CSVs originais e colocá-los em `solution/data/raw/`:

- [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) — `customer_support_tickets.csv`
- [IT Service Ticket Classification Dataset](https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset) — `all_tickets_processed_improved_v3.csv`

Os CSVs não são redistribuídos dentro da submissão.

Para validar:

```bash
python -m pytest -q tests/
```

**Baseline de engenharia:** instalação limpa concluída e 21 testes aprovados.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Finalidade |
|---|---|
| ChatGPT | Decomposição do challenge, hipóteses, análise, programação, propostas de arquitetura, revisão técnica, depuração e elaboração de testes |

### Workflow

O desenvolvimento partiu da auditoria dos dados e da identificação de restrições analíticas. A solução evoluiu de uma proposta centrada em automação para um produto operacional completo, com assistência seletiva de IA.

Foram documentadas decisões de produto, validações analíticas, correções de código, procedimentos de publicação e testes.

### Onde a IA errou e como corrigi

Os episódios documentados incluem erro na estratégia de download dos datasets, expressão booleana que gerou contagem negativa de tickets não encerrados e alterações de código que exigiram correção e validação de entrega.

### O que eu adicionei que a IA sozinha não faria

Defini a prioridade de um workspace operacional completo, rejeitei automação indiscriminada, preservei os limites evidenciais dos datasets e estabeleci regras de governança com owners canônicos, `EXACT_REPLACE`, SHA256, backup, validação e rollback.

A cronologia e as decisões estão em [Process Log](process-log/decisions.md), complementadas pelas evidências visuais E01–E06 na demonstração da aplicação.

## Evidências

- [Process Log — decisões documentadas](process-log/decisions.md)
- [Evidências visuais do Process Log](process-log/evidence.md)
- [Código-fonte e README técnico](solution/README.md)
- [Testes](solution/tests/)
- [Aplicação demonstrativa](https://aimaster.yeff.com.br/)
- Relatórios operacionais, treinamento, protótipo e os dois cenários de ROI disponíveis na aplicação.

---

**Data de submissão:** a preencher quando o Pull Request for aberto.
