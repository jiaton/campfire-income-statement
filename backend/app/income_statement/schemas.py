from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, PlainSerializer

from app.income_statement.service import IncomeStatement, StatementSection


def _money_to_str(amount: Decimal) -> str:
    # Inputs have at most two decimals and are only added and subtracted, so this never rounds.
    # abs() turns a negative zero into "0.00".
    return f"{abs(amount) if amount == 0 else amount:.2f}"


# Sent as a string so no JSON parser turns it into a float.
Money = Annotated[Decimal, PlainSerializer(_money_to_str, return_type=str)]


class StatementLineOut(BaseModel):
    account_number: str
    account_name: str
    amount: Money


class StatementSectionOut(BaseModel):
    lines: list[StatementLineOut]
    total: Money

    @classmethod
    def from_section(cls, section: StatementSection) -> "StatementSectionOut":
        return cls(
            lines=[
                StatementLineOut(
                    account_number=line.account.number,
                    account_name=line.account.name,
                    amount=line.amount,
                )
                for line in section.lines
            ],
            total=section.total,
        )


class IncomeStatementOut(BaseModel):
    company: str
    currency: str
    start: date
    end: date
    revenue: StatementSectionOut
    cost_of_goods_sold: StatementSectionOut
    gross_profit: Money
    operating_expenses: StatementSectionOut
    operating_income: Money
    other_income: StatementSectionOut
    net_income: Money

    @classmethod
    def from_statement(cls, statement: IncomeStatement, company: str, currency: str) -> "IncomeStatementOut":
        return cls(
            company=company,
            currency=currency,
            start=statement.start,
            end=statement.end,
            revenue=StatementSectionOut.from_section(statement.revenue),
            cost_of_goods_sold=StatementSectionOut.from_section(statement.cost_of_goods_sold),
            gross_profit=statement.gross_profit,
            operating_expenses=StatementSectionOut.from_section(statement.operating_expenses),
            operating_income=statement.operating_income,
            other_income=StatementSectionOut.from_section(statement.other_income),
            net_income=statement.net_income,
        )
