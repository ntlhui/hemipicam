#!/bin/bash

# Manual script for stopping the hemipicam system via ssh.  Do not use if the
# init service is enabled.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
kill -s SIGINT `cat /var/run/hemipicam.pid`
echo "Service stopped!"
rm -f /var/lock/hemipicam
exit