# Printer Cleaner

Printer Cleaner is a small LAN-only utility for running scheduled printer
maintenance commands. The first supported printer model is `epson_l3250`, which sends
an Epson ESC/P2 Remote Mode head-cleaning command over raw TCP/JetDirect,
usually port `9100`.

The tool is designed to run either as a short-lived one-shot process or as a
long-running process with an internal cron schedule.

## Operational Warning

Head cleaning consumes ink and contributes to the printer's waste ink
absorber/maintenance pad usage. Do not schedule it too frequently. For routine
prevention, printing a small color page periodically may be more appropriate
than running head cleaning often.

`ACTION=head-clean` is a generic application-level action available for printer
models that support head cleaning. `ACTION=test-head-clean` is the one-shot form
of the same action: if `DRY_RUN=false`, it sends the same real head-cleaning
command as `ACTION=head-clean` and then exits. It is not a harmless simulation.

Use `DRY_RUN=true` when you want to validate configuration without sending any
command to the printer.

## Configuration

All configuration is provided through environment variables.

| Env | Default | Description |
| --- | --- | --- |
| `PRINTER_MODEL` | `epson_l3250` | Printer model value. Currently only `epson_l3250` is supported. |
| `PRINTER_IP` | empty | Printer IPv4/IPv6 address in the local network. |
| `PRINTER_MAC` | empty | Printer MAC address in the local network. Resolved through the runtime's local ARP table. Best for local runs, not Docker Desktop. |
| `PRINTER_HOSTNAME` | empty | Printer hostname that resolves in the local network. |
| `PRINTER_PORT` | `9100` | Raw TCP/JetDirect port. |
| `ACTION` | `head-clean` | `head-clean` for normal operation, or generic `test-head-clean` for a one-shot run. |
| `CLEAN_TARGET` | `all` | Cleaning target: `all`, `black`, or `color`. Model support may vary. |
| `CRON_SCHEDULE` | empty | Five-field cron expression, for example `0 9 * * 1`. |
| `RUN_ON_START` | `true` without cron, otherwise `false` | Whether to run immediately on process startup. |
| `DRY_RUN` | `false` | If `true`, logs the command but does not send anything. |
| `LAN_ONLY` | `true` | Refuses to run unless the printer host resolves to a local/private address. |
| `SOCKET_TIMEOUT_SECONDS` | `10` | TCP connection timeout. |

## Finding The Printer Host

Configure exactly one of `PRINTER_IP`, `PRINTER_MAC`, or `PRINTER_HOSTNAME`.

Use a printer address that resolves inside your local network. Good options:

- Router admin page: look for connected devices, DHCP leases, or clients.
  Printers often appear with names containing the vendor or model number.
- Printer network status page: print a network status sheet from the printer or
  check the printer vendor's mobile/desktop app. Use the IPv4 address shown
  there.
- macOS: open `System Settings -> Printers & Scanners`, select the printer, and
  inspect printer details/options. If the address is not visible, use the router
  page or vendor app.
- Local network scan: from a trusted LAN machine, scan for devices with port
  `9100` open.

Example scan with `nmap`:

```bash
nmap -p 9100 --open 192.168.1.0/24
```

After finding a candidate address, verify that the printer web page opens:

```text
http://192.168.1.50
```

If your router supports DHCP reservations, reserve a fixed IP for the printer so
the scheduled job does not break after the printer receives a new address.

MAC address support has one important limitation: the application must resolve
the MAC address to an IP address before connecting to the printer. It does that
through the runtime's local ARP table. This usually works only when the process
has direct LAN visibility. Docker Desktop commonly runs containers behind
bridge/NAT networking, so the container cannot see the LAN ARP table. In Docker,
prefer `PRINTER_IP` or `PRINTER_HOSTNAME`.

## Local Run

Run once without sending anything to the printer:

```bash
PRINTER_IP=192.168.1.50 DRY_RUN=true python3 -m printer_cleaner
```

Run a real one-shot head-cleaning command:

```bash
PRINTER_IP=192.168.1.50 DRY_RUN=false python3 -m printer_cleaner
```

Run with the internal scheduler:

```bash
PRINTER_IP=192.168.1.50 \
CRON_SCHEDULE="0 9 * * 1" \
RUN_ON_START=false \
DRY_RUN=false \
python3 -m printer_cleaner
```

## Docker

Build the image:

```bash
docker build -t printer-cleaner .
```

## Publishing

Docker image publishing is handled by
[`.github/workflows/docker-publish.yml`](.github/workflows/docker-publish.yml).
The workflow reads the image version from [`VERSION`](VERSION), builds the image
in the first job, and publishes it to GitHub Container Registry in the second
job.

Published tags:

- `ghcr.io/<owner>/<repo>:<VERSION>`
- `ghcr.io/<owner>/<repo>:latest`

Update `VERSION` before publishing a new release.

Run once in dry-run mode:

```bash
docker run --rm \
  -e PRINTER_IP=192.168.1.50 \
  -e DRY_RUN=true \
  printer-cleaner
```

Run one real head-cleaning attempt and remove the container afterwards:

```bash
docker run --rm \
  -e PRINTER_IP=192.168.1.50 \
  -e ACTION=test-head-clean \
  -e DRY_RUN=false \
  printer-cleaner
```

Do not use `ACTION=test-head-clean` with a Docker Compose service that has
`restart: unless-stopped` or another automatic restart policy. The process exits
after one run, and the restart policy will start it again. The application keeps
a per-container marker to avoid sending the command repeatedly after a restart,
but the correct one-shot Docker command is `docker run --rm`.

You can use a hostname instead of `PRINTER_IP`:

```bash
docker run --rm \
  -e PRINTER_HOSTNAME=printer.local \
  -e DRY_RUN=true \
  printer-cleaner
```

`docker run --rm` removes the container after the process exits. The application
does not remove project files or host files.

Run continuously with Docker Compose:

```bash
cp docker-compose.example.yml docker-compose.yml
docker compose up -d --build
```

Example schedule:

```text
0 9 * * 1
```

This means every Monday at 09:00 according to the container timezone. Set
`TZ=Europe/Warsaw` or another timezone if you need predictable local wall-clock
time.

## Adding Printer Models

Add a new model package under `printer_cleaner/models/`, implement the
capability methods required by `PrinterModel`, and register it in
`printer_cleaner/models/__init__.py`.

Keep model names explicit and stable. For example, the Epson L3250 model is
registered as `epson_l3250`.

## Supported Models

See [SUPPORTED_MODELS.md](SUPPORTED_MODELS.md) for the list of supported printer
models and backend notes.
