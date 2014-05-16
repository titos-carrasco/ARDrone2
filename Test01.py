#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading

from ARDrone2 import ARDrone2

drone=None
try:
    drone = ARDrone2("192.168.1.1")
except Exception, e:
    print "Init Error. May be Drone's hostname/address is wrong..."

if(drone!=None):
    drone.SetNavData()
    #drone.Emergency()
    #time.sleep(2)
    #drone.EmergencyReset()
    drone.FlatTrim()
    drone.GetConfig()
    #drone.TakeOff()
    #time.sleep(5)
    #drone.Calibrate()
    #drone.Land()
    drone.LedsAnim(1, 10, 2)
    time.sleep(2)
    drone.LedsAnim(2, 10, 2)
    time.sleep(2)
    drone.LedsAnim(3, 10, 2)
    time.sleep(2)
    drone.LedsAnim(4, 10, 2)
    time.sleep(2)
    print "Saliendo..."
    drone.Stop()
    print threading.enumerate()
