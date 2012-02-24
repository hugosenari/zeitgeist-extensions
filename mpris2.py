'''
Created on Feb 24, 2012

@author: hugosenari
'''
import gobject
#mpris2source
from mpris2source import Mpris2Sources
#zeitgeist
from _zeitgeist.engine.extension import Extension

class gmusicbrowser(Extension):
    def __init__(self, engine):
        Extension.__init__(self, engine)

        mpris2sources = Mpris2Sources()

        def rescan():
            mpris2sources.rescan()
            gobject.timeout_add_seconds(TIME_FOR_RESCAN, rescan)

        rescan()
