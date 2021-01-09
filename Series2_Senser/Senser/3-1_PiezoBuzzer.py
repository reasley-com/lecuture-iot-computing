import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer = 17
scales = [261, 294, 329, 349, 392, 440, 493, 523]
GPIO.setup(buzzer,GPIO.OUT)
p = GPIO.PWM(buzzer, 600)

p.start(50)

try:
	for scale in scales:
		p.ChangeFrequency(scale)
		sleep(0.5)

except KeyboardInterrupt:
	pass
	print('Exit with ^C. Goodbye!')
	GPIO.cleanup()
	exit()
