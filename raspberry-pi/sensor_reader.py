"""
main.py - ACS712 Power Monitor with Calibration and Overcurrent Protection
==========================================================================

This is the main program that integrates:
- Calibration module (for zero-point accuracy)
- Overcurrent protection module (for safety)

Usage:
    python main.py              # Normal operation with calibration & protection
    python main.py --calibrate  # Run calibration only
    python main.py --test       # Test mode (faster readings)
"""

import board
import busio
import digitalio
import time
import sys
from datetime import datetime

# Import custom modules
from ACS712_Calibration import Calibration
from ACS712_Overcurrent import OvercurrentProtection, OvercurrentError


# ========================= CONFIGURATION =========================

# ACS712 Sensor Parameters (ACS712-20A)
ACS712_VCC = 5.3               # Supply voltage to ACS712 (Volts)
ACS712_SENSITIVITY = 0.100     # 100 mV/A for 20A version (Volts per Ampere)
ACS712_THEORETICAL_OFFSET = 0.5  # 50% offset (2.5V when no current)

# Load parameters
LOAD_VOLTAGE = 5.0             # Voltage of the load being measured (Volts)

# Reading parameters
SAMPLES_PER_READ = 100         # Number of samples for averaging
READ_INTERVAL_NORMAL = 10      # Seconds between readings (production mode)
READ_INTERVAL_TEST = 2         # Seconds between readings (test mode)

# Overcurrent thresholds (Amps)
WARNING_THRESHOLD = 15.0       # Warning at 15A (75% of 20A range)
CRITICAL_THRESHOLD = 18.0      # Critical at 18A (90% of 20A range)
AUTO_SHUTDOWN = True           # Automatically trigger emergency stop


# ========================= HARDWARE INITIALIZATION =========================

def init_mcp3008():
    """
    Initialize MCP3008 ADC via SPI.
    
    Returns:
        AnalogIn: MCP3008 channel 0 object, or None if initialization fails
    """
    try:
        # Create SPI bus
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        
        # Chip select pin
        cs = digitalio.DigitalInOut(board.D8)
        
        # Import and initialize MCP3008
        import adafruit_mcp3xxx.mcp3008 as MCP
        from adafruit_mcp3xxx.analog_in import AnalogIn
        
        # Create MCP3008 object and channel 0
        mcp = MCP.MCP3008(spi, cs)
        channel = AnalogIn(mcp, MCP.P0)  # CH0 for ACS712 VOUT
        
        print("✓ MCP3008 initialized successfully")
        return channel
        
    except Exception as e:
        print(f"✗ MCP3008 initialization failed: {e}")
        return None


def read_adc_raw(channel, samples=SAMPLES_PER_READ):
    """
    Read raw ADC value with multiple sampling for stability.
    
    Args:
        channel: MCP3008 analog input channel
        samples (int): Number of samples to average
        
    Returns:
        float: Average raw ADC value (0 ~ 65535), None on error
    """
    try:
        total = 0
        for _ in range(samples):
            total += channel.value
            time.sleep(0.0001)  # 100 microseconds between samples
        
        return total / samples
    except Exception as e:
        print(f"✗ ADC read error: {e}")
        return None


def adc_to_voltage(adc_value, calibration_zero_voltage=None):
    """
    Convert ADC raw value to voltage with optional calibration correction.
    
    Args:
        adc_value (float): Raw ADC reading (0 ~ 65535)
        calibration_zero_voltage (float): Calibrated zero-voltage from calibration module
        
    Returns:
        float: Voltage in volts (0 ~ ACS712_VCC), None if input is None
    """
    if adc_value is None:
        return None
    
    # Convert ADC value to raw voltage (0-5V range)
    raw_voltage = (adc_value / 65535.0) * ACS712_VCC
    
    # Apply calibration correction if provided
    if calibration_zero_voltage is not None:
        theoretical_zero = ACS712_VCC * ACS712_THEORETICAL_OFFSET
        offset_correction = theoretical_zero - calibration_zero_voltage
        calibrated_voltage = raw_voltage + offset_correction
        return calibrated_voltage
    
    return raw_voltage


def voltage_to_current(voltage, calibration_zero_voltage=None):
    """
    Convert sensor output voltage to current using ACS712 formula.
    
    Formula: I (A) = (V_out - V_offset) / Sensitivity
    
    Args:
        voltage (float): Measured voltage in volts
        calibration_zero_voltage (float): Calibrated zero-current voltage
        
    Returns:
        float: Current in Amps (positive or negative), None if input is None
    """
    if voltage is None:
        return None
    
    # Determine offset voltage (calibrated or theoretical)
    if calibration_zero_voltage is not None:
        offset_voltage = calibration_zero_voltage
    else:
        offset_voltage = ACS712_VCC * ACS712_THEORETICAL_OFFSET
    
    # Calculate current
    current_a = (voltage - offset_voltage) / ACS712_SENSITIVITY
    return abs(current_a)


