from HTMLParser import HTMLParser
from settings import config
from random import randrange
import datetime


class MLStripper(HTMLParser):
	def __init__(self):
		self.reset()
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)


def tj_weather_icon(value):
	conditions = {
		'clear-day':           'wi-day-sunny',
		'clear-night':         'wi-night-clear',
		'rain':                'wi-rain',
		'snow':                'wi-snow',
		'sleet':               'wi-rain-mix',
		'wind':                'wi-windy',
		'fog':                 'wi-fog',
		'cloudy':              'wi-cloudy',
		'partly-cloudy-day':   'wi-day-cloudy',
		'partly-cloudy-night': 'wi-night-cloudy',
		'hail':                'wi-hail',
		'thunderstorm':        'wi-thunderstorm',
		'tornado':             'wi-tornado'
	}

	if value in conditions:
		return conditions[value]

	return 'wi-refresh'


def tj_format_timestamp(value, offset):
	future_day = datetime.datetime.fromtimestamp(value + (3600 * offset))

	return future_day.strftime('%I:%M %p')


def tj_hotels_big_photos(value, is_large):
	url = None

	if is_large:
		url = value.replace('_s', '_z')
	else:
		url = value.replace('_s', '_y')		

	return url


def tj_hotels_medium_photos(value):
	return value.replace('_s', '_y')


def tj_striphtml(value):
	parser = HTMLParser()

	s = MLStripper()
	s.feed(parser.unescape(value))

	return s.get_data()


def tj_hotel_description(value):
	return value.replace('Property Location ', '')


def tj_hotels_amenities_mask(value):
	if value == 0:
		return 'N/A'

	amenities_map = {	
		'1':         'Business Center',
		'2':         'Fitness Center',
		'4':         'Hot Tub On-site',
		'8':         'Internet Access Available',
		'16':        'Kids\' Activities',
		'32':        'Kitchen or Kitchenette',
		'64':        'Pets Allowed',
		'128':       'Pool',
		'256':       'Restaurant On-site',
		'512':       'Spa On-site',
		'1024':      'Whirlpool Bath Available',
		'2048':      'Breakfast',
		'4096':      'Babysitting',
		'8192':      'Jacuzzi',
		'16384':     'Parking',
		'32768':     'Room Service', 
		'65536':     'Accessible Path of Travel',
		'131072':    'Accessible Bathroom',
		'262144':    'Roll-in Shower',
		'524288':    'Handicapped Parking',
		'1048576':   'In-room Accessibility',
		'2097152':   'Accessibility Equipment for the Deaf',
		'4194304':   'Braille or Raised Signage',
		'8388608':   'Free Airport Shuttle',
		'16777216':  'Indoor Pool',
		'33554432':  'Outdoor Pool',
		'67108864':  'Extended Parking',
		'134217728': 'Free Parking'
	}

	getBin = lambda x: x >= 0 and str(bin(x))[2:] or "-" + str(bin(x))[3:]
	amenities = getBin(int(value))

	amenities_unpacked = []
	for index, digit in enumerate(amenities):
		if digit == '1':
			amenities_unpacked.append(amenities_map[str(pow(2, index))])

	if not amenities_unpacked:
		amenities_unpacked.append('Not Specified')

	return ', '.join(amenities_unpacked)


def tj_rating_system(value):
	if not value:
		value = 0

	value = float(value)
	star  = '<i class="fa %s"></i>'

	rating = []
	for i in range(1, 6):
		i = float(i)

		if value >= i:
			rating.append(star % 'fa-star rating')
		elif value >= (i - 0.5) and value < i:
			rating.append(star % 'fa-star-half-o rating')
		else:
			rating.append(star % 'fa-star-o rating')

	return ''.join(rating)


