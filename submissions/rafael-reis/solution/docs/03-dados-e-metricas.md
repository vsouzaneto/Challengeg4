# Dados, qualidade e contrato de métricas

**Estado:** especificação e auditoria dos arquivos disponíveis; não declara produto implementado.  
**Escopo:** um sistema de Inteligência de Suporte, com a mesma procedência e as mesmas métricas nas seis lentes.  
**Relacionados:** [índice](00-indice.md), [arquitetura compartilhada](01-arquitetura-compartilhada.md), [plano](02-plano-de-implementacao.md).

## 1. Inventário verificado

A leitura foi feita com `csv.DictReader`, em UTF-8 com suporte a BOM, contando registros CSV lógicos, não linhas físicas. Campo vazio significa string vazia após `strip()`. Os arquivos originais não foram modificados. Não foram encontrados registros com quantidade incorreta de colunas nem valores literais `NA`, `N/A`, `null`, `None` ou `NaN` nos campos. Isso não prova validade semântica dos conteúdos.

| Fonte local | Registros | Colunas | Bytes | Papel no sistema |
|---|---:|---:|---:|---|
| `customer_support_tickets.csv` — Dataset 1 | 8.469 | 17 | 3.945.533 | Perfil operacional, status, canais, prioridades, tipos, CSAT observado e casos com resolução registrada |
| `all_tickets_processed_improved_v3.csv` — Dataset 2 | 47.837 | 2 | 14.568.920 | Taxonomia IT, corpus de classificação, recuperação de tickets semelhantes e avaliação de classificação |

Checksums SHA-256 dos bytes originais:

```text
customer_support_tickets.csv
b06a9cde84da65db388bd964d75f88ee1eed96607cf75d0c35f09c3f11bf8bea

all_tickets_processed_improved_v3.csv
044fdace33fa564e1e60453f2941dafc95539c99878b0d32746950394b9dd4d4
```

O [README da submissão](../../README.md) registra que o briefing mencionava aproximadamente 30.000 registros no Dataset 1 e uma operação com aproximadamente 30.000 tickets por ano. O arquivo local contém 8.469 registros; volume da amostra e volume anual do cenário são grandezas diferentes. Não extrapolar a amostra como um ano observado. O README do challenge atribui origem Kaggle e licença CC0 aos dois datasets; esta auditoria conferiu os arquivos locais, não verificou independentemente as páginas de origem nem a representatividade dos dados.

## 2. Identidade, normalização e privacidade

- Identificador Dataset 1: `ds1:<Ticket ID>`. Os 8.469 IDs são únicos e variam de 1 a 8.469.
- Identificador Dataset 2: `ds2:<sha256(texto_normalizado)>`, utilizando Unicode NFC, remoção de espaços nas bordas e normalização de sequências de whitespace para um espaço. Preservar maiúsculas, acentos e pontuação. Armazenar também a origem e o hash do arquivo.
- Normalização de comparação para avaliação pode aplicar `casefold()` adicionalmente; não muda o ID canônico. Registrar a versão da regra usada.
- Nunca relacionar os datasets por número de linha, similaridade como se fosse identidade, pessoa ou um ID inventado. Eles representam domínios e taxonomias diferentes.
- `Customer Name` e `Customer Email` não entram no índice de busca, nos prompts, nos gráficos nem nas evidências exibidas. Texto livre exige mascaramento adicional antes de eventual uso externo, pois também pode conter dados pessoais.
- Idade e gênero não devem orientar prioridade, escalonamento ou elegibilidade de automação. Não são necessários para os objetivos operacionais deste protótipo.
- Logs registram IDs, versões, contagens, decisões e erros; não copiam nomes, e-mails ou descrições integrais. Hash de texto não é garantia de anonimização.

## 3. Dicionário do Dataset 1

Os nomes abaixo correspondem exatamente ao cabeçalho local. `Não informado` é uma apresentação de ausência, nunca uma categoria adicionada ao CSV.

