# -*- coding: utf-8 -*-
import socket
import threading
import time

class Control:
    """Class to receive CONTROL data from port 5559

    Usage:
        debug = Debug()
        control = Control("192.168.1.1", debug)
        ...
        ... send AT Command ...
        control.GetAnswer()
        ...
        control.Stop()

    """
    CONTROL_PORT = 5559

    def __init__(self, address, debug):
        """Constructor

        Args:
            adress: Drone's address/hostname
            debug: Debug object
        """
        self._address = address
        self._debug = debug
        self._data = ''
        self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._socket.settimeout(None)
        self._running = False
        self._tcontrol = threading.Thread(target=self._TControl, args=(), name="TControl")
        self._tcontrol.start()
        while(not self._running):
            time.sleep(0.01)

    def _TControl(self, *args):
        """Thread to receive the data from the drone
        """
        self._running = True
        try:
            data = ''
            self._socket.connect((self._address, Control.CONTROL_PORT))
            while(True):
                c = self._socket.recv(1)
                if(not c):
                    raise socket.error
                if(ord(c) == 0):
                    self._data = data
                    data = ''
                else:
                    data = data + c
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[TControl]: %s" % e)
        self._debug.Print("[TControl]: Aborting the thread")

    def GetAnswer(self):
        """ Get the control data from the last AT command

        Returns:
            The control data or '' if error
        """
        # busy wait
        t = time.time()
        while(self._data == ''):
            if((time.time()-t)>3):
                self._debug.Print("[TControl]: No Control data from drone")
                break
            time.sleep(0.01)

        # the data
        data = self._data
        self._data = ''
        return data

    def Stop(self):
        """Stop the Control thread
        """
        self._running = False
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[Control]: %s" % e)
        self._tcontrol.join()

