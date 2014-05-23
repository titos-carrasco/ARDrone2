ARDrone2
========

Python Code for the Parrot ARDrone2:

* Show video using Comupter Vision (cv2) and Numpy
* Add callback to preprocessing the frame. Example with Canny
* Pitch, Roll, Yaw and Gaz with the joystick (need joystick with
  four axes and twelve buttons
    * Flat Trim: button 5
    * Calibrate magnetromes: button 6
    * Emergency: button 7
    * Exit: button 8
    * Land: Button 9 (select)
    * Take Off: button 10 (start)
    * Pitch, Roll: axis 1 and 2
    * Gaz, Yaw: axis 3 and 4

ChangeLog
=========
22 May 2014

* ATCommand.py
    * Fix documentation in SetNavData()

* Video.py
    * Dimensions for the image have no effects
    * Show FPS

* ARDrone2.py
    * Add Move() method
    * Add Hover method

* Test01.py
    * Rewrite application
    * Add joystick support
    * Now you can fly using the joystick

