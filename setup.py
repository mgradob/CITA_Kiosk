from distutils.core import setup

setup(
    name='CITA Kiosk',
    version='1.0',
    packages=['VMC', 'VMC.Utils', 'VMC.Coin_Changer', 'VMC.Bill_Dispenser', 'Lockers', 'Lockers.Utils', 'Printer',
              'Frontend', 'Frontend.Utils', 'LockersApi.SaltoLockers.Lockers', 'LockersApi.SaltoLockers.SaltoLockers',
              'LockersApi.SaltoLockers.socketSender'],
    url='',
    license='',
    author='',
    author_email='',
    description='',
    timezone="America/Chihuahua", requires=['pytz', 'requests']
)

'''
Salto Lockers Controller.
    IP addresses:
        MainController: localhost:1024
        VmcController: localhost:1025
        PrinterController: localhost:1026
        LockersSocket: <IP_de_la_maquina>:1028

    Configurar estas direcciones antes de correr el programa.
    Configurar el puerto COM de Changer_Thread al puerto del cable USB-Serial.
    Iniciar el API (LockersAPI) antes de iniciar el programa.

    Para iniciar el frontend:
        1.- En terminal o cmd, navegar a la carpeta ..Cita Kiosk/Frontend/html
        2.- Comando: python -m SimpleHTTPServer 80

    Los archivos apiTest.py y jsonTest.py son simples archivos usados para probar funcionalidades antes de utilizarlas
    en el codigo principal.
'''