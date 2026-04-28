import time
import board
import adafruit_dht

# D4 represents GPIO 4. If you connect it to another pin, please change the number accordingly.
# Use adafruit_dht.DHT11 for DHT11 sensor; if you use a white DHT22 sensor, change it to DHT22.
dhtDevice = adafruit_dht.DHT11(board.D4)

while True:
    try:
        # Read temperature and humidity values
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        print(f"Temperature: {temperature_c:.1f}°C    Humidity: {humidity}%")

    except RuntimeError as error:
        # DHT sensors are quite unstable and reading errors happen frequently.
        # We just catch the error and continue the process.
        print(f"Reading failed: {error.args[0]}")
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)
