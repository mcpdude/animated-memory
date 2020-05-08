import asyncio
import sys
import os
import newspaper
import sqlite3

from simpletransformers.classification import ClassificationModel
import torch
cuda_available = torch.cuda.is_available()


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
conn = sqlite3.connect('articles.db')

cursor = conn.cursor()

# create a lock file to indicate that the process has started
# print(os.listdir())
if 'lock' not in os.listdir():
	with open('lock', 'w') as file:
		print('lock created!') 

else:
	print('lockfile present, exiting')
	sys.exit()


# iterate through the sources and grab new articles
sources = cursor.execute('select root_url, name, id from sources')
sources = sources.fetchall()


current_articles = cursor.execute('select url from articles')
current_articles = [item[0] for item in current_articles.fetchall()]
conn.commit()

rows = []

for source in sources:
	print(source[1])
	# Grab articles, with a short timeout
	articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=False)
	# articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=True)

	for article in articles.articles:
		# print(article.url)
	# Filter out feeds from major sites
		if str(article.url).endswith('feed') or str(article.url).endswith('feeds'):
			continue

		# insert articles in the temp table
		elif article.url not in current_articles and article.title is not None and article.title.strip() is not "":
			rows.append([article.url, article.title, source[2]])

# then, insert articles from the temp table to the actual table

for article in rows:
	cursor.execute('insert into articles(url, title, source_id) values (?,?,?)', article)
	conn.commit()
# drop the temp table

conn.commit()

# delete the lock file
os.remove('lock')
print('lock removed')

# Close the db connection
conn.close()



