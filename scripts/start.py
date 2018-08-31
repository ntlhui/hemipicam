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
import argparse

parser = argparse.ArgumentParser(description = 'HemiPiCam Start Script.  Use me '
	'to start the entire cluster via ssh')
parser.parse_args()

username = 'pi'
command = 'sudo ./hemipicam_start.sh'

cameraNumbers = range(1, 19)
hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]
paramiko.util.log_to_file("parallel_execute.log")

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

def execute(channel):
	global command
	# print("Creating files")
	# while channel.recv_ready():
	# 	channel.recv(1024)
	# channel.invoke_shell()

	# print("Executing commands")
	# print("Executing sudo su")
	# channel.sendall('sudo su\n')
	# print("Executing command")
	# channel.sendall('%s\n' % (command))
	# print("Reading output")
	print("Executing command")
	channel.exec_command(command)
	if channel.recv_ready:
		data = channel.recv(1024)
		print(data)
	print "exit status: %s" % channel.recv_exit_status()


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


	
for hostname in hostnames:
	connectHost(hostname)

pool = ThreadPool(4)
pool.map(execute, channels.values())

for hostname, channel in channels.items():
	t = channel.get_transport()
	channel.close()
	t.close()

for hostname in hostnames:
	print("%s: %s" % (hostname, str(status[hostname])))