def tj_default_cover_photo(value, index):
	default_covers = [
		'http://farm4.static.flickr.com/3525/5778645762_d6903af1e7_b.jpg',
		'http://farm3.staticflickr.com/2143/2480440516_dcd1fefd03_o.jpg',
		'http://farm7.staticflickr.com/6203/6088693202_e784e77081_b.jpg',
		'http://farm4.staticflickr.com/3383/3480670171_3c6ab80304_b.jpg',
		'http://farm4.staticflickr.com/3094/3212771920_6ac23db25d_b.jpg',
		'http://farm5.staticflickr.com/4033/4249956507_45a8b1df21_b.jpg',
		'http://farm9.staticflickr.com/8328/8364081429_042115b07e_b.jpg',
		'http://farm5.staticflickr.com/4061/4312013288_3920ed5314_o.jpg',
		'http://farm3.staticflickr.com/2724/4057118827_0e97344705_o.jpg',
		'http://farm9.staticflickr.com/8400/8749429799_ce3965574c_b.jpg'
	]

	if not value:
		return default_covers[index % 10]

	return value


def tj_default_plan_card_photo(value, location):
	if not value:
		return 'http://maps.google.com/maps/api/staticmap?size=400x400&zoom=14&scale=2&maptype=roadmap&markers=color:green|%s&sensor=false&key=%s' % (location, config['API_KEY'])

	return value


def tj_map_link(value, description, zoom=17):
	if not value:
		return 'http://maps.google.com/?t=h'

	url = 'http://maps.google.com/?ll=%s&z=%s&t=h'

	if description:
		url = url + ('&q=%s' % description) 

	return url % (value, zoom)


def tj_profile_photo(value):
	if not value:
		return '/static/img/default_user.jpg'

	return '%s?sz=300' % value


def tj_background_image(value):
	default_covers = [
		'http://farm4.static.flickr.com/3525/5778645762_d6903af1e7_b.jpg',
		'http://farm3.staticflickr.com/2143/2480440516_dcd1fefd03_o.jpg',
		'http://farm7.staticflickr.com/6203/6088693202_e784e77081_b.jpg',
		'http://farm4.staticflickr.com/3383/3480670171_3c6ab80304_b.jpg',
		'http://farm4.staticflickr.com/3094/3212771920_6ac23db25d_b.jpg',
		'http://farm5.staticflickr.com/4033/4249956507_45a8b1df21_b.jpg',
		'http://farm9.staticflickr.com/8328/8364081429_042115b07e_b.jpg',
		'http://farm5.staticflickr.com/4061/4312013288_3920ed5314_o.jpg',
		'http://farm3.staticflickr.com/2724/4057118827_0e97344705_o.jpg',
		'http://farm9.staticflickr.com/8400/8749429799_ce3965574c_b.jpg'
	]

	random_index = randrange(0, len(default_covers))

	if not value:
		return default_covers[random_index]

	return value


def tj_max_wind_speed(value):
	maxWindSpeed = 0

	for item in value:
		if 'windSpeed' in item and float(item['windSpeed']) > maxWindSpeed:
			maxWindSpeed = float(item['windSpeed'])

	return maxWindSpeed


def tj_capitalize(value):
	if not value:
		return value

	s = [i.capitalize() for i in value.split(',')]

	return ', '.join(s)


def tj_place_icon(value):
	if not value:
		return 'fa fa-map-marker'

	value = value.split('|')[0]

	types = {
		'cafe':          'fa fa-coffee',
		'bar':           'fa fa-glass',
		'restaurant':    'fa fa-cutlery',
		'food':          'fa fa-cutlery',
		'bakery':        'fa fa-cutlery',
		'park':          'fa fa-leaf',
		'store':         'fa fa-gift',
		'shoe-store':    'fa fa-gift',
		'movie_theater': 'fa fa-film'
	}

	if value not in types:
		return 'fa fa-map-marker'

	return types[value]


def tj_share_facebook(value):
	pass


def tj_share_google(value):
	pass


def tj_share_twitter(value):
	pass