| Campo | Tipo na importação / unidade | Vazios | Distintos não vazios | Interpretação e restrição |
|---|---|---:|---:|---|
| `Ticket ID` | Inteiro convertido para ID com prefixo | 0 | 8.469 | Identidade do registro na fonte |
| `Customer Name` | Texto restrito | 0 | 8.028 | Dado pessoal; não expor nem indexar |
| `Customer Email` | Texto restrito | 0 | 8.320 | Dado pessoal; não expor nem indexar |
| `Customer Age` | Número inteiro / anos | 0 | 53 | Não usar para decisões de suporte |
| `Customer Gender` | Categoria restrita | 0 | 3 | Não usar para decisões de suporte |
| `Product Purchased` | Categoria | 0 | 42 | Produto relacionado, não uma fila IT |
| `Date of Purchase` | Data `YYYY-MM-DD` | 0 | 730 | Compra entre 2020-01-01 e 2021-12-30; não é abertura do ticket |
| `Ticket Type` | Categoria | 0 | 5 | Taxonomia do Dataset 1 |
| `Ticket Subject` | Texto/categoria | 0 | 16 | Assunto resumido |
| `Ticket Description` | Texto | 0 | 8.077 | Conteúdo do chamado; contém placeholders |
| `Ticket Status` | Categoria | 0 | 3 | Estado registrado no snapshot, não histórico de transições |
| `Resolution` | Texto opcional | 5.700 (67,30%) | 2.769 | Resposta histórica, sem comprovação de qualidade ou aprovação como base de conhecimento |
| `Ticket Priority` | Categoria ordinal | 0 | 4 | Prioridade histórica; não é rótulo de risco nem SLA contratado |
| `Ticket Channel` | Categoria | 0 | 4 | Canal registrado |
| `First Response Time` | Timestamp sem fuso `YYYY-MM-DD HH:MM:SS` | 2.819 (33,29%) | 5.470 | Data/hora aparente da primeira resposta; não uma duração FRT |
| `Time to Resolution` | Timestamp sem fuso `YYYY-MM-DD HH:MM:SS` | 5.700 (67,30%) | 2.728 | Data/hora aparente da resolução; não uma duração TTR |
| `Customer Satisfaction Rating` | Número inteiro semântico / escala 1–5; CSV usa `1.0` etc. | 5.700 (67,30%) | 5 | Nota observada somente em tickets fechados |

Valores e contagens auditados:

| Dimensão | Distribuição |
|---|---|
| Tipo | `Technical issue`: 1.747; `Billing inquiry`: 1.634; `Cancellation request`: 1.695; `Product inquiry`: 1.641; `Refund request`: 1.752 |
| Status | `Open`: 2.819; `Pending Customer Response`: 2.881; `Closed`: 2.769 |
| Prioridade | `Low`: 2.063; `Medium`: 2.192; `High`: 2.085; `Critical`: 2.129 |
| Canal | `Email`: 2.143; `Phone`: 2.132; `Chat`: 2.073; `Social media`: 2.121 |
| CSAT informado | 1: 553; 2: 549; 3: 580; 4: 543; 5: 544 |

### 3.1 Cobertura vinculada ao status

| Status | Registros | Primeira resposta preenchida | Resolução preenchida | Timestamp resolução preenchido | CSAT preenchido |
|---|---:|---:|---:|---:|---:|
| `Closed` | 2.769 | 2.769 | 2.769 | 2.769 | 2.769 |
| `Open` | 2.819 | 0 | 0 | 0 | 0 |
| `Pending Customer Response` | 2.881 | 2.881 | 0 | 0 | 0 |

A ausência depende do status; não imputar zero, média, insatisfação ou resolução falha. Comparar CSAT significa comparar respondentes fechados, não todos os clientes. Os 5.700 registros não fechados descrevem a amostra, sem demonstrar o backlog atual de uma empresa real.

### 3.2 Bloqueio de indicadores temporais

Não existe campo de abertura do ticket, registro de esforço do agente, histórico de pausas ou contrato de SLA. Os dois campos chamados “Time” contêm timestamps:

- Primeira resposta: mínimo `2023-05-31 21:55:39`, máximo `2023-06-02 00:54:21`, sem fuso declarado.
- Resolução: mínimo `2023-05-31 21:53:30`, máximo `2023-06-02 00:55:33`, sem fuso declarado.
- Entre os 2.769 pares preenchidos: 1.365 (49,30%) têm resolução anterior à primeira resposta; 2 são iguais; 1.402 são posteriores.

