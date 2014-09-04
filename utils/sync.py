import MySQLdb
import urllib
import urlparse
import json
import datetime
import os

from settings import mysql
from google.appengine.api import mail


class Sync():
	conn = None
	

	@property
	def connection(self):
		if self.conn is None:
			if (os.getenv('SERVER_SOFTWARE') and os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
				self.conn = MySQLdb.connect(
					unix_socket = mysql['unix_socket'],
					user        = mysql['user'],
					db          = mysql['db'],
					charset     = mysql['charset']
				)
			else:	
				self.conn = MySQLdb.connect(
					host    = mysql['host'],
					port    = mysql['port'],
					user    = mysql['user'],
					passwd  = mysql['passwd'],
					db      = mysql['db'],
					charset = mysql['charset']
				)
			self.conn.set_character_set('utf8')

		return self.conn


	def count_tasks(self, plan_id):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		query = ("UPDATE plans SET total_tasks = total_tasks + 1 WHERE id = %s")
		cursor.execute(query, plan_id)

		db_conn.commit()

		return True


	def update_count(self, plan_id):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		query = ("UPDATE plans SET completed_tasks = completed_tasks + 1, status = IF(completed_tasks = total_tasks, 2, status) WHERE id = %s")
		cursor.execute(query, plan_id)

		db_conn.commit()

		# Send Notification E-mail
		query = ("SELECT status, total_tasks, completed_tasks FROM plans WHERE id = %s")
		cursor.execute(query, plan_id)

		db_conn.commit()

		# Get latest info
		plan = cursor.fetchone()

		if plan and plan['status'] == 2 and plan['total_tasks'] == plan['completed_tasks']:
			self.send_notification(plan_id)

		return True


	def send_notification(self, plan_id):
		# MySQL Cursor
		db_conn = self.connection
		cursor  = db_conn.cursor(MySQLdb.cursors.DictCursor)

		query = ("""SELECT
			            Users.display_name AS display_name,
			            Users.email AS email,
			            Cities.name AS city_name
			        FROM plans Plans
			        INNER JOIN users Users ON Users.id = Plans.user_id
			        INNER JOIN cities Cities ON Cities.id = Plans.city_id
			        WHERE Plans.id = %s""")
		cursor.execute(query, plan_id)
		db_conn.commit()

		info = cursor.fetchone()

		if not info or not info['email']:
			return False

		sender_address = "Travel Journal <horia.dragos@gmail.com>"
		user_address   = info['email']
		subject        = "Travel Journal - %s" % info['city_name']
		journal_url    = "http://gcdc2013-travel-journal.appspot.com/journal/%s"
		
		body = """Hello %s,

We're glad to let you know that your Journal page for %s is now complete.
Our goal is to deliver the best available information, so you can make an informed decision.

You can start by visiting %s

Make the best of your holiday!

The Travel Journal Team""" % (info['display_name'], info['city_name'], journal_url % plan_id)

		mail.send_mail(sender_address, user_address, subject, body)