import subprocess
import sys

print('What do you use to install python3 packages, pip or pip3?')
command_to_use = input('type pip or pip3 here.')

packages = ['newspaper3k', 'pyramid', 'pyramid.mako']

for package in packages:
	
	subprocess.check_call([command_to_use, 'install', package])