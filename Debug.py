# -*- coding: utf-8 -*-
"""Thread safe debug class

Need improvements
"""
import threading

class Debug:
    def __init__(self):
        self._lock = threading.Lock()

    def Print(self, *args):
        self._lock.acquire()
        print args
        self._lock.release()