def calculate_power(current_a, load_voltage=LOAD_VOLTAGE):
    """
    Calculate power in Watts: P = I × V
    
    Args:
        current_a (float): Current in Amps
        load_voltage (float): Load voltage in volts
        
    Returns:
        float: Power in Watts, None if input is None
    """
    if current_a is None:
        return None
    power_w = abs(current_a) * load_voltage
    return power_w


# ========================= DATA DISPLAY =========================

def format_output(data, show_adc=True):
    """
    Format power data for human-readable output.
    
    Args:
        data (dict): Power data from read_power_data()
        show_adc (bool): Whether to show ADC value
        
    Returns:
        str: Formatted output string
    """
    if not data:
        return "✗ Power reading failed"
    
    # Add alert symbol based on protection status
    alert_symbol = ""
    if data.get('alert'):
        if data['alert'] == 'CRITICAL':
            alert_symbol = " 🚨🚨🚨"
        elif data['alert'] == 'WARNING':
            alert_symbol = " ⚠️"
        elif data['alert'] == 'CRITICAL_STOP':
            alert_symbol = " 🔴 EMERGENCY STOPPED 🔴"
    
    output = f"""
{'='*50}
📊 ACS712 Power Monitor{alert_symbol}
Time     : {data['timestamp']}
"""
    
    if show_adc:
        output += f"ADC Value: {data['adc_value']:>8.1f} / 65535\n"
    
    output += f"""Voltage  : {data['voltage']:>6.3f} V
Current  : {data['current_a']:>7.4f} A
Power    : {data['power_w']:>7.3f} W
Location : {data['location']}
{'='*50}
"""
    return output


# ========================= MAIN READING FUNCTION =========================

def read_power_data(channel, calibration_zero_voltage=None, protection=None):
    """
    Complete data acquisition pipeline: ADC → Voltage → Current → Power.
    Includes optional calibration and overcurrent protection.
    
    Args:
        channel: MCP3008 analog input channel
        calibration_zero_voltage (float): Calibrated zero voltage (from calibration module)
        protection (OvercurrentProtection): Protection instance (from overcurrent module)
        
    Returns:
        dict: Power data including alert level if protection enabled
    """
    # Step 1: Read raw ADC value
    adc_value = read_adc_raw(channel)
    if adc_value is None:
        return None
    
    # Step 2: Convert ADC to Voltage (with calibration if available)
    voltage = adc_to_voltage(adc_value, calibration_zero_voltage)
    
    # Step 3: Convert Voltage to Current (with calibration if available)
    current = voltage_to_current(voltage, calibration_zero_voltage)
    
    # Step 4: Calculate Power
    power = calculate_power(current)
    
    # Build data dictionary
    data = {
        "timestamp": datetime.now().isoformat(),
        "adc_value": round(adc_value, 1),
        "voltage": round(voltage, 3) if voltage else None,
        "current_a": round(current, 4) if current else None,
        "power_w": round(power, 3) if power else None,
        "location": "USB Device Test",
        "alert": None
    }
    
    # Step 5: Check overcurrent protection if enabled
    if protection and current is not None:
        try:
            alert_level = protection.check(current)
            data["alert"] = alert_level.upper()
        except OvercurrentError as e:
            data["alert"] = "CRITICAL_STOP"
            print(f"🛑 {e}")
            raise  # Re-raise to let main loop handle it
    
    return data


# ========================= CALIBRATION ROUTINE =========================

def run_calibration_routine(channel):
    """
    Run the calibration routine with user prompts.
    
    Args:
        channel: MCP3008 analog input channel
        
    Returns:
        float: Calibrated zero voltage
    """
    print("\n" + "="*60)
    print("CALIBRATION ROUTINE")
    print("="*60)
    print("""
This routine will measure the zero-point voltage of your ACS712 sensor.

IMPORTANT:
1. DISCONNECT any load from the ACS712 (no current flowing)
2. Make sure the sensor is powered (VCC and GND connected)
3. Wait for the measurement to complete
""")
    
    input("Press ENTER to start calibration...")
    
    # Measure zero voltage
    zero_voltage = Calibration.measure_zero_voltage(channel)
    
    # Ask user to save
    response = input(f"\nSave calibration value {zero_voltage:.4f}V? (y/n): ")
    if response.lower() == 'y':
        Calibration.save_calibration(zero_voltage)
        print("✓ Calibration saved!")
    else:
        print("✗ Calibration not saved.")
    
    return zero_voltage


# ========================= MAIN LOOP =========================

