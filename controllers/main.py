from google.appengine.api import taskqueue
from base_handlers import BaseHandler
from settings import config, gapi

import MySQLdb
import urllib
import urlparse
import json
import datetime
import time
import random
import string
import base64


class MainHandler(BaseHandler):
	def get(self):
		# Check if User is already logged in
		if self.session.get('google_id'):
			return self.redirect('/plans')

		# Generate CSRF Token
		state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

		# Store State in Session
		self.session['state'] = state

		# oAuth Specifics
		scope = ['openid', 'email', 'profile']
		base_url = urlparse.urlparse(self.request.url)

		params = {
			'client_id':     config['OAUTH_CLIENT_ID'],
			'response_type': 'code',
			'scope':         ' '.join(scope),
			'redirect_uri':  base_url.scheme + '://' + base_url.netloc + '/oauthcallback',
			'state':         state,
			'access_type':   'online',
			'display':       'touch'
		}
		params = urllib.urlencode(params)

		# Generate OAUTH Request URL
		request_url = gapi['GOOGLE_OAUTH_REQUEST'] % params

		self.render_template('index.html', {
			'OAUTH_SIGN_IN_URL': request_url
		})


class OauthCallbackHandler(BaseHandler):
	def get(self):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		if not self.request.get('code'):
			return self.redirect('/')

		# Redirect to / if CSRF Token doesn't match
		if self.request.get('state') != self.session.get('state'):
			return self.redirect('/')
		
		# Your base is belong to us
		base_url = urlparse.urlparse(self.request.url)

		#Exchange Code for Access Token
		params = {
			'code':          self.request.get('code'),
			'client_id':     config['OAUTH_CLIENT_ID'],
			'client_secret': config['OAUTH_CLIENT_SECRET'],
			'redirect_uri':  base_url.scheme + '://' + base_url.netloc + '/oauthcallback',
			'grant_type':    'authorization_code'
		}
		params = urllib.urlencode(params)
		
		# Retrieve Token
		token  = json.loads(urllib.urlopen(gapi['GOOGLE_OAUTH_TOKEN'], params).read())

		# Check again to see that everything is in order
		if not 'access_token' in token:
			return self.redirect('/')

		# Check for the id_token field - since we are not yet passing it to other components we can assume it's valid
		if not 'id_token' in token:
			return self.redirect('/')

		# Check for the expires_in field
		if not 'expires_in' in token:
			return self.redirect('/')

		# Get Profile Information
		params = {
			'access_token': token['access_token']
		}
		params = urllib.urlencode(params)

		profile = json.loads(urllib.urlopen(gapi['GOOGLE_USER_PROFILE'] % params).read())

		# Find the user in our database
		new_user = {
			'google_id':    None,
			'access_token': None,
			'id_token':     None,
			'expires_at':   None
		}

		if 'id' in profile and profile['id']:
			new_user['google_id'] = profile['id']

		new_user['access_token'] = token['access_token']
		new_user['id_token']     = token['id_token']
		new_user['expires_at']   = int(time.time()) + token['expires_in'] - 100

		# Time to make triple sure everything is ok
		if not all(new_user.values()):
			return self.redirect('/')

		# Fetch extra information
		new_user['display_name'] = None
		if 'displayName' in profile and profile['displayName']:
			new_user['display_name'] = profile['displayName']

		new_user['avatar'] = None
		if 'image' in profile and profile['image'] and 'url' in profile['image'] and profile['image']['url']:
			new_user['avatar'] = profile['image']['url']
		if new_user['avatar']:
			new_user['avatar'] = urlparse.urlsplit(new_user['avatar'])
			new_user['avatar'] = '%s://%s%s' % (new_user['avatar'].scheme, new_user['avatar'].hostname, new_user['avatar'].path)

		new_user['profile_url'] = None
		if 'url' in profile and profile['url']:
			new_user['profile_url'] = profile['url']

		new_user['email'] = None
		if 'emails' in profile and profile['emails']:
			for email in profile['emails']:
				if 'type' in email and email['type'] == 'account' and 'value' in email and email['value']:
					new_user['email'] = email['value']

		# Check if we already have the user in our database
		query = ("SELECT * FROM users WHERE google_id = %s")
		cursor.execute(query, new_user['google_id'])

		db_user = cursor.fetchone()

		user_id = None

		# Add User to Database
		if not db_user:
			db_prep = (
				new_user['display_name'],
				new_user['avatar'],
				new_user['profile_url'],
				new_user['google_id'],
				new_user['access_token'],
				new_user['id_token'],
				new_user['email'],
				new_user['expires_at']
			)

			query = ("""INSERT IGNORE INTO users
				        (display_name, avatar, profile_url, google_id, access_token, id_token, email, expires_at)
				        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""")
			cursor.execute(query, db_prep)

			# Save User ID
			user_id = cursor.lastrowid

		# Update Information
		if db_user:
			db_prep = (
				new_user['access_token'],
				new_user['id_token'],
				new_user['expires_at'],
				new_user['avatar'],
				new_user['profile_url'],
				new_user['display_name'],
				new_user['email'],
				new_user['google_id']
			)

			query = ("""UPDATE users 
				        SET access_token = %s,
				            id_token = %s,
				            expires_at = %s,
				            avatar = %s,
				            profile_url = %s,
				            display_name = %s,
				            email = %s
				        WHERE google_id = %s""")
			cursor.execute(query, db_prep)

			# Get User ID
			user_id = db_user['id']

		db_conn.commit()

		# Store Session Info
		self.session['user_id'] = user_id
		self.session['google_id'] = new_user['google_id']
		self.session['profile_photo'] = new_user['avatar']
		self.session['profile_url'] = new_user['profile_url']

		# Successfully logged in
		return self.redirect('/plans')


class LogoutHandler(BaseHandler):
	def get(self):
		if 'state' in self.session:
			del(self.session['state'])
		if 'user_id' in self.session:
			del(self.session['user_id'])
		if 'google_id' in self.session:
			del(self.session['google_id'])
		if 'profile_photo' in self.session:
			del(self.session['profile_photo'])
		if 'profile_url' in self.session:
			del(self.session['profile_url'])
		if 'tj__plan__error' in self.session:
			del(self.session['tj__plan__error'])

		return self.redirect('/')
			