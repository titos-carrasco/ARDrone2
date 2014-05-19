#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading

from Debug import Debug
from ARDrone2 import ARDrone2

debug = Debug()
drone=None
try:
    drone = ARDrone2("192.168.1.1", debug)
except Exception, e:
    debug.Print("[MainApp]: No connection to ARDrone2. May be Drone's hostname/address is wrong...")

if(drone!=None):
    drone.SetNavData()
    #drone.Emergency()
    #time.sleep(2)
    drone.EmergencyReset()
    drone.FlatTrim()
    print drone.GetConfig()
    #drone.TakeOff()
    #time.sleep(3)
    #drone.Calibrate()
    #drone.LedsAnim(1, 10, 2)
    #time.sleep(2)
    drone.LedsAnim(2, 10, 2)
    time.sleep(2)
    #drone.LedsAnim(1, 10, 2)
    #time.sleep(4)
    #drone.Land()
    drone.Stop()
    print threading.enumerate()
