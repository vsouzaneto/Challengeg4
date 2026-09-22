# `dados/` — SupportIQ (challenge 002)

Contado no disco em 2026-09-21. Não inventar coluna. Dataset 2 (`Document`, `Topic_group`) **ausente**.

| Arquivo | Linhas | Colunas |
| --- | ---: | --- |
| `customer_support_tickets.csv` | 8469 | `Ticket ID`, `Customer Name`, `Customer Email`, `Customer Age`, `Customer Gender`, `Product Purchased`, `Date of Purchase`, `Ticket Type`, `Ticket Subject`, `Ticket Description`, `Ticket Status`, `Resolution`, `Ticket Priority`, `Ticket Channel`, `First Response Time`, `Time to Resolution`, `Customer Satisfaction Rating` |

Grain = ticket. Sem dimensão / FK.

Invariantes: Closed ⇔ Resolution + TTR + CSAT (2769). Open ⇔ FRT/TTR/Resolution/CSAT nulos (2819). Pending ⇔ tem FRT (2881).

`Time to Resolution` e `First Response Time` são datetime. Horas de fila = TTR − FRT.
