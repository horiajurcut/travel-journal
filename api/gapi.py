from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import gapi, config
from utils.broken import *
from utils.sync import Sync

import MySQLdb
import urllib
import urllib2
import urlparse
import json
import datetime


class AutocompletePlacesHandler(BaseHandler):
	def get(self):
		params = {
			'sensor': 'true',
			'input':  self.request.get('q').encode('utf8'),
			'key':    config['API_KEY'],
			'language': 'en',
			'types': '(cities)'
		}
		params = urllib.urlencode(params)
		
		places = json.loads(urllib2.urlopen(gapi['GOOGLE_PLACES_AUTOCOMPLETE'] % params).read())

		results = []
		if 'predictions' in places and places['predictions']:
			results = [{'value': item['description']} for item in places['predictions']]

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(results))


class TranslateTextHandler(BaseHandler):
	def post(self):
		params = {
			'target': 'en',
			'q':      self.request.get('q').encode('utf8'),
			'key':    config['API_KEY']
		}
		params = urllib.urlencode(params)

		headers = {
			'X-HTTP-Method-Override': 'GET'
		}

		req = urllib2.Request(url=gapi['GOOGLE_TRANSLATE'], data=params, headers=headers)
		translation = json.loads(urllib2.urlopen(req).read())

		translatedText = None
		if 'data' in translation and translation['data']:
			translation = translation['data']
		
		if 'translations' in translation and translation['translations']:
			translation = translation['translations']

		if len(translation) and type(translation) is list and 'translatedText' in translation[0] and translation[0]['translatedText']:
			translatedText = translation[0]['translatedText']

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(translatedText))


class SearchPlacesHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		location = self.request.get('location')
		types    = self.request.get('types')
		city_id  = self.request.get('city_id')
		plan_id  = self.request.get('plan_id')

		# Check if we already have this state stored in the database

		params = {
			'sensor':   'true',
			'location': location,
			'language': 'en',
			'types':    types,
			'radius':   1000,
			'rankby':   'prominence',
			'key':      config['API_KEY']
		}
		params = urllib.urlencode(params)
		places = json.loads(urllib.urlopen(gapi['GOOGLE_PLACES_SEARCH'] % params).read())

		places_queue = taskqueue.Queue('places')

		if 'status' in places and places['status'] == 'OK' and 'results' in places and places['results']:
			for place in places['results']:
				if 'reference' not in place:
					continue
				
				details = {
					'id':        None,
					'name':      None,
					'reference': None,
					'types':     None,
					'vicinity':  None,
					'latitude':  None,
					'longitude': None,
					'icon':      None
				}

				if 'id' in place and place['id']:
					details['id'] = place['id']

				if 'reference' and place['reference']:
					details['reference'] = place['reference']

				if 'name' in place and place['name']:
					details['name'] = place['name']

				if 'geometry' in place and place['geometry'] and 'location' in place['geometry'] and place['geometry']['location']:
					details['latitude']  = place['geometry']['location']['lat']
					details['longitude'] = place['geometry']['location']['lng']

				if 'types' in place and place['types']:
					details['types'] = '|'.join(place['types'])

				if 'icon' in place and place['icon']:
					details['icon'] = place['icon']

				if 'vicinity' in place and place['vicinity']:
					details['vicinity'] = place['vicinity']

				if not all(details.values()):
					continue

				details['rating'] = None
				if 'rating' in place and place['rating']:
					details['rating'] = place['rating']

				place_db = (
					details['id'],
					city_id,
					details['reference'],
					details['types'],
					details['name'],
					details['vicinity'],
					details['latitude'],
					details['longitude'],
					details['rating'],
					details['icon'],
					str(datetime.datetime.now())
				)

				cursor.execute(
					"""INSERT IGNORE INTO places (gapi_id, city_id, reference, types, name, vicinity, latitude, longitude, rating, icon, created)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
					place_db
				);

				place_id = cursor.lastrowid

				if 'photos' in place and place['photos'] and place_id:
					for photo in place['photos']:
						if 'photo_reference' in photo and photo['photo_reference']:
							cursor.execute("INSERT IGNORE INTO places_photos (place_id, reference) VALUES (%s, %s)", (place_id, photo['photo_reference']))

				if place_id:
					t = taskqueue.Task(
						url='/api/google/places/details',
						params={
							'reference': details['reference'],
							'place_id': place_id,
							'plan_id': plan_id
						},
						method='GET'
					)
					places_queue.add(t)
					s.count_tasks(plan_id)

		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(places))


class GetPlaceDetailsHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		place_id  = self.request.get('place_id')
		reference = self.request.get('reference')
		plan_id   = self.request.get('plan_id')

		if not place_id:
			# Sync completed Task
			s.update_count(plan_id)
			
			return False

		params = {
			'sensor':    'true',
			'reference': reference,
			'language': 'en',
			'key':       config['API_KEY']
		}
		params  = urllib.urlencode(params)
		details = json.loads(urllib.urlopen(gapi['GOOGLE_PLACES_DETAILS'] % params).read())

		if 'result' in details and details['result'] and 'photos' in details['result'] and details['result']['photos']:
			for photo in details['result']['photos']:
				if 'photo_reference' in photo and photo['photo_reference']:
					cursor.execute("INSERT IGNORE INTO places_photos (place_id, reference) VALUES (%s, %s)", (place_id, photo['photo_reference']))

		if 'result' in details and details['result'] and 'reviews' in details['result'] and details['result']['reviews']:
			for review in details['result']['reviews']:
				place_review = {
					'author_id':   None,
					'author_name': None,
					'review':      None,
					'rating':      None,
					'reviewed_on': None
				}

				if 'text' in review and review['text']:
					place_review['review'] = review['text']

				if 'author_url' in review and review['author_url']:
					place_review['author_id'] = urlparse.urlparse(review['author_url']).path[1:]

				if 'author_name' in review and review['author_name']:
					place_review['author_name'] = review['author_name']

				if 'rating' in review and review['rating']:
					place_review['rating'] = review['rating']

				if 'time' in review and review['time']:
					place_review['reviewed_on'] = datetime.datetime.fromtimestamp(review['time'])

				if not all(place_review.values()):
					continue

				place_review['aspects'] = None
				if 'aspects' in review and review['aspects']:
					place_review['aspects'] = json.dumps(review['aspects'])

				review_db = (
					place_id,
					place_review['author_id'],
					place_review['author_name'],
					place_review['review'],
					place_review['aspects'],
					place_review['rating'],
					place_review['reviewed_on'],
					httpExists(gapi['GOOGLE_PROFILE_PHOTO'] % place_review['author_id'])
				)

				cursor.execute(
					"""INSERT INTO places_reviews (place_id, author_id, author_name, review, aspects, rating, reviewed_on, has_photo)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
					review_db
				)

		if 'result' in details and details['result'] and 'events' in details['result'] and details['result']['events']:
			for event in details['result']['events']:
				place_event = {
					'event_id':   None,
					'start_time': None,
					'summary':    None,
					'url':        None
				}

				if 'event_id' in event and event['event_id']:
					place_event['event_id'] = event['event_id']

				if 'start_time' in event and event['start_time']:
					place_event['start_time'] = event['start_time']

				if 'summary' in event and event['summary']:
					place_event['summary'] = event['summary']

				if 'url' in event and event['url']:
					place_event['url'] = event['url']

				if not all(place_event.values()):
					continue

				event_db = (
					place_id,
					place_event['event_id'],
					place_event['start_time'],
					place_event['summary'],
					place_event['url']
				)

				cursor.execute(
					"""INSERT INTO places_events (place_id, event_id, start_time, summary, url)
					VALUES (%s, %s, %s, %s, %s)""",
					event_db
				)

		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(details))


class SearchVideosHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		city    = self.request.get('city').encode('utf8')
		city_id = self.request.get('city_id')
		plan_id = self.request.get('plan_id')
		
		# Process query string
		query = [item.replace(',', '') for item in city.split()]
		query.append('travel')
		query = '+'.join(query)

		params = {
			'part':            'snippet',
			'key':             config['API_KEY'],
			'type':            'video',
			'order':           'relevance',
			'maxResults':      30,
			'videoDefinition': 'high',
			'q':               query
		}
		params = urllib.urlencode(params)
		videos = json.loads(urllib.urlopen(gapi['GOOGLE_VIDEOS_SEARCH'] % params).read())

		if 'items' in videos and videos['items']:
			for item in videos['items']:
				video_db = {
					'video_id':  None,
					'title':     None,
					'thumbnail': None
				}

				if 'id' in item and item['id'] and 'videoId' in item['id'] and item['id']['videoId']:
					video_db['video_id'] = item['id']['videoId']

				if 'snippet' in item and item['snippet'] and 'title' in item['snippet'] and item['snippet']['title']:
					video_db['title'] = item['snippet']['title']

				if 'snippet' in item and item['snippet'] and 'thumbnails' in item['snippet'] and item['snippet']['thumbnails']:
					thumb = item['snippet']['thumbnails']
					if 'high' in thumb and thumb['high'] and 'url' in thumb['high'] and thumb['high']['url']:
						video_db['thumbnail'] = thumb['high']['url']

				if not all(video_db.values()):
					continue

				cursor.execute(
					"INSERT IGNORE INTO cities_videos (city_id, video_id, title, thumbnail) VALUES (%s, %s, %s, %s)",
					(city_id, video_db['video_id'], video_db['title'], video_db['thumbnail'])
				)

		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(videos))


class SearchBooksHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()
		
		city    = self.request.get('city').encode('utf8')
		city_id = self.request.get('city_id')
		plan_id = self.request.get('plan_id')

		# Process query string
		query = [item.replace(',', '') for item in city.split()]
		query.append('travel')
		query = '+'.join(query)

		params = {
			'key':        config['API_KEY'],
			'q':          query,
			'maxResults': 30,
			'orderBy':    'relevance',
			'country':    'US'
		}
		params = urllib.urlencode(params)
		books = json.loads(urllib.urlopen(gapi['GOOGLE_BOOKS_SEARCH'] % params).read())

		if 'items' in books and books['items']:
			for item in books['items']:
				book_db = {
					'book_id':     None,
					'title':       None,
					'description': None,
					'thumbnail':   None,
					'url':         None
				}

				if 'id' in item and item['id']:
					book_db['book_id'] = item['id']

				if 'volumeInfo' in item and item['volumeInfo'] and 'title' in item['volumeInfo'] and item['volumeInfo']['title']:
					book_db['title'] = item['volumeInfo']['title']

				if 'volumeInfo' in item and item['volumeInfo'] and 'description' in item['volumeInfo'] and item['volumeInfo']['description']:
					book_db['description'] = item['volumeInfo']['description']

				if 'volumeInfo' in item and item['volumeInfo'] and 'imageLinks' in item['volumeInfo'] and item['volumeInfo']['imageLinks']:
					img = item['volumeInfo']['imageLinks']

					if 'thumbnail' in img and img['thumbnail']:
						book_db['thumbnail'] = img['thumbnail']

				if 'volumeInfo' in item and item['volumeInfo'] and 'infoLink' in item['volumeInfo'] and item['volumeInfo']['infoLink']:
					book_db['url'] = item['volumeInfo']['infoLink']

				if not all(book_db.values()):
					continue

				cursor.execute(
					"INSERT IGNORE INTO cities_books (city_id, book_id, title, description, thumbnail, url) VALUES (%s, %s, %s, %s, %s, %s)",
					(city_id, book_db['book_id'], book_db['title'], book_db['description'], book_db['thumbnail'], book_db['url'])
				)

		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(books))