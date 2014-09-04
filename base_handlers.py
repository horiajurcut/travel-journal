import os
import webapp2
import MySQLdb
import time
import urlparse

from webapp2_extras import jinja2, sessions
from google.appengine.ext.webapp.util import run_wsgi_app
from settings import mysql

class BaseHandler(webapp2.RequestHandler):
	conn = None
	session_store = None


	@property
	def connection(self):
		if self.conn is None:
			if (os.getenv('SERVER_SOFTWARE') and os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
				self.conn = MySQLdb.connect(
					unix_socket = mysql['unix_socket'],
					user        = mysql['user'],
					db          = mysql['db'],
					charset     = mysql['charset']
				)
			else:	
				self.conn = MySQLdb.connect(
					host    = mysql['host'],
					port    = mysql['port'],
					user    = mysql['user'],
					passwd  = mysql['passwd'],
					db      = mysql['db'],
					charset = mysql['charset']
				)
			self.conn.set_character_set('utf8')

		return self.conn


	def dispatch(self):
		self.session_store = sessions.get_store(request=self.request)
		try:
			webapp2.RequestHandler.dispatch(self)
		finally:
			self.session_store.save_sessions(self.response)


	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session()


	@webapp2.cached_property
	def request(self):
		return self.get_request()


	@webapp2.cached_property
	def jinja2(self):
		return jinja2.get_jinja2(app=self.app)


	def render_template(self, filename, template_args):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# BASE URL
		base_url = urlparse.urlparse(self.request.url)
		template_args['BASE_URL'] = base_url

		# GLOBAL VARS
		query = ("""SELECT url FROM photos
			         WHERE width >= 1024
			           AND height > 600
			           AND width <= 1600
			           AND height <= 1024
			      ORDER BY RAND()
			         LIMIT 1""")
		cursor.execute(query)
		background = cursor.fetchone()

		template_args['TJ__PROFILE_PHOTO'] = self.session.get('profile_photo')
		template_args['TJ__PROFILE_URL'] = self.session.get('profile_url')
		template_args['TJ_BACKGROUND_IMG'] = None
		
		if background and 'url' in background and background['url']:
			template_args['TJ_BACKGROUND_IMG'] = background['url']
		
		self.response.write(self.jinja2.render_template(filename, **template_args))