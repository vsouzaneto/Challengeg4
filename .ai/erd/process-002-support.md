# ERD — 002 Support — schema observado

Fonte: `datasets/process-002-support/customer_support_tickets.csv` (8 469 × 17). Zip = o mesmo arquivo. Leitura 2026-09-21.

```
[Dataset 1] customer_support_tickets  8469
     PK Ticket ID
     (sem dimensão, sem FK)

[Dataset 2] IT classification
     AUSENTE neste disco
     brief: Document + Topic_group ~48k
```

Não há linha ligando #1 ↔ #2. Sem o CSV #2, classificação em 8 tópicos **não tem ground truth local**.

## Colunas físicas (≠ nomes do brief)

| Coluna no CSV | Brief | Tipo / nunique |
|---------------|-------|----------------|
| `Ticket ID` | Ticket ID | PK 8 469 |
| `Customer Name` | Customer Name | 8 028 |
| `Customer Email` | Email | 8 320 |
| `Customer Age` | Age | 18–70 |
| `Customer Gender` | Gender | Male, Female, Other (~iguais) |
| `Product Purchased` | Product Purchased | 42 SKUs (Canon EOS, GoPro Hero, …) |
| `Date of Purchase` | **ausente no brief** | 2020-01-01 … 2021-12-30 |
| `Ticket Type` | Type (3 citados) | **5**: Refund, Technical, Cancellation, Product inquiry, Billing |
| `Ticket Subject` | Subject | 16 assuntos |
| `Ticket Description` | Description | texto, 8 077 unique |
| `Ticket Status` | Status | Open 2 819 · Pending Customer Response 2 881 · Closed 2 769 |
| `Resolution` | Resolution | só Closed |
| `Ticket Priority` | Priority | Low / Medium / High / **Critical** |
| `Ticket Channel` | Channel | Email, Phone, Social media, Chat |
| `First Response Time` | FRT | datetime 2023-06-01…; **null só em Open** |
| `Time to Resolution` | TTR | datetime; **null se não Closed** |
| `Customer Satisfaction Rating` | CSAT | 1–5, só Closed; ~uniforme |

## Invariantes observadas

1. Closed ⇔ Resolution ∧ TTR ∧ CSAT preenchidos (2 769 / 2 769).
2. Open ⇔ FRT, Resolution, TTR, CSAT nulos.
3. Pending ⇔ tem FRT; sem Resolution/TTR/CSAT.
4. Grain = ticket. Cliente não é entidade (e-mail não único o bastante para ser PK: 8 320 < 8 469).

## Brief vs disco

| Brief | Disco |
|-------|-------|
| ~30 000 | **8 469** |
| Type: Technical, Billing, Product inquiry | + Refund request + Cancellation request |
| 2º dataset 48 k | **não baixado** |

Diagnóstico operacional (gargalo, CSAT, horas) fecha no Dataset 1. Proposta “8 classes / embeddings” **depende** de baixar o Dataset 2 — não inventar `Topic_group` neste ERD.
