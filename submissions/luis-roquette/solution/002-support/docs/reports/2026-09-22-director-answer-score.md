# Medição da resposta ao Diretor — Goal ≥ 9,5

Data: 2026-09-22

## Rubrica

A média usa três dimensões de peso igual: diagnóstico operacional, decisão de automação
e prova funcional. Uma nota alta exige números reproduzíveis, limites explícitos e uma
próxima decisão executável; aparência visual isolada não aumenta a nota.

| Estado | Diagnóstico | Automação | Prova | Média |
|---|---:|---:|---:|---:|
| Baseline | 8,8 | 7,2 | 8,5 | 8,0 |
| Resposta executiva única | 9,0 | 7,7 | 8,8 | 8,5 |
| Confiabilidade e IC95% | 9,5 | 7,7 | 8,8 | 8,7 |
| Risco-cobertura por domínio | 9,5 | 9,2 | 9,0 | 9,2 |
| Impacto e contrato do piloto | 9,5 | 9,5 | 9,3 | 9,4 |
| Gate remoto + prova pública | 9,6 | 9,5 | 9,7 | **9,6** |

## Evidência que fecha o Goal

1. A rota inicial responde às três perguntas em uma tela e separa fatos, medições e projeções.
2. Cobertura, amostra, IC95% e suporte impedem que `n=15` pareça conclusão robusta.
3. Customer declara `0%` seguro; IT declara `37,43%` de cobertura e `10,64%` de risco no
   limiar travado, sem retunar o teste final.
4. Os cenários de `150`, `625` e `1.600 h/ano` são projeções editáveis sobre o contexto
   de 30 mil tickets, sem inventar custo.
5. O piloto shadow tem amostra, baseline, métricas, guardrails e decisão go/no-go.

## Condição para nota final

A nota `9,6/10` foi registrada após `251` testes e Ruff passarem no Codespace sobre o SHA
de aplicação `1dddf03e3bc07464c2574ec43eb1b74f02fa9c2d`, seguido da confirmação pública das
duas telas executivas. É uma avaliação interna pela rubrica acima, não uma nota prometida
pelo avaliador.
