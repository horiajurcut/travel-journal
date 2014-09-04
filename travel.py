from utils.jinja_filters import *

from controllers.main import *
from controllers.plan import *
from controllers.plans import *
from controllers.journal import *
from controllers.places import *

from api.gapi import *
from api.evbrite import *
from api.flickr import *
from api.wikipedia import *
from api.weather import *
from api.forecast import *
from api.expedia import *

import webapp2
from webapp2_extras import jinja2
import base_handlers

config = dict()
config['webapp2_extras.sessions'] = {
	'secret_key': 'my-super-secret-key',
}
config['webapp2_extras.jinja2'] = {
	'template_path': 'templates',
	'compiled_path': None,
	'force_compiled': False,
	'environment_args': {
		'autoescape': True,
		'extensions': [
			'jinja2.ext.autoescape',
			'jinja2.ext.with_'
			]
		},
	'globals': {
		'url_for' : webapp2.uri_for
	},
	'filters': {
		'tj_hotels_big_photos':       tj_hotels_big_photos,
		'tj_hotels_medium_photos':    tj_hotels_medium_photos,
		'tj_hotels_amenities_mask':   tj_hotels_amenities_mask,
		'tj_striphtml':               tj_striphtml,
		'tj_hotel_description':       tj_hotel_description,
		'tj_rating_system':           tj_rating_system,
		'tj_weather_icon':            tj_weather_icon,
		'tj_format_timestamp':        tj_format_timestamp,
		'tj_default_cover_photo':     tj_default_cover_photo,
		'tj_default_plan_card_photo': tj_default_plan_card_photo,
		'tj_map_link':                tj_map_link,
		'tj_profile_photo':           tj_profile_photo,
		'tj_background_image':        tj_background_image,
		'tj_max_wind_speed':          tj_max_wind_speed,
		'tj_capitalize':              tj_capitalize,
		'tj_place_icon':              tj_place_icon
	},
}

application = webapp2.WSGIApplication([
	webapp2.Route(r'/',                               handler=MainHandler,               name='tja_main'),
	webapp2.Route(r'/logout',                         handler=LogoutHandler,             name='tja_logout'),
	webapp2.Route(r'/oauthcallback',                  handler=OauthCallbackHandler,      name='tja_oauthcallback'),
	webapp2.Route(r'/journal/<plan_id:\d+>',          handler=JournalHandler,            name='tja_journal'),
	webapp2.Route(r'/plan',                           handler=PlanDestinationHandler,    name='tja_plan_destination'),
	webapp2.Route(r'/plans',                          handler=ViewPlansHandler,          name='tja_view_plans'),
	webapp2.Route(r'/community',                      handler=CommunityPlansHandler,     name='tja_community_plans'),
	webapp2.Route(r'/faq',                            handler=FaqHandler,                name='tja_faq'),
	webapp2.Route(r'/street-view/<plan_id:\d+>',      handler=StreetViewHandler,         name='tja_street_view'),
	webapp2.Route(r'/hyperlapse/<plan_id:\d+>',       handler=HyperlapseHandler,         name='tja_hyperlapse'),
	webapp2.Route(r'/tj/plans/status',                handler=StatusPollingHandler,      name='tja_plans_status'),
	webapp2.Route(r'/tj/search/places/<plan_id:\d+>', handler=GetRouteHandler,           name='tja_search_places'),
	webapp2.Route(r'/api/google/translate',           handler=TranslateTextHandler,      name='api_google_translate'),
	webapp2.Route(r'/api/google/places/autocomplete', handler=AutocompletePlacesHandler, name='api_google_places_autocomplete'),
	webapp2.Route(r'/api/google/places/details',      handler=GetPlaceDetailsHandler,    name='api_google_places_details'),
	webapp2.Route(r'/api/google/places/search',       handler=SearchPlacesHandler,       name='api_google_places_search'),
	webapp2.Route(r'/api/google/videos/search',       handler=SearchVideosHandler,       name='api_google_videos_search'),
	webapp2.Route(r'/api/google/books/search',        handler=SearchBooksHandler,        name='api_google_books_search'),
	webapp2.Route(r'/api/eventbrite/events/search',   handler=SearchEventsHandler,       name='api_eventbrite_events_search'),
	webapp2.Route(r'/api/flickr/search',              handler=SearchPhotosHandler,       name='api_flickr_search'),
	webapp2.Route(r'/api/flickr/get_size',            handler=GetPhotoSizesHandler,      name='api_flickr_get_size'),
	webapp2.Route(r'/api/wikipedia/summary',          handler=GetWikiSummaryHandler,     name='api_wikipedia_summary'),
	webapp2.Route(r'/api/forecast/future',            handler=GetFutureForecastHandler,  name='api_frecast_future'),
	webapp2.Route(r'/api/weather/forecast',           handler=GetWeatherForecastHandler, name='api_weather_forecast'),
	webapp2.Route(r'/api/expedia/hotels/search',      handler=SearchHotelsHandler,       name='api_expedia_hotels_search'),
	webapp2.Route(r'/api/expedia/photos/search',      handler=SearchRoomPhotosHandler,   name='api_expedia_photos_search')
], config=config, debug=True)

# Custom 404
def handle_404(request, response, exception):
	c = {'exception': exception.status}
	t = jinja2.get_jinja2(app=application).render_template('error.html', **c)
	response.write(t)
	response.set_status(exception.status_int)

application.error_handlers[404] = handle_404