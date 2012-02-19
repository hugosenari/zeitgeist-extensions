# from src import common # For common functions used by journal
# from src import supporting_widgets to use the non view related widgets journal uses throughout
from pidginsource import PidginSource

__plugin_name__ = "Pidgin Plugin"
# Enter a detailed description here
__description__ = "Plugin message logger"

pidgin = None

def activate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by journal to handle event and content object request
    :param window: the activity journal primary window
    """
    pidgin = PidginSource()
    def event_sent(*args):
        pass
    pidgin.event_sent = event_sent
    print "Activate pidgin plugin"


def deactivate(client, store, window):
    """
    This function is called to activate the plugin.

    :param client: the zeitgeist client used by journal
    :param store: the date based store which is used by journal to handle event and content object request
    :param window: the activity journal primary window
    """
    del pidgin
    print "Deactivate pidgin plugin"
