from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import config

import MySQLdb
import urllib
import urlparse
import json
import datetime

class GetRouteHandler(BaseHandler):
	def get(self, plan_id):
		db = self.connection
		cursor = db.cursor(MySQLdb.cursors.DictCursor)

		# Retrieve types specific to this plan
		query = ("SELECT city_id, types FROM plans WHERE id = %s")
		cursor.execute(query, plan_id)
		
		types = cursor.fetchone()

		city_id = types['city_id']
		types   = types['types'].split('|')
		
		# Prepare filter conditions
		conditions = []
		for t in types:
			conditions.append("Places.types LIKE '%{0}%'".format(t))

		query = ("""SELECT
			            Places.name AS name,
			            Places.vicinity AS vicinity,
			            Places.longitude AS longitude,
			            Places.latitude AS latitude,
			            Places.rating AS rating,
			            Places.icon AS icon,
			            Places.types AS types
			        FROM places Places
			       WHERE (%s) 
			         AND Places.city_id = %s
			    ORDER BY Places.rating DESC LIMIT 10""")  % (' OR '.join(conditions), city_id)

		cursor.execute(query)
		places = cursor.fetchall()

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(places))


class StreetViewHandler(BaseHandler):
	def get(self, plan_id):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		query = ("""SELECT id FROM plans WHERE id = %s""")

		cursor.execute(query, plan_id)
		plan = cursor.fetchone()

		if not plan:
			return self.redirect('/')

		self.render_template('street_view.html', {
			'GOOGLE_API_KEY': config['API_KEY'],
			'plan_id':        plan_id
		})


class HyperlapseHandler(BaseHandler):
	def get(self, plan_id):
		# Check if User is already logged in
		if not self.session.get('google_id'):
			return self.redirect('/')

		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		query = ("""SELECT id FROM plans WHERE id = %s""")

		cursor.execute(query, plan_id)
		plan = cursor.fetchone()

		if not plan:
			return self.redirect('/')
		
		self.render_template('hyperlapse.html', {
			'GOOGLE_API_KEY': config['API_KEY'],
			'plan_id':        plan_id
		})