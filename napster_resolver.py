#!/usr/bin/python

# Playdar Napster resolver
# Copyright 2009, 2010 Alastair Porter
# Released under the MIT License

import playdar_resolver
import napster
import sys
import traceback

class NapsterResolver(playdar_resolver.PlaydarResolver):
	def __init__(self):
		napster.connect()
	def resolver_settings(self):
		return {'name':"Napster Resolver"}

	def results(self, query):
		if "artist" not in query or "track" not in query:
			return []
		data = napster.getStreamData(query["artist"], query.get("album", ""), query["track"])
		if data is None:
			return []

		res = []
		for track in data:
			res.append(self.make_track_result(track, query))
		return res	
		
	def make_track_result(self, track, query):
		playformat = self.choose_playback_format(query.get("mimetypes", []))
		url = "%s&mediaType=%s" % (track["url"], playformat)
		return {
				'artist': track["artist"],
				'track' : track["track"],
				'album' : track["album"],
				'source' : "Napster",
				'url' : url,
				'duration' : track["duration"],
				'score' : 1.00
		}

	def choose_playback_format(self, mimetypes):
		""" Choose what format to give the stream in.
		    TODO: Add AAC and FMS """
		if "audio/x-ms-wma" in mimetypes:
			return "STREAM_128"

		return "HTTP_STREAM_128_MP3"

if __name__ == "__main__":
	try:
		NapsterResolver.start_static()
	except:
		traceback.print_exc(file=sys.stderr)
