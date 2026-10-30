from pathlib import Path

import pytest

from app.ledger.models import Ledger
from app.ledger.repository import JsonLedgerRepository

LEDGER_PATH = Path(__file__).resolve().parents[2] / "ledger.json"


@pytest.fixture(scope="session")
def ledger() -> Ledger:
    return JsonLedgerRepository(LEDGER_PATH).get()


def account(number: str, type_: str, subtype: str, name: str | None = None) -> dict:
    return {
        "number": number,
        "name": name or f"Account {number}",
        "type": type_,
        "subtype": subtype,
        "is_active": True,
    }


def entry(id_: str, date: str, lines: list[tuple[str, str, str]], status: str = "posted") -> dict:
    return {
        "id": id_,
        "date": date,
        "status": status,
        "memo": "",
        "lines": [{"account": a, "debit": d, "credit": c} for a, d, c in lines],
    }


def raw_ledger(entries: list[dict], accounts: list[dict] | None = None) -> dict:
    return {
        "company": "Test Co",
        "currency": "USD",
        "accounts": accounts
        or [
            account("1000", "asset", "balance_sheet", "Cash"),
            account("4000", "revenue", "operating_revenue", "Sales"),
            account("4900", "revenue", "contra_revenue", "Returns"),
            account("5000", "expense", "cogs", "COGS"),
            account("6000", "expense", "operating_expense", "Salaries"),
            account("7000", "revenue", "other_income", "Interest Income"),
            account("7100", "expense", "other_income", "Interest Expense"),
        ],
        "journal_entries": entries,
    }
