import adafruit_dht
import RPi.GPIO as GPIO
import time

DHT_PIN = 4
dht_device = adafruit_dht.DHT11(DHT_PIN)

def read_dht11():
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        
        if humidity is not None and temperature is not None:
            print(f"Temperature: {temperature:.1f}°C |  Humidity: {humidity:.1f}%")
            return temperature, humidity
        else:
            print("Sensor are failing to read data...")
            return None, None
    except RuntimeError as error:
        print(f"Reading Error: {error.args[0]}")
        return None, None

if __name__ == "__main__":
    while True:
        read_dht11()
        time.sleep(2)
