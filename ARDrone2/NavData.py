# -*- coding: utf-8 -*-
import socket
import threading
import time

class NavData:
    """Class to receive NavData from port 5554

    Usage:
        def callback(droneState):
            ... process parameters

        debug = Debug()
        navdata = NavData("192.168.1.1", callback, debug)
        ...
        navdata.Stop()
    """
    NAVDATA_PORT = 5554

    # Class errors
    ERR_UNEXPECTED_EXCEPTION = 1
    ERR_SOCKET_TIMEOUT = 2
    ERR_SMALL_PACKET = 3
    ERR_BAD_HEADER = 4
    ERR_BAD_CKS_TAG = 5
    ERR_CHECKSUM = 6
    ERR_BAD_SEQUENCE = 7

    ERR_MESSAGE = [0]*8
    ERR_MESSAGE[ERR_UNEXPECTED_EXCEPTION] = "Unexpected Exception"
    ERR_MESSAGE[ERR_SOCKET_TIMEOUT] = "Socket Timeout"
    ERR_MESSAGE[ERR_SMALL_PACKET] = "Small Packet"
    ERR_MESSAGE[ERR_BAD_HEADER] = "Bad Header"
    ERR_MESSAGE[ERR_BAD_CKS_TAG] = "Bad Checksum Tag"
    ERR_MESSAGE[ERR_CHECKSUM] = "Bad Checksum"
    ERR_MESSAGE[ERR_BAD_SEQUENCE] = "Bad Sequence Number"

    # Drone State
    FLY_MASK            = 1 << 0  #FLY MASK : (0) ardrone is landed, (1) ardrone is flying */
    VIDEO_MASK          = 1 << 1  #VIDEO MASK : (0) video disable, (1) video enable */
    VISION_MASK         = 1 << 2  #VISION MASK : (0) vision disable, (1) vision enable */
    CONTROL_MASK        = 1 << 3  #CONTROL ALGO : (0) euler angles control, (1) angular speed control */
    ALTITUDE_MASK       = 1 << 4  #ALTITUDE CONTROL ALGO : (0) altitude control inactive (1) altitude control active */
    USER_FEEDBACK_START = 1 << 5  #USER feedback : Start button state */
    COMMAND_MASK        = 1 << 6  #Control command ACK : (0) None, (1) one received */
    CAMERA_MASK         = 1 << 7  #CAMERA MASK : (0) camera not ready, (1) Camera ready */
    TRAVELLING_MASK     = 1 << 8  #Travelling mask : (0) disable, (1) enable */
    USB_MASK            = 1 << 9  #USB key : (0) usb key not ready, (1) usb key ready */
    NAVDATA_DEMO_MASK   = 1 << 10 #Navdata demo : (0) All navdata, (1) only navdata demo */
    NAVDATA_BOOTSTRAP   = 1 << 11 #Navdata bootstrap : (0) options sent in all or demo mode, (1) no navdata options sent */
    MOTORS_MASK         = 1 << 12 #Motors status : (0) Ok, (1) Motors problem */
    COM_LOST_MASK       = 1 << 13 #Communication Lost : (1) com problem, (0) Com is ok */
    SOFTWARE_FAULT      = 1 << 14 #Software fault detected - user should land as quick as possible (1) */
    VBAT_LOW            = 1 << 15 #VBat low : (1) too low, (0) Ok */
    USER_EL             = 1 << 16 #User Emergency Landing : (1) User EL is ON, (0) User EL is OFF*/
    TIMER_ELAPSED       = 1 << 17 #Timer elapsed : (1) elapsed, (0) not elapsed */
    MAGNETO_NEEDS_CALIB = 1 << 18 #Magnetometer calibration state : (0) Ok, no calibration needed, (1) not ok, calibration needed */
    ANGLES_OUT_OF_RANGE = 1 << 19 #Angles : (0) Ok, (1) out of range */
    WIND_MASK           = 1 << 20 #WIND MASK: (0) ok, (1) Too much wind */
    ULTRASOUND_MASK     = 1 << 21 #Ultrasonic sensor : (0) Ok, (1) deaf */
    CUTOUT_MASK         = 1 << 22 #Cutout system detection : (0) Not detected, (1) detected */
    PIC_VERSION_MASK    = 1 << 23 #PIC Version number OK : (0) a bad version number, (1) version number is OK */
    ATCODEC_THREAD_ON   = 1 << 24 #ATCodec thread ON : (0) thread OFF (1) thread ON */
    NAVDATA_THREAD_ON   = 1 << 25 #Navdata thread ON : (0) thread OFF (1) thread ON */
    VIDEO_THREAD_ON     = 1 << 26 #Video thread ON : (0) thread OFF (1) thread ON */
    ACQ_THREAD_ON       = 1 << 27 #Acquisition thread ON : (0) thread OFF (1) thread ON */
    CTRL_WATCHDOG_MASK  = 1 << 28 #CTRL watchdog : (1) delay in control execution (> 5ms), (0) control is well scheduled */
    ADC_WATCHDOG_MASK   = 1 << 29 #ADC Watchdog : (1) delay in uart2 dsr (> 5ms), (0) uart2 is good */
    COM_WATCHDOG_MASK   = 1 << 30 #Communication Watchdog : (1) com problem, (0) Com is ok */
    EMERGENCY_MASK      = 1 << 31  #Emergency landing : (0) no emergency, (1) emergency */

    def __init__(self, address, callback, debug):
        """Constructor

        Send "\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" for
        the first time. The Drone wil connect only to this client

        Args:
            adress: Drone's address/hostname
            callback: Method to call when receive NavData.
                      def callback(droneState):
                         ...
            debug: Debug object

        Throws:
            Any exception throws by socket.sendto()
        """
        self._address = address
        self._callback = callback
        self._debug = debug
        self._sequenceNumber = 0
        self._socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self._socket.bind(('', NavData.NAVDATA_PORT))
        self._socket.settimeout(1.0)
        try:
            self._socket.sendto(
                "\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                (self._address, NavData.NAVDATA_PORT))
        except Exception as e:
            # no cleanup code required
            self._debug.Print("[NavData]: %s" % e)
            raise
        self._running = False
        self._tnavdata = threading.Thread(target=self._TNavData, args=(), name="TNavData")
        self._tnavdata.start()
        while(not self._running):
            time.sleep(0.01)

    def _Unpack32(self, s):
        """Convert 32bit drone integer to normal 32bit integer
        """
        return (ord(s[3])<<24) + (ord(s[2])<<16) + (ord(s[1])<<8) + (ord(s[0])<<0)

    def _Unpack16(self, s):
        """Convert 16bit drone's integer to norma 16bit integer
        """
        return (ord(s[1])<<8) + (ord(s[0])<<0)

    def _TNavData(self, *args):
        """Thread to receive the NavData from the drone
        """
        self._running = True
        while(self._running):
            try:
                packet, addr = self._socket.recvfrom(65535)
                plen = len(packet)
                if(plen<24):
                    self._debug.Print("[TNavData]: Error - %s" % NavData.ERR_MESSAGE[NavData.ERR_SMALL_PACKET])
                    continue
                header = self._Unpack32(packet[0:4])
                droneState = self._Unpack32(packet[4:8])
                sequenceNumber = self._Unpack32(packet[8:12])
                visionFlag = self._Unpack32(packet[12:16])
                cksId = self._Unpack16(packet[plen-8:plen-6])
                size = self._Unpack16(packet[plen-6:plen-4])
                cksData = self._Unpack16(packet[plen-4:plen])

                if(cksId != 0xFFFF):
                    self._debug.Print("[TNavData]: Error - %s" % NavData.ERR_MESSAGE[NavData.ERR_BAD_CKS_TAG])
                elif(cksData != sum(map(ord, packet[:plen-8]))):
                    self._debug.Print("[TNavData]: Error - %s" % NavData.ERR_MESSAGE[NavData.ERR_CHECKSUM])
                elif(header != 0x55667788 and header != 0x55667789):
                    self._debug.Print("[TNavData]: Error - %s" % NavData.ERR_MESSAGE[NavData.ERR_BAD_HEADER])
                elif(sequenceNumber<self._sequenceNumber):
                    self._debug.Print("[TNavData]: Error - %s" % NavData.ERR_MESSAGE[NavData.ERR_BAD_SEQUENCE])
                else:
                    self._sequenceNumber = sequenceNumber
                    self._callback(droneState)
            except socket.timeout :
                self._debug.Print("[TNavData]: Error - %s" % NavData.ERR_MESSAGE[NavData.ERR_SOCKET_TIMEOUT])
            except Exception as e:
                self._debug.Print("[TNavData]: %s" % e)
                self._debug.Print("[TNavData]: Error - %s" % NavData.ERR_MESSAGE[NavData.ERR_UNEXPECTED_EXCEPTION])
        self._debug.Print("[TNavData]: Aborting the thread")

    def Stop(self):
        """Stop NavData thread
        """
        self._running = False
        self._tnavdata.join()
