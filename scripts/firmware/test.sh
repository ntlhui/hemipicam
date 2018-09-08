#!/bin/bash

# Manual start script for starting the hemipicam system via ssh.  Do not use if 
# the init service is enabled.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
if [ ! -f /var/lock/hemipicam ]; then
	nohup /home/pi/peg.py &
	nohup /home/pi/thrash.py &
	echo $! > /var/run/hemipicam.pid
	echo "Service started!"
	touch /var/lock/hemipicam
fi
exit