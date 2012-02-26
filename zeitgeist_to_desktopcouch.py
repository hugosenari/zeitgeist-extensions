'''
Created on Feb 26, 2012

@author: hugosenari
'''
from couchdbsource import Consumer
from _zeitgeist.engine.extension import Extension

class DesktopCouchFeeder(Extension):
    def __init__(self, *args, **kws):
        Extension.__init__(self, *args, **kws)
        consumer = Consumer()
        consumer.monitor()
