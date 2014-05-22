# -*- coding: utf-8 -*-
import threading
import time

class Debug:
    """Class to debug in a thread safe way

    Use Lock/Unlock to print messages

    Usage:
        d = Debug()
        d.Print("Some message")
    """
    def __init__(self):
        """Constructor
        """
        self._lock = threading.Lock()

    def _Lock(self):
        """Acquire the lock
        """
        self._lock.acquire()

    def _Unlock(self):
        """Release the lock
        """
        self._lock.release()

    def Print(self, arg):
        """Print the argument

        Args:
            arg: text to print
        """
        self._Lock()
        print("%015.2f %s" % (time.time(), arg))
        self._Unlock()
