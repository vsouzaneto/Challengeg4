# Desafio 003 — Lead Scorer → Módulo **Vendas / Leads**

Fonte: `challenges/build-003-lead-scorer/README.md` (lido na íntegra; a pasta do desafio só contém esse arquivo).

## O que eles pedem

**Área:** Vendas / RevOps · **Tipo:** Build (**software funcionando**) · **Tempo sugerido:** 4–6 h

**Contexto:** 35 vendedores em escritórios regionais, com managers, e um pipeline de cerca de 8.800 oportunidades. A priorização hoje é "no feeling". A Head de RevOps pede: *"uma ferramenta que o vendedor abra, veja o pipeline e saiba onde focar. Pode ser simples, mas precisa funcionar"*.

### 1. Solução funcional (obrigatório)
**Requisitos mínimos:**
- Precisa **rodar** (nada de mockup ou PowerPoint).
- Usa os **dados reais**.
- Tem **lógica de scoring/priorização** (não é só ordenar por valor).
- O vendedor entende **por que** o score é alto ou baixo.

### 2. Documentação mínima (obrigatório)
**Setup** (dependências, comandos, URL), **lógica** (critérios e por quê) e **limitações** (o que não faz e o que precisaria para escalar).

### 3. Process log (obrigatório)
*"Especialmente interessante para quem usa vibe coding… Mostre o processo."*

## Critérios de qualidade (checklist de aceite)
- [ ] **Funciona de verdade** seguindo as instruções
- [ ] Scoring faz sentido, usa as features certas e vai além do óbvio
- [ ] Vendedor **não-técnico** usa e entende
- [ ] A interface **ajuda a decidir**, não só mostra dados
- [ ] Código limpo o bastante para outro dev manter

## Dicas deles (viram requisitos)
- Útil > ML perfeito. Começar simples e iterar.
- Features óbvias: stage, tempo no pipeline, tamanho da conta, produto, vendedor. **Olhar os dados para achar o resto.**
- *"Regras + heurísticas bem apresentadas valem mais que XGBoost sem interface."*
- **Explicabilidade ganha:** *"por que o deal tem score 85"*.
- Uso real: **segunda-feira de manhã, o que o vendedor precisa ver?**
- **Bônus:** filtros por **vendedor / manager / região**.

## Dados
Ver [`../04-datasets.md`](../04-datasets.md): `accounts`, `products`, `sales_teams` e `sales_pipeline` (a tabela central).

## Plano do módulo (sozinho)
1. **Perfil:** stages, datas, deals abertos (Prospecting/Engaging) × fechados (Won/Lost), nulos (ex.: deal sem conta).
2. **Aprender com o histórico (Won × Lost):** taxa de ganho por produto, setor, porte da conta, vendedor, região, tempo de ciclo → quais fatores realmente mudam a chance.
3. **Score explicável para deals abertos:** pontos por fator, com peso vindo dos dados (ex.: *"produto X ganha 64% vs. média 48% → +8"*), tempo parado no estágio (**deal esfriando**), valor esperado (chance × preço).
4. **Tela "segunda-feira":** filtros vendedor/manager/região; lista priorizada com score, faixa (Quente/Morno/Frio), **3 motivos principais em português** e a próxima ação sugerida.
5. **Visão manager:** pipeline do time, deals esfriando, concentração.
6. **Validação:** o score separa Won de Lost no histórico? (medir num conjunto separado, com honestidade).
7. **Documentação:** setup, lógica e limitações.

## O que o módulo exporta / recebe
- **Recebe do Churn** 🟢: contas RavenStack → score de **valor** da conta ("vale a pena manter?").
- **Recebe do Suporte** 🟡: tickets "Product inquiry" como oportunidades.
- **Recebe da Mídia** 🔵: perfil de audiência que engaja, como critério de segmento.
- **Exporta para Suporte** 🟡: deals ganhos → onboarding prioritário.
- **Exporta para Mídia** 🔵: setores e produtos que mais fecham.
