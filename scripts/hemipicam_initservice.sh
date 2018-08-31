#!/bin/bash
### BEGIN INIT INFO
# Provides: hemipicam_start
# Required-Start: $remote_fs $time $named $local_fs
# Required-Stop:
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Start HemiPiCam on startup
### END INIT INFO
#
# To install, copy to /etc/init.d and run sudo update-rc.d hemipicam_initservice.sh defaults

timestamp() {
	date
}

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

case "$1" in
	stop)
		kill -s SIGINT `cat /var/run/hemipicam.pid`
		echo "Service stopped!"
		rm -f /var/lock/hemipicam
		exit
		;;
	start)
		# start
		if [ ! -f /var/lock/hemipicam ]; then
			/home/pi/recordData.py &
			echo $! > /var/run/hemipicam.pid
			echo "Service started!"
			touch /var/lock/hemipicam
		fi
		exit
		;;
	restart|reload|condrestart)
		kill -s SIGINT `cat /var/run/hemipicam.pid`
		sleep 5
		echo "Service stopped!"
		rm -f /var/lock/hemipicam
		echo "Service started!"
		/home/pi/recordData.py &
		echo $! > /var/run/hemipicam.pid
		echo "Service started!"
		touch /var/lock/hemipicam
		exit
		;;
esac

