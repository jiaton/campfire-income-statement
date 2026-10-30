import { Fragment } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { IncomeStatement, StatementSection } from '@/lib/api/client'
import { formatMoney } from '../lib/format'

type Row =
  | { kind: 'section'; title: string; section: StatementSection; totalLabel: string }
  | { kind: 'subtotal'; label: string; amount: string; final?: boolean }

function rowsFor(statement: IncomeStatement): Row[] {
  return [
    { kind: 'section', title: 'Revenue', section: statement.revenue, totalLabel: 'Total revenue' },
    {
      kind: 'section',
      title: 'Cost of goods sold',
      section: statement.cost_of_goods_sold,
      totalLabel: 'Total cost of goods sold',
    },
    { kind: 'subtotal', label: 'Gross profit', amount: statement.gross_profit },
    {
      kind: 'section',
      title: 'Operating expenses',
      section: statement.operating_expenses,
      totalLabel: 'Total operating expenses',
    },
    { kind: 'subtotal', label: 'Operating income', amount: statement.operating_income },
    {
      kind: 'section',
      title: 'Other income',
      section: statement.other_income,
      totalLabel: 'Total other income',
    },
    { kind: 'subtotal', label: 'Net income', amount: statement.net_income, final: true },
  ]
}

function Amount({ value }: { value: string }) {
  return <TableCell className="text-right tabular-nums">{formatMoney(value)}</TableCell>
}

export function IncomeStatementTable({ statement }: { statement: IncomeStatement }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Account</TableHead>
          <TableHead className="text-right">{statement.currency}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rowsFor(statement).map((row) =>
          row.kind === 'section' ? (
            <Fragment key={row.title}>
              <TableRow>
                <TableCell colSpan={2} className="pt-4 font-semibold">
                  {row.title}
                </TableCell>
              </TableRow>
              {row.section.lines.length === 0 && (
                <TableRow>
                  <TableCell colSpan={2} className="pl-6 text-muted-foreground">
                    No activity
                  </TableCell>
                </TableRow>
              )}
              {row.section.lines.map((line) => (
                <TableRow key={line.account_number}>
                  <TableCell className="pl-6">
                    {line.account_number} {line.account_name}
                  </TableCell>
                  <Amount value={line.amount} />
                </TableRow>
              ))}
              <TableRow className="font-medium">
                <TableCell>{row.totalLabel}</TableCell>
                <Amount value={row.section.total} />
              </TableRow>
            </Fragment>
          ) : (
            <TableRow
              key={row.label}
              className={row.final ? 'border-t-2 border-b-4 border-double font-bold' : 'font-semibold'}
            >
              <TableCell>{row.label}</TableCell>
              <Amount value={row.amount} />
            </TableRow>
          ),
        )}
      </TableBody>
    </Table>
  )
}
