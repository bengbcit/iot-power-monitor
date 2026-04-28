import RPi.GPIO as GPIO
import time 

GPIO.setmode(GPIO.BCM)

# GPIO mode
GPIO.setmode(GPIO.BCM)

# use GPIO 17
GPIO.setup(17, GPIO.OUT)

print("LED blink test...")

# Blink 5 times
for i in range(5):
    GPIO.output(17, GPIO.HIGH)  # on
    print(f"[{i+1}] LED ON ✓")
    time.sleep(1)
    
    GPIO.output(17, GPIO.LOW)   # off
    print(f"[{i+1}] LED OFF")
    time.sleep(1)

GPIO.cleanup()
print("You Blink！")
