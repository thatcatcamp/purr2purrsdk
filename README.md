# purr2purrsdk

Builder SDK for Purr2Purr

## concept

Purr2Purr uses NFC tokens and small LIDAR sensors to provide interactivity to camps and artists.
There is no requirement to code to use Purr2Purr - there is an Android app
that will interact with tokens.  Optionally - camps may upload data or 
digital items, but it requires preregistration and a certificate exchange.  Once home - Burners can 
download items and see their 'history' on the Playa for a limited time.

You can pick and choose what you want to support.


See the documentation for uploading for more details.

The LIDAR interface is also documented in a separate markdown.

Tokens are per year and are distributed at participating camps, but contain
no personal information.  Camps _should_ write the following records - each record consists of a 
tag, a colon (:) and the value.

| tag | meaning                   | SDK default |                                        
|-----|---------------------------|-------------|
| xnm | Playa Name                | hooman      |
| xyr | Year issued (i.e. - 2023) | 2023        |
| xis | Issuing Camp              | losers      |


The key used to identify Burners is the serial number of the NFC 
device - which has the possibility (albeit small) of collisions if 
multiple vendors are used.  Given the relatively poor randomness
on playa, that's probably acceptable.

'Should' is used because open source to write these tags
is largely terrible.  CAT Camp uses an Android app to write them.

##

## NFC Setup /  ACR122U Only

*NOTE*: this reader appears incapable of reading extended tags and
has numerous problems.  That said - it is _extremely_ cheap and easy to find.  

This reader is DOA without installing our version of CCID rather than the one in your distribution.
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

Use `purracr122u.py` instead of purrnfc.py.

## NFC Setup / Sony-Gemalto Readers

See the (long) list of supported but more expensive devices at : 
https://nfcpy.readthedocs.io/en/latest/overview.html#supported-devices

Note that you likely will need to inhibit the kernel from claiming the device,
especially if you are running a full OS with X11.  the module will tell you
the command and if something is visible with:

`python -m nfc`

this command will output diagnostics you can use:

```This is the 1.0.4 version of nfcpy run in Python 3.10.6
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
```


if you are using a laptop with an integrated reader - you might need to change
the allowed devices for ContactlessFrontend


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

### hooman

A human has arrived identified by a 32 bit number and possibly a name.  There is a nearly zero chance of an ID collision, but it is not impossible.  This is the ID used to upload data to the Purr2Purr SkyNet.

### frob
 
Frob is a timeout based on FROB_DELAY.  This is a handler to let you blink lights, hoot, or whatever.  Nothing is going on so attract more hoomans.


## Legal Crap

SDK components are GPLv3 licensed and cannot be used
commercially.  All contents are Copyright &copy; 2023 CAT Camp.
