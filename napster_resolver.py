#!/usr/bin/python
# In your etc/playdar.conf scripts section, add "contrib/resolver_libs/example_respolver.py"
# to see this in action.
import playdar_resolver
import napster

class NapsterResolver(playdar_resolver.PlaydarResolver):
	def __init__(self):
		napster.createSession("SSHvRhrPsvDwVodGkPUw", "ap")
	def resolver_settings(self):
		return {'name':"Napster Resolver"}

	def results(self, query):
		data = napster.getStreamData(query['artist'], query['track'])
		if data is None:
			return []
		return [{
			'artist': data["artist"],
      'track' : data["track"],
      'album' : data["album"],
      'source' : "Napster",
      # NB this url should be url encoded properly:
      'url' : data["url"],
      'score' : 1.00
		}]
		
if __name__ == "__main__":
	try:
		NapsterResolver.start_static()
	except:
		traceback.print_exc(file=sys.stderr)
