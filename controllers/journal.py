from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import config

import MySQLdb
import urllib
import urlparse
import json
import datetime


class JournalHandler(BaseHandler):
	def get(self, plan_id):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Get user data
		user_id = self.session.get('user_id')

		query = ("""SELECT
			            Cities.id AS city_id,
			            Cities.name AS city,
			            Cities.summary AS summary,
			            Plans.future_day AS future_day,
			            Plans.types AS places_types,
			            Plans.events AS events_types,
			            Plans.status AS status
			      FROM plans Plans
			INNER JOIN cities Cities ON Cities.id = Plans.city_id
			     WHERE Plans.id = %s""")

		cursor.execute(query, plan_id)
		plan = cursor.fetchone()

		if not plan:
			return self.redirect('/')

		if 'status' in plan and plan['status'] == 0:
			self.render_template('in-progress.html', {})
			return

		places_types = plan['places_types'].split('|')
		
		# Prepare filter conditions for places
		places_conditions = []
		for t in places_types:
			places_conditions.append("Places.types LIKE '%{0}%'".format(t))

		events_types = plan['events_types'].split('|')
		
		# Prepare filter conditions for places
		events_conditions = []
		for t in events_types:
			events_conditions.append("Events.categories LIKE '%{0}%'".format(t))

		# Retrieve Photos
		query = ("""SELECT photo_id, url
			        FROM photos
			        WHERE city_id = %s
			          AND width >= 1024
			          AND height > 600
			          AND width <= 1600
			          AND height <= 1024
			     GROUP BY photo_id
			     ORDER BY RAND()
			        LIMIT 10""")
		cursor.execute(query, plan['city_id'])
		
		cover_photos = cursor.fetchall()

		if not cover_photos:
			cover_photos = []

		cover_photos = list(cover_photos)

		for index in range(len(cover_photos), 10):
			cover_photos.append(None)

		cover_photos = tuple(cover_photos)

		# Retrieve those awesome places
		query = ("""SELECT
			            Places.id AS place_id,
			            Places.name AS place_name,
			            Places.types AS place_types,
			            Places.vicinity AS place_vicinity,
			            Places.rating AS place_rating,
			            Places.latitude AS place_latitude,
			            Places.longitude AS place_longitude
			          FROM places Places
			         WHERE (%s)
			           AND Places.city_id = '%s'
			         ORDER BY Places.rating DESC
			         LIMIT 16""") % (' OR '.join(places_conditions), plan['city_id'])
		cursor.execute(query)
		
		places = cursor.fetchall()

		# Retrieve detailed information: reviews, events, photos
		for place in places:
			# Build location
			place['location'] = str(place['place_latitude']) + ',' + str(place['place_longitude'])

			# Get Photos
			query = ("SELECT DISTINCT(reference) FROM places_photos WHERE place_id = %s ORDER BY RAND() LIMIT 4")
			cursor.execute(query, place['place_id'])

			place['photos'] = cursor.fetchall()

			# Get Reviews
			query = ("""SELECT
				            author_id,
				            author_name,
				            review,
				            rating,
				            has_photo
				FROM places_reviews WHERE place_id = %s""")
			cursor.execute(query, place['place_id'])

			place['reviews'] = cursor.fetchall()

			# Retrieve Events
			query = ("""SELECT
				            event_id,
				            start_time,
				            summary,
				            url
				FROM places_events WHERE place_id = %s""")
			cursor.execute(query, place['place_id'])

			place['events'] = cursor.fetchall()

		# Retrieve the awesome forecast
		query = ("""SELECT
			            Forecast.future_day AS forecast_future_day,
			            Forecast.summary AS forecast_summary,
			            Forecast.offset AS forecast_offset,
			            Forecast.icon AS forecast_icon,
			            Forecast.hourly_data AS forecast_hourly_data
			        FROM plans_forecast Forecast
			        WHERE Forecast.plan_id = %s""")
		cursor.execute(query, plan_id)

		forecast = cursor.fetchone()
		
		# Convert Hourly Data
		if forecast:
			forecast['forecast_hourly_data'] = json.loads(forecast['forecast_hourly_data'])

		# Retrieve Hotels
		query = ("""SELECT
			            Hotels.id AS hotel_id,
			            Hotels.name AS hotel_name,
			            Hotels.description AS hotel_description,
			            Hotels.location_description AS hotel_location_description,
			            Hotels.url AS hotel_url,
			            Hotels.latitude AS hotel_latitude,
			            Hotels.longitude AS hotel_longitude,
			            Hotels.address AS hotel_address,
			            Hotels.low_rate AS hotel_low_rate,
			            Hotels.high_rate AS hotel_high_rate,
			            Hotels.rating AS hotel_rating,
			            Hotels.trip_advisor_rating AS hotel_trip_advisor_rating,
			            Hotels.amenity_mask AS hotel_amenity_mask
				    FROM cities_hotels Hotels
				   WHERE Hotels.city_id = %s
				     AND Hotels.filter_date = %s
				GROUP BY Hotels.hotel_id
				ORDER BY RAND()
				   LIMIT 16""")
		cursor.execute(query, (plan['city_id'], plan['future_day'].strftime('%Y-%m-%d %H:%M:%S')))
		hotels = cursor.fetchall()

		# Get additional information for hotels
		for hotel in hotels:
			# Build location
			hotel['location'] = str(hotel['hotel_latitude']) + ',' + str(hotel['hotel_longitude'])

			# Retrieve Hotel Photos
			query = ("SELECT DISTINCT(url), is_large FROM hotels_photos WHERE hotel_id = %s ORDER BY RAND() LIMIT 4")
			cursor.execute(query, hotel['hotel_id'])

			hotel['photos'] = cursor.fetchall()

		# Retrieve some awesome events
		query = ("""SELECT
			            Events.title,
			            Events.url,
			            Events.logo,
			            Events.categories,
			            Events.start_date,
			            Events.end_date,
			            Events.venue_latitude,
			            Events.venue_longitude,
			            Events.venue_address,
			            Events.venue_address_2,
			            Events.organizer_name,
			            Events.organizer_url,
			            Events.repeats,
			            CONCAT(Events.venue_latitude, ',', Events.venue_longitude) AS location
			 FROM cities_events Events
			WHERE (%s)
			  AND Events.city_id = '%s'
			  AND Events.filter_date = '%s'
			LIMIT 16""") % (' OR '.join(events_conditions), plan['city_id'], plan['future_day'].strftime('%Y-%m-%d %H:%M:%S'))
		cursor.execute(query)

		events = cursor.fetchall()

		# Retrieve Books
		query = ("""SELECT
			            Books.title,
			            Books.description,
			            Books.thumbnail,
			            Books.url
			          FROM cities_books Books
			         WHERE Books.city_id = %s
			      ORDER BY RAND()
			         LIMIT 20""")
		cursor.execute(query, plan['city_id'])

		books = cursor.fetchall()

		# Retrieve Videos
		query = ("""SELECT
			            Videos.title,
			            Videos.video_id,
			            Videos.thumbnail
			          FROM cities_videos Videos
			         WHERE Videos.city_id = %s
			      ORDER BY RAND()
			         LIMIT 20""")
		cursor.execute(query, plan['city_id'])

		videos = cursor.fetchall()

		# Retrieve City Info
		city_info = {
			'city':       plan['city'],
			'plan_id':    plan_id,
			'summary':    plan['summary'],
			'future_day': plan['future_day'],
			'future_end': plan['future_day'] + datetime.timedelta(days=30)
		}

		self.render_template('journal.html', {
			'GOOGLE_API_KEY': config['API_KEY'],
			'city_info':      city_info,
			'cover_photos':   cover_photos,
			'places':         places,
			'forecast':       forecast,
			'hotels':         hotels,
			'events':         events,
			'videos':         videos,
			'books':          books
		})