from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.income_statement.schemas import IncomeStatementOut
from app.income_statement.service import InvalidPeriodError, build_income_statement
from app.ledger.models import Ledger

router = APIRouter()


def get_ledger(request: Request) -> Ledger:
    return request.app.state.ledger_repository.get()


@router.get("/income-statement")
def get_income_statement(
    start: Annotated[date, Query(description="First day of the period, included")],
    end: Annotated[date, Query(description="Last day of the period, included")],
    ledger: Annotated[Ledger, Depends(get_ledger)],
) -> IncomeStatementOut:
    try:
        statement = build_income_statement(ledger, start, end)
    except InvalidPeriodError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return IncomeStatementOut.from_statement(statement, ledger.company, ledger.currency)
