# Notes

## Q1 2026 (2026-01-01 to 2026-03-31)

**Net income: (44,480.14)**, a loss of $44,480.14.

Net revenue 37,850.50 − COGS 14,272.75 = gross profit 23,577.75 − operating expenses
68,100.07 = operating income (44,522.32) + interest income 42.18.

## Decisions and assumptions about the data

- **Only `posted` entries count.** JE-019 (Q1 bonus accrual) is a draft and is left out, so
  March salaries are 18,500, not 23,500. JE-009 (February sales entered twice) and JE-025
  (unsigned check) are void and left out.
- **Both dates are included.** Month-end entries (payroll, revenue recognition, interest on
  03-31) land in the month they are dated. JE-001 (Dec 2025) and JE-024 (Apr 2026) fall outside Q1.
- **Entries are reported as recorded.** JE-007 books three months of rent on 01-01, so it all
  lands in January; I did not spread it. JE-004 bills an annual subscription to Deferred
  Revenue, which is a balance-sheet account, so only the monthly recognition entries hit revenue.
- **The subtype decides the section, and each section is shown from its own side.** Revenue and
  other income are credit minus debit; COGS and operating expenses are debit minus credit.
  Sales Returns & Discounts (contra revenue) therefore shows as (800.25) inside Revenue, and the
  vendor credit JE-020 reduces Software to 1,099.97 instead of appearing as income. An
  expense-type account with subtype `other_income` (interest expense, say) would show negative
  under Other income.
- **Inactive accounts still report their history.** Marketing (legacy) is inactive today but
  had a posted entry in January, so it is on the Q1 statement.
- **Accounts with no posted lines in the range are not listed.** An account whose lines net to
  zero is still listed at 0.00. Empty sections say "No activity" and total 0.00.
- **Bad books fail at startup.** Unbalanced posted entries, unknown accounts, amounts that are
  not decimal strings or have more than two decimals, a line with both or neither side, and a
  type/subtype that disagree all stop the app with a clear error, rather than producing a
  statement that is quietly wrong. Drafts may be unbalanced. The provided ledger passes.
- **Money** is `Decimal` from the JSON strings to the response, and leaves the API as a string.
  The frontend formats that string without turning it into a number.
- **One currency** (USD), as the file says. No fiscal-year or period-locking logic.

## How I checked the numbers

- Worked Q1 by hand from the journal, account by account, before looking at the app's output;
  the test asserts every line and subtotal against that.
- February alone and single days at the range edges, also by hand.
- An independent check over about 1,000 ranges (every start/end on, before and after each
  entry date): since every posted entry balances, net income must equal the net debit of the
  balance-sheet accounts for the same entries. That side uses no section or sign logic.
- Broke the code on purpose to see the tests fail: an exclusive end date, counting drafts and
  voids, flipping the sign of Other income, moving contra revenue to operating expenses. Each
  one fails at least two tests.

## Where AI helped, and where I did not trust it

- Used Claude Code for most of the code, the test scaffolding and the frontend wiring.
- It got a hand total wrong: the February test first expected (13,530.25). The app said
  (13,230.25). Re-adding by hand (8,549.75 − 3,280.00 − 18,500.00) showed the test was wrong,
  not the code. That is why every expected number in the tests has its working in a comment.
- The frontend tests first failed with "fetch failed": the generated API client captured
  `fetch` at import time, before the mock server replaced it. Fixed by looking `fetch` up per call.
- Date display: `new Date("2026-01-01")` is midnight UTC, which shows as December 31 in
  California. The formatter pins UTC and has a test.

## Next, with more time

- Drill down from a line to the journal entries behind it.
- Comparative columns (this period vs. prior period) and a balance sheet from the same ledger.
- Account hierarchy roll-ups, if the chart of accounts gets parents.
- One typed error shape for 422s: today a malformed date and start-after-end return different
  `detail` shapes, and the frontend handles both.
