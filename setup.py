import subprocess
import sys
import os
import sqlite3

print('What do you use to install python3 packages, pip or pip3?')
command_to_use = input('type pip or pip3 here.')

packages = ['newspaper3k', 'pyramid', 'pyramid.mako', 'simpletransformers', 'torch', 'torchvision']

for package in packages:
	
	subprocess.check_call([command_to_use, 'install', package])

try:
	os.mkdir('article_storage')

except:
	print('article_storage directory already exists')

here = os.path.dirname(os.path.abspath(__file__))
settings = {}
settings['db'] = os.path.join(here, 'articles.db')

wipe = input('Do you want to wipe your setup? Y/n \n')

if wipe == 'Y':
	try:
		os.remove('articles.db')
	except:
		print('articles.db does not exist')
	with open(os.path.join(here, 'schema_new.sql')) as f:
		statement = f.read()
		
		db = sqlite3.connect(settings['db'])
		db.executescript(statement)
		db.commit()
		db.close()

elif wipe == 'n':
	with open(os.path.join(here, 'schema.sql')) as f:
		statement = f.read()
		
		db = sqlite3.connect(settings['db'])
		db.executescript(statement)
		db.commit()
		db.close()

else:
	print("Sorry, didn't understand that. Make sure to use Y or n.")

