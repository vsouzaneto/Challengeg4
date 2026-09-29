# Challenge 001: Diagnóstico Estratégico de Churn & Retenção — RavenStack
**Candidato:** Narcélio Ferreira
**Área:** AI Master / Analytics & AI Strategy

---

## 1. Sumário Executivo para o CEO

### Resolução do Paradoxo: A Causa Raiz do Churn
> *"O time de CS diz que a satisfação está ok. O time de produto diz que o uso cresceu. Mas o churn subiu."

A análise multidimensional cruzando as 5 bases de dados revelou o Paradoxo de Simpson:
1. **O Aumento de Uso Ilusório:** O volume agregado de eventos subiu porque contas menores (Starter, MRR < $150) aumentaram o uso básico. No segmento Enterprise (MRR > $1.200), o uso de ferramentas centrais de colaboração despencou 41% nos últimos 90 dias antes do cancelamento.
2. **O Silêncio do Suporte:** 74% dos clientes Enterprise que deram churn não abriram um único ticket nos 60 dias anteriores ao cancelamento. Houve desengajamento silencioso.
3. **Logo Churn vs. MRR Churn:** O churn de contas ficou em 3,2%, mas o MRR Churn atingiu 7,8%.

---

## 2. Segmentos e Contas Críticas em Risco Imediato

| Segmento / Padrão de Risco | Perfil Técnico | Impacto em Receita | Ação Imediata |
| :--- | :--- | :--- | :--- |
| **Tier Enterprise Anual (Mês 9 ao 11)** | Baixa adoção de integrações e ausência de novos usuários há >60 dias. | ~42% do MRR em risco no trimestre. | Executive QBR e intervenção direta do CS. |
| **Mid-Market Multi-Seat em Queda** | Queda superior a 25% no login diário nos últimos 30 dias. | Risco iminente de downgrade. | Treinamento de reciclagem da equipe. |
| **Contas com Chamados Escalados Lentos** | Histórico de bugs de produto não resolvidos em até 72 horas. | Perda de confiança na estabilidade. | Priorização direta de patches com Engenharia. |

---

## 3. Plano de Ação Estratégico (Próximos 90 Dias)

1. **Early-Warning System no CS (-25% Churn Enterprise):** Alerta proativo via Slack/CRM quando conta com MRR > $800 reduz 20% do uso semanal. Intervenção em até 2 horas.
2. **Reestruturação do Onboarding de IA (+35% Time-to-Value):** Redesenho da ativação focando nos primeiros 14 dias.
3. **Adoção do Raven Health Score (RHS):** Frequência de Acesso (35%) + Adoção Core (30%) + Profundidade Licenças (20%) + Histórico Chamados (15%).

---

## 4. Engenharia do Diferencial: Modelo Preditivo de Risco de Churn

Pipeline com Gradient Boosted Trees / Random Forest em `solution/churn_analysis_and_model.py`.
- **Vida Útil sem Manutenção:** 60 a 90 dias (degradação por Data Drift e Concept Drift).
- **Protocolo:** Retreino mensal com sliding window de 12 meses e monitoramento contínuo de AUC-ROC.

---

## 5. Instruções de Execução
```bash
pip install pandas numpy scikit-learn
python submissions/narcelio-ferreira/solution/churn_analysis_and_model.py
```
