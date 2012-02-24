#! /usr/bin/env python
from zeitgeist.client import ZeitgeistDBusInterface
from zeitgeist.datamodel import Event, Interpretation, TimeRange, \
 StorageState, ResultType
from datetime import datetime
import dateutil

zg = ZeitgeistDBusInterface()
events = zg.FindEvents(
    #timerange
    TimeRange.always(),
    #Evente template
    [Event.new_for_values(
           interpretation=\
           Interpretation.EVENT_INTERPRETATION.LEAVE_EVENT)],
    #Storage State
    StorageState.Any,
    #How many results
    10,
    #Result sort
    ResultType.MostRecentEvents)

for event in events:
    last_event = Event(event)
    last_subject = last_event.get_subjects()[0]
    print last_subject.uri, datetime.fromtimestamp(float(last_event.timestamp) / 1000)

