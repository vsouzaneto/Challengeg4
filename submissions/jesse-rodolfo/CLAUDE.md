# CLAUDE.md: AI Master Challenge G4, Case 002 (Redesign de Suporte)

Este arquivo dirige a sessão. Leia inteiro antes de qualquer ação.

## Quem está no comando

Jessé Rodolfo Machado decide. A IA analisa, propõe, constrói e mede.
Toda decisão de escopo, de interpretação dos dados e de "o que não automatizar" é do Jessé e vai registrada no process log com a voz dele.

Método do Jessé, nesta ordem, sempre: mapear o processo, eliminar o que não precisa existir, padronizar, automatizar, medir. IA entra por último.

## O desafio, em uma linha

Diretor de Operações de uma empresa de tecnologia com cerca de 30 mil tickets por ano quer três coisas: onde a operação perde tempo, o que pode ser automatizado com IA, e algo rodando que prove que funciona.

Brief completo: challenges/process-002-support/README.md do repositório original.

## Regras do G4 que eliminam se quebradas

1. Só mexer em arquivos dentro de submissions/jesse-rodolfo/. Nada fora.
2. Process log obrigatório e verdadeiro. Sem process log = desclassificado.
3. Eles já rodaram o brief no Claude, GPT e Gemini e têm essas respostas. Parecer com isso = eliminado. O valor está no julgamento e no contexto do Jessé.
4. Automatizar 100% é red flag. Mostrar onde parar é critério de qualidade.
5. Protótipo medido em amostra aleatória, nunca em exemplos escolhidos a dedo.
6. Usar os dois datasets. Dataset 1 tem métricas, dataset 2 tem texto classificado.
7. Documento curto. Cinco páginas que resolvem valem mais que quarenta.
8. Orçamento de tempo: 4 a 6 horas. Horas extras não ganham ponto.

## Regras de conduta da IA nesta sessão

- Nenhum número é afirmado sem código rodado nesta sessão. Se não rodou, diga "hipótese, não verificado".
- Toda premissa de cálculo (tempo de tratamento, custo hora, taxa de retrabalho) vai escrita ao lado do número, em faixa quando houver incerteza.
- Antes de calcular qualquer média, verificar unidade e significado da coluna. Coluna chamada "tempo" pode ser carimbo de hora e não duração.
- Quando corrigir uma afirmação anterior, dizer explicitamente "corrijo: eu disse X, o correto é Y, porque Z". Essas correções são o material do process log.
- Não escrever texto que serviria para qualquer empresa. Cada parágrafo precisa de um dado deste dataset ou de uma decisão do Jessé.
- Não propor ferramenta, modelo ou arquitetura antes do diagnóstico estar fechado.
- Não commitar dados brutos. Só script de download e amostra pequena.
- Responder em português, direto, sem travessões, sem adjetivos de autoelogio.

## Os cinco blocos (relógio ligado)

| Bloco | Tempo | Entrega | Commit |
|---|---|---|---|
| 0 Setup e leitura do problema | 30 min | PROCESS-LOG.md com hipóteses escritas ANTES de abrir dados | `bloco0: leitura do problema e hipoteses` |
| 1 Auditoria dos dados | 45 min | docs/auditoria-dados.md: esquema, nulos, unidades, o que dá e o que não dá para concluir | `bloco1: auditoria dos dados` |
| 2 Diagnóstico | 60 min | solution/01-diagnostico.md: gargalos, o que move satisfação, desperdício em horas com premissas | `bloco2: diagnostico` |
| 3 Proposta de automação | 45 min | solution/02-proposta-automacao.md: fluxo, portão humano, o que não automatizar com exemplos, ROI em faixa, piloto | `bloco3: proposta` |
| 4 Protótipo | 90 min | solution/prototipo/: classificador medido, limiar de confiança, interface mínima, testes de regressão | `bloco4: prototipo` |
| 5 Fechamento | 30 min | README.md no template, limitações, process log revisado, PR | `bloco5: fechamento` |

Ao fim de cada bloco: Jessé escreve a entrada do process log, a IA não escreve por ele. A IA pode listar o que fez para o Jessé editar.

Commit SEMPRE pelo script, nunca com git add direto. O .gitignore da raiz do G4 ignora submissions/ (não pode ser editado) e um `git add -f` cru subiria os CSVs brutos. O script força só o que deve subir e trava se entrar CSV ou arquivo fora da pasta:
`bash commit.sh "<mensagem do bloco>"` seguido de `git push`.

## Perguntas de auditor que a IA deve responder no Bloco 1 antes de qualquer análise

- Quantos registros existem de fato? Bate com os "30 mil" do brief?
- First Response Time e Time to Resolution são durações ou carimbos de hora? Em que unidade?
- Customer Satisfaction Rating está preenchido para quais tickets? Varia com alguma coisa ou parece uniforme?
- O texto de Ticket Description é real ou tem cara de gerado (placeholders, repetição, frases idênticas)?
- As 8 categorias do dataset 2 correspondem a algo no dataset 1? Se não, como o classificador vai ser testado em texto do dataset 1?
- Há tickets duplicados, datas impossíveis, prioridades sem padrão?

Se os dados forem sintéticos ou tiverem campos sem sentido, isso é uma descoberta a ser escrita no diagnóstico, não um problema a esconder.

## Lente de desperdício (do chão de fábrica para o suporte)

Espera: ticket parado sem dono, pendente de resposta do cliente, fila por canal.
Retrabalho: reabertura, troca de canal, resposta que não resolve.
Movimentação: repasse entre times, reclassificação manual.
Superprocessamento: humano fazendo triagem que uma regra ou um classificador faz.
Para cada um: quantas horas por mês, com premissa escrita, e quanto é recuperável.

## Portão humano (do que o Jessé aprendeu operando agentes)

Agente de IA em cima de processo mal definido não escala. Antes de automatizar um tipo de ticket, o processo dele precisa ter entrada, critério e padrão de resposta definidos.
Nunca automatizar sem portão: classificação abaixo do limiar de confiança vai para humano; cliente já insatisfeito vai para humano; disputa financeira vai para humano; crítico vai para humano com sugestão da IA, não com resposta automática.
Medir num piloto (um canal, um tipo de ticket) antes de expandir.

## Estrutura da pasta

```
submissions/jesse-rodolfo/
  README.md                  template do G4 preenchido
  CLAUDE.md                  este arquivo (vai como evidência)
  solution/
    01-diagnostico.md
    02-proposta-automacao.md
    prototipo/               código, setup, testes, resultados da avaliação
    data/
      download.sh            baixa os datasets do Kaggle
      sample/                amostra pequena para demo
      raw/                   ignorado pelo git
  process-log/
    PROCESS-LOG.md
    screenshots/
    chat-exports/
  docs/
    auditoria-dados.md
```

## Evidências a produzir durante, não depois

- Commits por bloco com as mensagens da tabela.
- PROCESS-LOG.md com horário de início e fim de cada bloco.
- Screenshot no momento de cada correção da IA.
- Export da sessão ao final (transcript do Claude Code ou prints).
