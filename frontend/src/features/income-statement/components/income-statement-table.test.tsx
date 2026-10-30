import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { q1Statement } from '@/test/server'
import { IncomeStatementTable } from './income-statement-table'

function rowText(label: string) {
  return within(screen.getByText(label).closest('tr')!).getAllByRole('cell').map((cell) => cell.textContent)
}

describe('IncomeStatementTable', () => {
  it('shows every section, line and subtotal in statement order', () => {
    render(<IncomeStatementTable statement={q1Statement} />)

    const labels = screen.getAllByRole('row').slice(1).map((row) => row.firstChild?.textContent)
    expect(labels).toEqual([
      'Revenue',
      '4000 Product Revenue',
      '4100 Subscription Revenue',
      '4900 Sales Returns & Discounts',
      'Total revenue',
      'Cost of goods sold',
      '5000 Cost of Goods Sold',
      'Total cost of goods sold',
      'Gross profit',
      'Operating expenses',
      '6000 Salaries',
      '6100 Rent',
      '6200 Software',
      '6300 Marketing (legacy)',
      'Total operating expenses',
      'Operating income',
      'Other income',
      '7000 Interest Income',
      'Total other income',
      'Net income',
    ])
  })

  it('shows negative amounts in parentheses', () => {
    render(<IncomeStatementTable statement={q1Statement} />)

    expect(rowText('4900 Sales Returns & Discounts')).toEqual(['4900 Sales Returns & Discounts', '(800.25)'])
    expect(rowText('Net income')).toEqual(['Net income', '(44,480.14)'])
  })

  it('says when a section has no activity', () => {
    const statement = { ...q1Statement, other_income: { lines: [], total: '0.00' } }
    render(<IncomeStatementTable statement={statement} />)

    expect(screen.getByText('No activity')).toBeInTheDocument()
    expect(rowText('Total other income')).toEqual(['Total other income', '0.00'])
  })
})
