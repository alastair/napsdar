#!/usr/bin/python

import urllib
import urllib2
import urlparse
import xml.etree.ElementTree
import re
from htmlentitydefs import name2codepoint
import httplib
import os
import ConfigParser
import sys
import time
import pickle

session_created=False
session_key = ""
session_expiry = 0

# XXX: For the hackday this can be anything - should be a MAC or something
DEVICE_ID="hack"

memocache = {}
def memoify(func):
	def memoify(*args,**kwargs):
		if func.__name__ not in memocache:
			memocache[func.__name__]={}
		key=pickle.dumps((args,kwargs))
		if key not in memocache[func.__name__]:
			memocache[func.__name__][key]=func(*args,**kwargs)

		return memocache[func.__name__][key]
	return memoify

def connect():
	config=ConfigParser.RawConfigParser()
	config.add_section("napsdar")
	config.set("napsdar", "username", "")
	config.set("napsdar", "password", "")
	config.set("napsdar", "apikey", "")
	config.read(os.path.expanduser("~/.playdar/napsdar"))
	user = config.get("napsdar", "username")
	passw = config.get("napsdar", "password")
	apiKey = config.get("napsdar", "apikey")
	if apiKey == "":
		raise Exception("Need an API key (napsdar.apikey)")

	if user != "" and passw != "":
		_login(apiKey, user, passw)
	else:
		_createSession(apiKey)

def _createSession(apiKey):
	global session_created, session_key, session_expiry
	res = _do_napster_query("security/createSession", apiKey=apiKey, deviceId=DEVICE_ID)
	session_key = res['sessionKey'][0]
	session_created = True
	session_expiry = time.time() + int(res['minutesUntilExpiry'][0]) * 60

def _login(apiKey, user, passw):
	global session_created, session_key, session_expiry
	res = _do_napster_query("security/login", apiKey=apiKey, deviceId=DEVICE_ID, username=user, password=passw)
	session_key = res['sessionKey'][0]
	session_created = True
	session_expiry = time.time() + int(res['minutesUntilExpiry'][0]) * 60

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

def _do_napster_query(method, **kwargs):
	""" You probably don't want to use this to do a query -
	    use _do_checked_query instead"""
	args = {}
	for k,v in kwargs.items():
		args[k] = v.encode("utf8")

	url=urlparse.urlunparse(('https',
		'api.napster.com:8443',
		'/rest/v4/%s' % method,
		'',
		urllib.urlencode(args),
		''))

	f = urllib2.Request(url)
	try:
		f = urllib2.urlopen(f)
	except Exception, e:
		print >> sys.stderr, e.msg
		print >> sys.stderr, e.fp.read()
		raise

	return _parse_tree(f)

@memoify
def _do_checked_query(method, **kwargs):
	if not session_created:
		raise Exception("Login or create a session first (use connect())")

	if time.time() > session_expiry:
		# re-login if session has expired
		connect()

	kwargs["sessionKey"] = session_key

	return _do_napster_query(method, **kwargs)

def searchArtists(name):
	return _do_checked_query("search/artists", searchTerm=name)

def searchTracks(title):
	return _do_checked_query("search/tracks", searchTerm=title)

def getStreamData(artist, title):
	artists = searchArtists(artist)
	artistlist = []
	for artist in artists.get('artist', []):
		artistlist.append(artist['restArtistURL'][0])
	tracks = searchTracks(title)
	ret = []
	for t in tracks.get('track', []):
		artistUrl = t['artistResourceURL'][0]
		if artistUrl in artistlist:
			url = t['playTrackURL'][0]
			url += "?sessionKey="+session_key
			# Napster currently returns a http:// url but the https port, so change it.
			url = url.replace(":8443", ":8080")

			duration = t['duration'][0]
			durparts = duration.split(":")
			if len(durparts) == 2:
				length = int(durparts[0]) * 60 + int(durparts[1])
			else:
				length = -1

			ret.append({
				"url": url,
				"artist": t['artistName'][0],
				"track": t['trackName'][0],
				"album": t['albumName'][0],
				"duration": length })
	return ret

def test():
	import time
	start = time.time()
#	print "starting at", start
	connect()
	m = time.time()
#	print "Logged in after",m-start,"secs"
	print getStreamData(sys.argv[1], sys.argv[2])
	print getStreamData(sys.argv[1], sys.argv[2])
#	print "got results after",time.time()-m,"secs"

if __name__ == "__main__":
	test()
