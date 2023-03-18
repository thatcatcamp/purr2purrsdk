"""
copyright (c) 2023 CAT Camp

copyright is just included for takedowns if this is used for commercial projects
DONT PANIC :)

this file is provided under the gplv3 license -see the full legal text in the project

LIDAR sensors aren't 'eyes' - they really only detect something is X mm away.  we sample and
fire the LIDAR handler when something big moves in front of us.  there is a limit on the sample
change of 10 seconds by default

to read more - there is a document on seeedstudio's S3:

https://s3-us-west-2.amazonaws.com/files.seeedstudio.com/products/101990656/res/SJ-PM-TF-Luna+A01+Product+Manual.pdf


"""
import time

import requests
import serial
from loguru import logger

HOOMAN_SAMPLE_SECONDS = 10


def hooman_detected():
    """
    not surprisingly - fires when a hooman is seem (i.e. - something changed in the LIDAR
    range
    :return:
    """
    # replace this with some custom stuff if you don't want to use the IPC proxy
    hooman_packet = {"eventtype": "hooman", "hooman_id": "", "hooman_name": "", "hooman_likes": ""}
    logger.info('hooman seen!')
    results = requests.post("http://localhost:8080/push", json=hooman_packet)
    print(results.status_code)


# DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING  :)
# this might need to change for you - by default though mostly
# you will have only one USB serial device
# check dmesg and insert the USB dongle - you should see 'serial device on /dev/tty*'
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=0)


def get_version():
    """
    comforting debug output to prove we're talking to the right device
    :return: none
    """
    info_packet = [0x5a, 0x04, 0x14, 0x00]
    ser.write(info_packet)
    time.sleep(0.1)  # wait to read
    bytes_to_read = 30  # prescribed in the product manual
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                version = bytes_data[3:-1].decode('utf-8')
                print('Version -' + version)  # print version details
                return
            else:
                ser.write(info_packet)  # if fails, re-write packet
                time.sleep(0.1)  # wait


def sample_lidar():
    """
    waits for a sample from the sensor
    :return:
    three values:
    - distance in meters
    - strength isn't super useful, but it can be used to filter small close things out
    - temperature is the sensor temp is C
    """
    while True:
        counter = ser.in_waiting  # count the number of bytes of the serial port
        if counter > 8:
            bytes_serial = ser.read(9)  # read 9 bytes
            ser.reset_input_buffer()  # reset buffer
            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:  # check first two bytes
                distance = bytes_serial[2] + bytes_serial[3] * 256  # distance in next two bytes
                strength = bytes_serial[4] + bytes_serial[5] * 256  # signal strength in next two bytes
                temperature = bytes_serial[6] + bytes_serial[7] * 256  # temp in next two bytes
                temperature = (temperature / 8.0) - 256.0  # temp scaling and offset
                return distance / 100.0, strength, temperature


logger.info("Purr2PurrSDK Copyright (c) 2023 CAT Camp")
logger.info("Source is GPLv3 Licensed - YOU MAY NOT USE FOR COMMERCE")
logger.info("Booting - looking for scanners....")

if ser.isOpen() == False:
    ser.open()  # open serial port if not open
try:
    get_version()
    last_meaningful_change = 0
    last_distance = 0
    last_strength = 0
    while True:
        distance, strength, temperature = sample_lidar()  # read values
        if distance == last_distance:
            time.sleep(1)
            continue

        if time.time() - last_meaningful_change < HOOMAN_SAMPLE_SECONDS:
            time.sleep(time.time() - last_meaningful_change)
            continue
        last_meaningful_change = time.time()  # unix time
        if temperature > 60.0:
            print("DANGER - sensor is overheating...")
        # remove minor changes
        flat_last = int(last_distance * 10)
        flat_distance = int(distance * 10)
        if flat_distance != flat_last:
            logger.info(f"change {flat_last} != {flat_distance}")
            hooman_detected()
        last_strength = strength
        last_distance = distance
        logger.info('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'. \
                    format(distance, strength, temperature))

except Exception as e:
    logger.warning("Something odd happened")
    logger.warning(e)
finally:
    ser.close()  # close serial port
