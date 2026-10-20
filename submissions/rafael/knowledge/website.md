# G4 Marketing — site de entrega (com servidor): arquitetura, design e como usar

Código: `solution/src/social_web/` · comando: `.venv/bin/social-web` · atualizado em 2026-10-19.
Substitui o site estático anterior (removido): agora há servidor, linguagem para leigos, previsões feitas no servidor e painel estilo Power BI.

## Como rodar
```bash
cd submissions/rafael
python -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pip install -e .
.venv/bin/social-web                 # http://127.0.0.1:8000  (1ª vez: treina e calcula tudo, ~5 min; depois sobe em segundos)
.venv/bin/social-web --rebuild       # após trocar o CSV pelos dados da empresa
.venv/bin/social-web --host 0.0.0.0 --port 8080   # para expor na rede
```
Cache: `solution/models/web_models.joblib` (modelos) e `site_payload.json` (conteúdo), fora do git.

## Arquitetura
| Módulo | Papel |
|---|---|
| `server.py` | FastAPI: `create_app(state)` (testável), rotas das páginas (Jinja2), API, filtros pt-BR (`num`, `pct`, `pt`, `label`, `val`, `words`), CLI `main()` |
| `state.py` | carrega o CSV, treina/lê do cache: chance de top 5%, previsão de views, engajamento; monta o payload de conteúdo (`site_export.build_payload`) |
| `predict.py` | `PredictionService`: monta o post (faixas, horário, histórico do creator), chama os 3 modelos, cruza com as descobertas e escreve o resumo em linguagem simples |
| `explore.py` | agregações do painel: filtros, cartões, comparação de grupos (com marcação de "diferença real" corrigida), série mensal sem meses incompletos, matriz e top 10 |
| `schemas.py` | validação das entradas da API (pydantic) |
| `templates/` | 8 páginas: Início · As 4 perguntas · Estratégia · Descobertas · Explorar dados · Simular post · Auditorias · Como chegamos lá; `_notes.html` = macros dos avisos (fuso horário, unidade da duração) |
| `static/` | CSS (tema claro/escuro, responsivo), `common.js` (formatação, selos de evidência, gráficos) e Chart.js embutido (funciona offline) |

## API (documentação automática em `/docs`)
| Rota | Uso |
|---|---|
| `POST /api/predict` | corpo = post planejado (plataforma, formato, tema, idioma, horário, seguidores, duração, público, patrocínio, creator opcional) → chance de top 5% por métrica, comparação entre formatos, views e engajamento esperados com faixa provável, descobertas que se aplicam, resumo em frases, `mercado` (idioma do mercado? rede disponível lá? via `audits.market_coherence_flags`) |
| `POST /api/explore` | filtros + agrupamento + métrica + linhas/colunas da matriz + período → tudo que o painel desenha |
| `GET /api/options` | valores dos filtros e métricas disponíveis |
| `GET /api/health` | status |

## Linguagem para leigos (padrão do site)
- "Virar destaque" = top 5%. "Faixa provável" = intervalo de 90%. "2x mais chance" = o dobro do normal.
- Selos: **confirmado** (passou em tudo) · **se repetiu nos 2 anos** (candidato a teste) · **pista** (pode ser coincidência).
- Jargão técnico (q-value, AUC, R²) só dentro de "Detalhes técnicos".

## Testes
`solution/tests/test_web.py` (dados sintéticos e modelos leves) cobre:
- filtros, cartões, marcação de diferença real e ordem natural;
- remoção de meses incompletos e casamento das descobertas;
- as 7 páginas renderizando;
- as APIs `explore` e `predict`, incluindo a validação de entrada (422).

## Identidade visual e UX (2026-10-19)
- **Marca:** símbolo oficial do G4 (favicon `/favicon.ico` e `static/img/`) + "G4 Marketing" no cabeçalho, com a paleta do G4 Educação levantada do site oficial: azul-marinho `#031A26`/`#001F35`, dourado `#B9915B`, off-white `#F5F4F3` e azul `#184560`.
- **Tipografia:** Playfair Display (o equivalente livre mais próximo da PP Museum usada pelo G4) nos títulos, com algarismos alinhados nos números de destaque; Manrope no texto, como no site do G4.
- **Divulgação progressiva:**
  - o **Resumo** é um painel de uma tela: 4 respostas, 2 destaques, "Comece / Pare / Teste" e atalhos para as ferramentas;
  - cada cartão tem "+ Ver detalhes";
  - nas páginas de aprofundamento, gráficos, tabelas e textos técnicos ficam fechados até o clique.
