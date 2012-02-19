# from src import common # For common functions used by journal
# from src import supporting_widgets to use the non view related widgets journal uses throughout
from mpris2.interfaces import Interfaces
from mpris2.utils import SomePlayers
from mpris2source import Mpris2Source

__plugin_name__ = "Gmusicbrowser Plugin"
# Enter a detailed description here
__description__ = "Plugin for Gmusicbrowser played logger"

gmb = None

def activate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by journal to handle event and content object request
    :param window: the activity journal primary window
    """
    gmb = Mpris2Source.__init__(self,
                          "%s.%s" % (Interfaces.PLAYER, SomePlayers.GMUSICBROWSER), #dbus_uri: org.freedesktop.mpris2.gmusicbrowser
                          "application://gmusicbrowser.desktop", #app uri for zeitgeist
                          "Gmusicbrowser", #app name
                          "An open-source jukebox for large collections of mp3/ogg/flac/mpc/ape files, written in perl") #app description
    print "Activate Gmusicbrowser plugin"


def deactivate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by journal to handle event and content object request
    :param window: the activity journal primary window
    """
    del gmb
    print "Deactivate Gmusicbrowser plugin"
