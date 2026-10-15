# Agente 1: Designer front-end / UI-UX sênior

_Escopo: reestruturar o app Streamlit (`solution/03-prototipo/app.py`) para abrir num painel que responda ao Diretor de Operações, na ordem Diagnóstico → O que automatizar / o que não → Prova → Quanto vale → Decisões, sem alterar nenhum número._

## 1. Diagnóstico de UX do app antigo

| Problema | Por que pesa para um Diretor não técnico |
|---|---|
| Abria na aba "Triagem ao vivo" com `selectbox` em "— escolha um exemplo —" e caixa de texto **vazia** | A 1ª impressão era um formulário em branco. Nenhuma das 3 perguntas do enunciado era respondida na tela inicial |
| As respostas estavam espalhadas em 5 abas sem ordem narrativa (Triagem → Fila → Diagnóstico → ROI → Como funciona) | A prova vinha antes da pergunta; o ROI e as decisões ficavam escondidos no fim |
| Diagnóstico só em tabela markdown, com jargão (permutação, p = 0,68, IC) | O argumento mais forte da entrega ("os dados mentem") não tinha nenhum visual |
| Nenhum "O que preciso de você" no app | O enunciado pede decisão; o app não pedia nenhuma |
| Gráficos com legendas técnicas (`auto`/`sugere`/`humano`), pesos no formato americano (2.597), números de confiança sem padrão BR | Ruído de leitura |
| Ticket aleatório re-sorteava a cada interação (semente aleatória em todo rerun) | O texto mudava sozinho ao mexer em qualquer widget |

## 2. Decisões de design e por quê

1. **Painel primeiro, exploração depois.** A 1ª aba ("Resposta ao Diretor") é uma página única com rolagem, em 5 seções numeradas na ordem pedida. As abas seguintes são para quem quer explorar: Triagem ao vivo, Fila real, Calculadora de ROI, Metodologia e limites.
2. **Pirâmide invertida.** Topo: frase-resposta + "Decisão pedida" + 4 cartões (3 perguntas + "Quanto vale?"), cada um com 1 número-chave, uma legenda e uma resposta de 1 frase. Quem lê só a 1ª dobra já tem tudo.
3. **Cada gráfico tem um título que é a conclusão** ("Em 49% dos tickets, a resolução vem antes da 1ª resposta"), e não o nome da variável. A legenda explica em linguagem de negócio.
4. **O diagnóstico ganhou 3 visuais**: histograma das "durações" com os valores negativos em vermelho, barras do CSAT (frequências quase iguais) e a distribuição do acaso (1.000 sorteios) com a linha do gap observado. O p-valor é traduzido para "o acaso empata ou supera os dados reais em 68% dos sorteios". O jargão (p, IC95%, McNemar, Cramér, Bonferroni) foi para a aba Metodologia.
5. **Paleta semântica consistente**: verde #2E7D32 = automático, âmbar #F9A825 = sugestão, vermelho #C62828 = humano, bordô #7F1D1D = escalado para Segurança; azul-petróleo #1E3A5F = destaque neutro (o modelo escolhido, o cenário base); cinzas para contexto e acaso.
6. **Tema robusto a claro/escuro sem `config.toml`**: o CSS (injetado via `st.markdown`) usa só cores semitransparentes (`rgba(127,127,127,.06)`) para fundos e bordas e herda a cor do texto; os gráficos Plotly têm fundo transparente e herdam o tema do Streamlit. Não criei `.streamlit/config.toml`.
7. **Responsivo**: grids CSS de 4 → 2 → 1 colunas (quebras em 900 px e 600 px). Testado num iframe de 390 px: sem rolagem horizontal da página (`scrollWidth = 390`), cartões empilhados.
8. **"Mostre que funciona" dentro do próprio painel**: 4 tickets processados pelo motor real a cada abertura, um para cada saída (Automático → Hardware; Sugestão → Miscellaneous; Humano → Triagem humana; Escalado → Segurança da Informação). Prova que é software rodando, não slide.
9. **Triagem ao vivo nunca abre vazia**: abre em "Hardware rotineiro", com o resultado num bloco colorido pela faixa (fila, modo, confiança, quem executa a ação). Se o usuário apagar o texto, aparece uma orientação no lugar do vazio. O "ticket aleatório" agora tem semente estável e um botão "Sortear outro ticket".
10. **Números no padrão brasileiro em todo o app** (65,5%, 1.218 h, R$ 46.563, pesos 2,597), usando a mesma função de formatação do `01_auditoria_dados.py`.
11. **Nenhum número digitado à mão quando dá para recalcular.** Criei `src/painel.py`, que reproduz os métodos dos scripts oficiais. Isso se mostrou decisivo: durante o meu trabalho, outros agentes alteraram `src/politica.py` (regra de privilégio v2: 27,7% → 23,4%) e o `benchmark.md` (kNN-5: 73,3% → 76,0%). Os números recalculados acompanharam sozinhos; os poucos valores fixos (benchmark do LLM) foram revalidados contra o arquivo novo.

