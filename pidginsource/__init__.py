'''
Created on Feb 19, 2012

@author: hugosenari
'''
import re
import time
#pidgin dbus interface
import pidgin
#zeitgeist lib
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Interpretation, Manifestation, Subject

class PidginSource(object):
    def __init__(self):
        """Constructor"""
        self._client = None
        self.tags = re.compile("<\/?[^>]+>")
        self.uris = re.compile("[a-zA-Z1-9]+:\/\/[^\s\"<>]+")
        self.account_path = None
        self.event_sent = lambda s, e: e
        self.pigeon = pidgin.PurpleInterface()
        self.pigeon.SentChatMsg = self.register_sent_message
        self.pigeon.SentImMsg = self.register_sent_message
        self.pigeon.ReceivedChatMsg = self.register_received_message
        self.pigeon.ReceivedImMsg = self.register_received_message

    @property
    def zclient(self,
                    bus_name='im.pidgin.purple.PurpleInterface',
                    app_uri='application://pidgin.desktop',
                    app_name='Pidgin',
                    app_description="Pidgin is an easy to use and free chat client used by millions. Connect to AIM, MSN, Yahoo, and more chat networks all at once.",
                    event_template=None):

        if self._client:
            return self._client

        try:
            self._client = ZeitgeistClient()
            if hasattr(self._client, "register_data_source"):
                self.client.register_data_source(
                    bus_name,
                    app_name or bus_name,
                    app_description or bus_name,
                    event_template or \
                    [Event.new_for_values(actor=app_uri)])
        except:
            pass

        return self._client

    def _strip_tags(self, msg):
        return self.tags.sub("", msg)

    def register_received_message(self, obj, ac_id, who, msg, *args, **kw):
        self.account_path = "%s/%s" % (ac_id, who)
        self.register_message_event(ac_id, who, msg, {
            'manifestation': Manifestation.EVENT_MANIFESTATION.USER_ACTIVITY,
            'interpretation': Interpretation.EVENT_INTERPRETATION.RECEIVE_EVENT
        })

    def register_sent_message(self, obj, ac_id, who, msg, *args, **kw):
        self.account_path = "%s/%s" % (ac_id, who)
        self.register_message_event(ac_id, who, msg, {
            'manifestation': Manifestation.EVENT_MANIFESTATION.WORLD_ACTIVITY,
            'interpretation': Interpretation.EVENT_INTERPRETATION.SEND_EVENT
        })

    def register_message_event(self, ac_id, who, msg, event_info):
        subject = Subject.new_for_values(
                interpretation=unicode(Interpretation.IMMESSAGE),
                manifestation=unicode(Manifestation.SOFTWARE_SERVICE),
                origin=self.account_path,
                mimetype="text/plain",
                text="%s: %s" % (who, self._strip_tags(msg)))
        subjects = [subject]
        for link in self.uris.findall(msg):
            subject = Subject.new_for_values(
                    uri=link,
                    interpretation=unicode(Interpretation.WEBSITE),
                    manifestation=unicode(Manifestation.FILE_DATA_OBJECT.REMOTE_DATA_OBJECT),
                    origin=self.account_path,
                    mimetype="text/html",
                    text=link)
            subjects.append(subject)
        event_info['subjects'] = subjects

        event_info['actor'] = 'application://pidgin.desktop'
        self.zclient.insert_event_for_values(**event_info)
        self.event_sent(event_info)

if __name__ == "__main__":
    from dbus.mainloop.glib import DBusGMainLoop
    import gobject
    import dbus
    DBusGMainLoop(set_as_default=True)
    mloop = gobject.MainLoop()
    pidginsource = PidginSource()
    def event_sent(*args):
        print args
    pidginsource.event_sent = event_sent
    mloop.run()
