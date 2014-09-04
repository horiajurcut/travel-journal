from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import eventbrite
from utils.sync import Sync
from utils.broken import *

import MySQLdb
import urllib
import urlparse
import json
import datetime


class SearchEventsHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		# Every entity is created NOW
		created = str(datetime.datetime.now())

		city    = self.request.get('city')
		city_id = self.request.get('city_id')
		country = self.request.get('country')
		plan_id = self.request.get('plan_id')
		
		latitude = self.request.get('latitude')
		longitude = self.request.get('longitude')

		categories = self.request.get('categories')
		categories = categories.replace('|', ',')

		future_day = self.request.get('future_day')
		future_day = datetime.datetime.strptime(future_day, '%Y-%m-%d')

		# Filter Characters
		try:
			city= remove_accents(city).encode('utf8')
		except:
			city = city.encode('utf8')

		params = {
			'app_key':  eventbrite['EVENTBRITE_API_KEY'],
			'city':     city,
			'country':  country,
			'max':      16,
			'category': categories,
			'date':     '%s %s' % (future_day.strftime('%Y-%m-%d'), (future_day + datetime.timedelta(days=30)).strftime('%Y-%m-%d')),
			'display':  'repeat_schedule'
		}
		params = urllib.urlencode(params)
		events = json.loads(urllib.urlopen(eventbrite['EVENTBRITE_EVENT_SEARCH'] % params).read())

		# Let the parsing begin
		if 'events' in events and events['events']:
			for item in events['events']:
				new_event = {
					'eventbrite_id':   None,
					'title':           None,
					'url':             None,
					'start_date':      None,
					'end_date':        None,
					'venue_latitude':  None,
					'venue_longitude': None,
					'organizer_name':  None
				}

				if 'event' not in item:
					continue

				event = item['event']

				if 'id' in event and event['id']:
					new_event['eventbrite_id'] = event['id']

				if 'title' in event and event['title']:
					new_event['title'] = event['title']

				if 'url' in event and event['url']:
					new_event['url'] = event['url']

				if 'start_date' in event and event['start_date']:
					new_event['start_date'] = event['start_date']

				if 'end_date' in event and event['end_date']:
					new_event['end_date'] = event['end_date']

				if 'venue' in event and event['venue'] and 'latitude' in event['venue'] and event['venue']['latitude']:
					new_event['venue_latitude'] = event['venue']['latitude']

				if 'venue' in event and event['venue'] and 'longitude' in event['venue'] and event['venue']['longitude']:
					new_event['venue_longitude'] = event['venue']['longitude']

				if 'organizer' in event and event['organizer'] and 'name' in event['organizer'] and event['organizer']['name']:
					new_event['organizer_name'] = event['organizer']['name']

				#  If minimum requirements are not met we move on
				if not all(new_event.values()):
					continue

				new_event['logo'] = None
				if 'logo' in event and event['logo']:
					new_event['logo'] = event['logo']

				new_event['organizer_url'] = None
				if 'organizer' in event and event['organizer'] and 'url' in event['organizer'] and event['organizer']['url']:
					new_event['organizer_url'] = event['organizer']['url']

				new_event['venue_name'] = None
				if 'venue' in event and event['venue'] and 'name' in event['venue'] and event['venue']['name']:
					new_event['venue_name'] = event['venue']['name']

				new_event['venue_address'] = None
				if 'venue' in event and event['venue'] and 'address' in event['venue'] and event['venue']['address']:
					new_event['venue_address'] = event['venue']['address']

				new_event['venue_address_2'] = None
				if 'venue' in event and event['venue'] and 'address_2' in event['venue'] and event['venue']['address_2']:
					new_event['venue_address_2'] = event['venue']['address_2']	

				new_event['repeats'] = 0
				if 'repeats' in event and event['repeats'] == 'yes':
					new_event['repeats'] = 1

				new_event['repeat_schedule'] = None
				if 'repeat_schedule' in event and event['repeat_schedule']:
					new_event['repeat_schedule'] = event['repeat_schedule']

				new_event['categories'] = None
				if 'category' in event and event['category']:
					new_event['categories'] = event['category']

				# Insert the new event into our database
				event_db = (
					city_id,
					new_event['eventbrite_id'],
					new_event['title'],
					new_event['url'],
					new_event['logo'],
					new_event['categories'],
					new_event['start_date'],
					new_event['end_date'],
					new_event['venue_latitude'],
					new_event['venue_longitude'],
					new_event['venue_address'],
					new_event['venue_address_2'],
					new_event['venue_name'],
					new_event['organizer_name'],
					new_event['organizer_url'],
					new_event['repeats'],
					json.dumps(new_event['repeat_schedule']),
					future_day,
					created
				)

				query = ("""INSERT IGNORE INTO cities_events
					(city_id, eventbrite_id, title, url, logo, categories, start_date, end_date, venue_latitude,
					venue_longitude, venue_address, venue_address_2, venue_name, organizer_name,
					organizer_url, repeats, repeat_schedule, filter_date, created)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")

				cursor.execute(query, event_db)				

		# Write everything in DB
		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(events))