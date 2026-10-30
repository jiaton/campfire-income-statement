from datetime import date, timedelta
from decimal import Decimal
from itertools import combinations_with_replacement

import pytest

from app.income_statement.service import InvalidPeriodError, build_income_statement
from app.ledger.models import EntryStatus, Subtype
from app.ledger.parsing import parse_ledger
from tests.conftest import entry, raw_ledger


def amounts(section) -> dict[str, Decimal]:
    return {line.account.number: line.amount for line in section.lines}


def test_q1_2026_matches_hand_calculation(ledger):
    statement = build_income_statement(ledger, date(2026, 1, 1), date(2026, 3, 31))

    # JE-002 + JE-010 + JE-016 product sales; JE-009 is the void duplicate.
    assert amounts(statement.revenue) == {
        "4000": Decimal("35650.75"),
        "4100": Decimal("3000.00"),
        "4900": Decimal("-800.25"),  # JE-012 return 650.25 + JE-016 discount 150.00
    }
    assert statement.revenue.total == Decimal("37850.50")
    assert amounts(statement.cost_of_goods_sold) == {"5000": Decimal("14272.75")}
    assert statement.gross_profit == Decimal("23577.75")
    assert amounts(statement.operating_expenses) == {
        "6000": Decimal("55500.00"),  # three payrolls; JE-019 bonus is still a draft
        "6100": Decimal("9000.00"),
        "6200": Decimal("1099.97"),  # 1199.97 less the 100.00 vendor credit
        "6300": Decimal("2500.10"),  # inactive today, but posted in January
    }
    assert statement.operating_expenses.total == Decimal("68100.07")
    assert statement.operating_income == Decimal("-44522.32")
    assert amounts(statement.other_income) == {"7000": Decimal("42.18")}
    assert statement.net_income == Decimal("-44480.14")


def test_february_only(ledger):
    statement = build_income_statement(ledger, date(2026, 2, 1), date(2026, 2, 28))

    assert amounts(statement.revenue) == {
        "4000": Decimal("8200.00"),
        "4100": Decimal("1000.00"),
        "4900": Decimal("-650.25"),
    }
    # 8549.75 net revenue - 3280.00 COGS - 18500.00 payroll
    assert statement.net_income == Decimal("-13230.25")


def test_both_ends_of_the_range_are_included(ledger):
    statement = build_income_statement(ledger, date(2026, 3, 31), date(2026, 3, 31))

    assert amounts(statement.revenue) == {"4100": Decimal("1000.00")}
    assert amounts(statement.operating_expenses) == {"6000": Decimal("18500.00")}
    assert amounts(statement.other_income) == {"7000": Decimal("42.18")}


def test_range_with_no_activity_is_all_zero(ledger):
    statement = build_income_statement(ledger, date(2027, 1, 1), date(2027, 12, 31))

    assert statement.revenue.lines == ()
    assert statement.net_income == Decimal("0.00")


def test_start_after_end_is_rejected(ledger):
    with pytest.raises(InvalidPeriodError):
        build_income_statement(ledger, date(2026, 3, 31), date(2026, 1, 1))


def test_only_posted_entries_count():
    sale = [("1000", "100.00", "0.00"), ("4000", "0.00", "100.00")]
    ledger = parse_ledger(
        raw_ledger(
            [
                entry("JE-1", "2026-01-01", sale),
                entry("JE-2", "2026-01-01", sale, status="draft"),
                entry("JE-3", "2026-01-01", sale, status="void"),
            ]
        )
    )

    statement = build_income_statement(ledger, date(2026, 1, 1), date(2026, 1, 1))

    assert statement.net_income == Decimal("100.00")


def test_other_income_nets_income_and_expense_accounts():
    ledger = parse_ledger(
        raw_ledger(
            [
                entry("JE-1", "2026-01-01", [("1000", "50.00", "0.00"), ("7000", "0.00", "50.00")]),
                entry("JE-2", "2026-01-01", [("7100", "20.00", "0.00"), ("1000", "0.00", "20.00")]),
            ]
        )
    )

    statement = build_income_statement(ledger, date(2026, 1, 1), date(2026, 1, 1))

    assert amounts(statement.other_income) == {"7000": Decimal("50.00"), "7100": Decimal("-20.00")}
    assert statement.net_income == Decimal("30.00")


def test_account_that_nets_to_zero_is_still_listed():
    ledger = parse_ledger(
        raw_ledger(
            [
                entry("JE-1", "2026-01-01", [("1000", "10.00", "0.00"), ("4000", "0.00", "10.00")]),
                entry("JE-2", "2026-01-02", [("4000", "10.00", "0.00"), ("1000", "0.00", "10.00")]),
            ]
        )
    )

    statement = build_income_statement(ledger, date(2026, 1, 1), date(2026, 1, 31))

    assert amounts(statement.revenue) == {"4000": Decimal("0.00")}


def test_net_income_equals_the_balance_sheet_side_for_every_range(ledger):
    # Every posted entry balances, so whatever lands in revenue and expense accounts is mirrored
    # by the balance-sheet accounts. Computing it from that side is independent of the section
    # and sign logic. Ranges start and end on, just before, and just after every entry date.
    boundaries = sorted(
        {entry.date + timedelta(days=offset) for entry in ledger.entries for offset in (-1, 0, 1)}
    )
    for start, end in combinations_with_replacement(boundaries, 2):
        balance_sheet_net_debit = sum(
            (
                line.debit - line.credit
                for entry in ledger.entries
                if entry.status is EntryStatus.POSTED and start <= entry.date <= end
                for line in entry.lines
                if ledger.accounts[line.account].subtype is Subtype.BALANCE_SHEET
            ),
            Decimal("0"),
        )

        statement = build_income_statement(ledger, start, end)

        assert statement.net_income == balance_sheet_net_debit, (start, end)
