from google.appengine.api import taskqueue
from base_handlers import BaseHandler

import MySQLdb
import urllib
import urlparse
import json
import datetime


class ViewPlansHandler(BaseHandler):
	def get(self):
		# Check if User is already logged in
		if not self.session.get('google_id'):
			return self.redirect('/')

		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Get User data
		user_id = self.session.get('user_id')

		# Select plans for current User
		query = ("""SELECT
			           Cities.name AS city,
			           Cities.id AS city_id,
			           CONCAT(Cities.latitude, ',', Cities.longitude) AS location,
			           Plans.id AS plan_id,
			           Plans.status AS status,
			           Photos.url AS cover_url
			      FROM plans Plans
			INNER JOIN cities Cities ON Cities.id = Plans.city_id
			LEFT JOIN (
			    SELECT url, city_id 
			      FROM photos
			     WHERE size = %s
			  ORDER BY RAND()
			) Photos ON Photos.city_id = Plans.city_id
			     WHERE Plans.user_id = %s
			  GROUP BY Plans.id
			  ORDER BY Plans.id DESC""")

		cursor.execute(query, ('Medium', user_id))

		plans = cursor.fetchall()

		self.render_template('plans.html', {
			'plans': plans
		})


class CommunityPlansHandler(BaseHandler):
	def get(self):
		# Check if User is already logged in
		if not self.session.get('google_id'):
			return self.redirect('/')

		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Get User data
		user_id = self.session.get('user_id')

		# Select plans for current User
		query = ("""SELECT
			           Cities.name AS city,
			           Cities.id AS city_id,
			           CONCAT(Cities.latitude, ',', Cities.longitude) AS location,
			           Plans.id AS plan_id,
			           Plans.status AS status,
			           Photos.url AS cover_url
			      FROM plans Plans
			INNER JOIN cities Cities ON Cities.id = Plans.city_id
			LEFT JOIN (
			    SELECT url, city_id 
			      FROM photos
			     WHERE size = %s
			  ORDER BY RAND()
			) Photos ON Photos.city_id = Plans.city_id
			     WHERE Plans.user_id != %s
			       AND Plans.status != 0
			  GROUP BY Cities.id
			  ORDER BY RAND() DESC
			  LIMIT 20""")

		cursor.execute(query, ('Medium', user_id))

		plans = cursor.fetchall()

		self.render_template('community.html', {
			'plans': plans
		})


class StatusPollingHandler(BaseHandler):
	def post(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Get user data
		user_id = self.session.get('user_id')

		# Get Plan IDs
		plans = self.request.get_all('plans[]')

		results = None
		if plans and user_id:
			# Select Plans for current User
			format_strings = ','.join(['%s'] * len(plans))

			query = """SELECT
				            Plans.id AS plan_id,
				            Plans.status AS plan_status
				        FROM plans Plans
				       WHERE Plans.id IN (%s)""" % format_strings
			query += " AND Plans.user_id = %s" % user_id
			
			cursor.execute(query, tuple(plans))
			results = cursor.fetchall()

		db_conn.commit()

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(results))


class FaqHandler(BaseHandler):
	def get(self):
		self.render_template('faq.html', {})
