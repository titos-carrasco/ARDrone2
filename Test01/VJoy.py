#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import pygame

class Foo:
    pass

class VJoy:
    """Clase para utilizar el joystick en el control del drone

    Uso:
        debug = Debug()
        vj = VJoy(0, debug)
        while(True):
            (cmd, move) = vj.getCommand()
            if(cmd==vj.TAKEOFF):
                drone.TakeOff()
            elif(cmd==vj.EXIT):
                drone.Land()
                drone.Stop()
        ...
    """
    IDLE        = 0x00
    EXIT        = 0x01
    EMERGENCY   = 0x02
    FLAT_TRIM   = 0x03
    TAKE_OFF    = 0x04
    LAND        = 0x05
    CALIBRATE   = 0x06

    def __init__(self, jnum, debug):
        self._debug = debug
        self._roll = 0
        self._pitch = 0
        self._yaw = 0
        self._gaz = 0
        pygame.init()
        nj = pygame.joystick.get_count()
        if(nj==0 or jnum<0 or jnum>(nj-1)):
            self._joystick = None
        else:
            self._jnum = jnum
            self._joystick = pygame.joystick.Joystick(jnum)
            self._joystick.init()
            self._debug.Print("[VJoy]: Utilizando joystick #%d" % jnum)

    def GetCommand(self):
        cmd = self.IDLE
        if(self._joystick!=None):
            try:
                events = pygame.event.get()
                for event in events:
                    # botones del joystick
                    if(event.type==pygame.JOYBUTTONDOWN and event.joy == self._jnum):
                        if(event.button==4):
                            cmd = self.FLAT_TRIM
                        elif(event.button==5):
                            cmd = self.CALIBRATE
                        elif(event.button==6):
                            cmd = self.EMERGENCY
                        elif(event.button==7):
                            cmd = self.EXIT
                        elif(event.button==8):
                            cmd = self.LAND
                        elif(event.button==9):
                            cmd = self.TAKE_OFF
                    # movimiento en los ejes
                    elif(event.type == pygame.JOYAXISMOTION and event.joy == self._jnum):
                        axis = event.axis
                        value = int(round(event.value, 0))
                        if(axis==0):
                            self._roll = value
                        elif(axis==1):
                            self._pitch = value
                        elif(axis==2):
                            self._yaw = value
                        elif(axis==3):
                            self._gaz = -value
            except Exception as e:
                self._debug.Print("[VJoy:GetCommand]: %s" % e)

        move = Foo()
        move.roll = self._roll
        move.pitch = self._pitch
        move.yaw = self._yaw
        move.gaz = self._gaz
        # retornamos el comando asociado al botón presionado y el movimiento en los ejes
        return (cmd, move)

