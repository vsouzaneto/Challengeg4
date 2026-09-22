# ADR 0008 — Executar procedimentos e medir sua contribuição

Data: 21/09/2026. Status: implementado em demonstração local com sistemas fictícios.

Dhiego considerou baixo o retorno anterior e determinou que a solução aportasse valor. A conta agregada não fundamentava a escolha do produto. A nova implementação elimina conferências manuais repetitivas na demonstração e distingue participação do cliente, do atendente e do investigador.

## Decisão

Implementar três caminhos no mesmo fluxo: recuperação elegível pelo autosserviço; atendimento preparado por contexto; investigação humana. A IA extrai intenção, tentativas e sinais citados. Registros são consultados por adaptadores locais explícitos; contexto de identidade/estado nunca vem do LLM. A política determinística não usa score como autorização.

Recuperação exige escolha explícita do cliente e conta elegível no cenário. Token vinculado à execução, expirável e de uso único; reconsulta do contexto antes da conclusão; estado e eventos persistidos em transação. Falha pode ser informada antes ou depois da conclusão e transfere histórico para suporte. O provedor é simulado, sem senha/email real e sem alegação de autenticação de produção.

Pedidos múltiplos impedem resposta única presumidamente completa. O caso real de férias na rodada de IA reuniu fontes, mas permaneceu sem rascunho, por essa condição. Atendimento preparado com tentativa de reset frustrada apresenta rascunho editável e mantém a evidência. Incidente permanece investigando após recebimento, sem encerramento artificial.

## Valor

Separar volumes exclusivos, antes/depois, sucesso e custo de falha. O cenário por processo atribui a maior parte da capacidade à preparação, não ao reset isolado. O modelo também mostra perda de valor quando a revisão demora ou a recuperação falha. Os ganhos são hipóteses de processo; os testes demonstram software, não impacto medido.

## Consequências

Mantidos classificador e recap anteriores com histórico de avaliação. A extração restrita tem verificação de desenvolvimento própria, insuficiente para produção. Integrar fontes reais, autenticar usuários e validar elegibilidade/qualidade são trabalhos futuros. Nenhuma publicação, ação externa de atendimento ou saving efetivo ocorreu.

[Processos e economics](../valor-por-processo.md) · [script de verificação com IA](../../solution/avaliar_fluxos.py).
