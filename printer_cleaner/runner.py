import logging
import socket
import time
from datetime import datetime
from pathlib import Path

from printer_cleaner.config import Config
from printer_cleaner.cron import CronSchedule
from printer_cleaner.models import get_model
from printer_cleaner.models.base import PrinterCommand, PrinterModel
from printer_cleaner.network import assert_lan_host, resolve_printer_address

logger = logging.getLogger(__name__)
TEST_MODE_MARKER = Path("/tmp/printer-cleaner-test-head-clean.done")


def run_once(config: Config) -> None:
    printer_address = resolve_printer_address(
        config.printer_ip,
        config.printer_mac,
        config.printer_hostname,
    )
    if config.lan_only:
        assert_lan_host(printer_address)

    model = get_model(config.printer_model)
    command = build_command(config, model)

    logger.info("Prepared command: %s", command.description)
    if config.dry_run:
        logger.info("DRY_RUN=true; not sending %d bytes to printer", len(command.payload))
        return

    logger.info(
        "Sending %d bytes to %s:%s",
        len(command.payload),
        printer_address,
        config.printer_port,
    )
    with socket.create_connection(
        (printer_address, config.printer_port),
        timeout=config.socket_timeout_seconds,
    ) as sock:
        sock.settimeout(config.socket_timeout_seconds)
        sock.sendall(command.payload)
    logger.info("Command sent")


def build_command(config: Config, model: PrinterModel) -> PrinterCommand:
    if config.action in {"head-clean", "test-head-clean"}:
        return model.build_head_clean(config.clean_target)
    raise ValueError(f"Unsupported ACTION={config.action!r}")


def run_forever(config: Config) -> None:
    if config.test_mode:
        if _container_runtime() and TEST_MODE_MARKER.exists():
            logger.error(
                "Test mode has already run in this container. "
                "Not sending another head-cleaning command. "
                "If Docker Compose restart policy is enabled, stop the service or recreate the container."
            )
            while True:
                time.sleep(3600)

        if _container_runtime():
            logger.info("Test mode enabled; marking this container as used before sending command")
            TEST_MODE_MARKER.write_text(datetime.now().isoformat(), encoding="utf-8")
        else:
            logger.info("Test mode enabled; running once and exiting")
        run_once(config)
        logger.info("Test mode finished; exiting")
        return

    if config.run_on_start:
        run_once(config)

    if not config.schedule:
        return

    schedule = CronSchedule.parse(config.schedule)
    while True:
        now = datetime.now()
        next_run = schedule.next_after(now)
        sleep_seconds = max(0.0, (next_run - now).total_seconds())
        logger.info("Next run scheduled at %s", next_run.isoformat(timespec="minutes"))
        time.sleep(sleep_seconds)
        run_once(config)


def _container_runtime() -> bool:
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()
