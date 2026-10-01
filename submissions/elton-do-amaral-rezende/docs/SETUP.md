# Lead Scorer — Challenge 003

Aplicação em português para escolher quais oportunidades trabalhar primeiro, entender os motivos e executar a próxima ação. A rotina apresenta até dez missões por lote, com um card expandido por vez.

**Estado:** núcleo implementado com dados reais, avaliação histórica e persistência local. Publicada com acesso público, sem login: [abrir aplicação](https://lead-scorer-missoes-003.pokernachapa.chatgpt.site). O diário simples do trabalho está em [process-log/DIARIO.md](../process-log/DIARIO.md).

## Executar

Execute os comandos abaixo a partir da raiz do projeto, que contém solution/, mesmo que este guia esteja em docs/.

Requisito: Node.js 22.12+ da linha 22, linha 24 ou 26+. Validado com Node.js 22.14.0 e npm 10.9.2 no Windows. Dependências exatas e lockfile incluídos.

```sh
cd solution
npm ci
npm run prepare:data
npm run evaluate
npm test
npm run build
npm run dev
```

Abrir a URL informada pelo Vite. `dev` e `build` também regeneram os dados e a avaliação automaticamente; nenhuma conta Kaggle ou download é necessário em tempo de execução. Os CSVs originais estão incluídos sob a licença CC0 declarada na fonte. `npm run preview` serve o build de produção.

## Como usar

1. A primeira visita já abre a carteira de **Zane Levy**, com prioridades altas, produtos variados e datas de engajamento no Top 10. Use **Sua carteira** para trocar de vendedor. Na próxima visita, sua última escolha será lembrada.
2. Leia o score, os fatores e a próxima ação da missão expandida. Abra outro card para mudar somente a seleção.
3. **Copiar orientação** copia o texto, sem concluir. **Feito** registra a ação declarada pelo vendedor. **Adiar para amanhã** retira a missão do trabalho de hoje, sem contar para a meta.
4. Quando o lote termina, as próximas prioridades são carregadas automaticamente. O contador do lote e o total do dia são distintos.
5. Use **Desfazer** no aviso ou no histórico. Em lote anterior, a missão retorna por uma fila própria; no atual, volta à posição original.

A meta inicial é de dez ações únicas, ou a quantidade disponível se menor. A sequência usa dias consecutivos com metas realmente cumpridas. Trocar vendedor isola o histórico. O método, filtros de equipe e exportação CSV ficam em acessos secundários.

## Dados e priorização

- 8.800 oportunidades, 85 contas, sete produtos e 35 nomes na equipe. Há 2.089 oportunidades abertas; nem todo nome de equipe possui carteira no pipeline.
- Alias `GTXPro → GTX Pro` aplicado em 1.480 registros, preservando o valor original. 1.425 oportunidades sem conta; nenhum vínculo desconhecido nos arquivos congelados.
- Score operacional: `round(100 × (0,65H + 0,25A + 0,10V))`. H combina taxas suavizadas por produto/setor/conta; A usa idade desde o engajamento; V usa preço de catálogo em escala logarítmica.
- Os fatores, fallbacks e amostras vêm do próprio motor. Não há LLM gerando justificativas em tempo de execução.
- Referência histórica do score: **31/12/2017**. Calendário das ações: dia real em **America/Sao_Paulo**.

O score não é probabilidade de fechamento ou receita esperada. Preço de catálogo não é valor negociado. O dataset é público e contém empresas fictícias; a aplicação não representa uma carteira atual de clientes.

## Resultado histórico

Regra candidata mantida com os pesos originais, sem ajuste no horizonte final. Corte em 30/09/2017; resultados até 31/12/2017. Histórico com 4.726 encerrados; 2.409 candidatos, dos quais 559 Won, 376 Lost e 1.474 sem resultado conhecido.

No Top 10 de cada um dos 30 vendedores com candidatos, o score selecionou 300 negócios: **145 Won, 112 Lost e 43 censurados**. Taxa de vitória entre resolvidos: **56,4%**; referência aleatória com seed fixa: **60,7%**. Lift do score entre resolvidos: **0,944**. O score não demonstrou superioridade nessa métrica. A diferença de cobertura de resolvidos impede interpretar a captura de vitórias como ganho causal de conversão.

[Validação e comparações completas](VALIDATION.md). Métricas por vendedor e K=10/20/50 são regeneradas em `solution/data/generated/evaluation-report.json`.

## Estrutura

```text
Referencias/                 plano original, plano por etapas e imagem
solution/
  data/raw/                 CSVs originais e proveniência
  data/generated/           manifestos, qualidade, estatísticas e avaliação
  scripts/                  preparação e avaliação em TypeScript
  src/domain/               ingestão, scoring, avaliação, datas e missões
  src/components/           cards, fila e progresso
  src/data/                 JSONs gerados consumidos pelo app
  src/state/                validação, armazenamento e integração React
  tests/                    integridade, vazamento, fila e jornada
docs/                       dados, scoring, validação e entrega
process-log/                diário, decisões e capturas reais
```

Os comandos do produto funcionam a partir de `solution/`; a solução pode ser transportada inteira para a pasta de submissão.

## Verificações e limites

39 testes aprovados, verificação de tipos e build concluídos. Uma cópia limpa instalou, preparou os dados, avaliou, testou e compilou sem os artefatos do ambiente anterior. Revisão real no navegador: seleção da missão 7, feito, adiamento, desfazer, restauração e versão de celular. Capturas em `process-log/screenshots/`.

- Estado local ao navegador, com versão de contrato/dataset e vendedor. Não autentica identidade, não sincroniza dispositivos ou abas em tempo real e não atualiza CRM. Falha ou corrupção do armazenamento usa fallback na sessão e aviso.
- Feito não comprova contato ou venda; adiar não altera score ou estágio. Não existe telefone ou URL de CRM nos dados, por isso o app não mostra um link inventado.
- Backtest parcial: cadastros atuais sem snapshots, viés entre resolvidos, Prospecting sem data de criação e política de adiamento sem validação histórica.
- Os dados estáticos estão no bundle: o build informa um chunk acima de 500 kB (cerca de 255 kB gzip). É um compromisso desta demonstração sem API; dividir/carregar dados por carteira é uma evolução de desempenho.

## Entrega e referências

[Dados](DATA.md) · [Scoring](SCORING.md) · [Validação](VALIDATION.md) · [Plano por etapas](../Referencias/PLANO_IMPLEMENTACAO_LEAD_SCORER.md) · [Diário](../process-log/DIARIO.md).

A aplicação está pública para revisão. O README da raiz segue o template oficial, preenchido com Elton do Amaral Rezende, GitHub MunhozVs e LinkedIn. A candidatura foi enviada em 01/10/2026 pelo [Pull Request #173](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/pull/173). [Registro da entrega](ENTREGA.md).
