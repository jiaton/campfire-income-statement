from decimal import Decimal

import pytest

from app.ledger.models import EntryStatus
from app.ledger.parsing import LedgerError, parse_ledger
from tests.conftest import account, entry, raw_ledger


def test_provided_ledger_loads(ledger):
    assert len(ledger.accounts) == 15
    assert len(ledger.entries) == 25
    je_008 = next(e for e in ledger.entries if e.id == "JE-008")
    assert je_008.lines[0].debit == Decimal("2500.10")


def test_amounts_are_exact_decimals():
    ledger = parse_ledger(raw_ledger([entry("JE-1", "2026-01-01", [("1000", "0.10", "0.00"), ("4000", "0.00", "0.10")])]))
    assert ledger.entries[0].lines[0].debit == Decimal("0.10")


def test_unbalanced_posted_entry_is_rejected():
    raw = raw_ledger([entry("JE-1", "2026-01-01", [("1000", "100.00", "0.00"), ("4000", "0.00", "99.99")])])
    with pytest.raises(LedgerError, match="does not balance"):
        parse_ledger(raw)


def test_unbalanced_draft_is_allowed():
    raw = raw_ledger([entry("JE-1", "2026-01-01", [("1000", "100.00", "0.00")], status="draft")])
    assert parse_ledger(raw).entries[0].status is EntryStatus.DRAFT


def test_unknown_account_is_rejected():
    raw = raw_ledger([entry("JE-1", "2026-01-01", [("1000", "1.00", "0.00"), ("9999", "0.00", "1.00")])])
    with pytest.raises(LedgerError, match="unknown account 9999"):
        parse_ledger(raw)


@pytest.mark.parametrize("amount", [12.5, "1.005", "-1.00", "abc", "NaN"])
def test_bad_amounts_are_rejected(amount):
    raw = raw_ledger([entry("JE-1", "2026-01-01", [("1000", amount, "0.00"), ("4000", "0.00", "1.00")])])
    with pytest.raises(LedgerError):
        parse_ledger(raw)


def test_line_with_both_sides_is_rejected():
    raw = raw_ledger([entry("JE-1", "2026-01-01", [("1000", "1.00", "1.00"), ("4000", "1.00", "1.00")])])
    with pytest.raises(LedgerError, match="exactly one"):
        parse_ledger(raw)


def test_subtype_must_agree_with_type():
    raw = raw_ledger([], accounts=[account("4000", "revenue", "balance_sheet")])
    with pytest.raises(LedgerError, match="does not match"):
        parse_ledger(raw)


def test_duplicate_entry_ids_are_rejected():
    lines = [("1000", "1.00", "0.00"), ("4000", "0.00", "1.00")]
    raw = raw_ledger([entry("JE-1", "2026-01-01", lines), entry("JE-1", "2026-01-02", lines)])
    with pytest.raises(LedgerError, match="duplicate"):
        parse_ledger(raw)
