"""
copyright (c) 2023 CAT Camp

copyright is just included for takedowns if this is used for commercial projects
DONT PANIC :)

this file is provided under the gplv3 license -see the full legal text in the project
"""
import logging
from time import sleep
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, PACK
import smartcard.System
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from smartcard.Exceptions import CardConnectionException
getsn = [0xFF, 0xCA, 0x00, 0x00, 0x04]

"""
luser area!

This is the area you add handlers for your project

"""
# this is the delay in seconds between frobs, when the system
# resets.  we usually use this for attract mode - playing a tune
# or flashing lights to sucker people over
FROB_DELAY = 120

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


def anonymous_hooman(hooman_id: str):
    """
    we see a hooman - but we dont have any extra info about
    name or anything to roast them.  hooman_id is likely
    unique but might not be - it's only a 32 bit number

    for playa use, 32 bits is 'fine' though.  just use
    the hooman_id and assume it is unique
    """
    print("you have been terminated, hooman ", hooman_id)


def frob():
    """
    used to trigger attract mode - the timer ran out
    so play a song or something
    """
    print("Look at me!")

class PrintObserver(CardObserver):
    """
        this is the handler that sees the cards coming and going
        from the scanner
    """
    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("Inserted ATR: ", toHexString(card.atr, PACK))
            card.connection = card.createConnection()
            try:
                card.connection.connect()
                response, sw1, sw2 = card.connection.transmit(getsn)
                nfc_id = "{}".format(toHexString(response, format=PACK)).replace(" ", "").lower()            
                anonymous_hooman(nfc_id)
            except CardConnectionException:
                premature_ejection()
        for card in removedcards:
            slinking_away(toHexString(card.atr, format=PACK))


print("Purr2PurrSDK Copyright (c) 2023 CAT Camp")
print("Source is GPLv3 Licensed - YOU MAY NOT USE FOR COMMERCE")
print("Booting - looking for scanners....")
scanners = smartcard.System.readers()
if len(scanners) == 0:
	logging.error("nothing found - did you install the hacked library and deps?")
print("Available devices:")
for d in scanners:
	print(f"\t{d}")
while True:
    print(smartcard.System.readers())
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver()
    cardmonitor.addObserver(cardobserver)
    print("Waiting...")
    sleep(FROB_DELAY)
    frob()

# don't forget to remove observer, or the
# monitor will poll forever...
cardmonitor.deleteObserver(cardobserver)


