# Radar de Conteúdo: desenho

Especificação aprovada pelo candidato em 25/09/2026, parte por parte, antes de qualquer código. É a base do plano de implementação.

## Para que serve

O Head de Marketing e o time de social media abrem o Radar na segunda-feira e, em 5 minutos, sabem:
- o que o dado diz e o que não diz;
- quanto das práticas sem critério aconteceu na semana e quanto isso custa, sob uma premissa ajustável;
- se alguma diferença de desempenho virou sinal;
- de quantos posts e semanas precisa o próximo teste.

O app vale hoje para o arquivo do desafio. Amanhã, vale para o dado do [plano de rastreamento](plano_rastreamento.md), desde que ele seja convertido para as colunas do arquivo do desafio; esse conversor fica fora deste escopo.

**Critério de sucesso:** alguém não técnico abre o app, entende a tela de abertura sem ajuda, ajusta o custo por post, calcula o tamanho de um teste e sai com o brief da semana.

## Decisões tomadas

| Tema | Decisão |
|---|---|
| Ferramenta | Streamlit, com 4 páginas e navegação entre elas |
| Dados | Resumos pequenos gerados por script a partir do CSV. O CSV bruto nunca entra no repo |
| Telas | Brief de segunda (abertura), Saúde do dado, Mapa de sinal e ruído, Calculadora de teste |
| Visual | UX do g4business.com: cores, fontes, componentes e logo, aplicados por CSS no app |
| Rodapé | "Protótipo de candidato ao AI Master Challenge, sem vínculo oficial com o G4" |
| Top 3 e bottom 3 | Por grupo da semana (plataforma, formato ou categoria), não por post |
| Deploy | Streamlit Community Cloud, tratado como teste; se falhar, roda local |

## Parte 1: arquitetura e dados

```
solution/
├── gerar_resumos.py        roda local: lê o CSV e grava app/resumos/
├── src/resumos.py          monta cada resumo (testado)
├── src/brief.py            brief da semana a partir dos resumos (testado)
└── app/
    ├── radar.py            entrada: tema, cabeçalho, navegação, rodapé
    ├── tema.py             CSS do G4 e logo
    ├── leitura.py          lê os resumos com cache, a partir da pasta do app
    ├── paginas/            brief.py, saude.py, mapa.py, calculadora.py
    ├── resumos/            CSVs versionados
    ├── assets/logo_g4.svg  logo branco do site do G4 (download autorizado)
    └── requirements.txt    o Streamlit Cloud procura aqui antes da raiz
```

**Resumos:**

| Arquivo | Conteúdo |
|---|---|
| `laudo.csv` | `chave, valor`: índices de dispersão das quatro métricas, creators com seguidores variando, razão mediana, correlação seguidores x views, parcelas redondas, fit observado e esperado por sorteio, patrocinadores de um post só, posts em chinês, japonês ou hindi com escrita da língua |
| `simulacao.csv` | cópia de `resultados/validacao_metodo_resumo.csv` |
| `celulas.csv` | saída de `mapa_celulas` para os 4 objetivos (60 células x 4), com a coluna `objetivo` |
| `semanas.csv` | por semana: dias com post, data do último post, posts, patrocinados, sem fit, divulgação implícita, só hashtags, em parceria de um post só, com pelo menos um dos três problemas |
| `semanas_grupos.csv` | por semana e grupo (`dimensao`, `valor`): posts, média e variância do engajamento; mais uma linha `total` por semana |

**Definições:**
- A **semana** começa na segunda-feira.
- A semana padrão é a última completa do arquivo: a mais recente cujo domingo não passa da última data.
- **Parceria de um post só:** o patrocinador aparece num único post em todo o histórico.
- **Pelo menos um dos três problemas:** o post patrocinado está sem fit, com divulgação implícita ou em parceria de um post só (como na §3 do notebook).

**Regras de código:**
- Toda conta vem de `src/`. As páginas só leem e mostram.
- A comparação "grupo contra o resto" a partir de resumos sai de `celulas.py` para uma função reutilizável, usada pelo mapa de células e pelo brief.
- Os caminhos partem da pasta do arquivo, porque no Cloud o diretório de trabalho é a raiz do repo.

## Parte 2: telas

