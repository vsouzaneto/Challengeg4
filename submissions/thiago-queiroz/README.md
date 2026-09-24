# Submissão — Thiago Queiroz — Challenge 004

## Sobre mim

- **Nome:** Thiago Queiroz
- **LinkedIn:** https://www.linkedin.com/in/tgqueiroz/
- **Challenge escolhido:** 004 — Estratégia Social Media

---

## Executive Summary

Construí um sistema de decisão offline para auditar 52.214 publicações e responder, com níveis explícitos de confiança, o que os dados realmente permitem concluir. A principal descoberta não foi um formato, creator ou plataforma vencedora: a fonte declara que o dataset é simulado, a identidade dos creators é instável e as diferenças observadas são pequenas demais para sustentar decisões operacionais. Em vez de produzir recomendações frágeis, o protótipo bloqueia extrapolações, mostra as evidências e transforma as lacunas em um plano de instrumentação e experimentação. A recomendação principal é proteger o orçamento agora e medir corretamente antes de alterar verba, frequência, creator ou política de patrocínio.

---

## Solução

### Entrega principal

Abra `solution/social-growth-decision-system-v2.html` em qualquer navegador moderno. O arquivo é offline, autocontido e não realiza requisições externas.

O pacote reproduzível completo está em `solution/source-checkpoint.zip`. Ele contém código-fonte, dados congelados, testes, evidências estruturadas e instruções de reprodução.

**Nota de estado:** o HTML e os documentos internos do ZIP preservam literalmente o estado da geração quando ela foi congelada e, por isso, ainda mostram expressões como “aguardando revisão”. A revisão técnica ocorreu depois, sobre esses mesmos bytes, e está registrada em `process-log/authoritative-skeptic-review.md`: `PASS`, nota `10,0/10`, `C0/H0/M0/L0` e `safe_to_checkpoint=true`.

### Como executar e reproduzir

Para avaliação imediata, não há instalação: basta abrir o HTML.

Para reproduzir o código, extraia `solution/source-checkpoint.zip`, entre na pasta extraída e execute:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -v
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_all.py
```

A verificação visual completa usa Playwright e Chromium no ambiente documentado dentro do pacote:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/local/lib/hermes-agent/venv/bin/python -B scripts/run_visual_qa.py --root .
```

### Abordagem

1. Congelei e validei a proveniência do dataset e do brief.
2. Auditei qualidade, granularidade, identidade, distribuição, patrocínio, temporalidade e campos necessários para retorno sobre investimento.
3. Separei integridade técnica de validade para decisão de negócio.
4. Transformei cada pergunta do desafio em uma resposta, uma evidência, uma limitação e uma ação permitida.
5. Implementei um protótipo offline com um Guardião da Qualidade dos Dados que bloqueia claims incompatíveis com as evidências.
6. Usei desenvolvimento orientado a testes, builds determinísticos, revisão visual em múltiplas larguras e zoom, e revisões Céticas em contextos separados.
7. Preservei as gerações rejeitadas e converti cada bloqueio material em uma regressão antes de corrigir.

### Resultados / Findings

- A fonte do Kaggle declara o dataset como **simulado**.
- O CSV possui **52.214 linhas e 27 colunas**, sem duplicatas exatas.
- Todos os **5.000 `creator_id`** aparecem associados a múltiplos nomes; o identificador não sustenta histórico longitudinal real.
- Os spreads marginais entre plataforma, tipo de conteúdo, categoria e audiência são muito pequenos e não sustentam um vencedor operacional.
- Patrocinado e orgânico apresentam taxas brutas praticamente iguais: **19,9048% versus 19,9059%**, diferença de **−0,0011 ponto percentual**.
- A base não possui custo, receita, conversão e atribuição suficientes para calcular Custo de Aquisição de Cliente ou Retorno Sobre Investimento.
- Entre **970 hashtags** elegíveis, nenhuma manteve evidência suficiente após correção de Holm para múltiplas comparações.
- A taxa trimestral ficou entre **19,8993% e 19,9074%**, comportamento compatível com a fixture sintética e insuficiente para uma recomendação temporal.
- O sistema foi validado com **47 testes**, dois builds idênticos e **30 capturas autenticadas** em desktop, celular, larguras intermediárias e zoom ampliado.

### Recomendações

