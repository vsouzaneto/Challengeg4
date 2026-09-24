# Arquitetura: um núcleo, 4 ferramentas, sozinhas e cooperando

## A ideia

Cada desafio é uma **ferramenta** completa: Churn (001), Suporte (002), Leads (003) e Mídia (004). Toda análise acontece dentro de uma **sessão**, que guarda a ferramenta, os arquivos e o De/Para das colunas. O resultado de uma sessão pode virar a entrada de outra ferramenta, em uma **sub-sessão**. Esse é o modo cooperativo.

```
            ┌────────────── núcleo ──────────────┐
arquivos →  │ leitura → De/Para (contratos) →    │ → ferramenta (análise) → telas, relatório, exportação
(desafio    │ carregar → sessão (SQLite + pasta) │                     │
 ou próprios)└────────────────────────────────────┘                     └→ ponte → sub-sessão em outra ferramenta
```

## Pastas (`solution/g4_analise/app`)

| Parte | O que faz |
|---|---|
| `nucleo/contratos.py` | Contrato de dados de cada ferramenta: tabelas, campos obrigatórios e opcionais, tipos. É o que permite rodar com **qualquer base**, não só a do desafio |
| `nucleo/depara.py` | Sugere qual coluna do arquivo corresponde a cada campo do contrato (o usuário confere) |
| `nucleo/leitura.py`, `carregar.py` | Leem CSV (vírgula ou ponto e vírgula), Excel e JSON e aplicam o De/Para e os tipos |
| `nucleo/sessoes.py` | Sessões em SQLite, cada uma com a sua pasta (entrada, análise salva) |
| `nucleo/cruzamentos.py`, `perfis.py` | Matriz 4×4 de cruzamentos, com selos e filtros por perfil (Tipo B) |
| `nucleo/exportar.py` | CSV (`;` e vírgula decimal) e Excel com uma aba por tabela |
| `modulos/<ferramenta>/analise.py` | Toda a estatística, sem interface; testável e usada também pelo agente |
| `modulos/<ferramenta>/tela.py`, `relatorio.py` | Abas da janela e relatório em PDF/Markdown |
| `modulos/<ferramenta>/pontes.py` | Transformam o resultado desta ferramenta em entrada de outra |
| `servicos.py` | Criar sessões, analisar (com resultado salvo em disco), cruzar e exportar. Usado pela janela e pelo agente |
| `servidor_mcp.py` | 12 ferramentas MCP para o agente do G4 OS usar o sistema |
| `principal.py`, `tela.py` | Janela própria (pywebview) e navegação |

## Cruzamentos entre ferramentas

As 4 bases são de **empresas diferentes e não têm chave em comum**. Tratar qualquer ligação entre elas como fato seria inventar dado. Por isso cada cruzamento tem um selo:

| Selo | Significado |
|---|---|
| **Dado real ligado** (verde) | Os mesmos registros, ligados por chave |
| **Proxy** (laranja) | Sinal indireto, com a adaptação explicada |
| **Hipótese configurável** (azul) | Perfil de uma base (país, idade, setor) usado para filtrar outra; o teste estatístico do perfil aparece junto |
| **Não dá** (cinza) | A base de origem não tem o que o destino precisa. Dizer "não dá" também faz parte da resposta |

| Origem → destino | Selo | Tipo | O que acontece |
|---|---|---|---|
| Churn → Suporte | verde | A | Chamados das contas em risco com problema de suporte são analisados pela ferramenta de Suporte |
| Churn → Leads | laranja | A | Contas ativas viram carteira de expansão: chance de ficar × MRR |
| Churn → Mídia | azul | B | Países que mais cancelam → posts com essa audiência |
| Suporte → Churn | laranja | A | Quem pediu cancelamento vira "cancelou" → o que diferencia esses clientes |
| Suporte → Leads | laranja | lista | Tickets de "pergunta sobre produto" → lista CSV de oportunidades |
| Suporte → Mídia | azul | B | Idade e gênero de quem pior avalia → posts com esse público |
| Leads → Mídia | azul | B | Países onde mais ganhamos → onde concentrar conteúdo |
| Mídia → Leads | azul | B | Países da audiência que mais engaja → deals desses países |
| Leads → Churn/Suporte, Mídia → Churn/Suporte | cinza | — | O CRM não tem cancelamentos nem tickets; o social não tem clientes nem tickets |

**Tipo A:** a ferramenta de destino roda sobre os dados da origem. **Tipo B:** o perfil encontrado na origem filtra uma base do destino (a do desafio ou a de uma sessão escolhida).

## Decisões de engenharia

- **Estatística honesta em todas as telas:** intervalo de confiança, teste de hipótese, correção para muitos testes e selo de evidência em cada afirmação (forte, indício, sem evidência). Quando os dados não mostram diferença, o sistema diz isso e **prova que enxergaria um efeito real** (teste de sanidade com efeito injetado, no 004).
- **Sem vazamento:** o score de Leads não usa a duração total do ciclo, que só se conhece depois do fechamento. A validação é feita numa foto do passado.
- **Análise salva:** o resultado fica na pasta da sessão, com uma assinatura dos dados, do De/Para, das premissas e do código. Só é refeito se algo disso mudar.
- **Premissas editáveis** (custo/hora, metas, % de recuperação etc.) ficam visíveis na tela, e todo impacto estimado aponta a premissa usada.
- **Dependências com versão fixa** e `iniciar.py` só com a biblioteca padrão, para rodar do zero no Python 3.11 a 3.14.
