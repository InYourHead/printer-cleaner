from printer_cleaner.models.epson_l3250 import EpsonL3250


def test_head_clean_all_payload():
    command = EpsonL3250().build_head_clean("all")

    assert command.payload == (
        b"\x1b\x01@EJL 1284.4\n@EJL     \n"
        b"\x1b@"
        b"\x1b(R\x08\x00REMOTE1"
        b"CH\x02\x00\x00\x00"
        b"\x1b\x00\x00\x00"
        b"\x0c"
    )
