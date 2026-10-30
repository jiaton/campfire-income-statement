import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useIncomeStatement, type Period } from '../api/use-income-statement'
import { formatDate } from '../lib/format'
import { IncomeStatementTable } from './income-statement-table'

function invalidReason(period: Period): string | null {
  if (!period.start || !period.end) return 'Pick a start and an end date.'
  // ISO dates compare correctly as strings.
  if (period.start > period.end) return 'The start date must be on or before the end date.'
  return null
}

export function IncomeStatementReport({ period }: { period: Period }) {
  const reason = invalidReason(period)
  const query = useIncomeStatement(reason ? null : period)

  if (reason) {
    return (
      <Alert>
        <AlertTitle>{reason}</AlertTitle>
      </Alert>
    )
  }
  if (query.isPending) {
    return <Skeleton className="h-96 w-full" />
  }
  if (query.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load the income statement</AlertTitle>
        <AlertDescription>{query.error.message}</AlertDescription>
      </Alert>
    )
  }

  const statement = query.data
  return (
    <Card>
      <CardHeader>
        <CardTitle>{statement.company}</CardTitle>
        <CardDescription>
          Income statement, {formatDate(statement.start)} to {formatDate(statement.end)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <IncomeStatementTable statement={statement} />
      </CardContent>
    </Card>
  )
}
