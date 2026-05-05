import RPi.GPIO as GPIO
import time

# Configure GPIO
GPIO.setmode(GPIO.BCM)
TRIG = 23  # PIN 16
ECHO = 24  # PIN 18

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    """Measure distance (unit: cm)"""
    # send trigger pulse
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)  # 10 microseconds
    GPIO.output(TRIG, GPIO.LOW)
    
    # wait for ECHO to go high
    while GPIO.input(ECHO) == GPIO.LOW:
        start_time = time.time()
    
    # wait for ECHO to go low
    while GPIO.input(ECHO) == GPIO.HIGH:
        end_time = time.time()
    
    # calculate distance
    duration = end_time - start_time
    distance = (duration * 34300) / 2  # speed of sound 340 m/s
    
    return distance

if __name__ == "__main__":
    try:
        while True:
            dist = measure_distance()
            print(f"Distance: {dist:.2f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
