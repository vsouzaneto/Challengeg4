# DealPilot — AI Lead Scorer

Solução desenvolvida para o **AI Master Challenge — Challenge 003: Lead Scorer**.

O DealPilot transforma um pipeline comercial de 8.800 oportunidades em uma fila priorizada para vendedores, usando dados 
históricos e regras explicáveis.

## Problema

A priorização atual das oportunidades é feita principalmente por percepção do vendedor. Com milhares de oportunidades no CRM, 
isso dificulta identificar rapidamente quais negócios merecem atenção.

O objetivo foi criar uma ferramenta funcional que responda:

> **"Quais oportunidades devo priorizar agora e por quê?"**

## Solução

O DealPilot analisa as oportunidades abertas e calcula um **Priority Score de 0 a 100**.

O score considera:

* etapa atual da oportunidade;
* tempo no estágio Engaging;
* histórico de win rate do produto;
* porte da conta;
* disponibilidade dos dados da conta.

O score representa **prioridade comercial**, e não probabilidade de fechamento.

Além do score, cada oportunidade recebe uma explicação com os fatores que contribuíram para sua pontuação e possíveis alertas de 
risco.

## Interface

O dashboard permite:

* visualizar o pipeline aberto;
* filtrar por vendedor;
* filtrar por gerente;
* filtrar por região;
* filtrar por etapa;
* visualizar as oportunidades prioritárias;
* consultar o motivo do score;
* identificar possíveis oportunidades envelhecidas no pipeline.

## Dados

Foram utilizados os arquivos do dataset CRM Sales Predictive Analytics:

* `sales_pipeline.csv`
* `accounts.csv`
* `sales_teams.csv`
* `products.csv`

O dataset possui aproximadamente 8.800 oportunidades históricas.

Na análise inicial foram identificadas:

* 4.238 oportunidades Won;
* 2.473 oportunidades Lost;
* 1.589 oportunidades Engaging;
* 500 oportunidades Prospecting.

O pipeline aberto utilizado pelo DealPilot contém **2.089 oportunidades**.

## Scoring

O modelo utiliza regras determinísticas e explicáveis.

### Etapa

* Engaging: até 35 pontos
* Prospecting: até 15 pontos

### Tempo em Engaging

O tempo no estágio é utilizado como sinal de atenção operacional:

* até 30 dias: +5
* 31–90 dias: +10
* 91–180 dias: +17
* 181–270 dias: +21
* acima de 270 dias: +25

Oportunidades muito antigas também recebem um alerta de possível estagnação.

### Produto

O histórico de oportunidades fechadas é utilizado para calcular o win rate por produto.

O sinal contribui com até 15 pontos.

### Conta

A receita anual da conta é utilizada como indicador de porte:

* receita ≥ 3.000: +15
* receita ≥ 1.000: +10
* abaixo de 1.000: +5

### Qualidade dos dados

O vínculo da oportunidade com uma conta adiciona até 10 pontos.

Quando informações importantes estão ausentes, o sistema sinaliza o problema em vez de simplesmente assumir um valor.

## Por que não usar Machine Learning?

A solução prioriza explicabilidade e utilidade operacional.

O dataset apresenta sinais relativamente próximos entre produtos e regiões, enquanto estágio e tempo no pipeline fornecem sinais 
mais diretamente acionáveis para o vendedor.

Por isso, uma abordagem baseada em regras foi escolhida para o primeiro protótipo. Ela permite que o usuário entenda 
imediatamente por que uma oportunidade recebeu determinada prioridade e facilita manutenção e ajuste das regras.

## Uso de IA

A solução foi desenvolvida com apoio de ferramentas de IA.

A IA foi utilizada para:

1. estruturar o problema;
2. sugerir hipóteses de features;
3. auxiliar na exploração dos dados;
4. propor uma primeira abordagem de scoring;
5. revisar problemas encontrados durante os testes;
6. gerar e revisar partes da implementação;
7. apoiar a documentação.

As sugestões geradas pela IA foram testadas contra os dados reais do dataset.

Durante a implementação, o primeiro modelo de scoring apresentou excesso de oportunidades empatadas no score máximo. Esse 
resultado foi analisado e utilizado para revisar a lógica de pontuação, especialmente o tratamento do tempo no pipeline.

O processo completo está documentado em `process-log/`.

## Limitações

O Priority Score não representa probabilidade estatística de fechamento.

Também existem oportunidades com dados incompletos, especialmente informações de conta e datas.

O modelo atual é baseado em regras e não foi treinado para prever conversão futura.

Uma evolução possível seria validar o score contra resultados futuros e comparar a abordagem com modelos supervisionados.

## Como executar

Instale as dependências:

```bash
python3 -m pip install -r requirements.txt
```

Execute o dashboard:

```bash
python3 -m streamlit run app.py
```

O aplicativo será disponibilizado localmente pelo Streamlit.

## Estrutura

```text
ai-master-challenge/
│
├── app.py
├── README.md
├── requirements.txt
├── solution/
│   └── scoring.py
├── data/
│   ├── README.md
│   ├── accounts.csv
│   ├── products.csv
│   ├── sales_pipeline.csv
│   └── sales_teams.csv
├── tests/
└── process-log/
```

## Autor

**Gabriel Arolde Manica**

AI / Python Developer

