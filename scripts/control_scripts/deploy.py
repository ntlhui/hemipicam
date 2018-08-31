#!/usr/bin/env python
import argparse
import subprocess
from multiprocessing.pool import ThreadPool

cameraNumbers = range(1, 19)
hostnames = ["hemipicam%02d.local" % (x) for x in cameraNumbers]
username = "pi"

parser = argparse.ArgumentParser(description = "Hemipicam cluster deployment tool")
parser.add_argument("-u", "--username",  default = "pi")
parser.add_argument("input_path")
parser.add_argument("deploy_path", default=".", nargs = '?')
args = parser.parse_args()

username = args.username
print(username)
input_path = args.input_path
print(input_path)
remote_path = args.deploy_path
print(remote_path)
for hostname in hostnames:
	command = "scp -p %s %s@%s:%s" % (input_path, username, hostname, remote_path)
	print(command)
	subprocess.call(command, shell = True)
	print("complete")