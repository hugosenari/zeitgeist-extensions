'''
Created on Feb 19, 2012

@author: hugosenari
'''
import re
import time
#pidgin dbus interface
import pidgin_purple_service as pidgin
#zeitgeist lib
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Interpretation, Manifestation, Subject

TAGS = re.compile("<\/?[^>]+>")
URIS = re.compile("[a-zA-Z1-9]+:\/\/[^\s\"<>]+")
HTTP = re.compile("^http.+")
FILE = re.compile("^file.+")

def storage_from_uri(uri):
    if FILE.match(uri):
        return 'local'
    return 'web'

def origin_from_uri(uri):
    parts = uri.split('://')
    return "%s://%s" % (parts[0], parts[1].split('/')[0])

class PidginSource(object):
    def __init__(self):
        """Constructor"""
        self._client = None
        self.account_path = None
        self.event_sent = lambda * e: e
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
        return TAGS.sub("", msg)

    def register_received_message(self, obj, ac_id, who, msg, *args, **kw):
        self.register_message_event(ac_id, who, msg, {
            'manifestation': Manifestation.EVENT_MANIFESTATION.WORLD_ACTIVITY,
            'interpretation': Interpretation.EVENT_INTERPRETATION.RECEIVE_EVENT
        })

    def register_sent_message(self, obj, ac_id, who, msg, *args, **kw):
        self.register_message_event(ac_id, who, msg, {
            'manifestation': Manifestation.EVENT_MANIFESTATION.USER_ACTIVITY,
            'interpretation': Interpretation.EVENT_INTERPRETATION.SEND_EVENT
        })

    def register_message_event(self, ac_id, who, msg, event_info):
        subject = Subject.new_for_values(
                uri="pidgin://%s/%s" % (ac_id, who),
                interpretation=unicode(Interpretation.IMMESSAGE),
                manifestation=unicode(Manifestation.SOFTWARE_SERVICE),
                origin="pidgin://%s" % (ac_id,),
                mimetype="text/plain",
                storage="local",
                text="%s" % (self._strip_tags(msg)))
        subjects = [subject]
        uris = URIS.findall(self._strip_tags(msg))
        for link in uris:
            if uris.count(link) == 1:
                subject = Subject.new_for_values(
                        uri=link,
                        interpretation=unicode(Interpretation.WEBSITE),
                        manifestation=unicode(#WEB if match http
                                              Manifestation.WEB_DATA_OBJECT  if HTTP.match(link)\
                                              #File if match file
                                              else Manifestation.FILE_DATA_OBJECT if FILE.match(link)\
                                              #something else
                                              else Manifestation.FILE_DATA_OBJECT.REMOTE_DATA_OBJECT
                                            ),
                        origin=origin_from_uri(link),
                        storage=storage_from_uri(link),
                        text=link)
                subjects.append(subject)
            else:
                uris.remove(link)
        event_info['subjects'] = subjects
        event_info['timestamp'] = int(time.time() * 1000)

        event_info['actor'] = 'application://pidgin.desktop'
        self.zclient.insert_event_for_values(**event_info)
        self.event_sent(ac_id, who, msg, event_info)

if __name__ == "__main__":
    from dbus.mainloop.glib import DBusGMainLoop
    import gobject
    import dbus
    DBusGMainLoop(set_as_default=True)
    mloop = gobject.MainLoop()
    pidginsource = PidginSource()
    def event_sent(ac_id, who, msg, event_info):
        print who, ', sayd: ', msg
    pidginsource.event_sent = event_sent
    mloop.run()
