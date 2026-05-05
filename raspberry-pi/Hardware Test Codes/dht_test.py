import adafruit_dht
import board
import time

# GPIO4 board.D4（Physical Pin 7）
dht_device = adafruit_dht.DHT11(board.D4)

def read_dht11():
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        
        if humidity is not None and temperature is not None:
            print(f"Temperature: {temperature:.1f}°C  Humidity: {humidity:.1f}%")
            return temperature, humidity
        else:
            print("failed to retrieve data from DHT11 sensor...")
            return None, None
            
    except RuntimeError as error:
        print(f"Error reading DHT11 sensor: {error.args[0]}")
        return None, None
    except Exception as error:
        print(f"Unexpected error: {error}")
        return None, None

if __name__ == "__main__":
    while True:
        read_dht11()
        time.sleep(2)   # DHT11 every 2 sec read once
