"""
MCP3008 ADC Test Script for Raspberry Pi
=======================================

This script reads analog values from MCP3008 ADC chip using SPI interface.
"""

import board
import busio
import digitalio
import time


def main():
    print("🔌 Initializing MCP3008 ADC...")

    # Create SPI bus
    spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    # Chip Select (CS) pin - Physical pin 24 (BCM 8)
    cs = digitalio.DigitalInOut(board.D8)

    # Import MCP3008 library
    import adafruit_mcp3xxx.mcp3008 as MCP
    from adafruit_mcp3xxx.analog_in import AnalogIn

    # Create MCP3008 object
    mcp = MCP.MCP3008(spi, cs)

    # Create analog input channel 0 (CH0)
    channel = AnalogIn(mcp, MCP.P0)

    print("✅ MCP3008 initialized successfully!\n")
    print("Reading CH0... (Press Ctrl+C to stop)\n")
    print("Raw Value    Voltage (V)     Avg Voltage")
    print("-" * 45)

    readings = []
    
    try:
        while True:
            raw = channel.value          # 0 ~ 65535
            voltage = channel.voltage    # Actual voltage

            # Calculate moving average
            readings.append(voltage)
            if len(readings) > 20:
                readings.pop(0)
            
            avg_voltage = sum(readings) / len(readings)

            # Print result
            print(f"{raw:8d}    {voltage:.3f}         {avg_voltage:.3f}", end="\r")
            
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user.")
        print(f"Final average voltage: {avg_voltage:.3f} V")


if __name__ == "__main__":
    main()

