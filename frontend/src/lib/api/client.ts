import createClient from 'openapi-fetch'
import type { components, paths } from './schema'

// Same origin: Vite proxies /income-statement to the backend in development.
// fetch is looked up per call (not captured at import) so test request mocks can see it.
export const api = createClient<paths>({
  baseUrl: window.location.origin,
  fetch: (request) => globalThis.fetch(request),
})

export type IncomeStatement = components['schemas']['IncomeStatementOut']
export type StatementSection = components['schemas']['StatementSectionOut']