Consequências obrigatórias:

1. FRT, TTR, aging, cumprimento de SLA e evolução por abertura ficam **indisponíveis na fonte atual**, com explicação e campos faltantes.
2. Não subtrair a data de compra; ela não representa abertura. Não converter os timestamps para horas desde uma origem arbitrária.
3. Não descartar silenciosamente os pares negativos e apresentar os restantes como amostra temporal válida. A diferença resolução menos primeira resposta também não é TTR.
4. Exibir as inconsistências como qualidade do dado. Elas não permitem concluir que um canal, produto ou equipe é lento.
5. Liberar métricas temporais somente após nova fonte com `created_at`, `first_response_at`, `resolved_at`, fuso e semântica confirmados, além de validação de ordem cronológica. Esforço requer medição própria.

### 3.3 Repetição e conteúdo

- Não há linhas inteiras duplicadas.
- Há 8.077 descrições distintas por igualdade exata: 392 ocorrências excedentes de texto repetido.
- NFC + whitespace, preservando case: 8.067 textos distintos; 402 ocorrências excedentes.
- NFC + whitespace + `casefold()`: 8.066 textos distintos; 403 ocorrências excedentes; 54 grupos com mais de um registro. Desses grupos, 49 possuem mais de um `Ticket Type`.
- Todas as 8.469 descrições contêm ao menos um trecho entre chaves `{...}`. Comprimento: mínimo 151, mediana 298, máximo 397 caracteres.

Placeholders e repetições indicam conteúdo templateado que precisa de revisão; não comprovam sozinhos sua origem. Não preencher placeholders com informações inventadas. Similaridade textual não comprova duplicidade operacional, mesma pessoa, mesma causa ou mesmo atendimento. Grupos repetidos precisam ficar no mesmo conjunto de avaliação para evitar vazamento entre treino e teste.

## 4. Dicionário e capacidade do Dataset 2

| Campo | Tipo | Vazios | Distintos | Uso autorizado pelos dados |
|---|---|---:|---:|---|
| `Document` | Texto | 0 | 47.837 | Consulta, classificação e recuperação de chamados semelhantes |
| `Topic_group` | Categoria | 0 | 8 | Rótulo observado para avaliação da classificação IT |

| Rótulo exato | Registros | Participação |
|---|---:|---:|
| `Hardware` | 13.617 | 28,47% |
| `HR Support` | 10.915 | 22,82% |
| `Access` | 7.125 | 14,89% |
| `Miscellaneous` | 7.060 | 14,76% |
| `Storage` | 2.777 | 5,81% |
| `Purchase` | 2.464 | 5,15% |
| `Internal Project` | 2.119 | 4,43% |
| `Administrative rights` | 1.760 | 3,68% |

Não há linhas nem textos exatos duplicados, inclusive após a normalização conservadora e após `casefold()`. Similaridade aproximada não foi auditada. Comprimento dos textos: mínimo 7, mediana 175 e máximo 7.015 caracteres. A classe majoritária representa 28,47%: esse é o baseline de acurácia de sempre prever `Hardware`.

O Dataset 2 **não possui** resolução, canal, prioridade, status, CSAT, timestamps, ID de cliente ou chave de vínculo com o Dataset 1. Portanto:

- É válido recuperar “tickets semelhantes”, mostrando ID e categoria; não chamar esses resultados de soluções resolvidas.
- Não é possível avaliar qualidade factual de respostas, taxa de resolução, economia de tempo ou satisfação usando apenas seus rótulos.
- `Hardware` e as demais oito classes não equivalem aos cinco `Ticket Type` do Dataset 1. Uma classificação projetada entre domínios deve ser identificada como previsão, nunca rótulo original.
- Casos de `Administrative rights`, `Access` e `HR Support` podem sugerir revisão humana por segurança ou sensibilidade. A categoria sozinha não comprova risco nem autoriza concessão de acesso, alteração de privilégio ou decisão sobre pessoas.

## 5. Contrato compartilhado de métricas