## 3. Nova estrutura (na ordem)

**Aba 1 · Resposta ao Diretor** (abre aqui)
- Cabeçalho: "Resposta ao Diretor de Operações", frase-resposta e "Decisão pedida: aprovar instrumentação + piloto de 4 semanas (seção 5)".
- 4 cartões: 1 · Onde perdemos tempo? (49%) · 2 · O que automatizar? (65,5%) · 3 · Funciona? (9.568) · Quanto vale? (1.218 h, ≈ 101 h/mês, faixa 552 a 2.106 h/ano).
- **Seção 1, Diagnóstico**: 3 gráficos (durações negativas, CSAT uniforme, permutação) + veredito + 4 itens do plano de instrumentação.
- **Seção 2, O que automatizar e o que não**: barra 100% das faixas (65,5 / 23,3 / 11,2) com pílulas de legenda; 3 KPIs (96,4% de acerto; 91,0% certa entre 2; 34,1% → 10,8% fora do domínio); acerto por categoria com a régua de 95%; modelo simples × LLM; 6 cartões vermelhos do "não automatizar", com a % de cada regra e o total (23,4%); o que mais não se automatiza.
- **Seção 3, Prova**: fluxo em 4 etapas + 4 tickets processados ao vivo.
- **Seção 4, Quanto vale**: 3 cenários (base destacado), leitura mensal, ressalvas (tempo liberado ≠ caixa; o que ficou de fora).
- **Seção 5, O que preciso de você**: 3 decisões + piloto em 4 etapas com o critério "avança se". Rodapé com as fontes.

**Aba 2 · Triagem ao vivo**: pré-preenchida; bloco de decisão colorido; por quê; palavras que pesaram; 2 categorias mais prováveis; travas; tickets parecidos; rascunho (Gemini, opcional e bloqueado por política).
**Aba 3 · Fila real (9.568 tickets)**: igual à anterior, com rótulos em português nas faixas e cores da paleta.
**Aba 4 · Calculadora de ROI**: `roi.renderizar` (sem alteração).
**Aba 5 · Metodologia e limites**: testes estatísticos com p-valores, desempenho por faixa com IC95%, tabela completa do benchmark com McNemar, fluxo, tabela de regras, limitações.

## 4. Número exibido → origem

Todos os números do painel são calculados ao abrir o app, salvo os marcados "arquivo".

