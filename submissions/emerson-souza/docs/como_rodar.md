# Como rodar o G4 Analise

O sistema é um programa em janela própria: Python + Streamlit dentro de uma janela `pywebview`. Foi testado no Windows e no Linux, com **Python 3.11 a 3.14**. No Mac, as dependências têm versão para o sistema, mas ele não foi testado.

## 1. Rodar (um comando)

```bash
cd solution/g4_analise
python iniciar.py
```

No Windows, basta dar dois cliques em `solution/g4_analise/ABRIR_G4_ANALISE.bat`.

O `iniciar.py` só usa a biblioteca padrão do Python. Na primeira vez ele:

1. confere a versão do Python (3.11–3.14) e explica o que fazer se não for compatível;
2. cria um ambiente isolado `.venv` dentro da pasta, sem precisar de administrador e sem mexer no Python do computador;
3. instala as dependências de `requirements.txt` (versões fixas; leva alguns minutos, conforme a internet);
4. abre a janela.

A partir da segunda vez, ele abre direto.

Se você tem mais de um Python instalado, escolha a versão assim: `py -3.12 iniciar.py` (Windows) ou `python3.12 iniciar.py` (Mac/Linux).

## 2. Dados

| Desafio | Onde colocar | Arquivos | Download |
|---|---|---|---|
| 001 Churn | `solution/dados/001-churn/` | já incluídos (RavenStack, licença MIT, crédito a River @ Rivalytics) | [Kaggle](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset) |
| 002 Suporte | `solution/dados/002-suporte/` | `customer_support_tickets.csv` (obrigatório) e `all_tickets_processed_improved_v3.csv` (treino do classificador) | [DS1](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) · [DS2](https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset) |
| 003 Leads | `solution/dados/003-lead-scorer/` | `sales_pipeline.csv`, `sales_teams.csv`, `products.csv`, `accounts.csv` | [Kaggle](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) |
| 004 Mídia | `solution/dados/004-social/` | `social_media_dataset.csv` | [Kaggle](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset) |

Só o 001 vai no repositório. Os outros somam cerca de 42 MB e têm licença própria no Kaggle. Para eles, baixe o `.zip`, extraia e deixe os `.csv` com esses nomes na pasta indicada.

Você também pode rodar qualquer ferramenta com **arquivos próprios** (CSV ou Excel): em **Nova sessão → Enviar meus arquivos**, o sistema sugere o De/Para das colunas e você confere.

Para usar outra pasta de dados, defina a variável `G4_DADOS=/caminho/da/pasta` antes de iniciar.

## 3. Primeiro uso

1. **Nova sessão** → escolha a ferramenta (Churn, Suporte, Leads ou Mídia) → **Usar os dados do desafio** → Criar sessão. A tela mostra quais arquivos foram encontrados e quais faltam.
2. A análise roda **uma vez** (de segundos a cerca de 30 s, conforme a base e o computador) e fica salva. Ao reabrir o sistema, ela aparece na hora.
3. Navegue pelas abas: resumo executivo, causa raiz ou achados, plano de ação, método, qualidade dos dados, relatório (PDF/Markdown) e "Como ler".
4. Na aba **Usar em outra ferramenta**, envie o resultado para outra ferramenta. Isso cria uma **sub-sessão** (modo cooperativo) com um selo que diz o quanto a ligação entre as bases é forte.
5. Na aba **Exportar**, salve os dados analisados em CSV ou tudo junto em Excel. Os arquivos vão para `Downloads/G4 Analise`, e a tela mostra o caminho.

## 4. Testes

```bash
cd solution/g4_analise
.venv/bin/python -m pip install -r requirements-dev.txt     # Windows: .venv\Scripts\python
.venv/bin/python -m pytest -q
```

São 69 testes: núcleo, as 4 ferramentas, os cruzamentos, a exportação e o servidor do agente. Os testes das ferramentas usam os dados do desafio (pasta `solution/dados`). Se só o 001 estiver presente, passam os testes do núcleo e do Churn e os demais aparecem como *skipped*, com o arquivo que falta.

## 5. Opcional: usar pelo agente do G4 OS

`python iniciar.py --g4os` (ou `INSTALAR_NO_G4OS.bat`) cadastra o G4 Analise no G4 OS como fonte MCP local, junto com uma skill. Depois disso, o agente responde perguntas como "quais contas eu salvo esta semana?" usando o mesmo motor e as mesmas sessões da janela. Veja o exemplo real em `process-log/chat-exports/g4os-agente-usando-g4-analise.md`.
