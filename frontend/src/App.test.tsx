import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'
import App from './App'
import { q1Statement, server } from './test/server'
import { renderWithQuery } from './test/render'

describe('App', () => {
  it('asks for the statement for the chosen dates and shows it', async () => {
    let requested: URLSearchParams | undefined
    server.use(
      http.get('*/income-statement', ({ request }) => {
        requested = new URL(request.url).searchParams
        return HttpResponse.json(q1Statement)
      }),
    )
    renderWithQuery(<App />)

    const netIncome = await screen.findByText('Net income')
    expect(within(netIncome.closest('tr')!).getByText('(44,480.14)')).toBeInTheDocument()
    expect(requested?.get('start')).toBe('2026-01-01')
    expect(requested?.get('end')).toBe('2026-03-31')
    expect(screen.getByText(/January 1, 2026 to March 31, 2026/)).toBeInTheDocument()
  })

  it('does not ask the server when the start is after the end', async () => {
    let calls = 0
    server.use(
      http.get('*/income-statement', () => {
        calls += 1
        return HttpResponse.json(q1Statement)
      }),
    )
    renderWithQuery(<App />)
    await screen.findByText('Net income')

    const start = screen.getByLabelText('Start date')
    await userEvent.clear(start)
    await userEvent.type(start, '2026-04-30')

    expect(await screen.findByText('The start date must be on or before the end date.')).toBeInTheDocument()
    expect(calls).toBe(1)
  })

  it('shows the server error message', async () => {
    server.use(
      http.get('*/income-statement', () => HttpResponse.json({ detail: 'start is after end' }, { status: 422 })),
    )
    renderWithQuery(<App />)

    expect(await screen.findByText('start is after end')).toBeInTheDocument()
  })
})
