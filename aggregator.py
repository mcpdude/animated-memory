import os
import logging
import sqlite3
import newspaper
import sys
import tempfile
import subprocess
import webbrowser


from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.events import ApplicationCreated
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from wsgiref.simple_server import make_server

# Set a debug flag. Hacky, but quick and sufficient
try:
	if sys.argv[1] == 'debug':
		debug = True
except:
	debug = False


logging.basicConfig()
log = logging.getLogger(__file__)
here = os.path.dirname(os.path.abspath(__file__))

# Main view, shows the list of articles
@view_config(route_name='list', renderer='list.mako')
def list_view(request):
	rs = request.db.execute('select articles_to_show from settings')
	amount_of_articles = rs.fetchone()[0]
	rs = request.db.execute('select id, title, url, interesting from articles where read = 0 and visible = 1 order by inferred_interest desc limit ?', [amount_of_articles])
	articles = [dict(id=row[0], title=row[1], url=row[2], interesting=row[3]) for row in rs.fetchall()]
	return {'articles': articles}

# Starts a child process to prevent blocking when refreshing the articles
@view_config(route_name='refresh')
def refresh_articles(request):
	# This process will exit early if a lock file exists in the main project directory. remove the lock file if it's not working
	if 'lock' not in os.listdir():
		with open('lock', 'w') as file:
			print('lock created!') 

	else:
		request.session.flash('lockfile present, exiting')

	subprocess.Popen(['python3', 'scraper.py'])

	return HTTPFound(location=request.route_url('list'))

# Show articles that have been read. 
@view_config(route_name='read', renderer='read.mako')
def read_articles(request):
	rs = request.db.execute('select id, title, url, interesting from articles where read = 1 group by interesting order by inferred_interest desc ')
	articles = [dict(id=row[0], title=row[1], url=row[2], interesting=row[3]) for row in rs.fetchall()]
	return {'articles': articles}

# A place to hold settings. Not very well setup, but the best I can do. Can't submit multiple fields at once, for example
@view_config(route_name='settings', renderer='settings.mako')
def settings(request):
	rs = request.db.execute('select * from settings')
	# print(rs.fetchall())
	settings = [dict(name=row[1], articles_to_show=row[2]) for row in rs.fetchall()]
	print(settings)
	return {'settings': settings}

# Used to update the settings
@view_config(route_name='change_settings')
def change_settings(request):

	if request.GET.get('field') == "Articles to Show":
		if request.GET.get('articles_to_show') == "":
			print("no amount supplied, defaulting to 1.")
			request.session.flash("Please provide a value!")
			value = '1'

		elif int(request.GET.get('articles_to_show')) < 1:
			request.session.flash("You can't show negative articles")
			value = '1'

		else:
			value = request.GET.get('articles_to_show')
		request.db.execute('update settings set articles_to_show = ?', [value])

	elif request.GET.get('field') == "Change Name":
		if request.GET.get('name') == "":
			request.session.flash("Name set to Anon")
			value = 'Anon'

		else:
			value = request.GET.get('name')

		request.db.execute('update settings set name = ?', [value])

	request.db.commit()
	request.session.flash("Settings updated!")

	return HTTPFound(location=request.route_url('settings'))

# Where new sources are added. Currently sends people back to the list after submitting, 
# which might be annoying
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

# Interesting and not interesting are used to update the db based on user input
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

# initiate a training process
@view_config(route_name='train')
def train(request):
	if 'lock' not in os.listdir():
		with open('lock', 'w') as file:
			print('lock created!') 

	else:
		request.session.flash('lockfile present, exiting')

	subprocess.Popen(['python3', 'train.py'])

	return HTTPFound(location=request.route_url('list'))


# Allows the user to delete a source, and hides the stories from that source
@view_config(route_name='delete_source')
def delete_source(request):
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
	config.add_route('train', '/train')
	config.add_route('settings', '/settings')
	config.add_route('change_settings', '/change_settings')
	config.add_route('read', '/read')
	config.add_route('delete_source', '/delete_source/{id}')
	config.add_route('new', '/new')
	config.add_route('interesting', '/interesting/{id}')
	config.add_route('not_interesting', '/not_interesting/{id}')
	config.add_static_view('static', os.path.join(here, 'static'))
	config.scan()



	app = config.make_wsgi_app()
	server = make_server('0.0.0.0', 8080, app)
	webbrowser.open('localhost:8080')

	server.serve_forever()


if __name__ == '__main__':
	main()



