from base_handlers import BaseHandler
from settings import wikipedia
from utils.sync import Sync

import MySQLdb
import urllib
import json


class GetWikiSummaryHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		# Sync Directive
		s = Sync()

		city    = self.request.get('city').encode('utf8')
		city_id = self.request.get('city_id')
		plan_id = self.request.get('plan_id')

		params = {
			'format':      'json',
			'action':      'query',
			'prop':        'extracts',
			'titles':      city,
			'redirects':   1,
			'exsentences': 4,
			'explaintext': 1
		}
		params = urllib.urlencode(params)
		details = json.loads(urllib.urlopen(wikipedia['WIKI_BASE_URL'] % params).read())

		if 'query' in details and 'pages' in details['query'] and details['query']['pages']:
			page_ids = details['query']['pages'].keys()
			page_id = page_ids.pop()

			page = None
			if page_id:
				page = details['query']['pages'][page_id]

			summary = None
			if page and 'extract' in page:
				summary = page['extract']
				summary = [i for i in summary.split('.')]

				if len(summary) > 1:
					summary = summary[1:]
				
				summary = '.'.join(summary)

			if summary:
				query = ("UPDATE cities SET summary = %s WHERE id = %s")
				cursor.execute(query, (summary, city_id))

		db_conn.commit()

		# Sync completed Task
		s.update_count(plan_id)

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(summary))