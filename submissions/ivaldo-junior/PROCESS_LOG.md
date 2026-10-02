# Registo de Processo (PROCESS_LOG.md)

Este documento centraliza as decisões de arquitetura e o processo conduzido utilizando metodologias modernas de desenvolvimento, com suporte nativo da IA Antigravity (Gemini) atuando no papel de Engenheiro Sênior.

## 0. Vibe Coding & Colaboração IA-Humano
O processo de desenvolvimento seguiu o modelo de **"Vibe Coding"**, em que o escopo, julgamento de produto e as métricas de negócio foram ditadas pelo operador humano (Ivaldo Junior), enquanto a IA Antigravity acelerou massivamente a componente operacional. 
- **Julgamento Humano:** Definição das regras heurísticas de *RevOps*, validação de estéticas corporativas (UI/UX) e recusa de soluções enviesadas ou não funcionais.
- **Aceleração Operacional da IA:** Implementação assíncrona, orquestração pelo Cortex Hub, testes unitários automatizados (QA), e minificação de componentes visuais complexos.

## 1. Escolha Arquitetural Crítica: Inteligência Analítica Pura vs. LLM
Num mundo focado em GenAI, o projeto abdicou **estrategicamente** da utilização de Modelos de Linguagem (LLMs) para o "Lead Scoring" per-se, preferindo um motor de dados determinístico em Python Puro (Pandas/NumPy). O racional baseou-se em:
- **Alta Disponibilidade e Latência:** Um processamento local com DataFrames corre a <20ms por lote de milhares de instâncias. LLMs demoram segundos por batch e adicionam atrito temporal.
- **Determinismo Perfeito:** Comissões e fluxos corporativos ("RevOps") requerem métricas consistentes. Regras matemáticas e funções de decaimento oferecem auditoria 100% perfeita face ao risco de "alucinações" de um LLM.
- **Eficiência Financeira (Zero API Cost):** Sem integração de OpenAI ou Anthropic em backend.

## 2. Implementação Funcional do Motor (lead_scorer.py)
A refatoração analítica incluiu o desenvolvimento de:
- *Stripping* dinâmico das colunas CSV no processo de ingestão.
- Agrupamento estatístico para cálculo de Win Rates de Setores.
- Algoritmo Multi-fator com **Decaimento Logarítmico (Stagnation Decay)**: A fórmula reduz progressivamente a validade do Lead após 45 dias estacionados.
- **NLG Simulado:** Geração de Explicabilidade Natural (NLG) sem IA, apenas através da concatenação lógica de *triggers*.

## 3. Identidade Visual (G4 Educação) e UI/UX
- Foi inserido o *branding* do G4: paleta oficial `#0A0E1A` (Midnight) e `#E5B842` (Dourado).
- O logotipo SVG embutido eliminou a dependência de ficheiros PNG estáticos, carregando sem fricções na mesma cor vetorial Dourada.
- Refatoração minuciosa seguindo os padrões das **Heurísticas de Nielsen**, convertendo um Dashboard tradicional numa ferramenta de execução de trabalho "Engine".

Em suma: A jornada começou num protótipo de exploração de dados, validou métricas cruas, melhorou a estética SaaS genérica e, finalmente, transitou para uma solução "Enterprise-Ready" imbuída da cultura técnica de alta performance exigida pelo ecossistema G4.

## 4. Garantia de Qualidade (QA) de Ponta a Ponta
Para assegurar "zero defeitos", foi conduzida uma rotina estrita de Qualidade (QA):
- **Camada Visual:** Ajustes CSS profundos para esconder o cabeçalho predefinido do Streamlit, correção do preenchimento (`padding`) no topo da página e na barra lateral, e inclusão de uma "Top Bar" fixa. A tabela customizada HTML foi substituída por `st.dataframe` altamente estendido através do `st.column_config` para manter o nível de elegância com maior robustez e suporte a ordenação/scroll.
- **Camada Analítica & Tolerância a Falhas:** Injeção de lógica defensiva no `lead_scorer.py`, incluindo desinfeção de strings (`.str.strip()`), renomeação dinâmica de esquemas instáveis (como a coluna `stage`), e preenchimentos seguros para `NaN`.
- **Suíte de Testes Automatizada:** Implementação do ficheiro `test_pipeline_qa.py`, garantindo rastreio contínuo e validação algorítmica rigorosa sobre as balizas matemáticas de scoring, preservação de completude do merge de dados, consistência do explicador gerado e gestão sem quebras (`crash-free`) perante filtros de subconjuntos vazios.
