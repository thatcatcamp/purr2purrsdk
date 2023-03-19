# purr2purrsdk
Builder SDK for Purr2Purr

## concept

Purr2Purr uses NFC tokens and small LIDAR sensors to provide interactivity to camps and artists.
There is no requirement to code to use Purr2Purr - there is an Android app
that will interact with tokens.  Optionally - camps may upload data or 
digital items, but it requires preregistration and a certificate exchange.  Once home - Burners can 
download items and see their 'history' on the Playa for a limited time.

See the documentation for uploading for more details.

The LIDAR interface is also documented in a separate markdown.

Tokens are per year and are distributed at participating camps, but contain
no personal information.  Camps _should_ write the following records - each record
on an NFC device is limited to 16 bytes.

- 1 - Playa Name or the string 'hooman', SDK defaults to 'hooman'
- 2 - Year issued, i.e. - the string '2023', SDK defaults to '2023'
- 3 - Issuing camp, artwork or event, SDK defaults to 'rogue'

The key used to identify Burners is the serial number of the NFC 
device - which has the possibility (albeit small) of collisions if 
multiple vendors are used.

## setup

Affordable NFC readers seem to have many problems - install our version of CCID rather than the one in your distribution.
On a clean install:

1) git clone https://github.com/thatcatcamp/CCID.git && cd CCID
2) sudo apt-get install build-essential flex libusb-1* python3-pip swig libpcsclite-dev libpcsclite1 libusb-dev
3) run ./bootstrap
4) run ./configure (errors are problems with these instructions, PR fixes back)
5) sudo make install
6) sudo apt-get install pcscd pcscd-tools
7) run `pcscd -d -f ` and ensure the device inits correctly - from another terminal, run `pcsc_scan`.  it should pause and read an NFC card
8) `systemctl enable pcscd` and `systemctl start pcscd`


Once this is done - you should be able to run pcsc_scan and it will halt at 'card removed', which just means there is nothing to read.

```
root@catbook:/home/cat/CCID# pcsc_scan 
Using reader plug'n play mechanism
Scanning present readers...
0: ACS ACR122U PICC Interface 00 00
1: Broadcom Corp 5880 [Contacted SmartCard] (0123456789ABCD) 01 00
 
Tue Mar 14 16:38:04 2023
 Reader 0: ACS ACR122U PICC Interface 00 00
  Event number: 2
  Card state: Card removed, 
 Reader 1: Broadcom Corp 5880 [Contacted SmartCard] (0123456789ABCD) 01 00
  Event number: 0
  Card state: Card removed, 
```

## using the sdk

Do you want to upload data?  Then you need to check the readme under `network`.

The main SDK is a single file - checkout the source and directly edit purr.py and it will merge automatically.  ONLY EDIT THE LUSER AREA SECTION!
There is an additional library file (`purrutils.py`) included with utility functions you 
don't need unless you want to connect to the backend services.

As always, if this is too hard - you can use the app on any Android device too.

### premature_ejection

This means the user touched the scanner but pulled away before the transfer was complete (around 1 second).  Depending on camp themes, you can 
probably do any number of fun things with this.  We expect to use a buzzer sound because we are adults.  :)

### slinking_away

Means the user has disconnected the badge/card.  This is a noop for most art - but you can use this to 'turn off' when people leave.

### anonymous_hooman

A human has arrived only identified by a 32 bit number.  There is a nearly zero chance of an ID collision, but it is not impossible.  This is the ID used to upload data to the Purr2Purr SkyNet.

### frob
 
Frob is a timeout based on FROB_DELAY.  This is a handler to let you blink lights, hoot, or whatever.  Nothing is going on so attract more hoomans.



## legal crap

SDK components are GPLv3 licensed and cannot be used
commercially.  All contents are Copyright (c) 2023 CAT Camp.
