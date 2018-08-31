#!/usr/bin/env python

# This script checks that the network is up, and that all PIs in the cluster are
# connected to the network.

import socket
from multiprocessing.pool import ThreadPool

cameraNumbers = range(1, 19)

hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]


port = 22
status = {}

pool = ThreadPool()
def checkHost(host):
	global status
	s = socket.socket()
	try:
		s.connect((host, port))
		s.close()
		status[host] = True
	except:
		status[host] = False

pool.map(checkHost, hostnames)

for hostname in hostnames:
	print("%s: %s" % (hostname, str(status[hostname])))