Toda métrica retorna: `key`, `value` ou `null`, unidade, numerador/denominador quando aplicáveis, `source`, filtros aplicados, cobertura, período quando válido, `status` (`observed`, `estimated`, `simulated`, `unavailable`), versão do cálculo e motivo quando indisponível. `source` identifica a origem (`historical`, `simulation`, `user_created`, `model_evaluation`); `status` identifica a natureza/disponibilidade do valor. Ausência não é zero. Formatação pt-BR na interface; armazenamento numérico sem strings formatadas.

Filtros sempre precedem agregação. Dataset 1 e Dataset 2 mantêm populações separadas; uma soma de 56.306 registros pode aparecer apenas como “registros nas duas fontes”, sem ser tratada como operação homogênea. Contagens e porcentagens mudam juntas após filtros. Mostrar `n` e cobertura em comparações.

| Métrica | Fórmula / população | Disponibilidade e limite |
|---|---|---|
| Volume da amostra | Contagem dos IDs da fonte selecionada após filtros | Observado; sem extrapolação temporal |
| Participação por dimensão | `n_grupo / n_filtrado × 100` | Observado; categorias vazias separadas se surgirem em nova importação |
| Não fechados na amostra | `Open + Pending Customer Response` | 5.700 no DS1 completo; não chamar de backlog atual |
| Proporção de fechados | `n_Closed / n_total × 100` | 32,70% no DS1; não é taxa de resolução no período |
| Cobertura de CSAT | `n_notas_validas / n_filtrado × 100` | 32,70% no DS1 completo; 100% entre os fechados desta fonte |
| Nota média CSAT | Soma das notas válidas / número de notas válidas | 2,9913/5 no DS1 completo; UI 2,99/5, `n=2.769` |
| Mediana CSAT | Mediana das notas válidas | 3/5 no DS1 completo |
| CSAT positivo, convenção do protótipo | `n_notas_4_ou_5 / n_notas_validas × 100` | 1.087 / 2.769 = 39,26%; mostrar escala e corte adotado |
| Distribuição CSAT | Contagem de cada nota entre respondentes | Mais informativa que média isolada; sem imputação |
| FRT | `first_response_at − created_at`, unidade definida | Indisponível nos CSVs atuais |
| TTR | `resolved_at − created_at`, unidade definida | Indisponível nos CSVs atuais; incluir só resolvidos elegíveis numa fonte válida |
| Horas de esforço | Soma de minutos efetivamente trabalhados / 60 | Indisponível; não derivar de TTR |
| Violações de SLA | Comparação com regra de SLA acordada e calendário aplicável | Indisponível: faltam regra e timestamps confiáveis |
| Ocorrências repetidas de texto | `n_documentos − n_textos_distintos`, com normalização declarada | Indicador de corpus; não número de tickets duplicados confirmados |
| Candidatos à automação | Contagem dos IDs que passam regras explícitas de elegibilidade | Estimativa por política versionada, não benefício realizado |
| Precisão de categoria | `TP / (TP + FP)` por classe | Só após avaliação em conjunto separado; denominador zero = indisponível |
| Recall de categoria | `TP / (TP + FN)` por classe | Só após avaliação; exibir suporte por classe |
| F1 macro | Média não ponderada do F1 das classes avaliadas | Principal comparação para classes desbalanceadas; informar tratamento de classes sem suporte |
| Acurácia | Previsões corretas / total avaliado | Comparar com baseline majoritário 28,47% apenas no DS2 completo; recalcular no teste |
| Cobertura de decisão | Decisões que superam política / entradas válidas | Sempre exibir também taxa de abstenção e motivos |
| Latência | Tempo medido da execução local, de início a término | Medir no protótipo; não apresentar meta como resultado |

Uma diferença observada de CSAT entre grupos é uma associação descritiva. Não afirmar que prioridade, canal ou tipo “causa” satisfação; não atribuir efeitos de automação sem experimento. Comparações com menos de 30 respostas exibem “amostra pequena”, uma regra de cautela de interface, não um teste estatístico. Ordenação usa valor e contagem visíveis; não declara significância. Se não houver respostas, apresentar estado vazio e denominador zero.

