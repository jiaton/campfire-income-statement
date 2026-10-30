from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from app.ledger.models import (
    Account,
    AccountType,
    EntryStatus,
    JournalEntry,
    JournalLine,
    Ledger,
    Subtype,
)

BALANCE_SHEET_TYPES = {AccountType.ASSET, AccountType.LIABILITY, AccountType.EQUITY}


class LedgerError(ValueError):
    pass


def parse_ledger(raw: dict[str, Any]) -> Ledger:
    accounts: dict[str, Account] = {}
    for raw_account in raw["accounts"]:
        account = _parse_account(raw_account)
        if account.number in accounts:
            raise LedgerError(f"duplicate account {account.number}")
        accounts[account.number] = account

    entries: list[JournalEntry] = []
    seen_ids: set[str] = set()
    for raw_entry in raw["journal_entries"]:
        entry = _parse_entry(raw_entry, accounts)
        if entry.id in seen_ids:
            raise LedgerError(f"duplicate journal entry {entry.id}")
        seen_ids.add(entry.id)
        entries.append(entry)

    return Ledger(
        company=raw["company"],
        currency=raw["currency"],
        accounts=accounts,
        entries=tuple(entries),
    )


def _parse_account(raw: dict[str, Any]) -> Account:
    account = Account(
        number=raw["number"],
        name=raw["name"],
        type=AccountType(raw["type"]),
        subtype=Subtype(raw["subtype"]),
        is_active=raw["is_active"],
    )
    # The subtype places the account on the statement, so it has to agree with the type.
    on_balance_sheet = account.subtype is Subtype.BALANCE_SHEET
    if on_balance_sheet != (account.type in BALANCE_SHEET_TYPES):
        raise LedgerError(
            f"account {account.number}: type {account.type} does not match subtype {account.subtype}"
        )
    return account


def _parse_entry(raw: dict[str, Any], accounts: dict[str, Account]) -> JournalEntry:
    entry_id = raw["id"]
    lines = tuple(_parse_line(entry_id, raw_line, accounts) for raw_line in raw["lines"])
    entry = JournalEntry(
        id=entry_id,
        date=date.fromisoformat(raw["date"]),
        status=EntryStatus(raw["status"]),
        memo=raw["memo"],
        lines=lines,
    )
    # Drafts may still be unbalanced while someone works on them, and voids never count.
    # A posted entry that does not balance would make every statement wrong, so refuse it.
    if entry.status is EntryStatus.POSTED:
        debits = sum((line.debit for line in lines), Decimal("0"))
        credits = sum((line.credit for line in lines), Decimal("0"))
        if len(lines) < 2 or debits != credits:
            raise LedgerError(f"{entry_id}: posted entry does not balance ({debits} vs {credits})")
    return entry


def _parse_line(entry_id: str, raw: dict[str, Any], accounts: dict[str, Account]) -> JournalLine:
    if raw["account"] not in accounts:
        raise LedgerError(f"{entry_id}: unknown account {raw['account']}")
    debit = _parse_amount(entry_id, raw["debit"])
    credit = _parse_amount(entry_id, raw["credit"])
    if (debit == 0) == (credit == 0):
        raise LedgerError(f"{entry_id}: each line needs exactly one of debit or credit")
    return JournalLine(account=raw["account"], debit=debit, credit=credit)


def _parse_amount(entry_id: str, value: Any) -> Decimal:
    # Strings only: a JSON number would already have gone through a float.
    if not isinstance(value, str):
        raise LedgerError(f"{entry_id}: amount {value!r} must be a decimal string")
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise LedgerError(f"{entry_id}: amount {value!r} is not a number") from None
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise LedgerError(f"{entry_id}: amount {value!r} must be non-negative with at most 2 decimals")
    return amount
