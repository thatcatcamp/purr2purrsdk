#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
this works with the more expensive but more functional readers:

https://nfcpy.readthedocs.io/en/latest/overview.html#supported-devices

note that you likely will need to inhibit the kernel from claiming the device,
especially if you are running a full OS with X11.  the module will tell you
the command and if something is visible with:

python -m nfc

this command will output diagnostics you can use:

This is the 1.0.4 version of nfcpy run in Python 3.10.6
on Linux-5.19.0-35-generic-x86_64-with-glibc2.35
I'm now searching your system for contactless devices
** found usb:054c:06c1 at usb:003:009 but it's already used
-- scan sysfs entry at '/sys/bus/usb/devices/3-3.1:1.0/'
-- the device is used by the 'port100' kernel driver
-- this kernel driver belongs to the linux nfc subsystem
-- you can remove it to free the device for this session
   sudo modprobe -r port100
-- and blacklist the driver to prevent loading next time
   sudo sh -c 'echo blacklist port100 >> /etc/modprobe.d/blacklist-nfc.conf'
I'm not trying serial devices because you haven't told me
-- add the option '--search-tty' to have me looking
-- but beware that this may break other serial devs
Sorry, but I couldn't find any contactless device



if you are using a laptop with an integrated reader - you might need to change
the allowed devices for ContactlessFrontend

copyright (c) 2023 CAT Camp

copyright is just included for takedowns if this is used for commercial projects
DONT PANIC :)

this file is provided under the gplv3 license -see the full legal text in the project
"""
import _thread
import binascii
import logging
import time

import nfc
import requests
from loguru import logger


def premature_ejection():
    """
    this fires when the person did not let the transfer
    from the tag to the reader complete.  you probably
    want to add a buzzer or something for this
    """
    print("Premature ejection - am I too sexy for you?")


def slinking_away(session_tag: str):
    """
    card removed - possibly add a power down sound here?
    session tag is the ATR of the card, which sort of useful
    but not really - read more at https://en.wikipedia.org/wiki/Answer_to_reset

    """
    print("not going to stay the night?  ", session_tag)


def hooman(hooman_id: str, xnm='hooman', xyr='2023', xis='losers'):
    """
    we see a hooman - but we dont have any extra info about
    name or anything to roast them.  hooman_id is likely
    unique but might not be - it's only a 32 bit number

    for playa use, 32 bits is 'fine' though.  just use
    the hooman_id and assume it is unique
    """
    print("you have been terminated, hooman ", hooman_id)
    hooman_packet = {"eventtype": "tap", "hooman_id": hooman_id, "xnm": xnm, "xyr": xyr, "xis": xis}
    logger.info('hooman seen!')
    try:
        results = requests.post("http://localhost:8080/push", json=hooman_packet)
        print(results.status_code)
    except requests.exceptions.ConnectionError:
        logging.exception("ipcproxy is down?")



def frob():
    """
    used to trigger attract mode - the timer ran out
    so play a song or something
    """
    print("Look at me!")


def on_startup(targets):
    if targets is None or len(targets) == 0:
        logging.exception("Unable to find a reader - try to run `python -m nfc` or `lsusb` to ensure it is there")
    for target in targets:
        print("allowed target: ", target)
    # return devices you want to use here - you can disable
    # integrated readers this way (laptops usually have them on the handrest area)
    return targets


def on_release(tag_in):
    # short read - we couldn't get any data
    premature_ejection(tag_in)


def smart_extract(tag_text: str, default_text: str):
    split = tag_text.split(":")
    if len(split) != 2:
        return default_text
    # python unicode handling is absolutely crap
    return split[1].encode('utf-8').lstrip().rstrip().decode('utf-8')


def backfrob():
    time.sleep(120)
    frob()
    _thread.start_new(backfrob, ())


clf = nfc.ContactlessFrontend()
# open any supported
assert clf.open('usb') is True
# start background frob
_thread.start_new(backfrob, ())
try:
    while True:
        tag = clf.connect(rdwr={
            'on-connect': lambda tag: False,
            'on-startup': on_startup,
            'on-release': on_release,
            'beep-on-connect': True})
        # reset defaults
        hooman_name = "hooman"
        hooman_year = "2023"
        hooman_camp = "losers"
        hooman_id = binascii.hexlify(tag.identifier).decode('utf-8')
        logger.info(f"base scan of hooman {hooman_id}")
        if tag.ndef is not None:
            for record in tag.ndef.records:
                # there are a lot of complex tags - ignore
                # anything weird people scan that has wifi tags or something
                if record.type == 'urn:nfc:wkt:T':
                    # name is usually empty for text.  encoding is always unicode (usually 8)
                    # people almost certainly will add crap to the text - clean
                    clean = str(record.text).lstrip().rstrip()
                    logger.info(clean)
                    if clean.startswith("xnm"):
                        hooman_name = smart_extract(clean, "hooman")
                    if clean.startswith("xyr"):
                        hooman_year = smart_extract(clean, "2023")
                    if clean.startswith("xis"):
                        hooman_camp = smart_extract(clean, "losers")
            hooman(hooman_id, hooman_name, hooman_year, hooman_camp)

            # stop processing crap
            time.sleep(5)
finally:
    clf.close()
