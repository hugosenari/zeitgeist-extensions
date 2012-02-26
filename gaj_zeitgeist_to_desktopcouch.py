'''
Created on Feb 26, 2012

@author: hugosenari
'''
import logging
from couchdbsource import Consumer

__plugin_name__ = "Zeitgeist to Desktopcouch"
# Enter a detailed description here
__description__ = "Push events from zeitgeist to destktopcouch"
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
    window.ZGDESCKTOPCOUCH = consumer = Consumer(log=log)
    consumer.monitor()
    log(logging.INFO, "Activate Zeitgeist to Desktopcouch plugin:")



def deactivate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by
        journal to handle event and content object request
    :param window: the activity journal primary window
    """
    del window.ZGDESCKTOPCOUCH
    log(logging.INFO, "Deactivate Zeitgeist to Desktopcouch plugin:")
