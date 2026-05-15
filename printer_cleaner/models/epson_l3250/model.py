from printer_cleaner.models.base import PrinterCommand


class EpsonL3250:
    """ESC/P2 Remote Mode commands used by Epson inkjet maintenance tools."""

    _EJL_1284_4_EXIT = b"\x1b\x01@EJL 1284.4\n@EJL     \n"
    _ESC_INIT = b"\x1b@"
    _REMOTE_START = b"\x1b(R\x08\x00\x00REMOTE1"
    _REMOTE_END = b"\x1b\x00\x00\x00"
    _JOB_PREFIX = b"\x00\x00\x00"
    _TIMER_INIT = b"TI\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    _TARGETS = {
        "all": 0x00,
        "black": 0x01,
        "color": 0x02,
    }

    def build_head_clean(self, clean_target: str) -> PrinterCommand:
        if clean_target not in self._TARGETS:
            supported = ", ".join(sorted(self._TARGETS))
            raise ValueError(f"Unsupported CLEAN_TARGET={clean_target!r}; supported values: {supported}")

        target = self._TARGETS[clean_target]
        payload = (
            self._JOB_PREFIX
            + self._EJL_1284_4_EXIT
            + self._ESC_INIT
            + self._ESC_INIT
            + self._REMOTE_START
            + self._TIMER_INIT
            + b"CH\x02\x00\x00"
            + bytes([target])
            + self._REMOTE_END
        )
        return PrinterCommand(payload=payload, description=f"Epson ESC/P2 head cleaning ({clean_target})")
