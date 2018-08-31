#!/usr/bin/env python

from binascii import hexlify
import paramiko
import threading
import select
import socket
import sys
import os
from multiprocessing.pool import ThreadPool
import argparse

parser = argparse.ArgumentParser(description = 'HemiPiCam Reboot Tool')
parser.parse_args()


# cameraNumbers = [18]
cameraNumbers = range(1, 19)
hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]
print(hostnames)
paramiko.util.log_to_file("reboot.log")

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

def enable_camera(channel):
	print("Creating files")
	while channel.recv_ready():
		channel.recv(1024)
	channel.invoke_shell()

	print("Executing commands")
	print("Executing sudo su")
	channel.sendall('sudo su\n')
	print("Executing cd /usr/bin")
	channel.sendall('cd /usr/bin\n')
	print("Executing . raspi-config nonint")
	channel.sendall('. raspi-config nonint\n')
	print("Executing do_camera 1")
	channel.sendall('do_camera 1\n')

	print("Reading output")
	if channel.recv_ready:
		data = channel.recv(1024)
		print(data)

def shutdown(channel):
	while channel.recv_ready():
		channel.recv(1024)
	channel.invoke_shell()

	channel.sendall('sudo shutdown -r now\n')

def connectHost(hostname):
	global channels
	global status
	if hostname in status and status[hostname] is True:
		print("Attempting to connect to %s" % hostname)
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

def resolveHost(hostname):
	print("Resolving %s" % hostname)
	global status
	try:
		socket.gethostbyname(hostname)
		status[hostname] = True
		print("%s is up" % hostname)
	except socket.error:
		status[hostname] = False
		print("%s is not up!" % hostname)
	
for hostname in hostnames:
	resolveHost(hostname)
	connectHost(hostname)



pool = ThreadPool(4)
pool.map(shutdown, channels.values())
# for hostname, channel in channels.items():
# 	shutdown(channel)

for hostname, channel in channels.items():
	t = channel.get_transport()
	channel.close()
	t.close()

for hostname in hostnames:
	print("%s: %s" % (hostname, str(status[hostname])))

alive = 0
for hostname in hostnames:
	if status[hostname]:
		alive += 1
print("%d of %d told to reboot" % (alive, len(hostnames)))
