# Proposta de automação com IA

## Como funciona na prática

```text
Ticket (portal, e-mail, chat, social)
  │
  ▼
1. Input Guardrail ── injeção / jailbreak / dados de terceiros → BLOQUEIA + revisão humana
  │                   PII (cartão, CPF, e-mail, telefone) → mascarada antes de qualquer LLM
  ▼
2. Classificação ──── TF-IDF + LogReg (Dataset 2) → categoria + confiança → time
  │                   confiança < 0,60 → cascata LLM (Groq 8B → 70B)
  ▼
3. Sentimento ─────── 0–100 + tendência na conversa (queda ≥ 15 → "frustration detected")
  ▼
4. Risco & intenção ─ regras do que NÃO automatizar (abaixo)
  ▼
5. Prioridade ─────── severidade + urgência + sentimento + risco (explicável)
  ▼
6. Knowledge Base ─── similaridade × cobertura; < 0,6 → Knowledge Gap (agrupado por similaridade)
  ▼
7. Confidence Gate
     ├─ risco ALTO ou confiança < 0,60 ......... HUMANO (upstream, com resumo + motivo)
     ├─ risco MÉDIO ou 0,60 ≤ confiança < 0,85 . SUGESTÃO (agente aprova / edita / rejeita)
     └─ confiança ≥ 0,85 e risco baixo ......... AUTO (IA responde)
  ▼
8. Output Guardrail ─ groundedness, promessas não autorizadas, PII, disclaimer
  ▼
Cliente → resolve → CSAT (com contexto: automação, categoria, sentimento, tempo)
  ▲
Humano decide (ex.: aprova estorno) → "Devolver para IA" (downstream) → IA confirma, encerra, pede CSAT
```

## O que automatizar

| Alavanca | Base nos dados | Ganho |
|---|---|---|
| **Primeira resposta imediata** | 33% dos tickets sem nenhuma resposta | Zera o backlog de "sem resposta"; FRT em segundos |
| **Triagem e roteamento** | Classificador com 86,6% de acurácia (97% na faixa ≥0,85) | ~1.080 h/ano de triagem manual |
| **Prioridade calculada** | 50% dos tickets marcados como High/Critical | Fila deixa de ser FIFO disfarçado |
| **Resposta automática** | ~15% dos tickets em assuntos documentáveis e de baixo risco | ~470 h/ano |
| **Resposta sugerida** | ~30% em assuntos que precisam de verificação | ~590 h/ano |
| **Preparo para humano** | ~55% obrigatoriamente humanos | ~460 h/ano (resumo, contexto, artigo) |
| **Knowledge Gaps** | Perguntas repetidas sem resposta | Cada gap resolvido vira automação futura |

## O que NÃO automatizar (e por quê)

| Caso | Exemplo nos dados | Por quê |
|---|---|---|
| Reembolso / chargeback | 20,7% dos tickets são "Refund request" | Decisão financeira irreversível |
| Cancelamento / churn | 20,0% são "Cancellation request" | Oportunidade de retenção exige julgamento |
| Cobrança indevida | "Payment issue" + "Billing inquiry" | Impacto financeiro; no máximo sugestão |
| Perda de dados | Assunto "Data loss" (5,8%) | Irreversível, exige diagnóstico técnico |
| Jurídico / LGPD | "Procon", "advogado", "apagar meus dados" | Risco regulatório |
| Fraude / conta invadida | "não reconheço a compra" | Segurança |
| Emoção severa / frustração crescente | Queda de sentimento na conversa | Bot insistente piora a experiência |

Nesses casos a IA continua trabalhando (classifica, resume, puxa a política e redige o rascunho), mas **quem decide e envia é um humano**.

## Métrica norte

**Safe Resolution Rate** = tickets resolvidos pela IA com CSAT ≥ 4 / tickets automatizados. Maximizar só a automation rate incentiva automação errada.
