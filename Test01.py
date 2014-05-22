#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import cv2
import numpy as np

from ARDrone2.Debug import Debug
from ARDrone2.ARDrone2 import ARDrone2

def Canny(img):
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
    debug = Debug()
    drone=None
    try:
        drone = ARDrone2("192.168.1.1", debug, None, Canny)
    except Exception as e:
        debug.Print("[MainApp]: No connection to ARDrone2. May be Drone's hostname/address is wrong...")

    if(drone!=None):
        drone.SetNavData()
        #drone.Emergency()
        #time.sleep(2)
        drone.EmergencyReset()
        drone.FlatTrim()
        #debug.Print("[MainApp]\n%s" % drone.GetConfig())
        #drone.TakeOff()
        #time.sleep(3)
        #drone.Calibrate()
        #drone.LedsAnim(1, 10, 2)
        #time.sleep(2)
        drone.LedsAnim(2, 10, 2)
        time.sleep(2)
        drone.LedsAnim(1, 10, 2)
        time.sleep(4)
        drone.Land()
        time.sleep(5)
        drone.Stop()

    # running threads
    debug.Print("[MainApp]: %s " % threading.enumerate())

###
main()
