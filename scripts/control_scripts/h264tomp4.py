#!/usr/bin/env python

import subprocess
import argparse
import os

parser = argparse.ArgumentParser(description = 'H264 to MP4 folder converter')
parser.add_argument('folder', type = str, help = 'Directory containing H264 videos to convert')

args = parser.parse_args()

cameras = ["hemipicam%02d" % (i) for i in range(1, 19)]
input_ext = ".h264"
output_ext = ".mp4"

for camera in cameras:
	infile = os.path.join(args.folder, '%s%s' % (camera, input_ext))
	outfile = os.path.join(args.folder, '%s%s' % (camera, output_ext))
	subprocess.call("ffmpeg -i %s -y -c copy %s" % (infile, outfile), shell = True)