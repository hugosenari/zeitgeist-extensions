'''
Created on Feb 19, 2012

@author: hugosenari
'''
import gobject, logging
#couchdb lib
from desktopcouch.records.server import DesktopDatabase
from desktopcouch.records.record import Record as CouchRecord
from couchdb.http import ResourceNotFound

#zeitgeist lib
from zeitgeist.client import ZeitgeistClient, ZeitgeistDBusInterface
from zeitgeist.datamodel import Event, Interpretation, Manifestation, Subject, \
 TimeRange, ResultType, StorageState

class _constant(object):
    def __init__(self):
        self._d = {}

    def __getattribute__(self, attr, *args, **kwargs):
        if attr is '_d':
            return super(_constant, self).__getattribute__(attr, *args, **kwargs)
        if not self._d.has_key(attr):
            self._d[attr] = None
        return self._d.get(attr)

    def __setattr__(self, attr, val, *args, **kwargs):
        if attr is '_d':
            super(_constant, self).__setattr__(attr, val, *args, **kwargs)
        else:
            self._d[attr] = val

def log(*args, **kw):
    logging.getLogger('couchdbsource').log(*args, **kw)

DATABASE_NAME = "zeitgeist"

COUCH_OBJ_TYPE = "https://github.com/hugosenari/zeitgeist-extensions/wiki/ZeitgeistEvent"
COUCH_CFG_TYPE = "https://github.com/hugosenari/zeitgeist-extensions/wiki/zgcfg"

VIEW = _constant()
VIEW.DEFAULT = _constant()
VIEW.DEFAULT.name = "bytimestamp_and_id"
VIEW.DEFAULT.view = '''function(doc) {
    if (doc.record_type == '%s')
        emit([doc.timestamp, doc.id], doc);
}''' % COUCH_OBJ_TYPE

VIEW.ID = _constant()
VIEW.ID.name = "byid"
VIEW.ID.view = '''function(doc) {
    if (doc.record_type == '%s')
        emit(doc.id, doc);
}''' % COUCH_OBJ_TYPE

VIEW.TIMESTAMP = _constant()
VIEW.TIMESTAMP.name = "bytimestamp"
VIEW.TIMESTAMP.view = '''function(doc) {
    if (doc.record_type == '%s')
        emit(doc.timestamp, doc);
}''' % COUCH_OBJ_TYPE

VIEW.CFG = _constant()
VIEW.CFG.name = "withzgcfg"
VIEW.CFG.view = ''''function(doc) {
    if (doc.record_type == '%s')
        emit(doc._id, doc);
}''' % COUCH_CFG_TYPE

