import os

config = None
mysql = None

mysql_dev = {
	'port':    3306,
	'host':    'localhost',
	'user':    'root',
	'passwd':  '',
	'db':      '',
	'charset': 'utf8'
}

mysql_prod = {
	'unix_socket': '',
	'db':          '',
	'user':        '',
	'passwd':      '',
	'charset':     ''
}

config_dev = {
	'MIN_PLACES_REQUIRED':     10,
	'API_KEY':                 '',
	'OAUTH_CLIENT_ID':         '',
	'OAUTH_CLIENT_SECRET':     '',
	'COOKIEPOLICY':            ''
}

config_prod = {
	'MIN_PLACES_REQUIRED':     10,
	'API_KEY':                 '',
	'OAUTH_CLIENT_ID':         '',
	'OAUTH_CLIENT_SECRET':     '',
	'COOKIEPOLICY':            ''
}

config = {
	'API_PROFILE':             '',
	'API_USER_INFO':           '',
	'DASHBOARD_PLANS_LIMIT':   6
}

flickr = {
	'FLICKR_API_KEY':    '',
	'FLICKR_API_SECRET': '',
	'FLICKR_BASE_URL':   'http://api.flickr.com/services/rest/?%s',
	'FLICKR_SEARCH':     'flickr.photos.search',
	'FLICKR_GET_SIZE':   'flickr.photos.getSizes'
}

wikipedia = {
	'WIKI_BASE_URL': 'http://en.wikipedia.org/w/api.php?%s'
}

gapi = {
	'GOOGLE_OAUTH_REQUEST':       'https://accounts.google.com/o/oauth2/auth?%s',
	'GOOGLE_OAUTH_TOKEN':         'https://accounts.google.com/o/oauth2/token',
	'GOOGLE_USER_PROFILE':        'https://www.googleapis.com/plus/v1/people/me?%s',
	'GOOGLE_PLACES_AUTOCOMPLETE': 'https://maps.googleapis.com/maps/api/place/autocomplete/json?%s',
	'GOOGLE_PLACES_SEARCH':       'https://maps.googleapis.com/maps/api/place/nearbysearch/json?%s',
	'GOOGLE_PLACES_DETAILS':      'https://maps.googleapis.com/maps/api/place/details/json?%s',
	'GOOGLE_TRANSLATE':           'https://www.googleapis.com/language/translate/v2',
	'GOOGLE_VIDEOS_SEARCH':       'https://www.googleapis.com/youtube/v3/search?%s',
	'GOOGLE_BOOKS_SEARCH':        'https://www.googleapis.com/books/v1/volumes?%s',
	'GOOGLE_PROFILE_PHOTO':       'https://plus.google.com/s2/photos/profile/%s?sz=300'
}

eventbrite = {
	'EVENTBRITE_API_KEY':      '',
	'EVENTBRITE_API_SECRET':   '',
	'EVENTBRITE_EVENT_SEARCH': 'https://www.eventbrite.com/json/event_search?%s'
}

openweather = {
	'OPENWEATHER_API_KEY':  '',
	'OPENWEATHER_FORECAST': 'http://api.openweathermap.org/data/2.5/forecast/daily?%s'
}

forecast = {
	'FORECAST_API_KEY': '',
	'FORECAST_FUTURE':  'https://api.forecast.io/forecast/%s/%s'
}

expedia = {
	'EXPEDIA_API_KEY':         '',
	'EXPEDIA_API_SECRET':      '',
	'EXPEDIA_CID':             '',
	'EXPEDIA_HOTELS_SEARCH':   'http://api.ean.com/ean-services/rs/hotel/v3/list?%s',
	'EXPEDIA_PHOTOS_SEARCH':   'http://api.ean.com/ean-services/rs/hotel/v3/roomImages?%s',
	'EXPEDIA_IMAGES_BASE_URL': 'http//media.expedia.com'
}

if (os.getenv('SERVER_SOFTWARE') and os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
	config.update(config_prod)
	mysql = mysql_prod
else:
	config.update(config_dev)
	mysql = mysql_dev
