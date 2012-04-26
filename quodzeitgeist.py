'''
Created on Apr 26, 2012

@author: hugosenari
'''
#mpris2source
from mpris2source import Mpris2Source
from mpris2.interfaces import Interfaces
from mpris2.some_players import Some_Players
#quodlibet
from quodlibet.plugins.events import EventPlugin

#common
import logging

LOG_LEVEL = logging.DEBUG
def log(level, msg, *args, **kw):
    if level >= LOG_LEVEL:
        print Mpris2Source.__name__, msg % args, kw


class Zeitgeist(EventPlugin):
    PLUGIN_ID = "Zeigeist"
    PLUGIN_NAME = _("Zeitgeist")
    PLUGIN_DESC = "Zeitgeist dataprovider for Quodlibet (require mpris2 plugin)"
    PLUGIN_VERSION = "0.1"

    def enabled(self):
        Mpris2Source(
              #dbus_uri: org.mpris.MediaPlayer2.quodlibet
              "%s.%s" % (Interfaces.MEDIA_PLAYER, Some_Players.QUODLIBET),
              #app uri for zeitgeist
              "application://quodlibet.desktop",
              #app name
              "Quodlibet",
              #app description
              "audio library tagger, manager, and player for GTK+",
              log=log)

