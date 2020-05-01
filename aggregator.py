import os
import logging
import sqlite3
import newspaper
import sys
import tempfile

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.events import ApplicationCreated
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

try:
	if sys.argv[1] == 'debug':
		debug = True
except:
	debug = False

from wsgiref.simple_server import make_server

logging.basicConfig()
log = logging.getLogger(__file__)
here = os.path.dirname(os.path.abspath(__file__))

@view_config(route_name='list', renderer='list.mako')
def list_view(request):
	current_articles = request.db.execute('select url from articles')
	current_articles = [item[0] for item in current_articles.fetchall()]

	rs = request.db.execute('select id, title, url, interesting from articles where read = 0 and visible = 1 limit 50')
	articles = [dict(id=row[0], title=row[1], url=row[2], interesting=row[3]) for row in rs.fetchall()]
	return {'articles': articles}

@view_config(route_name='refresh')
def refresh_articles(request):
	sources = request.db.execute('select root_url, name, id from sources')
	current_articles = request.db.execute('select url from articles')
	current_articles = [item[0] for item in current_articles.fetchall()]

	for source in sources.fetchall():
		if debug:
			print('debug mode')
			articles = newspaper.build(source[0], memoize_articles=False)
		else:
			articles = newspaper.build(source[0])
		if articles.size() > 0:
			request.session.flash("Found new stories from " + source[1])
		for article in articles.articles:
			# print(article.title)	
			if article.url not in current_articles and article.title is not None and article.title.strip() is not "":
				print(article.title)
				print(article.url, article.title, source[2])
				request.db.execute('insert into articles(url, title, source_id) values (?, ?, ?)', [article.url, article.title, source[2]])
				request.db.commit()

	return HTTPFound(location=request.route_url('list'))


@view_config(route_name='read', renderer='read.mako')
def read_articles(request):
	rs = request.db.execute('select id, title, url, interesting from articles where read = 1')
	articles = [dict(id=row[0], title=row[1], url=row[2], interesting=row[3]) for row in rs.fetchall()]
	return {'articles': articles}

@view_config(route_name='new', renderer='new.mako')
def new_view(request):
	rs = request.db.execute('select root_url, name, id from sources')
	sources = [dict(url=row[0], name=row[1], id=row[2]) for row in rs.fetchall()]
	if request.method == 'POST':
		print(request.POST)
		if request.POST.get('url'):
			request.db.execute(
				'insert into sources (root_url, name) values (?, ?)',
				[request.POST['url'], request.POST['name']])
			request.db.commit()
			request.session.flash("New source added!")
			return HTTPFound(location=request.route_url('list'))
		else:
			request.session.flash('Please enter a url for the news source')
	return {'sources': sources}

@view_config(route_name='interesting')
def interesting(request):
	article_id = int(request.matchdict['id'])
	request.db.execute('update articles set read = ?, interesting = 1 where id = ?',
		(1, article_id))
	request.db.commit()
	request.session.flash('Read the article! Glad you enjoyed it!')
	return HTTPFound(location=request.route_url('list'))

@view_config(route_name='not_interesting')
def not_interesting(request):
	article_id = int(request.matchdict['id'])
	request.db.execute('update articles set read = ?, interesting = 0 where id = ?',
		(1, article_id))
	request.db.commit()
	request.session.flash("Read the article! Sorry, I'll try to find something more interesting next time.")
	return HTTPFound(location=request.route_url('list'))

@view_config(route_name='delete_source')
def delete_source(request):
	print(request)
	source_id = int(request.matchdict['id'])
	request.db.execute('delete from sources where id = ?',
		(str(source_id)))
	request.db.commit()
	request.db.execute('update articles set visible = 0 where source_id = ?',
		(str(source_id)))
	request.db.commit()
	request.session.flash("Deleted the source.")
	return HTTPFound(location=request.route_url('new'))

@subscriber(NewRequest)
def new_request_subscriber(event):
	request = event.request
	settings = request.registry.settings
	request.db = sqlite3.connect(settings['db'])
	request.add_finished_callback(close_db_connection)

def close_db_connection(request):
	request.db.close()

@subscriber(ApplicationCreated)
def application_created_subscriber(event):
	log.warning("Initializing database...")
	with open(os.path.join(here, 'schema.sql')) as f:
		statement = f.read()
		settings = event.app.registry.settings
		db = sqlite3.connect(settings['db'])
		db.executescript(statement)
		db.commit()

def main():
	settings = {}
	settings['reload_all'] = True
	settings['debug_all'] = True
	settings['db'] = os.path.join(here, 'articles.db')
	settings['mako.directories'] = os.path.join(here, 'templates')
	session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekret')


	config = Configurator(settings=settings, session_factory=session_factory)
	config.include('pyramid_mako')
	config.add_route('list', '/')
	config.add_route('refresh', '/refresh')
	config.add_route('read', '/read')
	config.add_route('delete_source', '/delete_source/{id}')
	config.add_route('new', '/new')
	config.add_route('interesting', '/interesting/{id}')
	config.add_route('not_interesting', '/not_interesting/{id}')
	config.add_static_view('static', os.path.join(here, 'static'))
	config.scan()

	app = config.make_wsgi_app()
	server = make_server('0.0.0.0', 8080, app)
	server.serve_forever()

if __name__ == '__main__':
	main()


