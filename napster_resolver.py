#!/usr/bin/env python

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
		return {
		    'name' : "Napster Resolver",
		    'weight' : 70,
		    'targettime' : 10000,
		    'localonly' : True
		}

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
		score = self.calculate_score(query, track)
		return {
				'artist': track["artist"],
				'track' : track["track"],
				'album' : track["album"],
				'mimetype' : "audio/mp4",
				'source' : "Napster",
				'url' : url,
				'duration' : track["duration"],
				'score' : score
		}

	def choose_playback_format(self, mimetypes):
		""" Choose what format to give the stream in.
		    TODO: Add AAC and FMS
		if "audio/x-ms-wma" in mimetypes:
			return "STREAM_128"
		if "audio/mp4" in mimetypes:
			return "HTTP_STREAM_MP4" """

		return "HTTP_STREAM_MP4"

	def calculate_score(self, query, track):
		artist_score = self.single_score(query.get("artist", "").lower(), track["artist"].lower())
		track_score = self.single_score(query.get("track", "").lower(), track["track"].lower())
		if query.get("album", "") == "":
			album_score = 1.0
		else:
			album_score = self.single_score(query.get("album", "").lower(), track["album"].lower())

		score = (artist_score + track_score + album_score) / 3.0
		return round(score, 2)

	def single_score(self, a, b):
		if a == b:
			return 1.0
		if playdar_resolver.soundex(a) == playdar_resolver.soundex(b):
			return 1.0
		m = self.percentage_match(a, b)
		return m

	def percentage_match(self, a, b):
		if a.find(b) > 0:
			return (len(b)*1.0)/(len(a)*1.0)
		elif b.find(a) > 0:
			return (len(a)*1.0)/(len(b)*1.0)
		else:
			return 0.0


if __name__ == "__main__":
	try:
		NapsterResolver.start_static()
	except:
		traceback.print_exc(file=sys.stderr)
