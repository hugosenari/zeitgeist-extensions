'''
Created on Feb 24, 2012

@author: hugosenari
'''
#mpris2source
from mpris2source import Mpris2Source
from mpris2.interfaces import Interfaces
from mpris2.some_players import Some_Players
#zeitgeist
from _zeitgeist.engine.extension import Extension

class gmusicbrowser(Extension, Mpris2Source):
    def __init__(self, engine):
        Extension.__init__(self, engine)
        PidginSource()
        Mpris2Source(
              #dbus_uri: org.mpris.MediaPlayer2.gmusicbrowser
              "%s.%s" % (Interfaces.MEDIA_PLAYER, SomePlayers.GMUSICBROWSER),
              #app uri for zeitgeist
              "application://gmusicbrowser.desktop",
              #app name
              "Gmusicbrowser",
              #app description
              "An open-source jukebox for large collections "
              "of mp3/ogg/flac/mpc/ape files, written in perl")
