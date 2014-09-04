tokens = [
]

import urllib
import urlparse
import time

for token in tokens:
	params = {
		'token': token
	}
	params = urllib.urlencode(params)
	res = urllib.urlopen('https://accounts.google.com/o/oauth2/revoke?%s' % params)

	print res.getcode()
	time.sleep(2)