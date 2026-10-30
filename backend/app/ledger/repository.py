import json
from pathlib import Path
from typing import Protocol

from app.ledger.models import Ledger
from app.ledger.parsing import parse_ledger


class LedgerRepository(Protocol):
    def get(self) -> Ledger: ...


class JsonLedgerRepository:
    """Reads and validates the file once; the ledger is read-only after that."""

    def __init__(self, path: Path) -> None:
        self._ledger = parse_ledger(json.loads(path.read_text()))

    def get(self) -> Ledger:
        return self._ledger