def main_loop(test_mode=False, enable_calibration=True, enable_protection=True):
    """
    Main monitoring loop with optional calibration and protection.
    
    Args:
        test_mode (bool): Use faster interval for testing
        enable_calibration (bool): Load and apply calibration
        enable_protection (bool): Enable overcurrent protection
    """
    # Step 1: Initialize hardware
    print("\n🔧 Initializing hardware...")
    channel = init_mcp3008()
    if channel is None:
        print("✗ Failed to initialize MCP3008. Exiting.")
        return
    
    # Step 2: Load calibration (if enabled)
    calibration_zero_voltage = None
    if enable_calibration:
        print("\n🔧 Loading calibration...")
        cal_data = Calibration.load_calibration()
        if cal_data:
            calibration_zero_voltage = cal_data['zero_voltage']
            print(f"✓ Using calibrated zero voltage: {calibration_zero_voltage:.4f} V")
        else:
            print("ℹ️  No calibration found. Using theoretical value (2.500V)")
            print("   Run 'python main.py --calibrate' to improve accuracy.")
    
    # Step 3: Initialize overcurrent protection (if enabled)
    protection = None
    if enable_protection:
        print("\n🔧 Initializing overcurrent protection...")
        protection = OvercurrentProtection(
            warning_threshold=WARNING_THRESHOLD,
            critical_threshold=CRITICAL_THRESHOLD,
            auto_shutdown=AUTO_SHUTDOWN
        )
        print(f"✓ Protection enabled:")
        print(f"   Warning : {protection.warning} A")
        print(f"   Critical: {protection.critical} A")
    
    # Step 4: Set interval
    interval = READ_INTERVAL_TEST if test_mode else READ_INTERVAL_NORMAL
    
    # Step 5: Display startup banner
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                 ACS712 IoT Power Monitor                     ║
╠══════════════════════════════════════════════════════════════╣
║  Mode        : {'TEST' if test_mode else 'PRODUCTION'}                                 ║
║  Interval    : {interval} seconds                                            ║
║  Calibration : {'ENABLED' if calibration_zero_voltage else 'DISABLED'} ({'loaded' if calibration_zero_voltage else 'theoretical'})    ║
║  Protection  : {'ENABLED' if enable_protection else 'DISABLED'}                                   ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Step 6: Main monitoring loop
    loop_count = 0
    
    try:
        while True:
            loop_count += 1
            print(f"\n[Reading #{loop_count}] {datetime.now().strftime('%H:%M:%S')}")
            
            # Read power data with calibration and protection
            power_data = read_power_data(channel, calibration_zero_voltage, protection)
            
            if power_data:
                print(format_output(power_data))
                
                # Show protection statistics every 10 readings
                if protection and loop_count % 10 == 0:
                    stats = protection.get_stats()
                    if stats['warning_count'] > 0 or stats['critical_count'] > 0:
                        print(f"📊 Protection Stats: {stats['warning_count']} warnings, "
                              f"{stats['critical_count']} critical events")
            else:
                print("✗ Data collection failed, retrying...")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n✓ Program stopped by user.")
        if protection:
            stats = protection.get_stats()
            print(f"\n📊 Final Protection Statistics:")
            print(f"   Total warnings : {stats['warning_count']}")
            print(f"   Total critical : {stats['critical_count']}")
            
    except OvercurrentError as e:
        print(f"\n🔴 Program terminated due to overcurrent: {e}")
        
    except Exception as e:
        print(f"\n✗ Critical error: {e}")


# ========================= COMMAND LINE INTERFACE =========================

def print_usage():
    """Print usage instructions"""
    print("""
ACS712 Power Monitor - Usage:
==============================

Commands:
    python main.py              Normal operation (with calibration & protection)
    python main.py --test       Test mode (faster readings, 2 second interval)
    python main.py --calibrate  Run calibration only
    python main.py --no-protection  Disable overcurrent protection
    python main.py --help       Show this help message

Examples:
    # First time setup - calibrate your sensor
    python main.py --calibrate
    
    # Normal monitoring
    python main.py
    
    # Quick testing
    python main.py --test
    
    # Monitoring without protection (for testing)
    python main.py --no-protection
""")


# ========================= ENTRY POINT =========================

if __name__ == "__main__":
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Add help command 
    if "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)
    
    if "--calibrate" in args:
        # Calibration mode
        print("\n🔧 Starting calibration mode...")
        channel = init_mcp3008()
        if channel:
            run_calibration_routine(channel)
        else:
            print("✗ Failed to initialize hardware. Cannot calibrate.")
        sys.exit(0)
    
    # Normal operation mode
    test_mode = "--test" in args
    enable_protection = "--no-protection" not in args
    
    main_loop(
        test_mode=test_mode,
        enable_calibration=True,  # Always try to load calibration
        enable_protection=enable_protection
    )