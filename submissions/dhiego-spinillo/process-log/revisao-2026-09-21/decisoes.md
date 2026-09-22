# Confronto dos pareceres e decisões

Claude Sonnet 5 e Grok 4.7 receberam o mesmo `briefing.md`, sem ver o parecer um do outro. Respostas originais, modelos retornados, fingerprints e uso reportado estão nos JSONs. São revisões documentais via OpenRouter; não executaram os scripts nem tiveram acesso aos CSVs completos. Codex fez uma revisão adicional dos arquivos e da consistência dos resultados.

| Questão | Pareceres | Resolução |
|---|---|---|
| Tamanhos do split | Grok identificou ambiguidade entre antes/depois do filtro | Corrigida a narrativa:46.637/400/800 antes,45.790/392/800 depois,855 retirados. Preservado o briefing original como evidência do erro de comunicação. |
| Nove pares próximos no teste | Ambos pediram cautela e sensibilidade | Removidos15registros envolvidos, sem retreino; resultado785casos confirma escolha. Codex distinguiu dependência interna do teste de vazamento do treino, que não foi demonstrado por esses pares. |
| Comparação assimétrica | Ambos destacaram treino supervisionado vs definições | Explicação colocada no relatório e na interface, não apenas no protocolo. |
| Limiar e risco | Grok pediu revisão humana se objetivo falhasse | Meta falhou no teste; confirmação humana para todos. Não anunciar cobertura como automação sem humano. |
| Reduzir escopo | Ambos priorizaram classificação; Claude sugeriu mockup/adiar Jev por falta de resultados no briefing | O lote real já foi concluído sem atrasar a implementação. Entrega mantém tela funcional e correção, para demonstrar uso; não confunde recomendações feitas antes dos resultados com revisão dos resultados finais. |
| Recap sem referência | Ambos recusaram usar acurácia de categoria como validação de compreensão | Avaliação separada em16textos com rubrica, gerador Claude e revisor Grok. Avaliação automatizada exploratória explicitada; sem ganho operacional ou validação humana alegados. |

Não houve votação para declarar números verdadeiros. Contagens, contratos, hashes e testes foram conferidos por código. Divergências e limites permanecem visíveis. O usuário autorizou avançar e concluir; a escolha técnica foi feita por Codex com base na comparação, e ainda será apresentada ao candidato para defesa na entrevista.
