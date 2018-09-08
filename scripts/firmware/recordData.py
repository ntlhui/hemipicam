#!/usr/bin/env python

import socket
import time
import picamera
import signal
import threading
import os
import pwd
import grp
import argparse

# This script runs on the Pi to record video.

parser = argparse.ArgumentParser(description = 'HemiPiCam Record Script')
parser.parse_args()


record_cv = threading.Condition()

run = True
hostname = socket.gethostname()
if hostname == 'hemipicam01':
	from gpiozero import LED
output_file = "/home/pi/%s.h264" % (hostname)

camera = picamera.PiCamera()


def handler(signum, frame):
	global record_cv
	global run
	global camera
	print("Got signal!")
	camera.stop_recording()
	run = False
	uid = pwd.getpwnam("pi").pw_uid
	gid = grp.getgrnam("pi").gr_gid
	os.chown(output_file, uid, gid)
signal.signal(signal.SIGINT, handler)


camera.resolution = (1640, 1232)
camera.framerate = 15
camera.awb_mode = 'sunlight'
# camera.awb_gains = (0, 0)
# camera.brightness = 50
# camera.contrast = 0
# camera.exposure_mode = 'off'

if hostname == 'hemipicam01':

	led = LED(24)
	led.on()

print("Recording")

camera.start_recording(output_file, format='h264')
camera.wait_recording(1)
if hostname == 'hemipicam01':

	led.off()
while run:
	camera.wait_recording(1)