Para grandezas contínuas válidas, resumir contagem, média, mediana, p75, p90, p95 e desvio-padrão populacional do recorte. Percentil usa interpolação linear em posição `(n − 1) × p` sobre valores ordenados; mediana é p50. Desvio-padrão usa denominador `n`, com descrição de que resume os registros do recorte, sem estimar população externa. Com `n=0`, todos os resumos exceto contagem são indisponíveis; com `n=1`, percentis iguais ao único valor e desvio-padrão zero, mantendo alerta de amostra pequena. Os CSVs atuais não habilitam esses resumos para duração. Na escala ordinal CSAT, priorizar distribuição, média e mediana; não inferir precisão adicional pelos percentis.

## 6. Avaliação de IA e prevenção de vazamento

1. Fixar manifestos da fonte, normalização e divisão dos dados antes de medir resultados. Preservar todas as oito classes com suporte suficiente.
2. Agrupar textos repetidos antes da divisão. O mesmo texto normalizado não aparece em treino/índice e teste. Para recuperar vizinhos, excluir o próprio ticket da consulta avaliada.
3. Se houver ajuste de regras/limiares, usar conjunto de validação; não escolher regras olhando o teste final. Relatar tamanho e suporte por classe, seed e versão.
4. Comparar baseline de classe majoritária, abordagem implementada e abstenção. Não prometer 92% de acurácia porque esse número aparece como exemplo no README.
5. Similaridade lexical, distância de embedding e voto de vizinhos são scores; não rotular como probabilidade calibrada. Usar “score de similaridade” ou “força da evidência”.
6. Dataset 1 e Dataset 2 exigem avaliações separadas. Rótulos do DS1 são tipos de solicitação; rótulos do DS2 são assuntos IT.
7. Qualidade de sugestão de resposta exige revisão humana amostrada: apoio nas evidências, ausência de dados pessoais, ausência de ações inventadas, clareza e necessidade de escalonamento. Texto histórico em `Resolution` não é verdade operacional validada.

## 7. ROI: hipótese mensurável, sem converter espera em esforço

Os CSVs não medem horas trabalhadas, salários, custo por atendimento, orçamento, adoção, taxa de sucesso de IA nem economia realizada. A lente de estratégia deve oferecer um **cenário estimado**, com premissas editáveis e fonte de cada premissa. Valores iniciais não confirmados ficam em branco ou explicitamente demonstrativos; nunca apresentados como diagnóstico observado.

Variáveis por mês e por atividade não sobreposta:

| Variável | Significado | Validação |
|---|---|---|
| `N` | Volume mensal elegível | Inteiro ≥ 0; amostra não vira volume mensal automaticamente |
| `a` | Fração de adoção dentro dos elegíveis | Entre 0 e 1 |
| `t_base` | Minutos de trabalho humano por atividade sem assistência | ≥ 0; medido ou premissa identificada |
| `t_proposto` | Minutos humanos com assistência, incluindo revisão, correção e fallback | ≥ 0; mesma atividade e população de `t_base` |
| `c_hora` | Custo por hora humana | ≥ 0, moeda explícita |
| `c_execucao` | Custo incremental por execução de IA | ≥ 0; inclui tentativas sem adoção quando houver execução |
| `n_execucoes` | Quantidade mensal de execuções | Inteiro ≥ 0; pode exceder `N × a` |
| `c_fixo` | Manutenção/custos recorrentes adicionais mensais | ≥ 0 |
| `investimento` | Implantação única | ≥ 0; separado dos custos mensais |

```text
horas_liberadas_mes = N × a × (t_base − t_proposto) / 60
capacidade_valorizada_mes = horas_liberadas_mes × c_hora
custo_recorrente_mes = n_execucoes × c_execucao + c_fixo
beneficio_liquido_mes = capacidade_valorizada_mes − custo_recorrente_mes
payback_meses = investimento / beneficio_liquido_mes
ROI_no_horizonte = (beneficio_no_horizonte − custo_total_no_horizonte)
                   / custo_total_no_horizonte × 100
```

Payback só existe com benefício líquido positivo; ROI percentual é indisponível se o custo total for zero. Não truncar economia negativa para zero: mostrar aumento de esforço/custo. No ROI por horizonte, benefício é capacidade valorizada acumulada, e custo total inclui investimento e recorrência uma única vez.

