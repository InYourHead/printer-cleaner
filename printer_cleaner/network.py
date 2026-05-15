import ipaddress
import re
import socket
import subprocess
from pathlib import Path


def resolve_printer_address(
    printer_ip: str | None,
    printer_mac: str | None,
    printer_hostname: str | None,
) -> str:
    if printer_ip:
        ipaddress.ip_address(printer_ip)
        return printer_ip
    if printer_hostname:
        return printer_hostname
    if printer_mac:
        return resolve_mac_to_ip(printer_mac)
    raise ValueError("No printer address configured")


def resolve_mac_to_ip(mac: str) -> str:
    normalized_mac = normalize_mac(mac)
    arp_entries = _read_arp_entries()
    if normalized_mac in arp_entries:
        return arp_entries[normalized_mac]

    runtime_note = ""
    if _looks_like_container():
        runtime_note = (
            " This process appears to run inside a container; Docker bridge/NAT "
            "networking usually cannot see the LAN ARP table. In Docker, prefer "
            "PRINTER_IP or PRINTER_HOSTNAME."
        )

    raise ValueError(
        f"Could not resolve PRINTER_MAC={normalized_mac} to an IP address. "
        "MAC lookup uses the local ARP table, so the printer must already be "
        "visible on the same LAN. Use PRINTER_IP or PRINTER_HOSTNAME if MAC "
        f"resolution is not available in this runtime.{runtime_note}"
    )


def normalize_mac(mac: str) -> str:
    compact = re.sub(r"[^0-9a-fA-F]", "", mac)
    if len(compact) != 12 or not re.fullmatch(r"[0-9a-fA-F]{12}", compact):
        raise ValueError(f"Invalid MAC address: {mac!r}")
    return ":".join(compact[index : index + 2].lower() for index in range(0, 12, 2))


def assert_lan_host(host: str) -> None:
    addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    if not addresses:
        raise ValueError(f"Could not resolve host: {host}")

    public_addresses: list[str] = []
    for _, _, _, _, sockaddr in addresses:
        address = ipaddress.ip_address(sockaddr[0])
        if _is_lan_address(address):
            return
        public_addresses.append(str(address))

    raise ValueError(
        "Resolved printer host is not a LAN address. "
        f"Refusing to continue with LAN_ONLY=true. Resolved addresses: {', '.join(public_addresses)}"
    )


def _is_lan_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
    )


def _read_arp_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    entries.update(_read_linux_proc_arp())
    entries.update(_read_arp_command())
    return entries


def _read_linux_proc_arp() -> dict[str, str]:
    path = Path("/proc/net/arp")
    if not path.exists():
        return {}

    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        columns = line.split()
        if len(columns) >= 4:
            ip_address = columns[0]
            mac_address = columns[3]
            try:
                entries[normalize_mac(mac_address)] = ip_address
            except ValueError:
                continue
    return entries


def _read_arp_command() -> dict[str, str]:
    try:
        result = subprocess.run(
            ["arp", "-an"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return {}

    entries: dict[str, str] = {}
    pattern = re.compile(
        r"\((?P<ip>[^)]+)\)\s+at\s+(?P<mac>(?:[0-9a-fA-F]{1,2}[:-]){5}[0-9a-fA-F]{1,2})"
    )
    for match in pattern.finditer(result.stdout):
        try:
            entries[normalize_mac(match.group("mac"))] = match.group("ip")
        except ValueError:
            continue
    return entries


def _looks_like_container() -> bool:
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()
