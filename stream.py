# SPDX-License-Identifier: LGPL-3.0
"""
    this is the watcher thread for the camera/model
    run this to scan the camera - look for items of interest,
    and update the screen

    camera == 0 is the first web cam - usually what you want

    copyright (c) that cat camp 2023 - all rights reserved
    LGPL
"""
import datetime
import os
import random
import shutil
import signal
import subprocess
import sys
import time
import uuid
from os.path import join
from string import Template
from imageai.Detection import ObjectDetection
import cv2
from loguru import logger

LAST_OUTPUT = time.time()
execution_path = os.getcwd()
RAMDISK = "/tmp/swap.jpg"
TEST_MODE = True
BORED_TIMEOUT = 360
execution_path = os.getcwd()
prediction = ObjectDetection()
prediction.setModelTypeAsYOLOv3()
model = "yolov3.pt"
print("Using model ", model)
prediction.setModelPath(model)
prediction.loadModel()


def play_sound(this_sound: str):
    """
    most libraries don't work right on this on the limited hardware - use aplay
    :param this_sound:
    :return:
    """
    print("aplay", this_sound)
    subprocess.check_output(['aplay', this_sound])


def signal_handler(sig, stack_frame):
    """
    closes camera correctly on stop so we don't have to unplug it
    :param sig:
    :param stack_frame:
    :return:
    """
    print('You pressed Ctrl+C!')
    print(sig)
    print(stack_frame)
    camera.release()


def update_view(boobs=False, butts=False, cats=True):
    """
    update the template with current state
    :param boobs:
    :param butts:
    :param cats:
    :return:
    """
    replacements = dict(boobs=boobs, butts=butts, debug=TEST_MODE, gmt=datetime.datetime.utcnow().isoformat(),
                        cats=cats)
    with open("template.html", "rt") as file_handle:
        data = file_handle.read()
        with open("/tmp/index.html", "w+t") as output_handle:
            output_handle.write(Template(data).safe_substitute(replacements))


def random_image():
    """
    test fixture, inject random images for testing
    :return:
    """
    if random.randint(0, 99) > 75:
        swap = random.choice(os.listdir("./test"))
        if swap is None:
            print("no test data?")
            return
        print("Adding random image...")
        shutil.copyfile(join("./test", swap), RAMDISK)


def random_sound(image_type: str):
    """
    play a random sound from this group
    :param image_type:
    :return:
    """
    global LAST_OUTPUT
    LAST_OUTPUT = time.time()

    swap = random.choice(os.listdir(f"./wav/{image_type}"))
    if swap is None:
        print("no test data?")
        return
    print("playing...", swap)
    play_sound("click.wav")
    temp_name = uuid.uuid4().hex
    shutil.copyfile(RAMDISK, f"keepers/{temp_name}")
    play_sound(join(f"./wav/{image_type}", swap))


logger.info("init")
signal.signal(signal.SIGINT, signal_handler)
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Cannot open camera")
    sys.exit()
update_view()

# CAP_PROP_FPS doesn't work for this - use sleep
while True:
    ret, frame = camera.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    cv2.imwrite(RAMDISK, frame)
    # add random images for testing
    if TEST_MODE:
        random_image()
    detections = prediction.detectObjectsFromImage(input_image="/tmp/swap.jpg", output_image_path="/tmp/annotated.jpg", minimum_percentage_probability=30)
    print(detections)
    if LAST_OUTPUT + BORED_TIMEOUT < time.time():
        random_sound("bored")
    time.sleep(5)

