from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import openweather
from utils.sync import Sync

import MySQLdb
import urllib
import urlparse
import json
import datetime

class GetWeatherForecastHandler(BaseHandler):
	def get(self):
		latitude  = self.request.get('latitude')
		longitude = self.request.get('longitude') 

		params = {
			'mode':  'json',
			'lat':   latitude,
			'lon':   longitude,
			'cnt':   14,
			'lang':  'en',
			'APPID': openweather['OPENWEATHER_API_KEY']
		}
		params   = urllib.urlencode(params)
		forecast = json.loads(urllib.urlopen(openweather['OPENWEATHER_FORECAST'] % params).read())

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(forecast))