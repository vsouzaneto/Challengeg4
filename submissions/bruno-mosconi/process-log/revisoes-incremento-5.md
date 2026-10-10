# Incremento 5 ("Como funciona") e D46–D49: revisor, testador de uso e o que foi feito

A página nova fica em `solution/src/ui/HowView.tsx`. Os números vêm de `solution/src/core/evidence.ts`, que usa as mesmas funções da auditoria. O teste `evidence.test.ts` confere esses números contra `auditoria-ts.md`. O modelo de ML é a única fonte externa: a saída do `analysis/significancia_ml.py` (semente 0), lida por vendedor e data. Ele é comparado nas mesmas unidades do backtest da regra final, e o `npm run auditoria` agora grava essa linha.

## Comandos

| Comando | Resultado |
|---|---|
| `npm run check` | Tipos ok. Biome sem erro, com 8 avisos (os mesmos do incremento 4). Vitest: 80 testes passando |
| `npm run e2e` | 16 testes passando (eram 12) |
| `npm audit --omit=dev` | 0 vulnerabilidades |
| `npm run personas` | 12 testes passando; medições abaixo |
| `npm run prints` | 8 testes passando. 37 prints em WebP e 2 vídeos em VP9, 4,1 MB em `screenshots/03-app/` |
| `npm run auditoria` | Mudaram só 2 linhas: o ML na regra final |

## Revisor (1 rodada)

Veredito: "aprovar após correções".

| Achado | Reproduzido? | O que foi feito |
|---|---|---|
| IMPORTANTE 1. A prova 3 chama a taxa de ganho entre concluídos de "chance de fechar" | **Sim.** `dimensionTest` usa só concluídos. Na coorte, vendedor e regional mudam o resultado (p < 0,001) | O texto diz que olhou a taxa de ganho ("de cada 100 negócios concluídos, quantos foram ganhos"). "Abaixo de 5 em 100" virou "seria sinal de que o fator muda a taxa". O título pedido pelo Bruno (CA16) ficou. O quadro "Para o gestor" explica a outra metade: o vendedor muda quanto fica aberto |
| IMPORTANTE 2. "O vendedor muda quanto esfria" sem o aviso da D3 | Sim | O quadro diz que os dados não separam o efeito do vendedor do efeito da carteira e da região. Nos detalhes, a regional também aparece. Há teste no e2e |
| IMPORTANTE 3. "É o que a tela Minha equipe mostra" iguala duas medidas diferentes | Sim. O quadro mostra de 0% a 31% (coorte de 31/12); a equipe mostra o % do valor frio na data | O texto diz só que a equipe mostra quanto da carteira de cada um está frio, e informa a data. Nos detalhes, consta que essa coorte não tem a correção de entrada tardia |
| IMPORTANTE 4. O número do ML na tela (43,18%) não existe na auditoria nem nos documentos (que trazem 45,03%, da preparação) | Sim | A linha entrou no `npm run auditoria`. **Pendente:** `AGENTS.md` §7, `docs/analise-exploratoria.md` e `docs/como-escalar.md` ainda citam só o número da preparação. Ficam para a revisão dos documentos antes do PR (o `AGENTS.md` pede confirmação) |
| IMPORTANTE 5. As frases da prova 1 são fixas, mas a curva segue a data | Não reproduziu: nas 4 datas, a curva real nunca sobe e a de "só concluídos" termina acima de onde começa | Teste novo em `model.test.ts`, que roda todas as datas disponíveis. Se uma data nova quebrar a frase, o teste falha |
| IMPORTANTE 6. O herói de ação fala "o seu nº 1" ao gestor e afirma que a prospecção "pesa mais" sem conta | Sim. Vindo da equipe, aparecia "A semana de Anna" e depois "O seu nº 1" | "O nº 1 de Anna" quando vem da equipe (e2e novo). "O que mais pesa" virou "Por isso a semana começa pela prospecção", que é a regra da D46, e não uma comparação |
| SUGESTÃO 7. "Comece pelos frios." soa como "trabalhe os frios primeiro" | Sim | "Comece atualizando os frios." (D46 atualizada) |
| SUGESTÃO 8. O teste da saudação não prova que ela conta só os 5 primeiros | Sim | Teste sintético: quando só o 6º esfria, a frase é "Nenhum deles esfria nesta semana."; outro cobre "1 fica frio". O laço da D46 roda todas as datas disponíveis |
| SUGESTÃO 9. Os exports de chat têm caminhos locais e IDs de sessão | Sim, por leitura | Não versionados. Vai ao Bruno, que já revisaria os exports |
| SUGESTÃO 10. `HowView.tsx` com 475 linhas num único componente | Sim | Não mudou. A página é uma leitura de cima para baixo, e o e2e cobre o texto. Divide-se se crescer |

