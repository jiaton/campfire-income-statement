// Amounts arrive as decimal strings ("-800.25"). They are formatted as text and never parsed
// into a number, so nothing is rounded on the way to the screen.
export function formatMoney(amount: string): string {
  const negative = amount.startsWith('-')
  const [whole, cents] = amount.replace('-', '').split('.')
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const text = `${grouped}.${cents}`
  return negative ? `(${text})` : text
}

// Formats a calendar date. Going through UTC on both sides keeps "2026-01-01" from becoming
// December 31 in a timezone west of UTC.
export function formatDate(isoDate: string): string {
  return new Date(`${isoDate}T00:00:00Z`).toLocaleDateString('en-US', {
    timeZone: 'UTC',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
