# -*- coding: utf-8 -*-
import socket
import threading
import time

class Control:
    """Clase para recibir data de CONTROL desde la puerta 5559

    Uso:
        debug = Debug()
        control = Control("192.168.1.1", debug)
        ...
        ... enviar comando AT ...
        control.GetAnswer()
        ...
        control.Stop()

    """
    CONTROL_PORT = 5559

    def __init__(self, address, debug):
        """Constructor

        Args:
            address: dirección/hostname del drone
            debug: objeto de debug
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
        """Hilo para recibir la data desde el drone
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
            # no se requiere código de limpieza
            self._debug.Print("[TControl]: %s" % e)
        self._debug.Print("[TControl]: Abortando el hilo")

    def GetAnswer(self):
        """Obtiene la data de control del último comando AT

        Retorna:
            La data de control o '' en caso de error
        """
        # espera ocupada
        t = time.time()
        while(self._data == ''):
            if((time.time()-t)>3):
                self._debug.Print("[TControl]: No hay data de control desde el drone")
                break
            time.sleep(0.01)

        # la data
        data = self._data
        self._data = ''
        return data

    def Stop(self):
        """Detiene el hilo de control
        """
        self._running = False
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            # no se requiere código de limpieza
            self._debug.Print("[Control]: %s" % e)
        self._tcontrol.join()

