import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { Period } from '../api/use-income-statement'

type Props = {
  period: Period
  onChange: (period: Period) => void
}

export function PeriodPicker({ period, onChange }: Props) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="grid gap-1.5">
        <Label htmlFor="start">Start date</Label>
        <Input
          id="start"
          type="date"
          value={period.start}
          onChange={(event) => onChange({ ...period, start: event.target.value })}
        />
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="end">End date</Label>
        <Input
          id="end"
          type="date"
          value={period.end}
          onChange={(event) => onChange({ ...period, end: event.target.value })}
        />
      </div>
    </div>
  )
}
