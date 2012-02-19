"""
Zeitgeist extension to register gmusicbrowser music playing information.
To be honest it is a zeitgeist dataprovider, but I made it as extension because I had problems with perl dbus lib
(https://rt.cpan.org/Public/Bug/Display.html?id=73313).


Thanks to: http://milky.manishsinha.net/2010/11/27/zeitgeist-daemon-extensions-explained/
Require:
https://github.com/hugosenari/mpris2 and https://github.com/hugosenari/pydbusdecorator

Install it with mpris2source.py at:
$HOME/.local/share/zeitgeist/extensions/
"""

from mpris2.interfaces import Interfaces
from mpris2.utils import SomePlayers
from mpris2source import Mpris2Source
from _zeitgeist.engine.extension import Extension

class gmusicbrowser(Extension, Mpris2Source):
	def __init__(self, engine):
		"""Constructor"""
		Extension.__init__(self, engine)
        Mpris2Source.__init__(self,
                                      "%s.%s" % (Interfaces.PLAYER, SomePlayers.GMUSICBROWSER), #dbus_uri: org.freedesktop.mpris2.gmusicbrowser
                                      "application://gmusicbrowser.desktop", #app uri for zeitgeist
                                      "Gmusicbrowser", #app name
                                      "An open-source jukebox for large collections of mp3/ogg/flac/mpc/ape files, written in perl") #app description
