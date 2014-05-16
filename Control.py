# -*- coding: utf-8 -*-
"""
"""
import socket
import threading
import time

class Control:
    CONTROL_PORT = 5559

    def __init__(self, address, callback, debug):
        try:
            self._address = address
            self._callback = callback
            self._debug = debug
            self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self._socket.bind(('', Control.CONTROL_PORT))
            self._socket.listen(5)
            self._socket.setblocking(1)
            #self._socket.settimeout(0)
        except Exception, e:
            raise
        self._running = True
        self._tcontrol = threading.Thread(target=self._TControl, args=(), name="Control")
        self._tcontrol.start()

    def _TControl(self, *args):
        while(self._running):
            conn = None
            try:
                (conn, address) = self._socket.accept()
                data = ''
                while(True):
                    d = conn.recv(4096)
                    if(not d):
                        break;
                    data = data + d
                self._control(data)
            except Exception, e:
                pass
            if(conn != None):
                conn.close()

    def Stop(self):
        if(self._running):
            self._running = False
            self._socket.shutdown(2)
            self._socket.close()
            self._tcontrol.join()
