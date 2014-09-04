from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import expedia
from utils.broken import *
from utils.sync import Sync

import MySQLdb
import urllib
import urllib2
import urlparse
import json
import datetime
import calendar
import hashlib


class SearchHotelsHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		# Get task specifics
		country    = self.request.get('country')
		city       = self.request.get('city')
		city_id    = self.request.get('city_id')
		plan_id    = self.request.get('plan_id')
		future_day = self.request.get('future_day')
		future_day = datetime.datetime.strptime(future_day, '%Y-%m-%d')

		# Filter Characters
		try:
			city= remove_accents(city).encode('utf8')
		except:
			city = city.encode('utf8')

		# Compose signature
		created = datetime.datetime.now()
		now = datetime.datetime.utcnow()
		now = calendar.timegm(now.utctimetuple())
		sig = expedia['EXPEDIA_API_KEY'] + expedia['EXPEDIA_API_SECRET'] + str(now)

		# Generate signature hash
		m = hashlib.md5()
		m.update(sig.encode('utf-8'))
		signature = m.hexdigest()

		params = {
			'cid':             expedia['EXPEDIA_CID'],
			'apiKey':          expedia['EXPEDIA_API_KEY'],
			'sig':             signature,
			'currencyCode':    'USD',
			'city':            city,
			'countryCode':     country,
			'arrivalDate':     future_day.strftime('%m/%d/%Y'),
			'departureDate':   (future_day + datetime.timedelta(days=10)).strftime('%m/%d/%Y'),
			'numberOfResults': 16,
			'_type':           'json'
		}
		params = urllib.urlencode(params)
		hotels = json.loads(urllib2.urlopen(expedia['EXPEDIA_HOTELS_SEARCH'] % params, timeout=20).read())

		# The Queue
		hotels_queue = taskqueue.Queue('hotels')

		if 'HotelListResponse' in hotels and hotels['HotelListResponse']:
			hotels = hotels['HotelListResponse']

		if 'HotelList' in hotels and hotels['HotelList']:
			hotels = hotels['HotelList']

		if 'HotelSummary' in hotels and hotels['HotelSummary']:
			hotels = hotels['HotelSummary']

		if not hotels:
			# Sync completed Task
			s.update_count(plan_id)

			return

		if type(hotels) is dict:
			hotels = [hotels]

		for hotel in hotels:
			new_hotel = {
				'hotel_id':             None,
				'name':                 None,
				'thumbnail':            None,
				'description':          None,
				'location_description': None,
				'url':                  None,
				'latitude':             None,
				'longitude':            None,
				'address':              None,
				'high_rate':            None,
				'low_rate':             None,
				'rating':               None
			}

			if 'hotelId' in hotel and hotel['hotelId']:
				new_hotel['hotel_id'] = hotel['hotelId']

			if 'name' in hotel and hotel['name']:
				new_hotel['name'] = hotel['name']

			if 'thumbNailUrl' in hotel and hotel['thumbNailUrl']:
				new_hotel['thumbnail'] = expedia['EXPEDIA_IMAGES_BASE_URL'] + hotel['thumbNailUrl']

			if 'shortDescription' in hotel and hotel['shortDescription']:
				new_hotel['description'] = hotel['shortDescription']

			if 'locationDescription' in hotel and hotel['locationDescription']:
				new_hotel['location_description'] = hotel['locationDescription']

			if 'deepLink' in hotel and hotel['deepLink']:
				new_hotel['url'] = hotel['deepLink']

			if 'latitude' in hotel and hotel['latitude']:
				new_hotel['latitude'] = hotel['latitude']

			if 'longitude' in hotel and hotel['longitude']:
				new_hotel['longitude'] = hotel['longitude']

			if 'address1' in hotel and hotel['address1']:
				new_hotel['address'] = hotel['address1']

			if 'lowRate' in hotel and hotel['lowRate']:
				new_hotel['low_rate'] = hotel['lowRate']

			if 'highRate' in hotel and hotel['highRate']:
				new_hotel['high_rate'] = hotel['highRate']

			if 'hotelRating' in hotel and hotel['hotelRating']:
				new_hotel['rating'] = hotel['hotelRating']

			if not all(new_hotel.values()):
				continue

			new_hotel['trip_advisor_rating'] = None
			if 'tripAdvisorRating' in hotel and hotel['tripAdvisorRating']:
				new_hotel['trip_advisor_rating'] = hotel['tripAdvisorRating']

			new_hotel['amenity_mask'] = None
			if 'amenityMask' in hotel and hotel['amenityMask']:
				new_hotel['amenity_mask'] = hotel['amenityMask']

			# Add new hotel to database
			hotel_db = (
				city_id,
				new_hotel['hotel_id'],
				new_hotel['name'],
				new_hotel['thumbnail'],
				new_hotel['description'],
				new_hotel['location_description'],
				new_hotel['url'],
				new_hotel['latitude'],
				new_hotel['longitude'],
				new_hotel['address'],
				new_hotel['low_rate'],
				new_hotel['high_rate'],
				new_hotel['rating'],
				new_hotel['trip_advisor_rating'],
				new_hotel['amenity_mask'],
				future_day,
				created
			)

			query = ("""INSERT INTO cities_hotels (city_id, hotel_id, name, thumbnail, description,
					location_description, url, latitude, longitude, address, low_rate, high_rate,
					rating, trip_advisor_rating, amenity_mask, filter_date, created)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")

			cursor.execute(query, hotel_db)

			hotel_id = cursor.lastrowid

			# Let's grab some photos for this hotel
			t = taskqueue.Task(
				url='/api/expedia/photos/search',
				params={
					'plan_id': plan_id,
					'city_id': city_id,
					'hotel_id': hotel_id,
					'expedia_hotel_id': new_hotel['hotel_id']
				},
				method='GET'
			)
			hotels_queue.add(t)
			s.count_tasks(plan_id)

		# Write everything in DB
		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(hotels))


class SearchRoomPhotosHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		# Get task specifics
		city_id  = self.request.get('city_id')
		hotel_id = self.request.get('hotel_id')
		plan_id  = self.request.get('plan_id')
		expedia_hotel_id = self.request.get('expedia_hotel_id')

		# Compose signature
		created = datetime.datetime.now()
		
		now = datetime.datetime.utcnow()
		now = calendar.timegm(now.utctimetuple())
		sig = expedia['EXPEDIA_API_KEY'] + expedia['EXPEDIA_API_SECRET'] + str(now)

		# Generate signature hash
		m = hashlib.md5()
		m.update(sig.encode('utf-8'))
		signature = m.hexdigest()

		params = {
			'cid':     expedia['EXPEDIA_CID'],
			'apiKey':  expedia['EXPEDIA_API_KEY'],
			'sig':     signature,
			'hotelId': expedia_hotel_id,
			'_type':   'json'
		}
		params = urllib.urlencode(params)
		
		photos = json.loads(urllib2.urlopen(expedia['EXPEDIA_PHOTOS_SEARCH'] % params, timeout=20).read())

		# Dear programmer, please remember to replace _s with _y and _z
		if 'HotelRoomImageResponse' in photos and photos['HotelRoomImageResponse']:
			photos = photos['HotelRoomImageResponse']

		if 'RoomImages' in photos and photos['RoomImages']:
			photos = photos['RoomImages']

		if 'RoomImage' in photos and photos['RoomImage']:
			photos = photos['RoomImage']

		if not photos:
			# Sync completed Task
			s.update_count(plan_id)
			return

		if type(photos) is dict:
			photos = [photos]

		for photo in photos:
			if 'url' in photo and photo['url']:
				if not httpExists(photo['url']):
					continue

				if not httpExists(photo['url'].replace('_s', '_y')):
					continue

				photo_db = (
					city_id,
					hotel_id,
					expedia_hotel_id,
					photo['url'],
					httpExists(photo['url'].replace('_s', '_z')),
					created
				)

				query = ("""INSERT INTO hotels_photos (city_id, hotel_id, expedia_hotel_id, url, is_large, created)
						VALUES (%s, %s, %s, %s, %s, %s)""")

				cursor.execute(query, photo_db)

		# Save everything in DB
		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(photos))