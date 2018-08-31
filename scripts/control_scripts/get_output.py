#!/usr/bin/env python
import os
import paramiko
import subprocess
from multiprocessing.pool import ThreadPool
import argparse

parser = argparse.ArgumentParser(description = "Hemipicam Output Downloader")
parser.add_argument("extension")
parser.add_argument("-o", "--output",  default = "../")
args = parser.parse_args()


paramiko.util.log_to_file('get_output.log')
paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

cameraNumbers = range(1, 19)
hostnames = ["hemipicam%02d" % (x) for x in cameraNumbers]
port = 22
username = 'pi'

extension = args.extension

remote_images_path = "/home/pi"
local_path = args.output

def getFile(username, hostname, port, remote_images_path, local_path):	
	files = ["%s.%s" % (hostname, extension)]
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname = "%s.local" % (hostname), port = port, username = username)
	sftp = ssh.open_sftp()
	for file in files:
		file_remote = os.path.join(remote_images_path, file)
		file_local = os.path.join(local_path, file)
		print("%s@%s.local:%s >>> %s" % (username, hostname, file_remote, file_local))
		sftp.get(file_remote, file_local)
	sftp.close()
	ssh.close()

def _getFile(hostname):
	global username
	global port
	global remote_images_path
	global local_path
	getFile(username, hostname, port, remote_images_path, local_path)

# pool = ThreadPool(8)
# pool.map(_getFile, hostnames)

def scpFile(hostname):
	global remote_images_path
	global local_path
	global username
	file = "%s.%s" % (hostname, extension)
	file_remote = os.path.join(remote_images_path, file)
	file_local = os.path.join(local_path, file)
	command = "scp %s@%s.local:%s %s" % (username, hostname, file_remote, file_local)
	print(command)
	subprocess.call(command, shell = True)
	

for hostname in hostnames:
	scpFile(hostname)
# pool = ThreadPool(8)
# pool.map(scpFile, hostnames)