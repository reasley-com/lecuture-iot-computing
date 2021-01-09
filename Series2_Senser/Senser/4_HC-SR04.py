import RPi.GPIO as GPIO
from time import sleep, time
 
GPIO.setmode(GPIO.BCM)
 
GPIO_TRIGGER = 17
GPIO_ECHO = 18
 
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

 
try:
    while True:
        GPIO.output(GPIO_TRIGGER, True)

        sleep(0.1)
        GPIO.output(GPIO_TRIGGER, False)

        StartTime = time()
        StopTime = time()

        while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time()

        while GPIO.input(GPIO_ECHO) == 1:
            StopTime = time()

        TimeElapsed = StopTime - StartTime
        distance = (TimeElapsed * 34300) / 2
        print ("Measured Distance = %.1f cm" % distance)
        sleep(1)

except KeyboardInterrupt:   
    pass
    print('Exit with ^C. Goodbye!')
    GPIO.cleanup()
    exit()