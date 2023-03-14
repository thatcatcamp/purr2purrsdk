# purr2purrsdk
Builder SDK for Purr2Purr

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


