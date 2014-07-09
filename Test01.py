#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import cv2
import numpy as np
import pygame

from ARDrone2.Debug import Debug
from ARDrone2.ARDrone2 import ARDrone2


class Main:
    def __init__(self):
        pass

    def Run(self):
        debug = Debug()

        pygame.init()
        if(pygame.joystick.get_count()==0):
            debug.Print("[MainApp]: You must have a Joystick...")
            return
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        axes = [0]*joystick.get_numaxes()
        buttons = [0]*joystick.get_numbuttons()
        if(len(axes)<4):
            debug.Print("[MainApp]: You must have a Joystick with at least 4 axes...")
            return
        if(len(buttons)<12):
            debug.Print("[MainApp]: You must have a Joystick with at least 12 buttons...")
            return

        try:
            drone = ARDrone2("192.168.1.1", debug, None, self.Canny)
        except Exception as e:
            debug.Print("[MainApp]: No connection to ARDrone2. May be Drone's hostname/address is wrong...")
            return
        drone.SetNavData()

        while(True):
            try:
                pygame.event.pump()

                for i in range(len(buttons)):
                    buttons[i] = joystick.get_button(i)
                btnFlatTrim = buttons[4]
                btnCalibrate = buttons[5]
                btnEmergency = buttons[6]
                btnExit = buttons[7]
                btnLand = buttons[8]
                btnTakeOff = buttons[9]

                if(btnExit == 1):
                    break
                elif(btnEmergency == 1):
                    drone.Emergency()
                elif(btnTakeOff == 1):
                    drone.TakeOff()
                elif(btnLand == 1):
                    drone.Land()
                elif(btnFlatTrim == 1):
                    drone.FlatTrim()
                elif(btnCalibrate == 1):
                    drone.Calibrate()

                for i in range(len(axes)):
                    axes[i] = int(round(joystick.get_axis(i),0))
                factor = 0.3
                flyRoll = axes[0] * factor
                flyPitch = axes[1] * factor
                flyYaw = axes[2] * factor
                flyGaz = -axes[3] * factor
                if(flyRoll==0 and flyPitch==0 and flyYaw==0 and flyGaz==0):
                    drone.Hover()
                else:
                    drone.Move(flyRoll, flyPitch, flyGaz, flyYaw)

                time.sleep(0.01)
            except Exception as e:
                debug.Print("[MainApp]: %s" % e)
                break

        debug.Print("[MainApp]: Exit button pressed...")
        drone.Land()
        time.sleep(5)
        drone.Stop()

        """
        self._drone.EmergencyReset()
        #debug.Print("[MainApp]\n%s" % drone.GetConfig())
        #drone.LedsAnim(1, 10, 2)
        drone.LedsAnim(2, 10, 2)
        drone.LedsAnim(1, 10, 2)
       """

        # running threads
        debug.Print("[MainApp]: %s " % threading.enumerate())

    def Canny(self, img):
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
    """main() for the application."""
    app = Main()
    app.Run()

if __name__ == "__main__":
    main()