| Número exibido | Origem (cálculo) | Confere com |
|---|---|---|
| 49%; 1.365 de 2.769 tickets fechados | `painel.diagnostico_ds1()`, mesmo cálculo de durações do `01_auditoria_dados.py` | `auditoria.md` §2 |
| 27 horas (janela dos carimbos) | `diagnostico_ds1()["janela_h"]` | `auditoria.md` §1 |
| 553 / 549 / 580 / 543 / 544 (CSAT); "543 a 580" | `diagnostico_ds1()["csat"]` | `auditoria.md` §2 |
| 0,2 ponto (diferença detectável) | `diagnostico_ds1()["csat_diferenca_detectavel"]` = 0,21 (mesma fórmula de poder do script) | `auditoria.md` §4 |
| 0 de 21 pares associados | `diagnostico_ds1()`: qui-quadrado nos 21 pares | `auditoria.md` §3 |
| 80 combinações; 7,6 h; 8,1 h; 68% (p = 0,68); −4,1 h | `diagnostico_ds1()`: `default_rng(0)`, 1.000 permutações. A média por grupo usa `np.bincount` (mais rápido); verificado: diferença máxima de 5×10⁻¹⁵ h contra o `groupby` original, p = 0,681 nos dois | `auditoria.md` §4b |
| 8.469 tickets (Dataset 1) | `diagnostico_ds1()["n_tickets"]` | `auditoria.md` §1 |
| 47.837 tickets (Dataset 2) | `len(base_ds2())` | `auditoria.md`, Dataset 2 |
| 9.568 tickets de teste | `avaliacao_teste()` (mesma divisão `dividir`, seed 42) | `motor_final.md` |
| 65,5% / 23,3% / 11,2% | `painel.faixas(av)` sobre `MotorTriagem.classificar_lote` | `motor_final.md` §1 |
| 96,4% (acerto automático); 91,0% (certa entre 2) | `faixas(av)` | `motor_final.md` §1 |
| 9,7% (trava de domínio); 1,5% (confiança baixa, aba Metodologia) | `faixas(av)["humano_trava"/"humano_confianca"]` | `motor_final.md` §1 |
| Acerto por categoria: 99,0 / 97,8 / 97,8 / 96,4 / 96,0 / 96,0 / 95,8 / 95,1% | `faixas(av)["por_categoria"]` | `motor_final.md` §2 |
| 34,1% → 10,8% (outro domínio, sem × com travas) | `painel.fora_do_dominio()`, mesmo cálculo do `avaliar_motor.py` §3 | `motor_final.md` §3 |
| 23,4% dos tickets acionam alguma regra; por regra: 0,7 / 2,0 / 2,0 / 10,4 / 3,5 / 7,7% | `painel.politica_ds2()` = `politica.avaliar` nos 47.837 tickets | docstring e `freq_ds2` de `src/politica.py` (v2) |
| 85,0 / 76,9 / 76,0 / 53,5 / 48,0 / 44,0% (modelo × LLM) | **arquivo**: `painel.BENCHMARK_LLM` (as chamadas ao LLM não são refeitas: custam cota) | `benchmark.md` §2, verificado por script linha a linha |
| 552 / 1.218 / 2.106 h/ano; 0,3 / 0,7 / 1,2 pessoa; R$ 21.105 / 46.563 / 80.508 | `roi.calcular(roi.CENARIOS[...], *roi.faixas_de(av))` | `modelo_desperdicio.md` |
| 46 a 175 h/mês; ≈ 101 h/mês; ≈ R$ 3.880/mês | os mesmos valores ÷ 12 | `modelo_desperdicio.md` (101 h/mês; 46 a 175) e relatório (R$ 3,9 mil/mês) |
| 81% do tempo de triagem liberado | 1.218 ÷ 1.500 (`horas_recuperaveis / horas_atual`) | relatório ("~80%") |
| 1,5 / 3,0 / 5,0 min; 30.000 tickets/ano; R$ 38,24/h | `roi.CENARIOS`, `roi.Premissas()` | `modelo_desperdicio.md` |
| 95% (régua), 4 semanas, 3 categorias do piloto | texto da proposta | `proposta.md` §4 |
| Aba Metodologia: IC95% 95,9 a 96,8%; p = 0,80; V = 0,021; McNemar 53 × 21 (p = 0,0003) e 70 × 7; 0,860; 10 testes | **arquivo** (texto) | `motor_final.md` §1, `auditoria.md` §2–4, `benchmark.md` §1–2 |

Verificação automática feita: um script conferiu cada valor acima contra o texto atual dos 4 arquivos `.md` e do `politica.py`: todos "OK".

