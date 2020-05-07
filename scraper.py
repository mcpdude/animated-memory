import asyncio
import sys
import os
import newspaper
import sqlite3

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
# Drop the temp table if it exists
cursor.execute('drop table if exists temp_articles')
conn.commit()

# create a new temp table, with urls and titles 
cursor.execute('create table temp_articles (url text, title text, source_id int)')
conn.commit()

# iterate through the sources and grab new articles
sources = cursor.execute('select root_url, name, id from sources')
sources = sources.fetchall()


current_articles = cursor.execute('select url from articles')
current_articles = [item[0] for item in current_articles.fetchall()]
conn.commit()


for source in sources:
	print(source[1])
	# Grab articles, with a short timeout
	articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=False)
	# articles = newspaper.build(source[0], fetch_images=0, request_timeout=1, memoize_articles=True)

	for article in articles.articles:
		print(article.url)
	# Filter out feeds from major sites
		if str(article.url).endswith('feed') or str(article.url).endswith('feeds'):
			continue

		# insert articles in the temp table
		elif article.url not in current_articles and article.title is not None and article.title.strip() is not "":
			cursor.execute('insert into temp_articles(url, title, source_id) values (?, ?, ?)', [article.url, article.title, source[2]])
# then, insert articles from the temp table to the actual table
	articles_to_transfer = cursor.execute('select url, title, source_id from temp_articles')
	for article in articles_to_transfer.fetchall():
		cursor.execute('insert into articles(url, title, source_id) values (?,?,?)', article)
		conn.commit()
# drop the temp table
cursor.execute('drop table if exists temp_articles')
conn.commit()

# delete the lock file
os.remove('lock')
print('lock removed')

# Close the db connection
conn.close()





# 			
# 				try:
# 					request.db.execute()
# 					request.db.commit()
# 					article_id = str(request.db.execute('select id from articles where url = ?', [article.url]).fetchall()[0][0])
# 					os.mkdir('article_storage/' + article_id)
# 					article.download()
# 					article.parse()
# 					with open('article_storage/'+article_id + '/article.html', 'w+') as html:
# 						html.write(article.article_html)
# 					with open('article_storage/'+article_id + '/article.txt', 'w+') as text:
# 						text.write(article.text)

# 				except Exception as e:
# 					print(e)
# 					request.db.execute('update articles set title = ? where id = ?', ['ERROR' + article.title, article_id])
# 					request.db.commit()

conn.close()


