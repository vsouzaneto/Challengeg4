# Verificação final — 30/09/2026

O produto das etapas 0–10 está implementado. A submissão oficial é um passo separado, conforme docs/ENTREGA.md.

| Entrega | Evidência |
| --- | --- |
| Fonte, licença e CSVs reproduzíveis | data/raw/provenance.json, docs/DATA.md; cinco CSVs incluídos; manifesto SHA-256 regenerado |
| Ingestão e joins | 8.800 oportunidades, 2.089 abertas, 1.480 aliases, nenhum vínculo desconhecido; testes de integridade |
| Motor e explicações | engine.ts; candidato sem resultado futuro; pesos congelados; testes de invariância e fallbacks |
| Missões e progresso | queue.ts; seleção independente, até dez, ações idempotentes, lotes, retornos, meta e sequência; testes puros e interface |
| Persistência e calendário | useDailyQueue.ts/storage.ts; namespaces vendedor/dataset; restauração, virada diária e falhas; testes |
| Interface | revisão real desktop/celular, missão 7, feito, adiar, desfazer e recarregar; screenshots/desktop.jpg e mobile.jpg; console sem erros |
| Avaliação | corte 30/09/2017, horizonte 31/12/2017; 2.409 candidatos, censura explícita, seis métodos e K=10/20/50; docs/VALIDATION.md |
| Execução independente | npm ci já verificado na cópia limpa; última versão: npm test (31 testes/5 arquivos), npm run build (prepara dados, avalia, checa tipos e compila) aprovados |
| Documentação | README, DATA, SCORING, VALIDATION, ENTREGA e diário atualizados |

Acessibilidade revisada manualmente e no código, sem certificação formal. O bundle contém os dados estáticos e gera aviso de tamanho; aproximadamente 216 kB gzip de JavaScript. O score não demonstrou superioridade entre os resolvidos. Registros são locais ao navegador e não atualizam CRM.

Publicação privada confirmada pela hospedagem com status succeeded em 30/09/2026: [abrir aplicação](https://lead-scorer-missoes-003.pokernachapa.chatgpt.site). Site appgprj_6abd26992f4c8191b288046cfe55c4c1; primeira publicação appgdep_6abd38555e7c8191acc0f6fec5b59d18. O build publicado passou nas verificações descritas acima.

