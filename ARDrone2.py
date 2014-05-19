# -*- coding: utf-8 -*-
"""API for the Parrot ARDRone2

Some commands need a delay
"""
import threading
import time

from Debug import Debug
from ATCommand import ATCommand
from NavData import NavData
from Control import Control

class ARDrone2:
    COMMAND_DELAY = 0.03    # Critical for timing... adjust if necessary

    def __init__(self, address, debug):
        try:
            self._lock = threading.Lock()
            self._droneState = None
            self._address = address
            self._debug = debug
            self._running = False
            self._atCommand = ATCommand(self._address, self._debug)
            self._control = Control(self._address, self._debug)
            self._navData = NavData(self._address, self._DoNavData, self._debug)
        except Exception, e:
            # no cleanup code required
            debug.Print("[ARDrone2]: %s" % e)
            raise
        t = time.time()
        while(self._droneState == None):
            if(time.time()-t > 4.0):
                self.Stop()
                raise Exception("TIMEOUT")
            time.sleep(ARDrone2.COMMAND_DELAY)
        self._running = True
        self._tmonitor = threading.Thread(target=self._TMonitor, args=(), name="Monitor")
        self._tmonitor.start()

    def _Lock(self):
        self._lock.acquire()

    def _Unlock(self):
        self._lock.release()

    def _IsSet(self, mask):
        return (self._droneState & mask)!=0

    # from NavData
    def _DoNavData(self, navDataError, droneState):
        if(navDataError == 0):
            self._droneState = droneState
        else:
            self._debug.Print("[ARDrone2]: NavData Error - %s" % NavData.ERR_MESSAGE[navDataError])

    def _TMonitor(self):
        while(self._running):
            # prevents disconnection
            if(self._IsSet(NavData.COM_WATCHDOG_MASK)):
                try:
                    self._atCommand.WatchDog()
                except Exception, e:
                    # no cleanup code required
                    self._debug.Print("[ARDrone2]: TMonitor - %s" % e)

            # alerts
            if(self._IsSet(NavData.COMMAND_MASK)):
                self._debug.Print("[ARDrone2]: NavData Flag - ACK Received")
            if(self._IsSet(NavData.MOTORS_MASK)):
                self._debug.Print("[ARDrone2]: NavData Flag - Motors Problems!!!")
            if(self._IsSet(NavData.COM_LOST_MASK)):
                self._debug.Print("[ARDrone2]: NavData Flag - Communication Lost!!!")
            if(self._IsSet(NavData.SOFTWARE_FAULT)):
                self._debug.Print("[ARDrone2]: NavData Flag - Software Lost!!!")
            if(self._IsSet(NavData.VBAT_LOW)):
                self._debug.Print("[ARDrone2]: NavData Flag - Battery Low!!!")
            if(self._IsSet(NavData.MAGNETO_NEEDS_CALIB)):
                self._debug.Print("[ARDrone2]: NavData Flag - Needs Calibration!!!")
            if(self._IsSet(NavData.ANGLES_OUT_OF_RANGE)):
                self._debug.Print("[ARDrone2]: NavData Flag - Angles Out of Range!!!")
            if(self._IsSet(NavData.WIND_MASK)):
                self._debug.Print("[ARDrone2]: NavData Flag - Too Much Wind!!!")
            if(self._IsSet(NavData.ULTRASOUND_MASK)):
                self._debug.Print("[ARDrone2]: NavData Flag - Ultrasound Detector Deaf!!!")
            if(self._IsSet(NavData.EMERGENCY_MASK)):
                self._debug.Print("[ARDrone2]: NavData Flag - EMERGENCY!!!")

            time.sleep(ARDrone2.COMMAND_DELAY)

    def SetNavData(self):
        try:
            self._Lock()
            # command ACK must be Off
            while(self._IsSet(NavData.COMMAND_MASK)):
                self._atCommand.ClearCommandAck()
                time.sleep(ARDrone2.COMMAND_DELAY)
            # the command
            self._atCommand.SetNavData()
            # wait for ACK
            while(not self._IsSet(NavData.COMMAND_MASK)):
                time.sleep(ARDrone2.COMMAND_DELAY)
            # clear ACK
            while(self._IsSet(NavData.COMMAND_MASK)):
                self._atCommand.ClearCommandAck()
                time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: SetNavData - %s" % e)
            raise
        finally:
            self._Unlock()

    def FlatTrim(self):
        try:
            self._Lock()
            if(not self._IsSet(NavData.FLY_MASK)):
                self._atCommand.FlatTrim()
                time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: FlatTrim: %s" % e)
            raise
        finally:
            self._Unlock()

    def Calibrate(self):
        try:
            self._Lock()
            if(self._IsSet(NavData.FLY_MASK)):
                self._atCommand.Calibrate()
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: Calibrate: %s" % e)
            raise
        finally:
            self._Unlock()

    def TakeOff(self):
        try:
            self._Lock()
            while(not self._IsSet(NavData.FLY_MASK)):
                self._atCommand.TakeOff()
                time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: TakeOff: %s" % e)
            raise
        finally:
            self._Unlock()

    def Land(self):
        try:
            self._Lock()
            while(self._IsSet(NavData.FLY_MASK)):
                self._atCommand.Land()
                time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: Land: %s" % e)
            raise
        finally:
            self._Unlock()

    def Emergency(self):
        try:
            self._Lock()
            if(not self._IsSet(NavData.EMERGENCY_MASK)):
                self._atCommand.Emergency()
                time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: Emergency: %s" % e)
            raise
        finally:
            self._Unlock()

    def EmergencyReset(self):
        try:
            self._Lock()
            if(self._IsSet(NavData.EMERGENCY_MASK)):
                self._atCommand.Emergency()
                time.sleep(ARDrone2.COMMAND_DELAY)
                self._atCommand.Land()
                time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: EmergencyReset: %s" % e)
            raise
        finally:
            self._Unlock()

    def LedsAnim(self, anim, frecuency, duration):
        try:
            self._Lock()
            self._atCommand.LedsAnim(anim, frecuency, duration)
            time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: LedsAnim: %s" % e)
            raise
        finally:
            self._Unlock()

    def GetConfig(self):
        try:
            self._Lock()
            # command ACK must be Off
            while(self._IsSet(NavData.COMMAND_MASK)):
                self._atCommand.ClearCommandAck()
                time.sleep(ARDrone2.COMMAND_DELAY)
            # the command
            self._control.StartServer()
            time.sleep(ARDrone2.COMMAND_DELAY)
            self._atCommand.GetConfig()
            # wait for ACK
            while(not self._IsSet(NavData.COMMAND_MASK)):
                time.sleep(ARDrone2.COMMAND_DELAY)
            # clear ACK
            while(self._IsSet(NavData.COMMAND_MASK)):
                self._atCommand.ClearCommandAck()
                time.sleep(ARDrone2.COMMAND_DELAY)
            return self._control.GetAnswer()
        except Exception, e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: GetConfig: %s" % e)
            raise
        finally:
            self._Unlock()

    def Stop(self):
        self._navData.Stop()
        if(self._running):
            self._running = False
            self._tmonitor.join()

