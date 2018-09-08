#!/usr/bin/env python

# This script checks that the network is up, and that all PIs in the cluster are
# connected to the network.

import socket
import sys
from multiprocessing.pool import ThreadPool

cameraNumbers = range(1, 19)

hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]
# hostnames = ["192.168.1.%02d" % (x) for x in cameraNumbers]


port = 22
status = {}

pool = ThreadPool(1)
def checkHost(host):
	global status
	print(host)
	s = socket.socket()
	try:
		s.connect((host, port))
		s.close()
		status[host] = True
	except:
		print("Unexpected error:", sys.exc_info()[0])
		status[host] = False

pool.map(checkHost, hostnames)

for hostname in hostnames:
	print("%s: %s" % (hostname, str(status[hostname])))

alive = 0
for hostname in hostnames:
	if status[hostname]:
		alive += 1
print("%d of %d up" % (alive, len(hostnames)))