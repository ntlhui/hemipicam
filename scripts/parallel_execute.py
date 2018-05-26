#!/usr/bin/env python

from binascii import hexlify
import paramiko
import threading
import select
import socket
import sys
import os
from multiprocessing.pool import ThreadPool
import time

# cameraNumbers = [18]
cameraNumbers = [2]
cameraNumbers = range(1, 19)
hostnames = ["e4e-brix.dynamic.ucsd.edu"]
# hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]
print(hostnames)
paramiko.util.log_to_file("check_startup.log")

username = "e4e_admin"

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

file = "script.sh"

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

def execute(channel):
	stream = open(file)
	channel.sendall("\n")

	while channel.recv_ready():
		channel.recv(1024)

	channel.exec_command('cd test')
	while not channel.exit_status_ready():
		time.sleep(0.1)
	channel.exec_command('touch test1')

	# for line in stream:
	# 	print("> " + line)
	# 	channel.sendall(line)
	# 	print("Sent, waiting for data")
	# 	while !channel.exit_status_ready():
	# 		time.sleep(0.1)
	# 	print("exit")
	# 	while channel.recv_ready():
	# 		data = channel.recv(1)
	# 		sys.stdout.write(data)
	# 		sys.stdout.flush()
	# 	print("No more data?")
	# 	sys.stdout.write('\n')
	# 	sys.stdout.flush()

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
	channel.set_combine_stderr(True)
	channel.get_pty()
	channel.invoke_shell()
	status[hostname] = True

	
for hostname in hostnames:
	connectHost(hostname)



# pool = ThreadPool(4)
# pool.map(execute, channels.values())
for hostname, channel in channels.items():
	execute(channel)

for hostname, channel in channels.items():
	t = channel.get_transport()
	channel.close()
	t.close()

for hostname in hostnames:
	print("%s: %s" % (hostname, str(status[hostname])))