## 5. Testes

**(a) Python padrão (pandas 2.2.3, Streamlit 1.66.0)**: `AppTest.from_file('app.py', default_timeout=900).run()`. Zero exceções; 1ª execução em ~20 s com o cache do motor. O teste confere 33 números-chave presentes no painel e faz interações:
- a triagem ao vivo abre preenchida ("Hi, my laptop...") com "Fila: Hardware / Automático";
- texto de phishing digitado → "Fila: Segurança da Informação" + alerta "Escalar agora";
- texto vazio → mensagem de orientação (nenhuma tela vazia);
- exemplo em português pelo selectbox → "Triagem humana";
- ticket aleatório + botão "Sortear outro";
- fila real reduzida a 1.000 tickets.
Resultado: **TUDO OK**. O teste não chama o Gemini (a variável `GEMINI_API_KEY` é removida antes).

**(b) venv com pandas 3.0.6 (simula o Cloud)**: mesmo script. **TUDO OK**, zero exceções. Também rodei com `-W error::FutureWarning`, sem falha.

**(c) Visual (Chrome)**: o servidor em `localhost:8510` está com módulos antigos em memória (`KeyError: 'motivo_humano'`, por um objeto do motor em cache de uma versão anterior da classe). Para não mexer nele, subi uma instância própria em `localhost:8511`, já encerrada. Inspecionei a 1.440 px: cabeçalho e cartões, as 3 seções de gráficos, faixas, regras, exemplos, cenários, decisões, Triagem ao vivo e Fila real. Problemas encontrados e corrigidos na iteração:
- anotações sobrepostas no histograma e no gráfico de permutação;
- eixo do CSAT mostrando só "2" e "4";
- a anotação ampliava o eixo do histograma até −120 h;
- rótulos longos espremendo as barras do comparativo com o LLM;
- "99,0%" cortado;
- rótulo "Humano" girado dentro da barra no celular;
- pesos no formato americano.

No celular (iframe de 390 px), os cartões empilham e não há rolagem horizontal. Também deixei o app imune ao cache velho: `motor(versao=2)` e `avaliacao_teste(versao=2)` mudam a chave do cache.

## 6. Limitações

- **O servidor 8510 do Arthur precisa ser reiniciado** (`Ctrl+C` e `streamlit run app.py`) para mostrar a versão nova; o Streamlit não recarrega objetos guardados em `cache_resource`. No Cloud, cada deploy reinicia o processo.
- A 1ª carga no Cloud ganha ~7 s (DS1 fora do domínio ≈ 5 s, política nos 47.837 tickets ≈ 1,5 s, permutação ≈ 0,1 s), tudo em `st.cache_data`.
- O modo escuro não foi inspecionado visualmente: o CSS foi desenhado para funcionar nos dois temas (neutros semitransparentes, cores herdadas), mas não houve captura de tela nesse modo. A largura de celular foi testada por iframe, não num aparelho.
- As capturas finais depois dos últimos ajustes finos (rótulo "◄ impossível", só o percentual dentro da barra de faixas, `cliponaxis`) não puderam ser refeitas porque a extensão do Chrome parou de responder. Esses ajustes passaram nos testes (a) e (b), e o DOM confirmou 5 seções e zero exceções.
- O benchmark do LLM e os valores textuais da aba Metodologia (IC, McNemar, p = 0,80) são fixos, porque recalculá-los custaria cota de API ou bootstrap pesado. Foram conferidos contra os arquivos atuais. Se outro agente reescrever `benchmark.md` ou `motor_final.md`, `BENCHMARK_LLM` em `src/painel.py` precisa ser reconferido.
- Arquivos alterados ou criados: `solution/03-prototipo/app.py` (reescrito) e `solution/03-prototipo/src/painel.py` (novo). Não alterei `triagem.py`, `politica.py`, `roi.py`, `llm.py`, os scripts nem os outputs. Não criei `.env` nem `config.toml`, não fiz commit e não adicionei dependências.
