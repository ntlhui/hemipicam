#!/usr/bin/env python

from binascii import hexlify
import paramiko
import threading
import select
import socket
import sys
import os

# hostnames = ["e4e-brix.dynamic.ucsd.edu"]
cameraNumbers = range(1, 19)
hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]

# username = "e4e_admin"
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

command = "sudo su"

keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

for hostname in hostnames:
	print("Attempting to connect to %s" % hostname)
	try:
		sock = socket.create_connection((hostname, port), 1)
	except Exception as e:
		print("Unable to connect to %s" % (hostname))
		continue

	t = paramiko.Transport(sock)
	t.get_security_options().key_types = key_types

	try:
		t.connect(hostkey = keys[hostname]['ecdsa-sha2-nistp256'], pkey = agent_keys[0], username = username)
	except paramiko.SSHException as e:
		print("Unable to connect to %s" % (hostname))
		continue

	channel = t.open_session()
	channels[hostname] = channel

for hostname, channel in channels.items():
	channel.exec_command(command)
	rl, wl, xl = select.select([channel],[],[],5.0)
	if len(rl) > 0:
		# Must be stdout
		print channel.recv(1024)
	if channel.recv_stderr_ready():
		print channel.recv_stderr(1024)

for hostname, channel in channels.items():
	t = channel.get_transport()
	channel.close()
	t.close()

# if __name__ == '__main__':
# 	main()