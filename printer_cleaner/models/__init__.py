from printer_cleaner.models.base import PrinterModel
from printer_cleaner.models.epson_l3250 import EpsonL3250


def get_model(name: str) -> PrinterModel:
    if name == "epson_l3250":
        return EpsonL3250()
    raise ValueError(f"Unsupported PRINTER_MODEL={name!r}")
