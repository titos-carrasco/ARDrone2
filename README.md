ARDrone2
========

Código Python para el ARDrone2 de Parrot.

* Despliega el video utilizando OpenCV (cv2) y Numpy
* Permite función de callback para preprocesar el video (por ejemplo con Canny)
* Pitch, Roll, Yaw and Gaz con joystick (4 ejes/12 botones)
    * Ajuste Horizontal: botón 5
    * Calibrar magnetrónomos: botón 6
    * Emergencia: botón 7
    * Salir: botón 8
    * Aterrizar: botón 9 (select)
    * Despegar: botón 10 (start)
    * Pitch, Roll: ejes 1 and 2
    * Gaz, Yaw: ejes 3 and 4
* TODO
    * Implementar control a través del teclado
    * Implementar los comandos AT listados al final del archivo ATCommand.py
    * Implementar los comandos de configuración listados en el Developer Guide Capítulo 8
    * Interpretar el resto de los Options blocks en NavData


ChangeLog
=========
17 Nov 2014

* Se cambian los mensajes al español
* Reestructura los directorios


08 Jul 2014

* ATCommand.py
    * Agrega SetARDroneName()

* NavData.py
    * Parses options blocks

* ARDrone2.py
    * Agrega Options blocks data
    * Agrega SetARDroneName()
    * Si videoCallback es null entonces no se procesa video


22 May 2014

* ATCommand.py
    * Corrige documentación en SetNavData()

* Video.py
    * Dimensiones de la imagen no tienen efecto
    * Muestra los FPS

* ARDrone2.py
    * Agrega el método Move()
    * Agrega el método Hover()

* Test01.py
    * Se reescribe la aplicación
    * Agrega soporte para joystick


