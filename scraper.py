#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import newspaper
import sqlite3
import requests

# Imports necessary for training
from simpletransformers.classification import ClassificationModel
import torch
cuda_available = torch.cuda.is_available()

print('oh duh')

# get the location of articles.db

db = sys.argv[1]
print(db)

# Let's see if there's a model available. If there is, we'll evaluate stories as they come in
try:
	model_found = True

	model = ClassificationModel(
    "roberta", "outputs/checkpoint-4-epoch-1",
    use_cuda=cuda_available
	)
	print('model loaded')
except Exception as e:
	print(e)
	model_found = False


# Create a db connection
conn = sqlite3.connect(db)
cursor = conn.cursor()



# iterate through the sources and grab new articles
sources = cursor.execute('select root_url, name, id from sources')
sources = sources.fetchall()


current_articles = cursor.execute('select url from articles')
current_articles = [item[0] for item in current_articles.fetchall()]
conn.commit()

rows = []

if model_found:
	for source in sources:
		# Grab articles, with a short timeout
		# articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=False)
		articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=True)

		for article in articles.articles:
			# Filter out feeds from major sites
			if str(article.url).endswith('feed') or str(article.url).endswith('feeds'):
				continue

			# insert articles in the temp table
			elif article.url not in current_articles and article.title is not None and article.title.strip() is not "":
				try:
					req = requests.get(article.url)
					html = req.text
					predictions, raw_outputs = model.predict([newspaper.fulltext(html)])
					inferred_interest = float(raw_outputs[0][1])
					row = [article.url, article.title, source[2], inferred_interest]
					cursor.execute('insert into articles(url, title, source_id, inferred_interest) values (?,?,?,?)', row)
					conn.commit()
				except Exception as e:
					print(e)
					print('Issue with ', article.url)

else:
	for source in sources:
		print(source[1])
		# Grab articles, with a short timeout
		# articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=False)
		articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=True)

		for article in articles.articles:
			# print(article.url)
		# Filter out feeds from major sites
			if str(article.url).endswith('feed') or str(article.url).endswith('feeds'):
				continue

			# insert articles in the temp table
			elif article.url not in current_articles and article.title is not None and article.title.strip() is not "":
				row = [article.url, article.title, source[2]]
				cursor.execute('insert into articles(url, title, source_id) values (?,?,?)', row)
				conn.commit()
		

# delete the lock file
os.remove('lock')
print('lock removed')

# Close the db connection
conn.close()



