import os
from pathlib import Path

from fastapi import FastAPI

from app.income_statement.router import router as income_statement_router
from app.ledger.repository import JsonLedgerRepository, LedgerRepository

DEFAULT_LEDGER_PATH = Path(__file__).resolve().parents[2] / "ledger.json"


def create_app(ledger_repository: LedgerRepository | None = None) -> FastAPI:
    app = FastAPI(title="Income statement")
    app.state.ledger_repository = ledger_repository or JsonLedgerRepository(
        Path(os.environ.get("LEDGER_PATH", DEFAULT_LEDGER_PATH))
    )
    app.include_router(income_statement_router)
    return app


app = create_app()
