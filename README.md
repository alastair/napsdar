Playdar napster resolver
========================

Currently will probably only work during the Boston Music Hackday.

If you have a napster account, create a file that looks like this:

	$ cat ~/.playdar/napsdar
	[napsdar]
	username=foo
	password=bar
	apikey=napsterApiKey

If you don't create this file then you will only be able to play 30 
second streams.

To install, do something like this:

	$ cd ~/playdar-core/contrib
	$ ln -s ~/napsdar .

then edit etc/playdar.conf and add a section like this:

	{scripts,[
	"contrib/napsdar/napster_resolver.py"
	]}.
