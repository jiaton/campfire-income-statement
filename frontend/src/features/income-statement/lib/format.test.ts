import { describe, expect, it } from 'vitest'
import { formatDate, formatMoney } from './format'

describe('formatMoney', () => {
  it('groups thousands and keeps the cents exactly', () => {
    expect(formatMoney('35650.75')).toBe('35,650.75')
    expect(formatMoney('1234567.10')).toBe('1,234,567.10')
    expect(formatMoney('42.18')).toBe('42.18')
    expect(formatMoney('0.00')).toBe('0.00')
  })

  it('shows negatives in parentheses', () => {
    expect(formatMoney('-800.25')).toBe('(800.25)')
    expect(formatMoney('-44480.14')).toBe('(44,480.14)')
  })
})

describe('formatDate', () => {
  it('shows the calendar date regardless of the local timezone', () => {
    expect(formatDate('2026-01-01')).toBe('January 1, 2026')
    expect(formatDate('2026-03-31')).toBe('March 31, 2026')
  })
})
