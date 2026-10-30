# Income statement

An income statement (P&L) for Northwind Coffee Roasters over any date range, built from
`ledger.json`. Decisions, the Q1 2026 number and how it was checked are in [NOTES.md](NOTES.md).

## Run it

Versions used: macOS, Python 3.12.13 via uv 0.11.32, Node 26.8.2, npm 11.19.1.
uv downloads Python 3.12 if it is missing (`brew install uv node` for the tools).

Backend (port 8100, chosen to stay clear of anything already on 8000):

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8100
```

Frontend (port 5173; Vite proxies `/income-statement` to the backend):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. It starts on Q1 2026.

The API on its own: http://localhost:8100/income-statement?start=2026-01-01&end=2026-03-31,
interactive docs at http://localhost:8100/docs.

## Tests

```bash
cd backend && uv run pytest
cd frontend && npm run check   # typecheck + lint + tests
```

The backend tests are the ones that guard the accounting: a hand-worked Q1 statement line by
line, single months and single days at the range edges, posted/draft/void filtering, contra
revenue and vendor credits, and a check over about 1,000 date ranges that net income equals the
mirror image on the balance-sheet side. Frontend tests cover money and date formatting, the
row order of the statement, and the request/validation flow against a mocked API using a
response recorded from the real backend.

## API

`GET /income-statement?start=YYYY-MM-DD&end=YYYY-MM-DD`, both dates included.
`422` if a date is missing or invalid, or if `start` is after `end`.

```json
{
  "company": "Northwind Coffee Roasters",
  "currency": "USD",
  "start": "2026-01-01",
  "end": "2026-03-31",
  "revenue": {
    "lines": [
      { "account_number": "4000", "account_name": "Product Revenue", "amount": "35650.75" },
      { "account_number": "4900", "account_name": "Sales Returns & Discounts", "amount": "-800.25" }
    ],
    "total": "37850.50"
  },
  "cost_of_goods_sold": { "lines": ["..."], "total": "14272.75" },
  "gross_profit": "23577.75",
  "operating_expenses": { "lines": ["..."], "total": "68100.07" },
  "operating_income": "-44522.32",
  "other_income": { "lines": ["..."], "total": "42.18" },
  "net_income": "-44480.14"
}
```

(Lines trimmed above.) Amounts are strings with two decimals so no client parses them into a
float. Each section's amounts are shown from that section's side, so a negative number always
means "reduces this section".

## Layout

```
ledger.json                     the provided data
backend/app/ledger/             models, JSON loading and validation, LedgerRepository protocol
backend/app/income_statement/   service.py (the accounting), schemas.py (response), router.py
backend/tests/
frontend/src/features/income-statement/   API hook, period picker, statement table, formatting
frontend/src/lib/api/           openapi-fetch client; schema.d.ts is generated
frontend/src/components/ui/     shadcn/ui primitives (generated)
```

After changing a response model, run `npm run gen:api` in `frontend/` to regenerate the types
from the backend's OpenAPI schema.
