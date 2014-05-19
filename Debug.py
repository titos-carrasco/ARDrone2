# -*- coding: utf-8 -*-
"""Thread safe debug class
"""
import threading
import time

class Debug:
    def __init__(self):
        self._lock = threading.Lock()

    def _Lock(self):
        self._lock.acquire()

    def _Unlock(self):
        self._lock.release()

    def Print(self, arg):
        self._Lock()
        print "%015.2f %s" % (time.time(), arg)
        self._Unlock()
