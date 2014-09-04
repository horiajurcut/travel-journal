from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from utils.sync import Sync
from settings import config, gapi

import MySQLdb
import urllib
import urlparse
import json
import datetime
import calendar


class PlanDestinationHandler(BaseHandler):
	def get(self):
		# Check if User is already logged in
		if not self.session.get('google_id'):
			return self.redirect('/')

		# Get error messages from session
		error_msg = self.session.get('tj__plan__error')

		# Remove this message from the session
		if error_msg and 'tj__plan__error' in self.session:
			del(self.session['tj__plan__error'])

		self.render_template('plan.html', {
			'ERROR_MSG': error_msg
		})

	def post(self):
		# Check if User is already logged in
		if not self.session.get('google_id'):
			return self.redirect('/')
		
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Every entity is created NOW
		created = str(datetime.datetime.now())

		# Get current user
		user_id = self.session.get('user_id')
		
		# Get address
		city = self.request.get('city')

		# Get geolocation data
		latitude   = self.request.get('latitude')
		longitude  = self.request.get('longitude')

		# Check to see if we have a valid location
		if not latitude or not longitude:
			self.session['tj__plan__error'] = 'The location you have selected is unknown. Please try again.'
			return self.redirect('/plan')

		country    = self.request.get('country')
		short_city = self.request.get('short_city')
		future_day = self.request.get('future_day_submit')

		# Check to see if user filled in the future day
		if not future_day:
			self.session['tj__plan__error'] = 'Please select a future date around which you would like to plan your trip.'
			return self.redirect('/plan')

		# Extra Validation
		future_day = datetime.datetime.strptime(future_day, '%Y-%m-%d')
		future_tmp = calendar.timegm(future_day.utctimetuple())
		future_day = future_day.strftime('%Y-%m-%d')

		# Check to see if we have short_city
		if not short_city:
			short_city = city.split(',')[0]

		# Get preferences
		places = self.request.get_all('places[]')

		# Check to see if the user has selected at least one type of place
		if not len(places):
			self.session['tj__plan__error'] = 'Please select at least one type of place that you would like to visit.'
			return self.redirect('/plan')

		places = '|'.join(places)
		
		events = self.request.get_all('events[]')

		# Check to see if the user has selected at least one type of event
		if not len(events):
			self.session['tj__plan__error'] = 'Please select at least one type of event that you would like to attend.'
			return self.redirect('/plan')

		events = '|'.join(events)

		# Do an extra call to Places API
		params = {
			'sensor':   'true',
			'location': str(latitude) + ',' + str(longitude),
			'language': 'en',
			'types':    places,
			'radius':   1000,
			'rankby':   'prominence',
			'key':      config['API_KEY']
		}
		params  = urllib.urlencode(params)
		test_pl = json.loads(urllib.urlopen(gapi['GOOGLE_PLACES_SEARCH'] % params).read())

		if 'status' not in test_pl or test_pl['status'] != 'OK' or 'results' not in test_pl or not test_pl['results'] or len(test_pl['results']) < 3:
			self.session['tj__plan__error'] = 'We couldn\'t find places that met your criteria. Please try to select more types.'
			return self.redirect('/plan')

		# Check if the city already exists in the Database
		query = ("""SELECT id,
					       latitude,
					       longitude,
					       country
					 FROM cities
					WHERE latitude = %s
					  AND longitude = %s""")
		
		cursor.execute(query, (latitude, longitude))
		
		city_db = cursor.fetchone()

		# Add city to database if it's not there
		if city_db is None:
			new_city = (
				short_city,
				city,
				latitude,
				longitude,
				country,
				created
			)

			query = ("""INSERT IGNORE INTO cities
						(name, address, latitude, longitude, country, created)
						VALUES (%s, %s, %s, %s, %s, %s)""")

			cursor.execute(query, new_city)
			city_id = cursor.lastrowid
		else:
			city_id = city_db['id']

		# Write plan to database
		new_plan = (
			user_id,
			city_id,
			places,
			events,
			datetime.datetime.fromtimestamp(future_tmp)
		)

		query = ("""INSERT INTO plans
					(user_id, city_id, types, events, future_day)
					VALUES (%s, %s, %s, %s, %s)""")

		cursor.execute(query, new_plan)
		db_conn.commit()

		plan_id = cursor.lastrowid

		# Let's fire up the Main queue
		main_queue = taskqueue.Queue('main')
		
		# Sync Directive
		s = Sync()

		# Let's search for some cool places
		location = str(latitude + ',' + longitude)

		t = taskqueue.Task(
			url='/api/google/places/search',
			params={
				'location': location,
				'types': places,
				'city_id': city_id,
				'plan_id': plan_id
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# Let's find some awesome videos
		t = taskqueue.Task(
			url='/api/google/videos/search',
			params={
				'city': short_city,
				'city_id': city_id,
				'plan_id': plan_id
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# Fancy reading a book?
		t = taskqueue.Task(
			url='/api/google/books/search',
			params={
				'city': short_city,
				'city_id': city_id,
				'plan_id': plan_id
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# Photos from flickr
		t = taskqueue.Task(
			url='/api/flickr/search',
			params={
				'city': short_city,
				'city_id': city_id,
				'plan_id': plan_id,
				'latitude': latitude,
				'longitude': longitude
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# Let's grab some events so we don't get bored on our trip
		t = taskqueue.Task(
			url='/api/eventbrite/events/search',
			params={
				'city': short_city,
				'city_id': city_id,
				'country': country,
				'latitude': latitude,
				'longitude': longitude,
				'categories': events,
				'plan_id': plan_id,
				'future_day': future_day
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# What about hotels?
		t = taskqueue.Task(
			url='/api/expedia/hotels/search',
			params={
				'city': short_city,
				'city_id': city_id,
				'plan_id': plan_id,
				'country': country,
				'future_day': future_day
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# How about a little wikipedia knowledge
		t = taskqueue.Task(
			url='/api/wikipedia/summary',
			params={
				'city': short_city,
				'city_id': city_id,
				'plan_id': plan_id
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# But what about the weather?
		t = taskqueue.Task(
			url='/api/forecast/future',
			params={
				'plan_id':    plan_id,
				'latitude':   latitude,
				'longitude':  longitude,
				'future_day': str(future_tmp)
			},
			method='GET'
		)
		main_queue.add(t)
		s.count_tasks(plan_id)

		# Write to DB
		db_conn.commit()

		# Let's go somewhere beautiful
		return self.redirect('/plans')