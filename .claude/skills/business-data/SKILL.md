---
name: business-data
description: Find youlytics' current numbers, dashboards and reports. Use for any question about revenue, clients, pipeline or metrics.
model: haiku
---

# /business-data

Router skill: it says where the live numbers are, so Claude doesn't search the workspace.

| Question | Where to look |
|---|---|
| Revenue, costs, invoices | `business/finance/` (latest `YYYY-MM.md` first) |
| Clients and status | `business/clients/<client>/status.md` |
| Offers and pricing | `business/offers/` |
| Content performance | `business/content/` |
| External dashboards | (add links here: analytics, payments, CRM) |

If the answer isn't in these places, say which source is missing and add a row here once Issam tells you where it lives.
