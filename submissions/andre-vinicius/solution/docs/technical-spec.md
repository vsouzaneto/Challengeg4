# Foco — especificação técnica

Descreve a implementação atual, conferida contra o código. Regras e motivos de negócio: [especificação de negócio](business-spec.md). Telas: [especificação funcional](functional-spec.md).

## 1. Arquitetura

```text
Kaggle (CSV público) → download_data.py → data/  (ignorada pelo Git)
                                            │
        accounts + products + sales_teams ──┤ junção por conta, produto e vendedor
                  sales_pipeline.csv ───────┘
                                            ▼
                         scoring.py: normalização, filas, índice, razões
                                            ▼
                         app.py: payload em memória, GET /api/deals
                                            ▼
        static/: filtros, três leituras, detalhe, painéis, tema, documentos
```

Um único processo Python da biblioteca padrão faz tudo: lê os CSVs ao iniciar, calcula a carteira uma vez e serve os arquivos de `static/` mais um endpoint JSON. O navegador faz o resto (filtros, agrupamentos, painéis). Não há banco, fila, serviço externo, build nem dependência instalada por `pip` ou `npm`.

| Arquivo | Papel |
| --- | --- |
| `download_data.py` | Baixa o ZIP público, avisa se o SHA-256 mudou e grava cinco CSVs em `data/` |
| `scoring.py` | `load_data`, `prioritize`, `rank_open`; também `fit_history` e `affinity`, usados apenas por `evaluate.py` |
| `app.py` | `summarize_sales`, `build_payload`, servidor HTTP |
| `audit.py` | Auditoria reproduzível dos CSVs (contagens, vazios, hashes, qualidade) |
| `evaluate.py` | Avaliação cronológica da afinidade histórica (hipótese descartada) |
| `sync_docs.py` | Copia os documentos para `static/source/` e verifica se estão atualizados |
| `static/filter.js`, `business.js`, `annotations.js` | Funções puras e testáveis em Node (`module.exports` condicional) |
| `static/app.js`, `panels.js`, `reader.js`, `mode.js`, `theme.js` | Interface; dependem do DOM, sem teste automatizado |

## 2. Dados

### 2.1 Entrada

| Arquivo | Chave | Usado para |
| --- | --- | --- |
| `sales_pipeline.csv` | `opportunity_id` | Oportunidades: `deal_stage`, `engage_date`, `account`, `product`, `sales_agent`, e `close_date`/`close_value` apenas para vendas históricas e avaliação |
| `accounts.csv` | `account` | `sector` |
| `products.csv` | `product` | `sales_price` (preço de catálogo) |
| `sales_teams.csv` | `sales_agent` | `manager`, `regional_office` |
| `metadata.csv` | — | Só `audit.py` |

Os arquivos são lidos com `utf-8-sig`. Os dicionários de apoio são montados por chave; se houvesse chave repetida, valeria a última linha (a auditoria não encontrou duplicidade de `opportunity_id`; ver [auditoria dos dados](data-audit.md)).

### 2.2 Transformações em `load_data`

| Campo derivado | Regra |
| --- | --- |
| `product_key` | `PRODUCT_ALIASES.get(product, product)`; hoje só `GTXPro → GTX Pro` |
| `sector` | `accounts[account].sector`, ou `""` se a conta é vazia ou desconhecida |
| `manager`, `region` | `sales_teams[sales_agent]`, ou `""` se o vendedor é desconhecido |
| `catalog_price` | `float(products[product_key].sales_price)`, ou `0` se o produto não existe no catálogo |

### 2.3 Contrato de `GET /api/deals`

`application/json; charset=utf-8`, `Cache-Control: no-store`, corpo serializado a cada requisição a partir do payload em memória.

```json
{
  "as_of": "2017-12-31",
  "counts": {"Avançar": 0, "Revisar": 0, "Qualificar": 0},
  "deals": [
    {"id": "…", "account": "…", "product": "…", "agent": "…", "manager": "…",
     "region": "…", "sector": "…", "stage": "Engaging", "queue": "Avançar",
     "priority": 85, "catalog_price": 0.0, "days_engaged": 12,
     "next_action": "…", "reasons": ["…"]}
  ],
  "sales_by_agent": {"Nome": {"won": 0, "lost": 0, "won_value": 0.0}}
}
```

Os números acima são ilustrativos do formato. `deals` já vem ordenado. `days_engaged` é `null` sem data de engajamento. `account` vazio vira `"Conta não informada"`. Em `sales_by_agent`, `won_value` soma `close_value` só dos negócios `Won` (valor inválido é ignorado) e vendedor vazio vira `"Não informado"`.

## 3. Regra de priorização (`scoring.prioritize`)

Entrada: uma linha de oportunidade aberta e a data de referência. Levanta `ValueError` se a etapa não é `Prospecting` ou `Engaging`.

