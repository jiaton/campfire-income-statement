import { useState } from 'react'
import type { Period } from '@/features/income-statement/api/use-income-statement'
import { IncomeStatementReport } from '@/features/income-statement/components/income-statement-report'
import { PeriodPicker } from '@/features/income-statement/components/period-picker'

const Q1_2026: Period = { start: '2026-01-01', end: '2026-03-31' }

export default function App() {
  const [period, setPeriod] = useState<Period>(Q1_2026)

  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-6 p-6">
      <h1 className="text-2xl font-semibold">Income statement</h1>
      <PeriodPicker period={period} onChange={setPeriod} />
      <IncomeStatementReport period={period} />
    </main>
  )
}
