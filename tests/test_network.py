from printer_cleaner.network import normalize_mac, resolve_printer_address


def test_normalize_mac_accepts_common_formats():
    assert normalize_mac("aa:bb:cc:dd:ee:ff") == "aa:bb:cc:dd:ee:ff"
    assert normalize_mac("AA-BB-CC-DD-EE-FF") == "aa:bb:cc:dd:ee:ff"
    assert normalize_mac("aabb.ccdd.eeff") == "aa:bb:cc:dd:ee:ff"


def test_resolve_printer_address_prefers_explicit_ip():
    assert resolve_printer_address("192.168.1.50", None, None) == "192.168.1.50"


def test_resolve_printer_address_accepts_hostname():
    assert resolve_printer_address(None, None, "printer.local") == "printer.local"
