"""
copyright (c) 2023 CAT Camp

"""
import logging


_decoder_ring = {
    "62": {
        "00": "no info returned from device",
        "81": "checksum error on data",
        "82": "data is truncated",
        "83": "invalid df",
        "84": "io error",

    }
}


def sw_decoder(sw1: int, sw2:int):
    """
    decodes and logs the cryptic sw code.  returns true if operation was okay
    :param sw1:
    :param sw2:
    :return:
    """
    if sw1 == 0 and sw2 == 0:
        logging.debug("read operation ok")
        return True
    try:
        logging.warning(_decoder_ring[sw1][sw2])
    except KeyError:
        logging.warning(f"undefined error {sw1}/{sw2} - see smartcard spec")
    return False
