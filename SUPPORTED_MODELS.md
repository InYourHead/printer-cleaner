# Supported Models

## Epson L3250

Printer model value: `epson_l3250`

The default Epson L3250 implementation sends an ESC/P2 Remote Mode command
sequence for print-head cleaning.

This is a local-network approach. It does not use Epson cloud services and does
not automate a desktop printer-driver UI. Compatibility depends on printer
firmware and whether the printer accepts raw TCP data on port `9100`.

Supported cleaning targets:

| Target | Description |
| --- | --- |
| `all` | Clean all heads. |
| `black` | Clean black head. |
| `color` | Clean color heads. |
