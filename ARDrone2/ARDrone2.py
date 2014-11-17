# -*- coding: utf-8 -*-
import threading
import time

from ATCommand import ATCommand
from NavData import NavData
from Control import Control
from Video import Video

class ARDrone2:
    """API for the Parrot ARDRone2

    Usage:
        debug = Debug()
        drone = ARDrone2("192.168.1.1", debug)
        drone.methods()
        ...
        drone.Stop()
    """
    COMMAND_DELAY = 0.01    # Critical for timing... adjust if necessary

    def __init__(self, address, debug, navdataCallback=None, videoCallback=None):
        """Constructor

        Args:
            adress: Drone's address/hostname
            debug: Debug object
        """
        self._lock = threading.Lock()
        self._address = address
        self._debug = debug
        self._navdataCallback = navdataCallback
        self._videoCallback = videoCallback
        self._droneState = None

        debug.Print("[ARDrone2]: Init ATCommand Object")
        self._atCommand = ATCommand(self._address, self._debug)
        debug.Print("[ARDrone2]: ATCommand Object OK")

        debug.Print("[ARDrone2]: Init Control Object")
        self._control = Control(self._address, self._debug)
        debug.Print("[ARDrone2]: Control Object OK")

        try:
            debug.Print("[ARDrone2]: Init NavData Object")
            self._navData = NavData(self._address, self._DoNavData, self._debug)
            debug.Print("[ARDrone2]: NavData Object OK")
        except Exception as e:
            self._control.Stop()
            debug.Print("[ARDrone2]: %s" % e)
            raise
        t = time.time()
        while(self._droneState == None):
            if((time.time()-t) > 4):
                self._control.Stop()
                self._navData.Stop()
                msg = "No navdata from the drone"
                debug.Print("[ARDrone2]: %s" % msg)
                raise Exception(msg)
            time.sleep(0.01)
        try:
            debug.Print("[ARDrone2]: Init Video Object")
            self._video = None
            if(self._videoCallback!=None):
                self._video = Video(address, self._DoVideo, debug)
                debug.Print("[ARDrone2]: Video Object OK")
            else:
                debug.Print("[ARDrone2]: No Video Object")
        except Exception as e:
            # no cleanup code required
            debug.Print("[ARDrone2]: %s" % e)
        self._running = False
        self._tmonitor = threading.Thread(target=self._TMonitor, args=(), name="Monitor")
        self._tmonitor.start()
        while(not self._running):
            time.sleep(0.01)

    def _Lock(self):
        """Acquire the lock
        """
        self._lock.acquire()

    def _Unlock(self):
        """Release the lock
        """
        self._lock.release()

    def _IsSet(self, mask):
        """Bitwise test of the command mask

        Returns:
            True if mask is set
        """
        return (self._droneState & mask)!=0

    def _ClearACK(self):
        """Clear the command mask
        """
        while(self._IsSet(NavData.COMMAND_MASK)):
            self._atCommand.ClearCommandAck()
            time.sleep(ARDrone2.COMMAND_DELAY)

    def _WaitACK(self):
        """Wait for the command mask to be true
        """
        while(not self._IsSet(NavData.COMMAND_MASK)):
            time.sleep(ARDrone2.COMMAND_DELAY)

    # from NavData
    def _DoNavData(self, droneState, options):
        """Method to receive the navdata
        """
        self._droneState = droneState
        self._options = options

    def _TMonitor(self):
        """Thread to monitor the watchdog mask and process alerts
        """
        self._running = True
        while(self._running):
            # prevents disconnection
            if(self._IsSet(NavData.COM_WATCHDOG_MASK)):
                try:
                    self._atCommand.WatchDog()
                    #self._debug.Print("[TMonitor]: NavData Flag - WATCHDOG Received")
                except Exception as e:
                    # no cleanup code required
                    self._debug.Print("[TMonitor]: %s" % e)

            # Alerts
            if(self._navdataCallback != None):
                self._navdataCallback(self._droneState, self._options)
            else:
                if(self._IsSet(NavData.COMMAND_MASK)):
                    self._debug.Print("[TMonitor]: NavData Flag - ACK Received")
                if(self._IsSet(NavData.MOTORS_MASK)):
                    self._debug.Print("[TMonitor]: NavData Flag - Motors Problems!!!")
                if(self._IsSet(NavData.COM_LOST_MASK)):
                    self._debug.Print("[TMonitor]: NavData Flag - Communication Lost!!!")
                if(self._IsSet(NavData.SOFTWARE_FAULT)):
                    self._debug.Print("[TMonitor]: NavData Flag - Software Lost!!!")
                if(self._IsSet(NavData.VBAT_LOW)):
                    self._debug.Print("[TMonitor]: NavData Flag - Battery Low!!!")
                if(self._IsSet(NavData.MAGNETO_NEEDS_CALIB)):
                    self._debug.Print("[TMonitor]: NavData Flag - Needs Calibration!!!")
                if(self._IsSet(NavData.ANGLES_OUT_OF_RANGE)):
                    self._debug.Print("[TMonitor]: NavData Flag - Angles Out of Range!!!")
                if(self._IsSet(NavData.WIND_MASK)):
                    self._debug.Print("[TMonitor]: NavData Flag - Too Much Wind!!!")
                if(self._IsSet(NavData.ULTRASOUND_MASK)):
                    self._debug.Print("[TMonitor]: NavData Flag - Ultrasound Detector Deaf!!!")
                if(self._IsSet(NavData.EMERGENCY_MASK)):
                    self._debug.Print("[TMonitor]: NavData Flag - EMERGENCY!!!")

            time.sleep(ARDrone2.COMMAND_DELAY)
        self._debug.Print("[TMonitor]: Aborting the thread")

    # from Video
    def _DoVideo(self, frame):
        """Method to receive the frame
        """
        return self._videoCallback(frame)

    def GetDroneState(self):
        """Get the drone state

        Returns:
            The drone state
        """
        return self._droneState

    def SetNavData(self):
        """Set navdata mode
        """
        try:
            self._Lock()
            self._ClearACK()
            self._atCommand.SetNavData()
            self._WaitACK()
            self._ClearACK()
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: SetNavData - %s" % e)
            raise
        finally:
            self._Unlock()

    def SetARDroneName(name):
        """Set drone name

        Args:
            name: drone name
        """
        try:
            self._Lock()
            self._atCommand.SetARDroneName(name)
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: SetARDroneName - %s" % e)
            raise
        finally:
            self._Unlock()

    def FlatTrim(self):
        try:
            self._Lock()
            if(not self._IsSet(NavData.FLY_MASK)):
                self._atCommand.FlatTrim()
                time.sleep(ARDrone2.COMMAND_DELAY)
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: LedsAnim: %s" % e)
            raise
        finally:
            self._Unlock()

    def GetConfig(self):
        try:
            self._Lock()
            self._ClearACK()
            self._atCommand.GetConfig()
            self._WaitACK()
            self._ClearACK()
            return self._control.GetAnswer()
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: GetConfig: %s" % e)
            raise
        finally:
            self._Unlock()

    def Move(self, roll, pitch, gaz, yaw):
        try:
            self._Lock()
            if(self._IsSet(NavData.FLY_MASK)):
                self._atCommand.Move(roll, pitch, gaz, yaw)
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: Move: %s" % e)
            raise
        finally:
            self._Unlock()

    def Hover(self):
        try:
            self._Lock()
            if(self._IsSet(NavData.FLY_MASK)):
                self._atCommand.Hover()
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[ARDrone2]: Hover: %s" % e)
            raise
        finally:
            self._Unlock()

    def Stop(self):
        """"Stop all the threads
        """
        self._debug.Print("[ARDrone2]: Stopping...")
        self._navData.Stop()
        self._control.Stop()
        if(self._video != None):
            self._video.Stop()
        self._running = False
        self._tmonitor.join()

