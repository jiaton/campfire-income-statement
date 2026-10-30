from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from app.ledger.models import Account, EntryStatus, Ledger, Subtype


class Section(Enum):
    REVENUE = "revenue"
    COST_OF_GOODS_SOLD = "cost_of_goods_sold"
    OPERATING_EXPENSES = "operating_expenses"
    OTHER_INCOME = "other_income"


SECTION_BY_SUBTYPE = {
    Subtype.OPERATING_REVENUE: Section.REVENUE,
    Subtype.CONTRA_REVENUE: Section.REVENUE,
    Subtype.COGS: Section.COST_OF_GOODS_SOLD,
    Subtype.OPERATING_EXPENSE: Section.OPERATING_EXPENSES,
    Subtype.OTHER_INCOME: Section.OTHER_INCOME,
}

# Each section is shown from its own side: income sections as credit minus debit, cost
# sections as debit minus credit. That way a contra-revenue account comes out negative inside
# Revenue, and a vendor credit comes out as a reduction inside its expense line.
CREDIT_SIDE_SECTIONS = {Section.REVENUE, Section.OTHER_INCOME}


class InvalidPeriodError(ValueError):
    pass


@dataclass(frozen=True)
class StatementLine:
    account: Account
    amount: Decimal


@dataclass(frozen=True)
class StatementSection:
    lines: tuple[StatementLine, ...]

    @property
    def total(self) -> Decimal:
        return sum((line.amount for line in self.lines), Decimal("0.00"))


@dataclass(frozen=True)
class IncomeStatement:
    start: date
    end: date
    revenue: StatementSection
    cost_of_goods_sold: StatementSection
    operating_expenses: StatementSection
    other_income: StatementSection

    @property
    def gross_profit(self) -> Decimal:
        return self.revenue.total - self.cost_of_goods_sold.total

    @property
    def operating_income(self) -> Decimal:
        return self.gross_profit - self.operating_expenses.total

    @property
    def net_income(self) -> Decimal:
        return self.operating_income + self.other_income.total


def build_income_statement(ledger: Ledger, start: date, end: date) -> IncomeStatement:
    """Posted activity between start and end, both days included."""
    if start > end:
        raise InvalidPeriodError(f"start {start} is after end {end}")

    net_debit_by_account: dict[str, Decimal] = defaultdict(Decimal)
    for entry in ledger.entries:
        if entry.status is not EntryStatus.POSTED or not start <= entry.date <= end:
            continue
        for line in entry.lines:
            net_debit_by_account[line.account] += line.debit - line.credit

    lines_by_section: dict[Section, list[StatementLine]] = {section: [] for section in Section}
    # Walk the chart of accounts so lines come out in account-number order. Accounts with no
    # posted lines in the period are left out; an account whose lines net to zero stays in.
    for number, account in ledger.accounts.items():
        section = SECTION_BY_SUBTYPE.get(account.subtype)
        if section is None or number not in net_debit_by_account:
            continue
        net_debit = net_debit_by_account[number]
        amount = -net_debit if section in CREDIT_SIDE_SECTIONS else net_debit
        lines_by_section[section].append(StatementLine(account, amount))

    sections = {section: StatementSection(tuple(lines)) for section, lines in lines_by_section.items()}
    return IncomeStatement(
        start=start,
        end=end,
        revenue=sections[Section.REVENUE],
        cost_of_goods_sold=sections[Section.COST_OF_GOODS_SOLD],
        operating_expenses=sections[Section.OPERATING_EXPENSES],
        other_income=sections[Section.OTHER_INCOME],
    )
