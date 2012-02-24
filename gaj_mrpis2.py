import logging, gobject

from mpris2.utils import SomePlayers
from mpris2source import Mpris2Sources

__plugin_name__ = "Mpris2 Plugin"
# Enter a detailed description here
__description__ = "Plugin for Mpris2 players logger"


TIME_FOR_RESCAN = 10 #in seconds
LOG_LEVEL = logging.DEBUG

def log(level, msg, *args, **kw):
    if level >= LOG_LEVEL:
        print Mpris2Sources.__name__, msg % args, kw

def activate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by
        journal to handle event and content object request
    :param window: the activity journal primary window
    """
    mpris2sources = Mpris2Sources(log=log)
    def rescan():
        mpris2sources.rescan()
        gobject.timeout_add_seconds(TIME_FOR_RESCAN, rescan)

    rescan()
    window.MPRIS2PLUGIN = mpris2sources

    log(logging.INFO, "Activate Mpris2 plugin:")



def deactivate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by
        journal to handle event and content object request
    :param window: the activity journal primary window
    """
    del window.MPRIS2PLUGIN
    log(logging.INFO, "Deactivate Mpris2 plugin")