## Testador de uso (1 rodada; Head de RevOps e a vendedora da D46)

| Tarefa | Resultado |
|---|---|
| RevOps: entender o score em 2 minutos | Conseguiu. A explicação fica possível depois da primeira tela, em menos de 1 minuto de leitura |
| RevOps: por que vendedor e produto não entram | Conseguiu com dificuldade (a conclusão não estava escrita); corrigido |
| RevOps: como a regra foi validada | Conseguiu |
| Anna (D46 e D47) | Conseguiu: "Comece pela prospecção.", com o herói de 55 contatos e US$ 77.845 |

Explicação que a RevOps daria ao time, segundo o testador: "A lista põe na frente o negócio que mais pode render: preço de lista vezes a chance de fechar, que depende só da idade. De cada 100 negócios que chegaram a 0–29 dias ainda em andamento, 47 fecharam; aos 120–138 dias, 9; acima de 138, nenhum. Potencial é o preço vezes essa chance: US$ 5.482 × 47% = US$ 2.577. O score é a posição do potencial, de 0 a 100."

| Achado | O que foi feito |
|---|---|
| MÉDIO. O passo 3 (score) ficava cortado na primeira tela em 1280 | O subtítulo cabe numa linha, e os espaços diminuíram. Em 1280 × 860, os três passos terminam em 834 px. Em 1280 × 800, a tabela cabe (e2e) e o passo 3 fica abaixo |
| MÉDIO. A frase do score ("Mais potencial que 98% dos 298 negócios…") é difícil de repetir | "Score 98: o potencial dele passa o de 98 de cada 100 negócios quentes e esfriando de todos os vendedores." No painel do negócio, a frase não mudou (D45) |
| MÉDIO. A prova 3 não dizia a conclusão | "Por isso a lista não usa nenhum deles." e "Abaixo de 5 em 100" |
| LEVE. O título da tabela é longo | Não mudou: é a mesma frase "De cada 100…" do painel, aprovada na D42 |
| LEVE. Em 390, a linha "Frio" fica sob a barra de abas na primeira tela | Não mudou: aparece com a rolagem, e a página tem folga embaixo |
| LEVE. O cartão do nº 1 da Anna mostra o score 0 sem rótulo | Não mudou: é o padrão dos cartões, com nome acessível "Score 0 de 100", e o herói explica o score 0 |
| LEVE. Trocar "Sem empresa no CRM" por "Empresa não informada" | Não mudou: a frase foi aprovada na D44 |

### Medições (`npm run personas`, depois das correções)

Tempo da máquina do clique até a resposta estar na tela, com o movimento ligado, em 1280 e 390 px, claro e escuro.

| Persona | Pergunta | Tempo | Sem rolar |
|---|---|---|---|
| RevOps | a tabela da regra | 106 a 124 ms | sim, nas 4 telas (altura de 800 e 844 px) |
| RevOps | os três passos do exemplo | na mesma tela | não em 800 px de altura; sim em 1280 × 860 (print `09-como-funciona-tela`) |
| RevOps | leitura do texto principal | regra: 105 palavras, cerca de 32 s; página inteira sem os detalhes: 628 palavras, cerca de 3 min a 200 palavras por minuto | — |
| Vendedora (Anna) | por onde começar | 93 a 97 ms | sim |
| Vendedora (Anna) | por que o nº 1 está em primeiro | 436 a 443 ms (inclui 0,4 s de espera pelo painel) | sim |
| Vendedora (Anna) | o que fazer com os frios | 27 a 57 ms | sim |
| Gestor | quanto valor está frio | 99 a 103 ms | sim |
