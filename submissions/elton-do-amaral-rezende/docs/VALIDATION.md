# Validação e resultados

## Verificações de software

39 testes em cinco arquivos cobrem CSV, cardinalidade, alias, vínculos ausentes/desconhecidos, scoring reproduzível, contribuições, fallbacks, exclusão de futuro, censura, fila estável, seleção, idempotência, adiamento, desfazer em lotes anteriores/esgotados, metas, sequência, storage corrompido/bloqueado e jornada React.

A jornada verifica a carteira inicial automática, a preservação da última escolha, a recuperação de uma escolha inválida, recarregar, isolamento de vendedores, carregamento do lote seguinte, cópia sem conclusão, falha de cópia, virada do dia ao retornar à aba e virada antes de uma ação. Tipos e build aprovados. A cópia limpa, inicialmente sem dependências e JSONs gerados, instalou e executou preparação, avaliação, testes e build. Na auditoria de 01/10, a sequência foi repetida em uma pasta nova no formato de submissão, com a versão atual. Detalhes em AUDITORIA.md.

No navegador real: missão 7 expandida com anteriores acima; feito, adiar, desfazer, histórico e restauração conferidos. Revisão em desktop e viewport de celular, com ações legíveis e sem rolagem horizontal da página. Capturas: `../process-log/screenshots/desktop.jpg` e `mobile.jpg`. Os registros de teste do navegador foram desfeitos ao final. Console de erros consultado: nenhuma mensagem de erro.

Os testes essenciais usam funções puras e Testing Library. A revisão visual foi manual; não há suíte de navegador automatizada. Contraste e foco foram revisados no código e na interface, sem afirmar certificação formal de acessibilidade.

## Protocolo temporal

Histórico de resultados conhecidos até 30/09/2017: 4.726 negócios. Candidatos com engage_date <= corte e close_date ausente ou posterior: 2.409. O contrato de scoring reconstruído usa Engaging, sem resultado futuro. Horizonte até 31/12/2017: 559 Won, 376 Lost e 1.474 censurados.

Comparação da regra congelada, variantes sem valor/idade e referências por preço, engajamento recente e aleatório. Seed aleatória: 20260930. Empates por ID. Todos os métodos usam os mesmos candidatos. Há 30 vendedores com candidatos; os outros nomes da tabela de equipe não entram como carteiras fictícias na avaliação.

## Resultado principal — K=10 por vendedor

Resumo agregado de 300 oportunidades selecionadas por método:

| Método | Won | Lost | Sem resultado | Vitória entre resolvidos | Lift entre resolvidos |
| --- | ---: | ---: | ---: | ---: | ---: |
| Score | 145 | 112 | 43 | 56,42% | 0,944 |
| Sem valor | 140 | 126 | 34 | 52,63% | 0,880 |
| Sem idade | 76 | 62 | 162 | 55,07% | 0,921 |
| Preço de catálogo | 67 | 57 | 176 | 54,03% | 0,904 |
| Engajamento recente | 144 | 120 | 36 | 54,55% | 0,912 |
| Aleatório | 82 | 53 | 165 | 60,74% | 1,016 |

A taxa entre todos os candidatos resolvidos é 559/935 = 59,79%. O score captura 145/559 = 25,94% dos Won conhecidos no horizonte; Won/K = 145/300 = 48,33% é vitória observada no período. O aleatório captura 82/559 = 14,67%, com Won/K = 27,33%. Essas diferenças coexistem com coberturas de resolvidos muito diferentes: 257 no score e 135 no aleatório.

**Conclusão:** o score não superou a referência aleatória na taxa entre resolvidos e não demonstrou ganho de conversão. A idade privilegia negócios cuja resolução acontece dentro do horizonte, o que altera a cobertura; não é evidência causal. Manter como regra operacional explicável, sem promessa preditiva, é a conclusão desta versão. Os pesos não foram alterados para melhorar o resultado final.

`npm run evaluate` regenera o relatório completo em `solution/data/generated/evaluation-report.json`, com métricas por vendedor e K=10/20/50, denominadores, tamanhos reais e casos sem resultado. Denominador zero retorna `null`, não uma taxa inventada.

## Limitações

Cadastros atuais são proxies sem snapshots; não sabemos quando a conta foi preenchida. Há viés ao analisar somente resolvidos, censura de oportunidades e ausência de atividades/transições. Prospecting não é reconstruível sem data de criação. A política de retorno de adiados é testada como comportamento do software, sem validação comercial no backtest. Feito é ação declarada localmente; não é resultado de venda.

Os CSVs vêm de uma empresa fictícia no dataset público. Não representar estes resultados como produção real ou carteira de 2026. Sem integração de contato, autenticação, banco, sincronização ou IA generativa em runtime.
