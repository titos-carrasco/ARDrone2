# -*- coding: utf-8 -*-
"""API for the Parrot ARDRone2
"""
import threading
import time

from Debug import Debug
from ATCommand import ATCommand
from NavData import NavData
from Control import Control

class ARDrone2:
    COMMAND_DELAY = 0.03

    def __init__(self, address):
        try:
            self._droneState = None
            self._address = address
            self._debug = Debug()
            self._atCommand = ATCommand(self._address, self._debug)
            self._navData = NavData(self._address, self._DoNavData, self._debug)
            try:
                self._control = Control(self._address, self._DoControl, self._debug)
            except Exception, e:
                self._navData.Stop()
                self._debug.Print(e)
                raise
        except Exception, e:
            # no cleanup code required
            self._debug.Print(e)
            raise
        t = time.time()
        while(self._droneState == None):
            if(time.time()-t > 4.0):
                self.Stop()
                raise Exception("timeout")
            time.sleep(ARDrone2.COMMAND_DELAY)

    def _DoNavData(self, navdata_error, droneState):
        if(navdata_error == 0):
            self._droneState = droneState
            """
            if(self._IsSet(NavData.COMMAND_MASK)):
                print "ACK Received"
            if(self._IsSet(NavData.MOTORS_MASK)):
                print "Motors Problems!!!"
            if(self._IsSet(NavData.COM_LOST_MASK)):
                print "Communication Lost!!!"
            if(self._IsSet(NavData.SOFTWARE_FAULT)):
                print "Software Lost!!!"
            if(self._IsSet(NavData.VBAT_LOW)):
                print "Battery Low!!!"
            if(self._IsSet(NavData.MAGNETO_NEEDS_CALIB)):
                print "Needs Calibration!!!"
            if(self._IsSet(NavData.ANGLES_OUT_OF_RANGE)):
                print "Angles Out of Range!!!"
            if(self._IsSet(NavData.WIND_MASK)):
                print "Too Much Wind!!!"
            if(self._IsSet(NavData.ULTRASOUND_MASK)):
                print "Ultrasound Detector Deaf!!!"
            if(self._IsSet(NavData.EMERGENCY_MASK)):
                print "EMERGENCY!!!"
            """

            # prevents disconnection
            if((droneState & NavData.COM_WATCHDOG_MASK)!=0):
                self._atCommand.WatchDog()
        else:
            self._debug.Print("Error en NavData:", navdata_error)

    def _DoControl(data):
        self._debug.Print(data)

    def _IsSet(self, mask):
        return (self._droneState & mask)!=0

    def Stop(self):
        self._navData.Stop()
        self._control.Stop()

    def SetNavData(self):
        # command ack must be Off
        while(self._IsSet(NavData.COMMAND_MASK)):
            self._atCommand.ClearCommandAck()
            time.sleep(ARDrone2.COMMAND_DELAY)
        # the config command
        self._atCommand.SetNavData()
        # command ack must be On
        while(not self._IsSet(NavData.COMMAND_MASK)):
            time.sleep(ARDrone2.COMMAND_DELAY)
        # command ack must be Off
        while(self._IsSet(NavData.COMMAND_MASK)):
            self._atCommand.ClearCommandAck()
            time.sleep(ARDrone2.COMMAND_DELAY)

    def FlatTrim(self):
        if(not self._IsSet(NavData.FLY_MASK)):
            self._atCommand.FlatTrim()
            time.sleep(ARDrone2.COMMAND_DELAY)

    def Calibrate(self):
        if(self._IsSet(NavData.FLY_MASK)):
            self._atCommand.Calibrate()

    def TakeOff(self):
        while(not self._IsSet(NavData.FLY_MASK)):
            self._atCommand.TakeOff()
            time.sleep(ARDrone2.COMMAND_DELAY)

    def Land(self):
        while(self._IsSet(NavData.FLY_MASK)):
            self._atCommand.Land()
            time.sleep(ARDrone2.COMMAND_DELAY)

    def Emergency(self):
        if(not self._IsSet(NavData.EMERGENCY_MASK)):
            self._atCommand.Emergency()
            time.sleep(ARDrone2.COMMAND_DELAY)

    def EmergencyReset(self):
        self._atCommand.Emergency()
        time.sleep(ARDrone2.COMMAND_DELAY)
        self._atCommand.Land()
        time.sleep(ARDrone2.COMMAND_DELAY)

    def LedsAnim(self, anim, frecuency, duration):
        self._atCommand.LedsAnim(anim, frecuency, duration)
        time.sleep(ARDrone2.COMMAND_DELAY)

    def GetConfig(self):
        # command ack must be Off
        while(self._IsSet(NavData.COMMAND_MASK)):
            self._atCommand.ClearCommandAck()
            time.sleep(ARDrone2.COMMAND_DELAY)
        # the command
        self._atCommand.GetConfig()
        # command ack must be On
        while(not self._IsSet(NavData.COMMAND_MASK)):
            time.sleep(ARDrone2.COMMAND_DELAY)
        # command ack must be Off
        while(self._IsSet(NavData.COMMAND_MASK)):
            self._atCommand.ClearCommandAck()
            time.sleep(ARDrone2.COMMAND_DELAY)
