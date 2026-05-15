import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Config:
    printer_model: str
    printer_ip: str | None
    printer_mac: str | None
    printer_hostname: str | None
    printer_port: int
    action: str
    clean_target: str
    schedule: str | None
    run_on_start: bool
    dry_run: bool
    lan_only: bool
    socket_timeout_seconds: float

    @property
    def test_mode(self) -> bool:
        return self.action == "test-head-clean"

    @classmethod
    def from_env(cls) -> "Config":
        printer_ip = _optional_env("PRINTER_IP")
        printer_mac = _optional_env("PRINTER_MAC")
        printer_hostname = _optional_env("PRINTER_HOSTNAME")

        configured_addresses = [
            value
            for value in (printer_ip, printer_mac, printer_hostname)
            if value is not None
        ]
        if len(configured_addresses) != 1:
            raise ValueError(
                "Configure exactly one printer address: "
                "PRINTER_IP, PRINTER_MAC, or PRINTER_HOSTNAME"
            )

        schedule = os.getenv("CRON_SCHEDULE") or None

        return cls(
            printer_model=os.getenv("PRINTER_MODEL", "epson_l3250").strip().lower(),
            printer_ip=printer_ip,
            printer_mac=printer_mac,
            printer_hostname=printer_hostname,
            printer_port=int(os.getenv("PRINTER_PORT", "9100")),
            action=os.getenv("ACTION", "head-clean").strip().lower(),
            clean_target=os.getenv("CLEAN_TARGET", "all").strip().lower(),
            schedule=schedule,
            run_on_start=_bool_env("RUN_ON_START", schedule is None),
            dry_run=_bool_env("DRY_RUN", False),
            lan_only=_bool_env("LAN_ONLY", True),
            socket_timeout_seconds=float(os.getenv("SOCKET_TIMEOUT_SECONDS", "10")),
        )


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None
