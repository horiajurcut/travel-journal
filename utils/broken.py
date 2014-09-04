import httplib
import urlparse
import unicodedata
import string

def httpExists(url):
	host, path = urlparse.urlsplit(url)[1:3]
	found = False
	try:
		connection = httplib.HTTPConnection(host)  ## Make HTTPConnection Object
		connection.request("HEAD", path)
		responseOb = connection.getresponse()      ## Grab HTTPResponse Object

		if responseOb.status in [200, 302]:
			found = True
		else:
			print "Status %d %s : %s" % (responseOb.status, responseOb.reason, url)
	except Exception, e:
		print e.__class__,  e, url
	return found


def remove_accents(data):
	data = unicode(data)
	return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')