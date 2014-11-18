#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
import time

sys.path.append('../ARDrone2')
from ARDrone2 import ARDrone2
from Debug import Debug


class MyApp:
    """Clase base sin manipulación de video no contro de joystick
    """
    def __init__(self):
        pass

    def Run(self):
        debug = Debug()

        # nos conectamos al ARDrone2 especificando los callback
        try:
            drone = ARDrone2("192.168.1.1", debug, None, None)
        except Exception as e:
            debug.Print("[MainApp]: No hay conexión al ARDrone. Quizás la dirección/hostname es incorrecta...")
            return

        # lo ponemos en modo navdata
        drone.SetNavData()

        # eliminamos cualquier condición de emergencia
        drone.EmergencyReset()

        # despegamos
        drone.TakeOff()
        time.sleep(3)

        # lo elevamos a una altura razonable
        t = time() + 3
        while(time() < t):
            drone.Move(0, 0, 0.3, 0)

        # un efecto de luces estando suspendido sin movimiento
        drone.LedsAnim(2, 10, 4)
        t = time() + 4
        while(time() < t):
            drone.Hover()

        # lo rotamos en su eje
        t = time() + 3
        while(time() < t):
            drone.Move(0, 0, 0, 1)

        # finalizamos el procesamiento
        drone.Land()
        time.sleep(5)
        drone.Stop()

        # no deberiamos tener hilos en ejecución, revisar lo desplegado...
        debug.Print("[MainApp]: %s " % threading.enumerate())


def main():
    """main() para la aplicación."""
    app = MyApp()
    app.Run()

if __name__ == "__main__":
    main()

