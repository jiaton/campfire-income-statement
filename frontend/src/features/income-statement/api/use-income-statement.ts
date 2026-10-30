import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api/client'

export type Period = { start: string; end: string }

export function useIncomeStatement(period: Period | null) {
  return useQuery({
    queryKey: ['income-statement', period],
    queryFn: async () => {
      const { data, error } = await api.GET('/income-statement', { params: { query: period! } })
      if (error) {
        const detail = (error as { detail?: unknown }).detail
        throw new Error(typeof detail === 'string' ? detail : 'The server rejected these dates.')
      }
      return data
    },
    enabled: period !== null,
    // Keep the last statement on screen while the next one loads, instead of flashing a skeleton.
    placeholderData: keepPreviousData,
  })
}
