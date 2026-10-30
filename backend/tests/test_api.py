from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.income_statement.schemas import _money_to_str
from app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def test_q1_2026_response(client):
    response = client.get("/income-statement", params={"start": "2026-01-01", "end": "2026-03-31"})

    assert response.status_code == 200
    assert response.json() == {
        "company": "Northwind Coffee Roasters",
        "currency": "USD",
        "start": "2026-01-01",
        "end": "2026-03-31",
        "revenue": {
            "lines": [
                {"account_number": "4000", "account_name": "Product Revenue", "amount": "35650.75"},
                {"account_number": "4100", "account_name": "Subscription Revenue", "amount": "3000.00"},
                {"account_number": "4900", "account_name": "Sales Returns & Discounts", "amount": "-800.25"},
            ],
            "total": "37850.50",
        },
        "cost_of_goods_sold": {
            "lines": [{"account_number": "5000", "account_name": "Cost of Goods Sold", "amount": "14272.75"}],
            "total": "14272.75",
        },
        "gross_profit": "23577.75",
        "operating_expenses": {
            "lines": [
                {"account_number": "6000", "account_name": "Salaries", "amount": "55500.00"},
                {"account_number": "6100", "account_name": "Rent", "amount": "9000.00"},
                {"account_number": "6200", "account_name": "Software", "amount": "1099.97"},
                {"account_number": "6300", "account_name": "Marketing (legacy)", "amount": "2500.10"},
            ],
            "total": "68100.07",
        },
        "operating_income": "-44522.32",
        "other_income": {
            "lines": [{"account_number": "7000", "account_name": "Interest Income", "amount": "42.18"}],
            "total": "42.18",
        },
        "net_income": "-44480.14",
    }


def test_empty_period_has_zero_totals(client):
    response = client.get("/income-statement", params={"start": "2030-01-01", "end": "2030-01-31"})

    assert response.status_code == 200
    body = response.json()
    assert body["revenue"] == {"lines": [], "total": "0.00"}
    assert body["net_income"] == "0.00"


@pytest.mark.parametrize(
    "params",
    [
        {"start": "2026-03-31", "end": "2026-01-01"},
        {"start": "2026-02-30", "end": "2026-03-31"},
        {"start": "2026-01-01"},
    ],
)
def test_bad_periods_are_rejected(client, params):
    assert client.get("/income-statement", params=params).status_code == 422


def test_negative_zero_is_shown_as_zero():
    assert _money_to_str(Decimal("-0.00")) == "0.00"
    assert _money_to_str(Decimal("-0.5")) == "-0.50"