1. **Brief de segunda** (abertura)
   - Seletor de semana e controle de custo por post (US$ 500 a 5.000; padrão 1.500).
   - Indicadores da semana: posts e % patrocinados; entre os patrocinados da semana, % sem fit, % com divulgação implícita e % em parceria de um post só; e o gasto estimado nas práticas a parar (posts com pelo menos um dos três problemas vezes o custo).
   - **Top 3 e bottom 3:** os 12 grupos da semana, cada um comparado com o resto dos posts da mesma semana. Correção de Benjamini-Hochberg entre os 12, regra de sinal do laudo, ordenação pela diferença.
   - Uma frase-veredito: se nenhum virou sinal, "nenhum virou sinal: não mude o mix por causa disso"; se algum virou, o nome do grupo e a diferença.
   - **Esta semana:** os quatro quick wins da estratégia, como lista fixa.
2. **Saúde do dado**
   - Veredito: "Resultado: sem sinal. Operação: sem critério."
   - Quatro cartões, um por teste do laudo: a pergunta, o número e o que ele quer dizer.
   - A tabela da validação do método, com a leitura da fronteira de 10%.
3. **Mapa de sinal e ruído**
   - Objetivo (engajamento, alcance, conversa, compartilhamento) e filtros de plataforma, categoria e formato. Os filtros só escondem células: a classe vem do mapa completo, com a correção feita sobre as 60 células.
   - Gráfico com ponto e intervalo por célula, faixa de ±10% e dica ao passar o mouse.
   - Tabela com os mesmos dados e contagem por classe.
4. **Calculadora de teste**
   - Três perguntas: efeito mínimo (10%, 20%, 30% ou outro), variação da métrica (CV 0,5, 1, 2 ou outro) e posts por semana (padrão 214).
   - Resposta: posts por grupo e semanas para um teste de dois grupos, por `src/experimentos.py`.
   - Atalhos H1, H2 e H3, com hipótese, métricas e guardrail do `03_estrategia.md`.

## Parte 3: visual

- **Cabeçalho:** faixa azul #001F35, logo branco do G4 e título em Manrope fino, com a palavra de destaque em Libre Baskerville itálico dourado #B9915B (5,8:1 sobre o azul).
- **Corpo:** fundo off-white #F5F4F3 e texto azul #001F35. Cartões brancos com cantos de 10 px e linha fina dourada no topo. Botão principal dourado com texto azul (5,8:1); secundário só com contorno.
- **Dourado sobre fundo claro:** só a variante escurecida #8A6A3F (4,5:1). O dourado #B9915B dá 2,6:1 sobre o off-white.
- **Gráfico:** pontos e intervalos em azul, faixa de ±10% com fundo dourado claro, bordas e rótulos em #8A6A3F. Tabela gêmea logo abaixo.
- **Fontes:** Google Fonts (licença livre), carregadas pelo CSS.
- **Checagens:** números no formato brasileiro (`src/formato.py`) e tela de 375 px de largura sem rolagem lateral.

## Parte 4: testes, erros e deploy

- **Testes (pytest, antes do código):**
  - `src/resumos.py` e `src/brief.py`, com dados pequenos montados à mão.
  - A função de comparação a partir de resumos, conferida contra `comparar`.
  - Telas: cada página e a entrada rodam sem erro e mostram o texto-chave. A calculadora confere contra `src/experimentos.py`.
- **Erros:**
  - Resumos ausentes geram a mensagem "rode `python solution/gerar_resumos.py`".
  - Coluna ausente gera uma mensagem com o nome da coluna.
- **Rodar local:** da raiz do repo, `streamlit run submissions/guilherme-ferreira/solution/app/radar.py`.
- **Deploy:** o candidato cria o app em share.streamlit.io, com repo `Gchapolin/ai-master-challenge`, branch `submission/guilherme-ferreira`, arquivo `submissions/guilherme-ferreira/solution/app/radar.py` e Python 3.12. O `config.toml` do Streamlit não é usado, porque no Cloud ele teria de ficar na raiz do repo. No fechamento, o deploy não foi feito: o Radar roda local (README; DECISOES, seção E).
- **Prints:** ficam em `process-log/evidencias/screenshots/05-radar_NN_*.png`. No fechamento, a pedido do candidato, foram tirados pela IA com o Chrome sem janela.

## Fora do escopo

Login, upload de CSV, posts um a um, modo escuro, salvar a lista de tarefas, editar hipóteses no app.

## Fontes técnicas

- O Cloud procura o `requirements.txt` na pasta do arquivo de entrada e depois na raiz ([app dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)).
- Com o arquivo de entrada numa subpasta, o `config.toml` fica na raiz, e o diretório de trabalho é a raiz ([file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)).
- Testes de tela com `AppTest` ([app testing](https://docs.streamlit.io/develop/api-reference/app-testing)).
