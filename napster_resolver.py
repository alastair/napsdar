#!/usr/bin/python
# In your etc/playdar.conf scripts section, add "contrib/resolver_libs/example_respolver.py"
# to see this in action.
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
		data = napster.getStreamData(query['artist'], query['track'])
		if data is None:
			return []

		res = []
		for track in data:
			res.append({
				'artist': track["artist"],
				'track' : track["track"],
				'album' : track["album"],
				'source' : "Napster",
				'url' : track["url"],
				'duration' : track["duration"],
				'score' : 1.00
					})
		return res	
		
if __name__ == "__main__":
	try:
		NapsterResolver.start_static()
	except:
		traceback.print_exc(file=sys.stderr)