class _CouchdbCommon(object):

    def __init__(self, log=log):
        self.log = log
        self._zclient = ZeitgeistClient()
        self._zdclient = ZeitgeistDBusInterface()
        self._database = DesktopDatabase(DATABASE_NAME, create=True)
        #create views
        self._add_view(VIEW.DEFAULT)
        self._add_view(VIEW.ID)
        self._add_view(VIEW.TIMESTAMP)
        self._add_view(VIEW.CFG)
        #get configs

    def _add_view(self, view):
        #create views if not exist
        if not self._database.view_exists(view.name, DATABASE_NAME):
            self.log(logging.DEBUG, """adding in %s view %s with: %s""", DATABASE_NAME, view.name, view.view)
            self._database.add_view(view.name, view.view, None, DATABASE_NAME)
            self._database.execute_view(view.name)
        else:
            self.log(logging.DEBUG, """view %s exist in %s with""", view.name, DATABASE_NAME)


    def last_transaction(self, when=None):
        '''
            Getter or Setter for last_transaction
            event: dict, last sync item
            return dict 
        '''
        if when:
            self.save_config("last_transaction", when)
        else:
            when = self.config("last_transaction")
            if not when:
                self._database.execute_view(VIEW.TIMESTAMP.name)
        return when

    def save_config(self, attr, val):
        self.log(logging.DEBUG, "setting value %s for %s", attr, val)
        if self._database.record_exists(attr):
            record = self._database.get_record(attr)
            self._database.update_fields(attr, {'value': val})
        else:
            record = CouchRecord({'value': val}, COUCH_CFG_TYPE, attr)
            self.put_record(record)


    def config(self, attr):
        self.log(logging.DEBUG, "getting info: %s", attr)
        if self._database.record_exists(attr):
            cfg = self._database.get_record(attr)
            self.log(logging.DEBUG, "value of info %s is %s", attr, cfg['value'])
            return cfg['value']
        self.log(logging.DEBUG, "can't get config %s", attr)

    def dbToZg(self, obj):
        '''
            Convert courchrecord in zeiteist event
        '''
        return Event.new_for_values(**obj)

    def zgToDb(self, obj):
        '''
            Convert zeitgeist event in couchrecord
        '''
        result = {}
        if obj.get_actor(): result['actor'] = obj.get_actor()
        if obj.get_id(): result['id'] = int(obj.get_id())
        if obj.get_interpretation(): result['interpretation'] = obj.get_interpretation()
        if obj.get_manifestation(): result['manifestation'] = obj.get_manifestation()
        if obj.get_origin(): result['origin'] = obj.get_origin()
        if obj.get_payload(): result['payload'] = obj.get_payload()
        if obj.get_timestamp(): result['timestamp'] = int(obj.get_timestamp())
        result['subjects'] = []
        for subject in obj.get_subjects():
            sub = {}
            if subject.get_interpretation(): sub['interpretation'] = subject.get_interpretation()
            if subject.get_manifestation(): sub['manifestation'] = subject.get_manifestation()
            if subject.get_mimetype(): sub['mimetype'] = subject.get_mimetype()
            if subject.get_origin(): sub['origin'] = subject.get_origin()
            if subject.get_storage(): sub['storage'] = subject.get_storage()
            if subject.get_text(): sub['text'] = subject.get_text()
            if subject.get_uri(): sub['uri'] = subject.get_uri()
            result['subjects'].append(sub)
        return CouchRecord(result, COUCH_OBJ_TYPE)

    def put_record(self, record):
        self._database.put_record(record)

    def put_records(self, records):
        self._database.put_records_batch(records)


class Source(_CouchdbCommon):
    '''
    This class transport couchdb events to Zeitgeist
    '''

class Consumer(_CouchdbCommon):
    '''
    This class transport zeitgeist events to CouchDB
    '''
    def __init__(self, *args, **kw):
        _CouchdbCommon.__init__(self, *args, **kw)


    def transport(self):
        '''
        Update couchdb with events
        '''
        events = []
        last = self.last_transaction()
        #get events
        if (last):
            self.log(logging.INFO, "getting itens created after %s", last)
            #update of database
            #count
            from_last_to_now = TimeRange.until_now()
            from_last_to_now.begin = int(last) + 1
            events = self._zdclient.FindEvents(
                #timerange
                from_last_to_now,
                [],
                StorageState.Any,
                0,
                ResultType.LeastRecentEvents
            )
        else:
            self.log(logging.INFO, "First interaction, getting last item")
            #fist interaction with database
            events = self._zdclient.FindEvents(
                #timerange
                TimeRange.always(),
                [],
                StorageState.Any,
                1,
                ResultType.MostRecentEvents
            )
        #convert into records
        records = []
        [records.append(self.zgToDb(Event(event)))\
            for event in events]
        #put on couchdb
        self.log(logging.INFO, "put %s records in couchdb", len(records))
        self.put_records(records)
        #save last as last_transaction
        if len(records): self.last_transaction(records[-1]['timestamp'])


if "__main__" == __name__:
    from dbus.mainloop.glib import DBusGMainLoop
    import gobject

    DBusGMainLoop(set_as_default=True)
    mloop = gobject.MainLoop()
    logging.basicConfig(level=logging.INFO)

    consumer = Consumer()
    def transport():
        consumer.transport()
        gobject.timeout_add_seconds(14, transport)

    transport()

    mloop.run()
