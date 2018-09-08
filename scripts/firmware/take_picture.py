#!/usr/bin/env python
import socket
import time
import picamera

hostname = socket.gethostname()

camera = picamera.PiCamera()
camera.resolution = (1640, 1232)
camera.framerate = 30
camera.awb_mode = 'sunlight'
camera.capture("%s.png" % (hostname))