- **Navegação:** Resumo · Explorar dados · Simular post · "Aprofundar ▾" (as 4 perguntas, estratégia, descobertas, como chegamos lá). Links do Resumo para `/perguntas#patrocinio` abrem a seção já expandida.
- **Ferramentas:**
  - **Explorar** mostra indicadores e o gráfico principal; evolução mensal, matriz e top 10 ficam em seções expansíveis.
  - **Prever** mostra só os campos essenciais (o resto em "Mais opções"); o resultado traz o resumo, as chances, as views e o engajamento, com "outro formato" e "descobertas" sob demanda.
  - As seções abertas pelo usuário continuam abertas quando o resultado é recalculado.
- **Gráficos em seções fechadas:** `lazyChart` desenha o gráfico ao abrir a seção, e um listener de `toggle` redimensiona gráficos já existentes.

## Painel "Explorar dados" (v2, 2026-10-19): simples e interativo
- **Métrica em um clique:** abas Views · Likes · Comentários · Engajamento + troca **Média / Chance de bombar** (top 5%). Os cartões de indicador também trocam a métrica.
- **Filtros:** chips de plataforma, formato e tema no topo; "Mais filtros" (popover) com os demais; período; etiquetas removíveis dos filtros ativos.
- **6 quadros sempre visíveis:** plataforma, formato, tema, tamanho do creator, uma característica à escolha e mês a mês.
  - As barras mostram a **diferença em relação à média** (centradas no zero, com o valor escrito).
  - Cores: dourado = acima de verdade, vermelho = abaixo de verdade, cinza = variação normal.
  - Cada quadro tem um selo ("sem diferença real" / "N diferenças reais").
- **Filtro cruzado (estilo Power BI):** clicar numa barra filtra o painel inteiro. O quadro da própria característica ignora o próprio filtro, para continuar mostrando todas as opções (as escolhidas ficam contornadas, as demais esmaecidas).
- **Frase-resumo automática:** o destaque real mais forte da seleção, ou "nenhum grupo se destaca".
- **Link compartilhável:** o estado fica no endereço, ex. `/explorar?m=likes&modo=chance&platform=TikTok&content_category=beauty`.
- **API:** `POST /api/explore` aceita `graficos: [...]` e devolve `graficos` (um breakdown por característica), `resumo` (destaque), `kpis`, `serie`, `matriz` e `top`.
- **Padrão: "Chance de bombar"** (top 5%), onde as diferenças reais aparecem.
- **Sugestões de filtro** (atalhos montados a partir dos resultados): ⭐ destaque confirmado (TikTok · beauty → qual idioma bomba em likes), melhor horário para comentários no YouTube, patrocinado × orgânico, público que mais bomba em likes, creators grandes × pequenos.
- **O painel abre pré-preenchido** com a sugestão ⭐ quando o endereço não traz uma visão (para mostrar a funcionalidade de cara). "Limpar filtros" volta à base inteira.

## "Simular post" (antes "Prever um post"; endereço `/simular`, e `/prever` redireciona), 2026-10-19
- **Formulário de 1 clique em 3 passos:**
  1. O post: botões de plataforma, formato, tema e idioma.
  2. Quando: dia em botões e hora em controle deslizante.
  3. Quem posta: seguidores com atalhos (5 mil, 25 mil, 100 mil, 1 mi) e chave de patrocínio.
  Duração, legenda, público e creator ficam em "Mais opções". Os **exemplos prontos** ("Experimente") vêm dos resultados (★ destaque confirmado, horário do YouTube).
- **Resultado em camadas:**
  - **veredito** ("Boa aposta para likes" / "Na média" / "Atenção");
  - **sugestão para o seu post**: a versão mais próxima e comprovadamente melhor (até 2 mudanças de formato, plataforma, tema ou idioma), com "Aplicar sugestão" e seletor **Otimizar para** (qualquer, views, likes, comentários);
  - cartões por métrica com selo (acima / na média / abaixo do normal), chance, "x o normal" e faixa provável;
  - outras melhorias com "Aplicar";
  - views e engajamento esperados;
  - outros formatos, descobertas e "como é calculado" sob demanda.
- **Honestidade da sugestão:** testar ~75 variações acha algumas por sorte. Por isso cada sugestão traz um selo: **confirmado** (apoiada por descoberta robusta), **se repetiu nos 2 anos** (descoberta replicada) ou **pista** (com o aviso "confirme com um teste").
- **API:** `POST /api/predict` aceita `objetivo` e devolve `status` por métrica, `melhorias` (trocas únicas) e `sugestao` (`mudancas`, métrica, de → para, faixa e evidência).

