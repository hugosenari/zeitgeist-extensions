'''
Gmusicbrowser Plugin

Plugin for Gmusicbrowser played logger
'''
import logging

from mpris2.interfaces import Interfaces
from mpris2.utils import SomePlayers
from mpris2source import Mpris2Source

__plugin_name__ = "Gmusicbrowser Plugin"
# Enter a detailed description here
__description__ = "Plugin for Gmusicbrowser played logger"

LOG_LEVEL = logging.DEBUG

def log(level, msg, *args, **kw):
    if level >= LOG_LEVEL:
        print Mpris2Source.__name__, msg % args, kw

def activate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by
        journal to handle event and content object request
    :param window: the activity journal primary window
    """
    window.GMB = Mpris2Source(
          #dbus_uri: org.mpris.MediaPlayer2.gmusicbrowser
          "%s.%s" % (Interfaces.MEDIA_PLAYER, SomePlayers.GMUSICBROWSER),
          #app uri for zeitgeist
          "application://gmusicbrowser.desktop",
          #app name
          "Gmusicbrowser",
          #app description
          "An open-source jukebox for large collections "
          "of mp3/ogg/flac/mpc/ape files, written in perl",
          log=log)
    log(logging.INFO, "Activate Gmusicbrowser plugin:")



def deactivate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by
        journal to handle event and content object request
    :param window: the activity journal primary window
    """
    del window.GMB
    log(logging.INFO, "Deactivate Gmusicbrowser plugin")
