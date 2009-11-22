#!/usr/bin/python

import urllib
import urllib2
import urlparse
import xml.etree.ElementTree
import re
from htmlentitydefs import name2codepoint
import httplib
import os

session_created=False
session_key = ""

# XXX: For the hackday this can be anything - should be a MAC or something
DEVICE_ID="hack"

def createSession(apiKey):
	global session_created, session_key
	args = {"apiKey": apiKey, "deviceId": DEVICE_ID}
	res = _do_parsed_napster_query("security/createSession", apiKey=apiKey, deviceId=DEVICE_ID)
	session_key = res['sessionKey'][0]
	session_created = True

def htmlentitydecode(s):
    os= re.sub('&(%s);' % '|'.join(name2codepoint), 
            lambda m: unichr(name2codepoint[m.group(1)]), s)
    return os

def _cleanname(x):
	if x is None:
		return ''
	return htmlentitydecode(x)

def _etree_to_dict(etree):
	result={}
	for i in etree:
		if i.tag not in result:
			result[i.tag]=[]
		if len(i):
			result[i.tag].append(_etree_to_dict(i))
		else:
			result[i.tag].append(_cleanname(i.text))
	return result

def _parse_tree(f):
	tree = xml.etree.ElementTree.ElementTree(file=f)
	return _etree_to_dict(tree.getroot())

def _do_raw_napster_query(url):
	f = urllib2.Request(url)
	try:
		f = urllib2.urlopen(f)
	except Exception, e:
		print >> sys.stderr, e.msg
		print >> sys.stderr, e.fp.read()
		raise
	return f

def _do_napster_query(method,**kwargs):
	args = {}
	if session_created:
		args = { "sessionKey" : session_key }
	elif method != "security/login" and method != "security/createSession":
		raise Exception("Login or create a session first")

	for k,v in kwargs.items():
		args[k] = v.encode("utf8")
	url=urlparse.urlunparse(('https',
		'api.napster.com:8443',
		'/rest/v4/%s' % method,
		'',
		urllib.urlencode(args),
		''))
	return _do_raw_napster_query(url)

def _do_parsed_napster_query(method, **kwargs):
	return _parse_tree(_do_napster_query(method, **kwargs))

def searchArtist(name):
	return _do_parsed_napster_query("search/artists", searchTerm=name)

def searchTrack(title):
	return _do_parsed_napster_query("search/tracks", searchTerm=title)


def getStreamData(artist, title):
	res = searchTrack(title)
	for t in res.get('track', []):
		# XXX: List of tracks - can we rank all of them?  based on how much of the name matches
                if t['trackName'][0] == title and t['artistName'][0] == artist:
			url = t['playTrackURL'][0]
			url = urlparse.urlparse(url)
			f = _do_napster_query("tracks/%s" % os.path.basename(url.path))

			return {"url": f.url, "artist": t['artistName'][0], "track": t['trackName'][0], "album": t['albumName'][0]}

def test():
	#createSession("SSHvRhrPsvDwVodGkPUw")
	print getStreamData("Miles Davis", "Bitches Brew")

if __name__ == "__main__":
	test()
