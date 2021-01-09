import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer = 17
GPIO.setup(buzzer,GPIO.OUT)

while True:
    try:
        GPIO.output(buzzer,GPIO.HIGH)
        print ("Beep")
        sleep(0.5)
        
        GPIO.output(buzzer,GPIO.LOW)
        print ("No Beep")
        sleep(0.5)
        
    except KeyboardInterrupt:
        pass
        print('Exit with ^C. Goodbye!')
        GPIO.cleanup()
        exit()
