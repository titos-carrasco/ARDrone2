# -*- coding: utf-8 -*-
import threading
import time
import cv2
import numpy

class Video:
    """Clase para recibir video desde la puerta 5555

    Utiliza la librería OpenCV (cv2)

    Uso:
        def callback(frame):
            ... procesar frame

        debug = Debug()
        video = Video("192.168.1.1", callback, debug)
        ...
        video.Stop()
    """
    VIDEO_PORT = 5555

    # tipos de errores
    ERR_UNEXPECTED_EXCEPTION = 1

    ERR_MESSAGE = [0]*2
    ERR_MESSAGE[ERR_UNEXPECTED_EXCEPTION] = "Excepción no esperada"

    def __init__(self, address, callback, debug):
        """Constructor

        Args:
            address: dirección/hostname del drone
            callback: método a invocar cuando se recibe un frame
                      def callback(frame)
                        ....
            debug: objeto de debug

        Throws:
            Exception si no puede leer el primer frame
        """
        self._address = address
        self._callback = callback
        self._debug = debug
        try:
            self._tps = cv2.getTickFrequency()
            self._cap = cv2.VideoCapture("tcp://%s:%d" % (address, Video.VIDEO_PORT))
            #self._cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
            #self._cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 480)
            ret, img = self._cap.read()
            if(not ret):
                msg = "No se puede leer el video desde el drone"
                self._debug.Print("[Video]: %s" % msg)
                raise Exception(msg)
            self._winName = "ARDrone2 Video"
            cv2.namedWindow(self._winName, cv2.CV_WINDOW_AUTOSIZE)
        except NameError as e:
            # no se requiere código de limpieza
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
        """Hilo para procesar el video del drone
        """
        self._running = True
        t1=cv2.getTickCount()
        while(self._running):
            try:
                ret, img = self._cap.read()
                if(ret):
                    frame = cv2.flip(img,1)
                    frame = self._callback(frame)
                    imgH, imgW, depth = img.shape
                    t2=cv2.getTickCount()
                    cv2.putText(frame, "%04.2f FPS" % (1/((t2-t1)/self._tps)), (10, imgH-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
                    cv2.imshow(self._winName, frame)
                    cv2.waitKey(1)
                    t1=t2
            except Exception as e:
                self._debug.Print("[TVideo]: %s" % e)
                self._debug.Print("[TVideo]: Error - %s" % Video.ERR_MESSAGE[Video.ERR_UNEXPECTED_EXCEPTION])
        self._debug.Print("[TVideo]: Aborting the thread")

    def Stop(self):
        """Detiene el hilo del video
        """
        self._running = False
        self._tvideo.join()
        self._cap.release()
        cv2.destroyAllWindows()
