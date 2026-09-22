# [Submission] Dhiego Spinillo — Challenge 002

Redesign de suporte com diagnóstico dos dois datasets e três caminhos executáveis: autosserviço elegível, atendimento preparado e investigação humana. O D1 não permite medir desperdício em horas: não há abertura e 49,3% dos pares temporais disponíveis estão invertidos. A proposta prioriza reduzir busca/reconstrução de contexto, com instrumentação e piloto para verificar o ganho.

No D2, o classificador local treinado concordou com 86% dos 800 rótulos reservados; Jev por definições, sem treino específico, com 45,25%. Também processei os 47.837 registros com o modelo congelado e preservei partições e resultados por linha. A concordância global inclui treino e não substitui a avaliação original. O limiar não atingiu a meta de erro no teste; a categoria permanece assistida.

## Onde olhar

| Material | Caminho | Para quê |
|---|---|---|
| Entrada e resumo | `submissions/dhiego-spinillo/README.md` | Respostas ao diretor, roteiro e links para a entrega. |
| Diagnóstico | `docs/resumo-executivo.md` e `solution/visual/index.html` | Qualidade das bases, achados e limites. |
| Comparação | `solution/visual/comparacao-local-jev.html` e `solution/comparacao.md` | Local × Jev, método, sensibilidade e guardrail de revisão. |
| Protótipo | `solution/` | Aplicação local, fluxos, modelo, testes e instruções Docker. |
| Processo | `process-log/` | Registro cronológico, decisões, evidências e capturas. |

## O que rodar

Na pasta `submissions/dhiego-spinillo/`, executar `docker compose up --build` e abrir `http://127.0.0.1:8766`.

- IA extrai intenção, tentativas, risco, temperatura e menção de prazo com citações; regras controlam procedimentos e estados. Sem chave, a demo identifica o uso de regras lexicais. Temperatura e urgência não reordenam a fila; a demo declara o SLA indisponível quando faltam eventos e política de prazo.
- Recuperação conclui no provedor simulado com token de uso único; falha transfere histórico. Atendimento preparado admite rascunho editado/aprovado; investigação permanece aberta.
- Consultas, contas e ações usam fontes locais fictícias explicitamente identificadas. Não há autenticação de produção, envio externo de respostas ou alteração de contas reais.
- `/classificador` preserva classificação/ficha anterior; `/resumo`, `/diagnostico` e `/valor` apresentam síntese, análise e economics por processo.

## Evidências e limites

- 219 testes passam localmente e no Docker. Reprodução sem chave em instância limpa foi verificada.
- As 1.192 previsões originais de validação/teste foram reproduzidas exatamente na rodada integral. CSV por registro, hashes, scripts e relatórios incluídos, sem redistribuir os datasets completos.
- Sete cenários conhecidos exercitados com IA: seis extrações aceitas e um fallback. Isso demonstra execução, não avaliação semântica independente ou taxa de resolução autônoma.
- Recap experimental separado, com limitações de fidelidade documentadas. Nenhuma alegação de sentimento validado ou ganho operacional medido.
- Cenários econômicos separam capacidade e despesa evitada, revisão e falhas. Elegibilidade, tempos e custos continuam premissas, com condição de equilíbrio e piloto proposto.
- One-pager, capturas desktop/celular e dez screenshots da execução local final, roteiro, process log, ADRs, pareceres de Claude/Grok/Codex e decisões do candidato disponíveis pelo README. Protótipo executado localmente, sem hospedagem em VPS. Credenciais e banco local não fazem parte do Git.

## Checklist

- [x] Challenge 002 escolhido e README completo lido.
- [x] Solução e process log em `submissions/dhiego-spinillo/`.
- [x] README segue o template de submissão e contém instruções de setup.
- [x] Protótipo, análise, comparativo e evidências podem ser revisados localmente.
- [x] 219 testes passam localmente e no Docker.
- [x] Nenhum arquivo fora da pasta da submissão foi alterado.

Alterações restritas à pasta da submissão. Este arquivo versiona o título e a descrição da PR.
