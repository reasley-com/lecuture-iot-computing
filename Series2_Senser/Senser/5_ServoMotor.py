import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

ServoPin = 17
GPIO.setup(ServoPin, GPIO.OUT)
p = GPIO.PWM(ServoPin, 50)
p.start(50)
cnt = 0

try:
	while True:
		p.ChangeDutyCycle(12.5)
		sleep(1)
		p.ChangeDutyCycle(10.0)
		sleep(1)
		p.ChangeDutyCycle(7.5)
		sleep(1)
		p.ChangeDutyCycle(5.0)
		sleep(1)
		p.ChangeDutyCycle(2.5)
		sleep(1)

except KeyboardInterrupt:
	pass
	print('Exit with ^C. Goodbye!')
	GPIO.cleanup()
	exit()
