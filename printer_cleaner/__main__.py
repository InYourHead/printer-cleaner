import logging
import sys

from printer_cleaner.config import Config
from printer_cleaner.runner import run_forever


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        run_forever(Config.from_env())
    except Exception:
        logging.exception("Printer maintenance failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
