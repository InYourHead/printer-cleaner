from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PrinterCommand:
    payload: bytes
    description: str


class PrinterModel(Protocol):
    def build_head_clean(self, clean_target: str) -> PrinterCommand:
        ...
