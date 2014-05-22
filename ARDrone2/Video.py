# -*- coding: utf-8 -*-
import threading
import time
import cv2
import numpy

class Video:
    """Class to receive Video from port 5555

    Use Computer Vision 2 Library

    Usage:
        def callback(frame):
            ... process frame

        debug = Debug()
        video = Video("192.168.1.1", callback, debug)
        ...
        Video.Stop()
    """
    VIDEO_PORT = 5555

    # Class errors
    ERR_UNEXPECTED_EXCEPTION = 1

    ERR_MESSAGE = [0]*2
    ERR_MESSAGE[ERR_UNEXPECTED_EXCEPTION] = "Unexpected Exception"

    def __init__(self, address, callback, debug):
        """Constructor

        Args:
            adress: Drone's address/hostname
            callback: Method to call when receive a frame.
                      def callback(frame)
                        ....
            debug: Debug object

        Throws:
            Exception if can't read first frame
        """
        self._address = address
        self._callback = callback
        self._debug = debug
        try:
            self._tps = cv2.getTickFrequency()
            self._cap = cv2.VideoCapture("tcp://%s:%d" % (address, Video.VIDEO_PORT))
            self._imgW = 320
            self._imgH = 240
            self._cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self._imgH)
            self._cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self._imgW)
            ret, img = self._cap.read()
            if(not ret):
                msg = "Can't read video from the drone"
                self._debug.Print("[Video]: %s" % msg)
                raise Exception(msg)
            self._winName = "ARDrone2 Video"
            cv2.namedWindow(self._winName, cv2.CV_WINDOW_AUTOSIZE)
        except NameError as e:
            # no cleanup code required
            self._debug.Print("[Video]: %s" % e)
            raise
        except Exception as e:
            self._cap.release()
            cv2.destroyAllWindows()
            self._debug.Print("[Video]: %s" % e)
            raise
        self._running = False
        self._tvideo = threading.Thread(target=self._TVideo, args=(), name="TVideo")
        self._tvideo.start()
        while(not self._running):
            time.sleep(0.01)

    def _TVideo(self, *args):
        """Thread to process the video from the drone
        """
        self._running = True
        while(self._running):
            try:
                ret, img = self._cap.read()
                if(ret):
                    frame = cv2.flip(img,1)
                    frame = self._callback(frame)
                    cv2.imshow(self._winName, frame)
                cv2.waitKey(1)
            except Exception as e:
                self._debug.Print("[TVideo]: %s" % e)
                self._debug.Print("[TVideo]: Error - %s" % Video.ERR_MESSAGE[Video.ERR_UNEXPECTED_EXCEPTION])
        self._debug.Print("[TVideo]: Aborting the thread")

    def Stop(self):
        """Stop Video thread
        """
        self._running = False
        self._tvideo.join()
        self._cap.release()
        cv2.destroyAllWindows()
