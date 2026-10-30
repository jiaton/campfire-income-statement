# AGENTS.md

## Project

Income statement (P&L) for one company over any date range. The backend loads `ledger.json`
(chart of accounts + journal entries) at startup and serves `GET /income-statement?start=&end=`.
The frontend picks the dates and renders the statement. No database, no auth.

## Setup / Test / Run

- Backend install: `cd backend && uv sync`
- Backend run: `cd backend && uv run uvicorn app.main:app --reload --port 8100`
- Backend tests: `cd backend && uv run pytest`
- Frontend install: `cd frontend && npm install`
- Frontend run: `cd frontend && npm run dev` (port 5173, proxies `/income-statement` to 8100)
- Frontend gate: `cd frontend && npm run check` (tsc + oxlint + vitest)
- Regenerate the API types after changing a response model: `cd frontend && npm run gen:api`

## Stack

- Backend: FastAPI, Python 3.12, Pydantic v2, uv. Data is a JSON file loaded once.
- Frontend: Vite + React 19 + TypeScript, shadcn/ui on Tailwind v4, TanStack Query for the one
  server resource, no client-state library (local `useState` is enough), lucide icons.
- Contract: FastAPI's OpenAPI schema → `openapi-typescript` → `src/lib/api/schema.d.ts`, called
  through `openapi-fetch`. Never hand-write response types.

## Accounting rules (the part that must stay correct)

- Money is `decimal.Decimal` parsed from the JSON strings, end to end. Never `float`.
  JSON responses carry amounts as strings with two decimals.
- Only `posted` entries count. `draft` and `void` never touch a number.
- The date range is inclusive on both ends.
- The account's `subtype` decides the section. Each section has a display side: revenue and
  other income show credit minus debit, COGS and operating expenses show debit minus credit.
  Contra revenue therefore shows as a negative line inside Revenue.
- Inactive accounts still report their history.
- Any change to the math gets a test that would fail on the old math.

## Layering

Backend is organised by domain: `app/ledger/` (models, port, JSON adapter, load-time validation)
and `app/income_statement/` (router → service → schemas). The service depends on the
`LedgerRepository` protocol, not on the JSON adapter. Routers hold no accounting logic.

Frontend: `components/ui/` holds generated shadcn primitives only; `features/income-statement/`
holds its API hook, components and formatting. Every control is a shadcn component.

## Forbidden

- `float` anywhere near an amount.
- Accounting logic in a router or a React component.
- Raw dict request/response bodies where a Pydantic model belongs.
- Hand-written API types on the frontend.
- Raw hex colours or Tailwind palette classes in feature code; use the theme tokens.
- AI attribution lines in commits.
