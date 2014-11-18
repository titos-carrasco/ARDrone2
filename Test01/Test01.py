#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
import time
import cv2
import numpy as np

from VJoy import VJoy

sys.path.append('../ARDrone2')
from ARDrone2 import ARDrone2
from Debug import Debug


class MyApp:
    """Clase base para construir programas que manipulen el drone
    """
    def __init__(self):
        pass

    def Run(self):
        debug = Debug()
        vj = VJoy(0, debug)

        # nos conectamos al ARDrone2 especificando los callback
        try:
            drone = ARDrone2("192.168.1.1", debug, None, self.VideoFilter)
        except Exception as e:
            debug.Print("[MainApp]: No hay conexión al ARDrone. Quizás la dirección/hostname es incorrecta...")
            return

        # lo ponemos en modo navdata
        drone.SetNavData()

        # interactuamos con el drone
        while(True):
            try:
                (cmd, move) = vj.GetCommand()
                if(cmd==vj.EXIT):
                    break
                elif(cmd==vj.EMERGENCY):
                    drone.Emergency()
                elif(cmd==vj.TAKE_OFF):
                    drone.TakeOff()
                elif(cmd==vj.LAND):
                    drone.Land()
                elif(cmd==vj.FLAT_TRIM):
                    drone.FlatTrim()
                elif(cmd==vj.CALIBRATE):
                    drone.Calibrate()

                factor = 0.3
                flyRoll = move.roll * 0.3
                flyPitch = move.pitch * 0.3
                flyYaw = move.yaw * 1.0
                flyGaz = move.gaz * 1.0
                if(flyRoll==0 and flyPitch==0 and flyYaw==0 and flyGaz==0):
                    #print("drone.Hover()")
                    drone.Hover()
                else:
                    #print("drone.Move(%f, %f, %f, %f)" % (flyRoll, flyPitch, flyGaz, flyYaw))
                    drone.Move(flyRoll, flyPitch, flyGaz, flyYaw)

                time.sleep(0.01)
            except Exception as e:
                debug.Print("[MainApp]: %s" % e)
                break

        debug.Print("[MainApp]: Se presionó botón de Salida...")
        drone.Land()
        time.sleep(5)
        drone.Stop()

        """
        self._drone.EmergencyReset()
        #debug.Print("[MainApp]\n%s" % drone.GetConfig())
        #drone.LedsAnim(1, 10, 2)
        drone.LedsAnim(2, 10, 2)
        drone.LedsAnim(1, 10, 2)
       """

        # no deberiamos tener hilos en ejecución, revisar lo desplegado...
        debug.Print("[MainApp]: %s " % threading.enumerate())

    # procesamos la data de navegación
    def NavData(self, droneState, options):
        pass

    # filtramos el video cuadro a cuadro aplicando Canny para la detección de bordes
    def VideoFilter(self, img):
        imgH, imgW, depth = img.shape
        frame = img.copy()

        # la mitad derecha
        mitad = img[:,imgW/2:]

        # necesario
        gray = cv2.cvtColor(mitad, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # bordes
        canny = cv2.Canny(blur, 5, 128)

        # final
        final = cv2.GaussianBlur(canny, (3,3), 0)

        # reemplazamos la mitad procesada
        frame[:,imgW/2:]=cv2.cvtColor(~final, cv2.COLOR_GRAY2BGR)
        return frame


def main():
    """main() para la aplicación."""
    app = MyApp()
    app.Run()

if __name__ == "__main__":
    main()
