from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import forecast
from utils.sync import Sync

import MySQLdb
import urllib
import urlparse
import json
import datetime

class GetFutureForecastHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		# Created Time
		created = datetime.datetime.now()

		# Get task specific data
		plan_id    = self.request.get('plan_id')
		latitude   = self.request.get('latitude')
		longitude  = self.request.get('longitude')
		future_day = self.request.get('future_day')

		params = [latitude, longitude, future_day]
		params = ','.join(params)

		print forecast['FORECAST_FUTURE'] % (forecast['FORECAST_API_KEY'], params)

		weather = json.loads(urllib.urlopen(forecast['FORECAST_FUTURE'] % (forecast['FORECAST_API_KEY'], params)).read())

		new_forecast = {
			'offset':      None,
			'hourly_data': None
		}

		if 'offset' in weather and weather['offset'] is not None:
			new_forecast['offset'] = weather['offset']

		if 'hourly' in weather and weather['hourly'] and 'data' in weather['hourly'] and weather['hourly']['data']:
			new_forecast['hourly_data'] = json.dumps(weather['hourly']['data'])

		if not new_forecast['hourly_data']:
			# Sync completed Task
			s.update_count(plan_id)
			
			return

		new_forecast['icon'] = None
		if 'hourly' in weather and weather['hourly'] and 'icon' in weather['hourly'] and weather['hourly']['icon']:
			new_forecast['icon'] = weather['hourly']['icon']

		new_forecast['summary'] = None
		if 'hourly' in weather and weather['hourly'] and 'summary' in weather['hourly'] and weather['hourly']['summary']:
			new_forecast['summary'] = weather['hourly']['summary']

		# Save everything in our DB
		forecast_db = (
			plan_id,
			future_day,
			new_forecast['summary'],
			int(new_forecast['offset']),
			new_forecast['icon'],
			new_forecast['hourly_data'],
			created
		)

		query = ("""INSERT IGNORE INTO plans_forecast
			        (plan_id, future_day, summary, offset, icon, hourly_data, created)
			        VALUES (%s, %s, %s, %s, %s, %s, %s)""")
		cursor.execute(query, forecast_db)

		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(weather))