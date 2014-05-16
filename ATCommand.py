# -*- coding: utf-8 -*-
"""AT Commands for the Parrot ARDrone2

    The transmission latency of the control commands is critical to the user
    experience. Those commands are to be sent on a regular basis
    (usually 30 times per second).
    --> Main app must take charge

    According to tests, a satisfying control of the AR.Drone 2.0 is reached
    by sending the AT-commands every 30 ms for smooth drone movements
    --> Main app must take charge

    To prevent the drone from considering the WIFI connection lost,
    two consecutive commands must be send within less than 2 seconds.
    --> Main app must take charge. See NavData.COM_WATCHDOG_MASK
"""
import threading
import socket
import struct

class ATCommand:
    AT_PORT = 5556

    def __init__(self, address, debug):
        try:
            self._lock = threading.Lock()
            self._address = address
            self._debug = debug
            self._sequence = 1
            self._socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self._socket.setblocking(1)
            self._socket.settimeout(1.0)
        except Exception, e:
            # no cleanup code required
            raise

    def _Lock(self):
        self._lock.acquire()

    def _Unlock(self):
        self._lock.release()

    def _SendCommand(self, cmd):
        try:
            self._Lock()
            cmd = cmd.replace("{SEQ}", str(self._sequence)) + chr(13)
            self._sequence = self._sequence + 1
            self._socket.sendto(cmd, (self._address, ATCommand.AT_PORT))
            self._debug.Print(cmd)
        except Exception, e:
            # no cleanup code required
            raise
        finally:
            self._Unlock()

    def _FloatToInt(self, f):
        return struct.unpack(">i", struct.pack(">f",f))[0]

    # AT*CTRL=%d,%d,%d\r
    def DoNothing(self):
        """
        Doing nothing
        """
        cmd = "AT*CTRL={SEQ},0,0"
        self._SendCommand(cmd)

    def GetConfig(self):
        """
        Send active configuration file to a client through the 'control'
        socket UDP 5559
        """
        cmd = "AT*CTRL={SEQ},4,0"
        self._SendCommand(cmd)

    def ClearCommandAck(self):
        """
        Reset command mask in navdata
        """
        cmd = "AT*CTRL={SEQ},5,0"
        self._SendCommand(cmd)

    def GetConfigIds(self):
        """
        Requests the list of custom configuration IDs
        """
        cmd = "AT*CTRL={SEQ},6,0"
        self._SendCommand(cmd)

    # AT*COMWDG=%d\r
    def WatchDog(self):
        cmd = "AT*COMWDG={SEQ}"
        self._SendCommand(cmd)

    # AT*REF=%d,%d\r
    def TakeOff(self):
        """ Take-off
        Send this command until navdata shows it.
        """
        ctrl = 0b10001010101000000000000000000 | 0b1000000000
        cmd = "AT*REF={SEQ},%d" % ctrl
        self._SendCommand(cmd)

    def Land(self):
        """ Land
        Send this command until navdata shows it.
        Send as  a safety whenever an abnormal situation is detected
        """
        ctrl = 0b10001010101000000000000000000 | 0b0000000000
        cmd = "AT*REF={SEQ},%d" % ctrl
        self._SendCommand(cmd)

    def Emergency(self):
        """ Emergency order
        Engines are cut-off no matter the drone state
        """
        ctrl = 0b10001010101000000000000000000 | 0b100000000
        cmd = "AT*REF={SEQ},%d" % ctrl
        self._SendCommand(cmd)

    def EmergencyReset(self):
        """ Reset emergency state
        Send again this order (emergency) to resume normal state
        Send an AT*REF command with this bit set to 0 (land) to make the drone
        consider following "emergency orders" commands
        """
        pass

    # AT*PCMD=%d,%d,%d,%d,%d,%d\r
    def Hover(self):
        cmd = "AT*PCMD={SEQ},0,0,0,0,0"
        self._SendCommand(cmd)

    def Move(self, roll, pitch, gaz, yaw):
        roll = self._FloatToInt(float(min(max(roll,-1.),1.)))
        pitch = self._FloatToInt(float(min(max(pitch,-1.),1.)))
        gaz = self._FloatToInt(float(min(max(gaz,-1.),1.)))
        yaw = self._FloatToInt(float(min(max(yaw,-1.),1.)))
        flag = 0b001
        cmd = "AT*PCMD={SEQ},%d,%d,%d,%d,%d" % (flag, roll, pitch, gaz, yaw)
        self._SendCommand(cmd)

    # AT*PCMD_MAG=%d,%d,%d,%d,%d,%d,%d,%d\r
    def MoveMag(self, roll, pitch, gaz, yaw, psi, accuracy):
        roll = self._FloatToInt(float(min(max(roll,-1.),1.)))
        pitch = self._FloatToInt(float(min(max(pitch,-1.),1.)))
        gaz = self._FloatToInt(float(min(max(gaz,-1.),1.)))
        yaw = self._FloatToInt(float(min(max(yaw,-1.),1.)))
        psi = self._FloatToInt(float(min(max(psi,-1.),1.)))
        accuracy = self._FloatToInt(float(min(max(accuracy,-1.),1.)))
        flag = 0b001
        cmd = "AT*PCMD_MAG={SEQ},%d,%d,%d,%d,%d,%d,%d" % (flag, roll, pitch,
                                                          gaz, yaw, psi,
                                                          accuracy)
        self._SendCommand(cmd)

    # AT*FTRIM=%d\r
    def FlatTrim(self):
        """ Flat Trim
        This command must not be sent when the ARDrone is flying
        """
        cmd = "AT*FTRIM={SEQ}"
        self._SendCommand(cmd)

    # AT*CALIB=%d,%d\r
    def Calibrate(self):
        """ Magnetrometer calibration
        This command must be sent when the ARDrone is flying
        """
        cmd = "AT*CALIB={SEQ},0"
        self._SendCommand(cmd)

    # AT*CONFIG=%d,\"%s\",\"%s\"\r
    def _Config(self, option, value):
        cmd = "AT*CONFIG={SEQ},\"%s\",\"%s\"" % (option, value)
        self._SendCommand(cmd)

    def SetNavData(self, Full=False):
        if(Full):
            flag = "FALSE"
        else:
            flag = "TRUE"
        self._Config("general:navdata_demo", flag)

    # AT*LED=%d,%d,%d,%d\r
    def LedsAnim(self, anim, frecuency, duration):
        cmd = "AT*LED={SEQ},%d,%d,%d" % (anim, self._FloatToInt(frecuency + 0.0), duration)
        self._SendCommand(cmd)

    """
    AT*PMODE=%d,%d\r
    AT*MISC=%d,%d,%d,%d,%d\r
    AT*GAIN=%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\r
    AT*ANIM=%d,%d,%d\r
    AT*VISP=%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\r
    AT*VISO=%d,%d\r
    AT*CAP=%d,%d,%d\r
    AT*ZAP=%d,%d\r
    AT*CAD=%d,%d,%d\r
    AT*MTRIM=%d,%d,%d,%d\r
    AT*POL=%d,%d,%d,%d,%d,%d\r
    AT*CONFIG_IDS=%d,\"%s\",\"%s\",\"%s\"\r
    AT*PWM=%d,%d,%d,%d,%d\r
    AT*AFLIGHT=%d,%d\r
    AT*VICON=%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\r
    AT*PR\r
    AT*PM\r
    AT*PM=!%d\r
    AT*PM=?\r
    AT*PM?\r
    AT*PM=%d,%d\r
    AT*PM!\r
    AT*PL\r
    AT*PL=!%d\r
    AT*PL=?\r
    AT*PL?\r
    AT*PL=%d\r
    AT*PAVS=?\r
    AT*PAVS?\r
    AT*PAVS=%d[,\"%s\"]\r
    AT*PAVI=?\r
    AT*PAVI?\r
    AT*PAVI=%l{[%d]}\r
    AT*PAO=?\r
    AT*PAO?\r
    AT*PAO=%d[,\"%s\"]\r
    AT*PCC=?\r
    AT*PCC?\r
    AT*PCC=[%d],[%d]\r
    AT*PCS=?\r
    AT*PCS?\r
    AT*PCS=%l{[%d]}\r
    AT*SDT\r
    AT*PIP=%d\r
    AT*PII=%d\r
    AT*PID=%d\r
    AT*DEM\r
    AT*INM\r
    AT*RSS=%d:%d:%d:%d:%d:%d\r
    """
