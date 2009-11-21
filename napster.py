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

def createSession(key, device):
	global session_created, session_key
	args = {"apiKey": key, "deviceId": device}
	url=urlparse.urlunparse(('http',
		'api.napster.com:8080',
		'/rest/v4/security/createSession',
		'',
		urllib.urlencode(args),
		''))
	res = _parse_tree(_do_raw_napster_query(url))
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
	result=_etree_to_dict(tree.getroot())
	return result

def _do_raw_napster_query(url):
	f = urllib2.Request(url)
	#print "sending query %s" % url
	try:
		f = urllib2.urlopen(f)
	except Exception, e:
		print e.msg
		print e.fp.read()
		raise
	return f

def _do_napster_query(method,**kwargs):
	if not session_created:
		raise Exception("Create session first")
	args = {
		"sessionKey" : session_key,
	 	}
	for k,v in kwargs.items():
		args[k] = v.encode("utf8")
	url=urlparse.urlunparse(('https',
		'api.napster.com:8443',
		'/rest/v4/%s' % method,
		'',
		urllib.urlencode(args),
		''))
	return _parse_tree(_do_raw_napster_query(url))

def searchArtist(name):
	return _do_napster_query("search/artists", searchTerm=name)

def searchTrack(title):
	return _do_napster_query("search/tracks", searchTerm=title)

def getStreamData(artist, title):
	res = searchTrack(title)
	for t in res['track']:
                if t['trackName'][0] == title and t['artistName'][0] == artist:
			url = t['playTrackURL'][0]
			url = urlparse.urlparse(url)
			path = os.path.basename(url.path)
			url=urlparse.urlunparse(('https',
				'api.napster.com:8443',
				url.path,
				'',
				urllib.urlencode({"sessionKey":session_key}),
				''))
			request = urllib2.Request(url)
			opener = urllib2.build_opener()
			f = opener.open(request)

			return {"url": f.url, "artist": t['artistName'][0], "track": t['trackName'][0], "album": t['albumName'][0]}

def test():
	createSession("SSHvRhrPsvDwVodGkPUw", "ap")
	#print searchArtist("Miles Davis")
	getStreamUrl("Miles Davis", "Jean Pierre")

if __name__ == "__main__":
	test()