Horas liberadas indicam capacidade, não redução comprovada de despesas ou de quadro. Não somar dois cenários que economizam os mesmos minutos do mesmo ticket. Candidaturas sobrepostas exigem deduplicação por atividade e ID. A referência de aproximadamente 30.000 tickets/ano pode entrar como premissa do README, resultando em 2.500/mês sob distribuição uniforme explicitamente assumida; não é volume mensal medido.

Comparar cenários conservador, base e otimista apenas depois de preencher premissas. Piloto deve medir minutos antes/depois, retrabalho, erros, satisfação e escalonamentos para substituir hipóteses por observações. Redução de FRT/TTR, mesmo quando futuramente mensurável, não equivale automaticamente à redução de esforço.

## 8. Verificação reprodutível do inventário

O bloco abaixo é uma receita de auditoria em Python da biblioteca padrão, executada a partir da pasta do challenge. Não altera os CSVs e não imprime conteúdo pessoal. As asserções ancoram a documentação nas versões locais auditadas; uma nova fonte deve atualizar a auditoria e seu manifesto antes de atualizar a interface.

```python
import csv
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path
from unicodedata import normalize

expected = {
    "customer_support_tickets.csv": (8469, 17, "b06a9cde84da65db388bd964d75f88ee1eed96607cf75d0c35f09c3f11bf8bea"),
    "all_tickets_processed_improved_v3.csv": (47837, 2, "044fdace33fa564e1e60453f2941dafc95539c99878b0d32746950394b9dd4d4"),
}
canonical = lambda text: " ".join(normalize("NFC", text).split())
for name, (n, width, digest) in expected.items():
    path = Path(name)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows, columns = list(reader), reader.fieldnames
    assert len(rows) == n and len(columns) == width
    assert all(None not in row and all(value is not None for value in row.values()) for row in rows)
    assert len({tuple(row[col] for col in columns) for row in rows}) == n
    empty = {col: sum(not row[col].strip() for row in rows) for col in columns}
    print(name, {"rows": n, "columns": width, "empty": empty})
    if "Ticket ID" in columns:
        assert len({row["Ticket ID"] for row in rows}) == n
        assert len({canonical(row["Ticket Description"]) for row in rows}) == 8067
        parse = lambda text: datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        pairs = [row for row in rows if row["First Response Time"] and row["Time to Resolution"]]
        negative = sum(parse(row["Time to Resolution"]) < parse(row["First Response Time"]) for row in pairs)
        assert len(pairs) == 2769 and negative == 1365
        scores = [float(row["Customer Satisfaction Rating"]) for row in rows if row["Customer Satisfaction Rating"]]
        assert len(scores) == 2769 and sum(score >= 4 for score in scores) == 1087
        assert set(scores) == {1, 2, 3, 4, 5}
        print({"invalid_order": negative, "csat_mean": sum(scores) / len(scores)})
    else:
        assert len({canonical(row["Document"]) for row in rows}) == n
        assert len({row["Topic_group"] for row in rows}) == 8
        print(dict(Counter(row["Topic_group"] for row in rows)))
```

## 9. Checkpoints de implementação e aceite

- [ ] Importação reproduz contagens, cabeçalhos e hashes; mudança da fonte aparece no manifesto.
- [ ] IDs e normalização obedecem ao contrato; Dataset 1 e Dataset 2 permanecem distinguíveis.
- [ ] CSVs originais permanecem intactos; cópias derivadas excluem dados pessoais desnecessários.
- [ ] Métricas compartilham filtros, denominadores, cobertura e estado de disponibilidade em todas as abas.
- [ ] FRT/TTR/SLA/esforço indisponíveis não aparecem como zero, gráfico temporal ou ranking de velocidade.
- [ ] CSAT mostra `n`, cobertura e população; não imputar ausências nem inferir causalidade.
- [ ] Similaridade de texto e resolução histórica não são apresentadas como solução validada.
- [ ] ROI separa premissa, cálculo e resultado observado; testa custo zero, ganho negativo e sobreposição de atividades.
- [ ] Avaliação exclui vazamento por texto e exibe classe, suporte, baseline e abstenção.
- [ ] Pelo menos uma verificação executável reproduz o inventário e os principais bloqueios de qualidade.