1. `age_days = referência − engage_date` (ou `None` se vazia); `stale = age_days > 90`.
2. Fila e base: `Prospecting` → Qualificar/35; `Engaging` e `stale` → Revisar/50; demais `Engaging` → Avançar/65 (inclui data vazia).
3. Bônus de +10 cada: `catalog_price ≥ 4000`; conta preenchida; Avançar com `age_days ≤ 30`; Revisar com `age_days ≥ 180`.
4. `priority = min(100, base + bônus)`.
5. `reasons`: fila e etapa; tempo (com a ressalva de confirmação se `stale`, ou “Ainda sem data de engajamento”); conta identificada ou ausente; preço como impacto potencial (se ≥ 4.000) ou como contexto.

| Fila | Base | Máximo alcançável | Valores possíveis |
| --- | ---: | ---: | --- |
| Avançar | 65 | 95 | 65, 75, 85, 95 |
| Revisar | 50 | 80 | 50, 60, 70, 80 |
| Qualificar | 35 | 55 | 35, 45, 55 |

`rank_open(rows, as_of=None)` filtra as etapas abertas, aplica `prioritize` e ordena por `(fila, −priority, id)`. A referência padrão é `DATASET_AS_OF = 2017-12-31`, constante: não é lida de `close_date`.

**Ausências deliberadas no cálculo:** desfechos, `close_value`, `close_date`, setor, vendedor e gerente não influenciam fila nem índice. A função rejeita etapas fechadas e copia setor, vendedor e gerente para o contexto da resposta. O setor também é usado por `evaluate.py`.

## 4. Servidor (`app.py`)

- `ThreadingHTTPServer` com `SimpleHTTPRequestHandler` servindo `static/`. Só `/api/deals` é tratado à parte.
- Opções: `--data` (pasta dos CSVs), `--port` (8843), `--host` (127.0.0.1).
- O payload é calculado antes de abrir o socket. Mudar CSV ou regra exige reiniciar o processo.
- Ao iniciar imprime endereço, quantidade de oportunidades abertas e referência.
- `Ctrl+C` encerra e fecha o socket.

## 5. Interface

- JavaScript sem framework e sem etapa de build; scripts carregados com `defer`.
- Texto de dados é inserido com `textContent`/nós DOM, nunca como HTML.
- `filter.js` e `business.js` são funções puras; o mesmo arquivo roda no navegador e em `node --test`.
- Estado de tela fica em memória (`state`) e em `localStorage` (chaves na seção “Preferências guardadas no navegador” da [especificação funcional](functional-spec.md)).
- Paginação em memória: 40 itens por vez.
- O mapa usa SVG com três formas fixas, associadas às regiões pela ordem de quantidade de oportunidades (maior primeiro).

## 6. Documentos servidos

`sync_docs.py` copia os arquivos listados em `SOURCES` para `static/source/`. O leitor (`reader.js`) tem uma tabela com os mesmos documentos e converte Markdown simples (títulos, listas, tabelas, código, negrito, links). `python sync_docs.py --check` falha se alguma cópia estiver ausente ou diferente. Um documento novo precisa entrar em `SOURCES` e na tabela `library` de `reader.js`.

## 7. Avaliação histórica (`evaluate.py`)

Ordena os negócios encerrados por `(close_date, opportunity_id)`, define o corte na posição 80% e separa treino (`close_date` anterior ao corte) e teste (igual ou posterior). Ajusta a afinidade com suavização 30 (peso 0,65 produto e 0,35 setor, só produto quando não há setor) e reporta taxas e AUC por Mann–Whitney com empates, mais a taxa de `Won` no quartil superior. O próprio resultado traz o aviso de escopo: estágio e idade não podem ser retrotestados. O resultado registrado está em [auditoria dos dados](data-audit.md).

## 8. Limites técnicos

| Limite | Efeito |
| --- | --- |
| Payload único com todas as oportunidades | Aceitável para 2.089 itens; uma versão multiusuário precisaria de paginação e filtros no servidor |
| Sem autenticação nem TLS | Não expor na internet; `--host` com IP de rede serve apenas para teste temporário |
| Dados lidos uma vez | Sem atualização ao vivo |
| Mapa com três formas | Uma quarta região no CSV não teria forma e quebraria a página do mapa |
| Painéis só listam quem tem carteira aberta | Vendedor sem oportunidade aberta não aparece, mesmo com vendas históricas |
| Preferências no navegador | Sem sincronização entre dispositivos |
| Listagem de diretório | O servidor padrão da biblioteca lista pastas sem `index.html` (por exemplo `/source/`); comportamento da biblioteca, não testado aqui |
| Texto de interface em português fixo | Sem internacionalização |
| Sem teste automatizado da interface | `app.js`, `panels.js`, `reader.js`, `mode.js` e `theme.js` só têm verificação visual |
