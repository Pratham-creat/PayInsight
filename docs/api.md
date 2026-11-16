# API reference

The API provides `/api/kpis/summary`, `/api/trends`, `/api/performance/banks`,
`/api/performance/methods`, `/api/matrix`, `/api/failures/reasons`,
`/api/customers/segments`, `/api/top`, `/api/risk/flagged`, and
`/api/risk/evaluation`, in addition to transaction and merchant routes. Transactions
accept pagination and status/method/merchant filters; trends accepts bank, method, and
date range filters. SQL values are always bound parameters.
