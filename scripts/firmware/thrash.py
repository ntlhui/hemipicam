#!/usr/bin/env python
#

import random
import subprocess

while True:
	subprocess.call(["sudo", "dd", "if=/dev/zero", "of=test.bin", "count=65536"])
