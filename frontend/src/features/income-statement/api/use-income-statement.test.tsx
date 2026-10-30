import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import type { ReactNode } from 'react'
import { describe, expect, it } from 'vitest'
import { q1Statement, server } from '@/test/server'
import { useIncomeStatement } from './use-income-statement'

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

describe('useIncomeStatement', () => {
  it('returns the statement as the server sent it', async () => {
    const { result } = renderHook(() => useIncomeStatement({ start: '2026-01-01', end: '2026-03-31' }), { wrapper })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.net_income).toBe('-44480.14')
  })

  it('sends nothing without a period', () => {
    let calls = 0
    server.use(
      http.get('*/income-statement', () => {
        calls += 1
        return HttpResponse.json(q1Statement)
      }),
    )
    const { result } = renderHook(() => useIncomeStatement(null), { wrapper })

    expect(result.current.fetchStatus).toBe('idle')
    expect(calls).toBe(0)
  })

  it('turns a validation error list into a readable message', async () => {
    server.use(
      http.get('*/income-statement', () =>
        HttpResponse.json({ detail: [{ loc: ['query', 'start'], msg: 'Input should be a valid date' }] }, { status: 422 }),
      ),
    )
    const { result } = renderHook(() => useIncomeStatement({ start: '2026-02-30', end: '2026-03-31' }), { wrapper })

    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(result.current.error?.message).toBe('The server rejected these dates.')
  })
})
