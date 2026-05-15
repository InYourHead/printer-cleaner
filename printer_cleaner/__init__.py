from pathlib import Path

__all__ = ["__version__"]


def _read_version() -> str:
    version_file = Path(__file__).resolve().parent.parent / "VERSION"
    return version_file.read_text(encoding="utf-8").strip()


__version__ = _read_version()
