# Revisão de Codex — comparação

Revisão do protocolo e dos arquivos por agente Codex separado, na mesma sessão. Não equivale a independência da participação anterior de Codex na autoria.

Antes dos resultados: verificar também validação × teste; exigir vetor completo de probabilidades; fixar objetivo do limiar; reportar intervalo pareado e assimetria entre sistema supervisionado e zero-shot.

Após resultados: conferidos 1.192 registros únicos por sistema, partições correspondentes, referências iguais entre sistemas, hashes dos prompts Jev e do artefato local. Não identificou erro que invalide acurácia de86% vs45,25%.

Correções solicitadas e aplicadas: validação de checkpoint por prompt/partição/referência, integridade de relatório e modelo; tratamento de resposta não objeto; NaN/score inválido vai para humano; custo esclarece saída gratuita segundo tabela consultada; Brier preserva arredondamento com limite explícito. O alvo de erro<=5% falhou no teste (44/658=6,69%): toda decisão permanece humana.

Nove pares próximos dentro do teste representam dependência residual, não demonstram vazamento do treino. Sensibilidade sem retreino/remove15casos:785restantes.
