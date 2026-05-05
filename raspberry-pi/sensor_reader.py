"""
IoT Power Monitor - ACS712 Current Sensor Reader
================================================

This module reads analog values from MCP3008 ADC and converts them
to current (A) and power (W) using ACS712 sensor.
"""

import board
import busio
import digitalio
import time
from datetime import datetime

# ========================= CONFIGURATION =========================

# MCP3008 SPI Configuration
SPI_CS_PIN = board.D8          # Physical pin 24 (BCM 8 / CE0)

# ACS712 Sensor Parameters (ACS712-20A)
ACS712_VCC = 5.0               # Supply voltage to ACS712
ACS712_SENSITIVITY = 0.100     # 100 mV/A for 20A version/ 185 mV/A for 5A version
ACS712_OFFSET = 0.5            # 50% offset (2.5V when no current)

# Load parameters
LOAD_VOLTAGE = 5.0             # Assumed USB load voltage
SAMPLES_PER_READ = 100         # Number of samples for averaging
READ_INTERVAL = 10             # seconds (test mode)


# ========================= INITIALIZATION =========================

def init_mcp3008():
    """Initialize MCP3008 ADC via SPI"""
    try:
        # Create SPI bus
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        
        # Chip Select
        cs = digitalio.DigitalInOut(SPI_CS_PIN)
        
        # Import and initialize MCP3008
        import adafruit_mcp3xxx.mcp3008 as MCP
        from adafruit_mcp3xxx.analog_in import AnalogIn

        # Create MCP3008 object and channel
        mcp = MCP.MCP3008(spi, cs)
        channel = AnalogIn(mcp, MCP.P0)  # CH0
        
        print("✓ MCP3008 initialized successfully")
        return channel
        
    except Exception as e:
        print(f"✗ MCP3008 initialization failed: {e}")
        return None


# ========================= CONVERSION FUNCTIONS =========================

def read_adc_raw(channel, samples=SAMPLES_PER_READ):
    """
    Read raw ADC value with multiple sampling for stability.
    
    Returns:
        float: Average raw ADC value (0 ~ 65535)
    """
    try:
        # Perform multiple readings and average them
        total = 0
        # Note: channel.value returns a 16-bit scaled value (0 ~ 65535) even for 10-bit ADC
        for _ in range(samples):
            total += channel.value
            time.sleep(0.0001)
        
        return total / samples
    except Exception as e:
        print(f"✗ ADC read error: {e}")
        return None


def adc_to_voltage(adc_value):
    """Convert ADC raw value to voltage (0 - ACS712_VCC)"""
    if adc_value is None:
        return None
    # MCP3008 is 10-bit, but library returns 16-bit scaled value
    voltage = (adc_value / 65535.0) * ACS712_VCC
    return voltage


def voltage_to_current(voltage):
    """
    Convert sensor output voltage to current using ACS712 formula.
    
    Formula: I (A) = (V_out - V_offset) / Sensitivity
    """
    if voltage is None:
        return None
    
    offset_voltage = ACS712_VCC * ACS712_OFFSET
    # Current can be positive or negative depending on direction, so we keep the sign
    current_a = (voltage - offset_voltage) / ACS712_SENSITIVITY
    return current_a


def calculate_power(current_a, load_voltage=LOAD_VOLTAGE):
    """Calculate power in Watts: P = I × V"""
    if current_a is None:
        return None
    power_w = abs(current_a) * load_voltage
    return power_w


def read_power_data(channel):
    """
    Complete data acquisition pipeline: ADC → Voltage → Current → Power
    """
    adc_value = read_adc_raw(channel)
    if adc_value is None:
        return None

    voltage = adc_to_voltage(adc_value)
    current = voltage_to_current(voltage)
    power = calculate_power(current)

    return {
        "timestamp": datetime.now().isoformat(),
        "adc_value": round(adc_value, 1),
        "voltage": round(voltage, 3) if voltage else None,
        "current_a": round(current, 4) if current else None,
        "power_w": round(power, 3) if power else None,
        "location": "USB Device Test"
    }


def format_power_output(data):
    """Format data for human readable output"""
    if not data:
        return "✗ Power reading failed"
    
    return f"""
📊 ACS712 Power Monitor
Time     : {data['timestamp']}
ADC Value: {data['adc_value']:>8} / 65535
Voltage  : {data['voltage']:>6.3f} V
Current  : {data['current_a']:>7.4f} A
Power    : {data['power_w']:>7.3f} W
Location : {data['location']}
"""


# ========================= MAIN LOOP =========================

def main_loop(test_mode=True):
    """Main monitoring loop"""
    channel = init_mcp3008()
    if channel is None:
        print("✗ Failed to initialize MCP3008. Exiting.")
        return

    interval = 10 if test_mode else READ_INTERVAL
    loop_count = 0

    print(f"""
╔════════════════════════════════════════════╗
║     ACS712 IoT Power Monitor Started       ║
║  Mode: {'TEST' if test_mode else 'PRODUCTION'} Mode          ║
║  Interval: {interval} seconds                          ║
╚════════════════════════════════════════════╝
""")

    try:
        while True:
            loop_count += 1
            print(f"\n[Reading #{loop_count}] {datetime.now().strftime('%H:%M:%S')}")

            power_data = read_power_data(channel)
            
            if power_data:
                print(format_power_output(power_data))
            else:
                print("✗ Data collection failed, retrying...")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n✓ Program stopped by user.")
    except Exception as e:
        print(f"\n✗ Critical error: {e}")


# ========================= START PROGRAM =========================
if __name__ == "__main__":
    # Test mode (fast reading for debugging)
    main_loop(test_mode=True)
    
    # Production mode (uncomment when ready)
    # main_loop(test_mode=False)


