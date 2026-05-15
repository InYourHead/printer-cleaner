from printer_cleaner.models.epson_l3250 import EpsonL3250


def test_head_clean_all_payload():
    command = EpsonL3250().build_head_clean("all")

    assert command.payload == (
        b"\x00\x00\x00"
        b"\x1b\x01@EJL 1284.4\n@EJL     \n"
        b"\x1b@"
        b"\x1b@"
        b"\x1b(R\x08\x00\x00REMOTE1"
        b"TI\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"CH\x02\x00\x00\x00"
        b"\x1b\x00\x00\x00"
    )


def test_head_clean_target_byte_changes():
    assert EpsonL3250().build_head_clean("black").payload[-5] == 0x01
    assert EpsonL3250().build_head_clean("color").payload[-5] == 0x02
