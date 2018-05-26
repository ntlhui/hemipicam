#!/usr/bin/env python

from binascii import hexlify
import paramiko
import threading
import select
import socket
import sys
import os
from multiprocessing.pool import ThreadPool

# cameraNumbers = [18]
cameraNumbers = range(1, 19)
hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]
print(hostnames)
paramiko.util.log_to_file("check_startup.log")

username = "pi"

port = 22
key_types = ('ecdsa-sha2-nistp256',
	'ssh-ed25519', 
	'ecdsa-sha2-nistp384',
	'ecdsa-sha2-nistp521',
	'ssh-rsa',
	'ssh-dss')

agent = paramiko.Agent()
agent_keys = agent.get_keys()
channels = {}
status = {}

keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

def connectHost(hostname):
	print("Attempting to connect to %s" % hostname)
	global channels
	global status
	try:
		sock = socket.create_connection((hostname, port), 1)
	except Exception as e:
		print("Unable to connect to %s" % (hostname))
		status[hostname] = False
		return

	t = paramiko.Transport(sock)
	t.get_security_options().key_types = key_types
	print("Authenticating with %s" % hostname)
	try:
		t.connect(hostkey = keys[hostname]['ecdsa-sha2-nistp256'], pkey = agent_keys[0], username = username)
	except paramiko.SSHException as e:
		print("Unable to authenticate with %s" % (hostname))
		status[hostname] = False
		t.close();
		return
	except KeyError:
		print("Key not found!")
		status[hostname] = False
		t.close();
		return
	print("Connected to %s" % hostname)

	channel = t.open_session()
	channels[hostname] = channel
	status[hostname] = True

	
# pool = ThreadPool(1)
# pool.map(connectHost, hostnames)
for hostname in hostnames:
	connectHost(hostname)


for hostname in hostnames:
	print("%s: %s" % (hostname, str(status[hostname])))

for hostname, channel in channels.items():
	t = channel.get_transport()
	channel.close()
	t.close()

# if __name__ == '__main__':
# 	main()