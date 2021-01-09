import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

while True:
  try:
    GPIO.output(18, False)
    print('OFF')
    time.sleep(2)
    
    GPIO.output(18, True)
    print('ON')
    time.sleep(2)
  except KeyboardInterrupt:
    pass
    print('Exit with ^C. Goodbye!')
    GPIO.cleanup()
    exit()
