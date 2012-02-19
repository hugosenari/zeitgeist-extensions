'''
Created on Feb 19, 2012

@author: hugosenari
'''
from pidginsource import PidginSource
from _zeitgeist.engine.extension import Extension

class pidgin(Extension, PidginSource):
    def __init__(self, engine):
        Extension.__init__(self, engine)
        PidginSource()
