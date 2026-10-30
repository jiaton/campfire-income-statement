import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import q1 from './fixtures/income-statement-q1-2026.json'
import type { IncomeStatement } from '@/lib/api/client'

// Recorded from the real backend for 2026-01-01..2026-03-31.
export const q1Statement = q1 satisfies IncomeStatement

export const server = setupServer(
  http.get('*/income-statement', () => HttpResponse.json(q1Statement)),
)
