# test_channels.py - MCP3008 Channel Test for ACS712 Sensor
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D8)
mcp = MCP.MCP3008(spi, cs)

print("MCP3008 channel test")
print("="*50)
print("Please keep ACS712 VOUT connected to the current test channel")
print()

# Test CH0 and CH1
channels = [
    (MCP.P0, "CH0"),
    (MCP.P1, "CH1"),
]

for channel_pin, name in channels:
    ch = AnalogIn(mcp, channel_pin)
    adc = ch.value
    voltage = (adc / 65535.0) * 5.0
    print(f"{name}: ADC={adc:6d} Voltage={voltage:.3f}V")
    time.sleep(0.5)

print()
print("If both channels read the same (~3.78V) → ACS712 is damaged")
print("If CH0 reads 3.78V and CH1 reads 2.5V → CH0 channel may be damaged")
print("If both channels read 0V → MCP3008 or SPI connection is damaged")