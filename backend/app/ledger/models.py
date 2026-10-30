from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class AccountType(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class Subtype(StrEnum):
    OPERATING_REVENUE = "operating_revenue"
    CONTRA_REVENUE = "contra_revenue"
    COGS = "cogs"
    OPERATING_EXPENSE = "operating_expense"
    OTHER_INCOME = "other_income"
    BALANCE_SHEET = "balance_sheet"


class EntryStatus(StrEnum):
    POSTED = "posted"
    DRAFT = "draft"
    VOID = "void"


@dataclass(frozen=True)
class Account:
    number: str
    name: str
    type: AccountType
    subtype: Subtype
    is_active: bool


@dataclass(frozen=True)
class JournalLine:
    account: str
    debit: Decimal
    credit: Decimal


@dataclass(frozen=True)
class JournalEntry:
    id: str
    date: date
    status: EntryStatus
    memo: str
    lines: tuple[JournalLine, ...]


@dataclass(frozen=True)
class Ledger:
    company: str
    currency: str
    # Keyed by account number, in chart-of-accounts order.
    accounts: dict[str, Account]
    entries: tuple[JournalEntry, ...]
