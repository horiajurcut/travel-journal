from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import flickr
from utils.broken import *
from utils.sync import Sync

import MySQLdb
import urllib
import urllib2
import json


class SearchPhotosHandler(BaseHandler):
	def get(self):
		city      = self.request.get('city')
		city_id   = self.request.get('city_id')
		plan_id   = self.request.get('plan_id')
		latitude  = self.request.get('latitude')
		longitude = self.request.get('longitude')
		tag_mode  = self.request.get('tag_mode') or 'all'

		# Sync Directive
		s = Sync()

		# Process query string
		city_query = []
		try:
			city_query = [remove_accents(city).encode('utf8')]
		except:
			city_query = [city.encode('utf8')]

		query = city_query

		if tag_mode == 'all':
			query.extend(['travel', '-women', '-girl', '-woman', '-nude'])

		query = ' '.join(query)

		params = {
			'api_key':        flickr['FLICKR_API_KEY'],
			'method':         flickr['FLICKR_SEARCH'],
			'text':           query,
			'per_page':       40,
			'page':           1,
			'privacy_filter': 1,
			'content_type':   1,
			'sort':           'interestingness-desc',
			'media':          'photos',
			'format':         'json',
			'nojsoncallback': 1
		}
		params = urllib.urlencode(params)
		photos = json.loads(urllib2.urlopen(flickr['FLICKR_BASE_URL'] % params, timeout=10).read())

		flickr_queue = taskqueue.Queue('flickr')

		photo_count = 0
		if 'photos' in photos and 'photo' in photos['photos']:
			for photo in photos['photos']['photo']:
				if 'id' in photo and photo['id']:
					t = taskqueue.Task(
						url='/api/flickr/get_size',
						params={
							'photo_id': photo['id'],
							'city_id': city_id,
							'plan_id': plan_id
						},
						method='GET'
					)
					flickr_queue.add(t)
					s.count_tasks(plan_id)
					photo_count = photo_count + 1

		# Safe Query for Flickr
		if photo_count < 5 and tag_mode == 'all':
			query = []
			query.extend(['forest', 'hills', 'clouds', 'summer', 'spring', 'winter', 'autumn', 'sky', 'mountains', '-women', '-girl', '-woman', '-nude'])
			query = ' '.join(query)
			
			params = {
				'api_key':        flickr['FLICKR_API_KEY'],
				'method':         flickr['FLICKR_SEARCH'],
				'text':           query,
				'per_page':       20,
				'page':           1,
				'privacy_filter': 1,
				'content_type':   1,
				'sort':           'interestingness-desc',
				'media':          'photos',
				'format':         'json',
				'nojsoncallback': 1
			}
			params = urllib.urlencode(params)
			photos = json.loads(urllib2.urlopen(flickr['FLICKR_BASE_URL'] % params, timeout=10).read())

			if 'photos' in photos and 'photo' in photos['photos']:
				for photo in photos['photos']['photo']:
					if 'id' in photo and photo['id']:
						t = taskqueue.Task(
							url='/api/flickr/get_size',
							params={
								'photo_id': photo['id'],
								'city_id': city_id,
								'plan_id': plan_id
							},
							method='GET'
						)
						flickr_queue.add(t)
						s.count_tasks(plan_id)

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(photos))


class GetPhotoSizesHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		photo_id = self.request.get('photo_id')
		city_id  = self.request.get('city_id')
		plan_id  = self.request.get('plan_id')

		params = {
			'api_key':        flickr['FLICKR_API_KEY'],
			'method':         flickr['FLICKR_GET_SIZE'],
			'photo_id':       photo_id,
			'format':         'json',
			'nojsoncallback': 1
		}
		params = urllib.urlencode(params)
		photo_details = json.loads(urllib2.urlopen(flickr['FLICKR_BASE_URL'] % params, timeout=10).read())

		if 'sizes' in photo_details and 'size' in photo_details['sizes']:
			for size in photo_details['sizes']['size']:
				if size and 'label' in size and 'source' in size and 'width' in size and 'height' in size:

					if size['label'] in ['Small', 'Small 320', 'Square', 'Large Square', 'Thumbnail']:
						continue

					details = (
						photo_id,
						city_id,
						size['label'],
						size['source'],
						int(size['width']),
						int(size['height'])
					)
					cursor.execute("INSERT IGNORE INTO photos (photo_id, city_id, size, url, width, height) VALUES (%s, %s, %s, %s, %s, %s)", details)

		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(photo_details))