## Revisão visual comparada ao g4educacao.com (2026-10-19)
| Elemento | g4educacao.com | Aplicado no G4 Marketing |
|---|---|---|
| Títulos | Manrope leve + palavra-chave em serifada itálica dourada ("O G4 *em números*") | h1/h2 em Manrope 300 + `<em>` em Libre Baskerville itálica dourada (ex.: "As 4 *respostas*", "Simule seu post *antes de publicar*") |
| Números grandes | serifada (PP Museum), dourada ou azul-marinho | Libre Baskerville nos números de destaque (cartões, chances, KPIs) |
| Marca | símbolo dourado + "G4" em sans negrito | símbolo + "**G4** *Marketing*" (Marketing em itálico serifado dourado) |
| Botões | retângulo de 6 px; principal dourado com texto azul-marinho; secundário contornado | idem (menu, abas, chips, "Aplicar sugestão") |
| Cartões | chapados, borda fina, sem sombra | sombras removidas, borda `--line` |
| Detalhes | filetes dourados finos; marca-d'água gigante em itálico; links "Explorar →" em negrito | filete dourado nos "+ Ver detalhes"; marca-d'água "dados" na faixa do Resumo; links de seção em negrito |
| Composição | faixas azul-marinho centralizadas | faixa do Resumo centralizada; ferramentas alinhadas à esquerda (escaneamento) |
Fontes: Manrope (300–800) + Libre Baskerville (a serifada que o próprio site do G4 carrega; a PP Museum é comercial).

## Auditorias e avisos (2026-10-19)
- **Página `/auditorias`** (`templates/auditorias.html`, no menu "Aprofundar"): primeiro, 5 cartões de veredito (disclosure, fit patrocinador × nicho, coerência idioma × mercado × rede, duração na unidade certa, poder dos testes), cada um com o número-chave e "Na prática". O resto fica em "Ver detalhes": barras empilhadas de risco por mercado, tabela nicho × patrocinador com o encaixe destacado, % coerente por mercado, redes bloqueadas, duração por formato, dispersão n × MDE e o veredito técnico de cada auditoria.
- **Regras editáveis:** `AD_RULES`, `SPONSOR_FIT`, `MARKET_LANGUAGES`, `UNAVAILABLE_PLATFORMS` (em `audits.py`) aparecem na seção "As regras usadas", com o aviso de que são premissas de mercado e não parecer jurídico.
- **Payload:** `auditorias` (gerado por `site_export.audits_section`), com `cartoes`, `risco_mercado`, `rotulo_local`, `nicho`, `mercado`, `bloqueadas`, `duracao`, `poder`, `regras` (+ `unidades`) e `nota_duracao`.
- **Aviso de fuso horário:** o texto fica definido uma única vez em `server.TIME_NOTE` (global do Jinja) e é exibido pela macro `time_note()`. Aparece em Início (destaque de horário e mitos), Perguntas (Q4), Estratégia, Descobertas (#horario), Simular (abaixo da hora) e Explorar (só quando hora, período ou dia da semana estão em uso). `post_date` é tratado como já normalizado e não é convertido.
- **Aviso de duração:** a macro `length_note(d)` mostra `auditorias.nota_duracao` onde duração ou faixas de duração aparecem: Início (mitos), Perguntas (Q4 e o gráfico de duração), Simular (o rótulo do campo muda conforme a unidade do formato) e Explorar (só com `length_bin`).
- **Simular:** cartão "Mercado" quando o idioma não é falado no país do público ou a rede está indisponível lá.
- **Contradições resolvidas (revisão de 2026-10-19):** o destaque TikTok · beauty · espanhol virou "testar antes de mudar o mix" (com nº de posts por grupo), e não mais "priorizar". O horário no YouTube passou a "entram mais no top 1% de comentários", não "recebem mais comentários", e vira desempate de agenda (A/B inviável, ~17 mil posts). Os quick wins ganharam a coluna **Base** (robusta × depende de premissa). Estratégia ganhou **Fila de testes** (`estrategia.testes`) e **sensibilidade do teto** (`estrategia.sensibilidade`). A manchete da home passou de "O preço muda" para "A decisão é de preço".
- **Texto de disclosure corrigido:** a estratégia e o quick win não dizem mais "elimina o risco / conformidade". Agora `strategy.disclosure_rule` exige rótulo verificável no texto e cita o % em risco alto, o % com rótulo visível e o custo (nenhum) em engajamento.
