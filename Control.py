# -*- coding: utf-8 -*-
"""Receive CONTROL data from the ARDrone2
"""
import socket
import threading
import time

class Control:
    CONTROL_PORT = 5559

    def __init__(self, address, debug):
        try:
            self._address = address
            self._debug = debug
            self._data = ''
            self._tcontrol = None
            self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self._socket.settimeout(2.0)
        except Exception, e:
            # no cleanup code required
            debug.Print("[Control]: %s" % e)
            raise

    def _TControl(self, *args):
        data = ''
        try:
            self._socket.connect((self._address, Control.CONTROL_PORT))
            while(True):
                d = self._socket.recv(64)
                if(not d):
                    break
                data = data + d
        except Exception, e:
            self._debug.Print("[TControl]: %s" % e)
        self._data = data

    def StartServer(self):
        self._data = ''
        self._tcontrol = threading.Thread(target=self._TControl, args=(), name="Control")
        self._tcontrol.start()

    def GetAnswer(self):
        if(self._tcontrol != None):
            self._tcontrol.join()
            self._tcontrol = None
        return self._data