1. **Não redistribuir orçamento com base nesta base.** Ela serve para prototipagem e auditoria do processo, não para inferência sobre a operação real.
2. **Instrumentar o próximo ciclo:** identificador estável de conta e publicação, parâmetros de rastreamento de campanha, eventos, custo, conversão, receita e margem.
3. **Pré-declarar a métrica e o menor efeito relevante para o negócio**, calcular potência e tamanho amostral antes de qualquer experimento.
4. **Executar testes prospectivos controlados**, com autorização humana separada, para patrocínio, formato e demais hipóteses.
5. **Preservar o Guardião da Qualidade dos Dados** para impedir que rankings sintéticos ou associações descritivas virem decisões automáticas.

### Limitações

- Os dados são sintéticos e não provam comportamento real do G4.
- O identificador de creator não representa uma pessoa ou conta estável.
- Não há variáveis financeiras e de atribuição suficientes para calcular retorno.
- Diferenças pequenas não provam ausência de efeitos reais, relações não lineares ou interações.
- Nenhum experimento ao vivo foi executado ou autorizado.

---

## Process Log — Como usei IA

### Ferramentas usadas

- **Hermes Agent / modelos de linguagem:** decomposição do problema, implementação assistida, geração de testes, revisão Cética e coordenação de agentes independentes.
- **Python:** auditoria determinística, cálculos estatísticos, construção do HTML e validação de contratos.
- **Playwright e Chromium:** verificação visual, responsividade, console, rede, overflow e autenticação de capturas.
- **Git:** preservação de gerações, checkpoints imutáveis e histórico auditável.

### Workflow

1. Comparei os desafios e escolhi o Challenge 004 como um problema de decisão, não apenas de visualização.
2. Congelei as fontes e auditei o dataset antes de produzir recomendações.
3. Converti o brief em contratos de claims, decisões, evidências e ações proibidas.
4. Implementei o primeiro protótipo e submeti cada geração a testes e revisão separada.
5. Preservei as reprovações, corrigi os problemas por desenvolvimento orientado a testes e gerei novos bytes para cada revisão.
6. Incorporei duas rodadas de feedback humano sobre clareza visual, linguagem executiva, risco financeiro e mensuração.
7. Executei uma auditoria adicional de um notebook público baseado no mesmo dataset para tentar refutar a tese antes da submissão.
8. Congelei a geração aprovada e preparei esta entrega sem alterar os bytes revisados.

### Onde a IA errou e como corrigi

- Produziu inicialmente claims mais fortes do que os dados permitiam. Restringi a tese a diferenças descritivas pequenas e explicitei que isso não prova ausência de efeitos reais.
- Tratou candidatos de hashtags como ruído ou falsos positivos conhecidos. Corrigi para “evidência insuficiente após correção”, sem presumir a verdade oculta.
- Misturou estimandos diferentes em comparações de engajamento. Padronizei a métrica principal e rotulei separadamente a comparação bruta de patrocínio.
- Omitiu dependências congeladas em uma geração. Tornei o checkout autossuficiente e adicionei reprodução em cópia limpa.
- Manteve estados e próximos passos obsoletos em documentos intermediários. As gerações foram bloqueadas, preservadas e substituídas por novas revisões.
- Um notebook externo sugeria alta acurácia preditiva. A reprodução mostrou que `follower_count` sozinho recompõe aproximadamente 96% das classes porque participa matematicamente do alvo; por isso o score não foi convertido em recomendação.

### O que eu adicionei que a IA sozinha não faria

- A decisão de interromper recomendações aparentemente “acionáveis” quando a fonte simulada e a identidade instável não sustentavam seu uso.
- A separação explícita entre descrição, previsão, causalidade e decisão financeira.
- A exigência de preservar reprovações e evidências, em vez de esconder as tentativas que falharam.
- O Guardião da Qualidade dos Dados como componente do produto, não apenas como ressalva metodológica.
- O foco executivo em proteger orçamento e construir um sistema de medição real antes de procurar vencedores sintéticos.

O registro detalhado está em `process-log/process-log.md`, `process-log/process-timeline.json` e `process-log/refutation-log.md`.

---

## Evidências

- [x] Narrativa detalhada do processo
- [x] Histórico Git e timeline estruturada
- [x] Gerações rejeitadas e correções documentadas
- [x] Revisão Cética autoritativa
- [x] Auditoria comparativa do notebook externo
- [x] Testes, QA visual e hashes no pacote reproduzível

---

_Submissão preparada em: 23/09/2026. O envio externo depende de aprovação humana final._
