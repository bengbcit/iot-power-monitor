import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
LIGHT_PIN = 27  # PIN 13

GPIO.setup(LIGHT_PIN, GPIO.IN)
print("Initial Read: ", GPIO.input(LIGHT_PIN))
try:
	while True:
		state = GPIO.input(LIGHT_PIN)
		if state ==GPIO.LOW:
			print("Dark: ",state)
		else:
			print("Bright: ",state)
		time.sleep(0.5)
except:
	GPIO.cleanup()
