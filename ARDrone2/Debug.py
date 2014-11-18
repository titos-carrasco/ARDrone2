# -*- coding: utf-8 -*-
import threading
import time

class Debug:
    """Clase para depurar de manera thread safe

    Utiliza Lock/Unlock para imprimir los mensajes

    Uso:
        d = Debug()
        d.Print("Mensaje...")
    """
    def __init__(self):
        """Constructor
        """
        self._lock = threading.Lock()

    def _Lock(self):
        """Adquiere el lock
        """
        self._lock.acquire()

    def _Unlock(self):
        """Libera el lock
        """
        self._lock.release()

    def Print(self, arg):
        """Imprime el argumento

        Args:
            arg: texto a imprimir
        """
        self._Lock()
        try:
            print(("%015.2f %s" % (time.time(), arg)).decode("utf-8"))
        except:
            print("%015.2f %s" % (time.time(), arg))
        self._Unlock()
