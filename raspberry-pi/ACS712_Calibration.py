"""
calibration.py - ACS712 Zero-Point Calibration Module
====================================================

This module handles zero-point calibration for ACS712 current sensor.

Why calibration is needed:
- Manufacturing tolerances (±1.5% sensitivity error)
- Power supply variance (4.8V-5.2V instead of exactly 5V)
- Solder joint resistance and PCB trace impedance
- Temperature drift over time

Without calibration, readings may have 2-5% error.

Steps: 
    1. Disconnect load, run calibration to measure actual zero voltage
    2. Save measured zero voltage to file
    3. Load calibration in main program to get accurate current readings    
            
"""

import json
import os
import time
from datetime import datetime

# ========================= CONFIGURATION =========================

# ACS712 Parameters (ACS712-20A)
ACS712_VCC = 5.0                    # Supply voltage to ACS712
ACS712_THEORETICAL_OFFSET = 0.5     # 50% offset (2.5V when no current)

# Calibration file
CALIBRATION_FILE = "calibration.json"

# Calibration settings
CALIBRATION_SAMPLES = 200           # Number of samples for calibration
CALIBRATION_DELAY = 3               # Seconds to wait before calibration


# ========================= CALIBRATION CLASS =========================

class Calibration:
    """
    Handles zero-point calibration for ACS712 sensor.
    
    Usage:
        # Perform calibration
        zero_v = Calibration.measure_zero_voltage(channel)
        Calibration.save_calibration(zero_v)
        
        # Load existing calibration
        cal_data = Calibration.load_calibration()
        zero_voltage = cal_data['zero_voltage']
    """
    
    @staticmethod
    def measure_zero_voltage(channel, samples=CALIBRATION_SAMPLES):
        """
        Measure the actual zero-current voltage output.
        
        Usage: 
            1. Disconnect the load (ensure no current through ACS712)
            2. Run this function
            3. Save the measured value as the new zero-point
        
        Args:
            channel: MCP3008 analog input channel
            samples (int): Number of samples for averaging
            
        Returns:
            float: Measured zero voltage in volts
            
        Example:
            >>> zero_v = Calibration.measure_zero_voltage(channel)
            🔧 Calibration: Please ensure NO current through ACS712...
            ✓ Zero voltage measured: 2.512 V
        """
        print("\n" + "="*60)
        print("🔧 CALIBRATION MODE")
        print("="*60)
        print("⚠️  IMPORTANT: Please DISCONNECT the load/current source!")
        print("   The sensor must have ZERO current flowing through it.")
        print(f"   Waiting {CALIBRATION_DELAY} seconds for stable reading...")
        print("-"*60)
        
        time.sleep(CALIBRATION_DELAY)
        
        # Read multiple samples for stability
        total = 0
        for i in range(samples):
            if channel:
                total += channel.value
            time.sleep(0.001)
        
        adc_average = total / samples
        measured_voltage = Calibration._adc_to_voltage(adc_average)
        theoretical_voltage = ACS712_VCC * ACS712_THEORETICAL_OFFSET
        
        print(f"\n📊 Calibration Results:")
        print(f"   ADC value    : {adc_average:.1f} / 65535")
        print(f"   Measured     : {measured_voltage:.4f} V")
        print(f"   Theoretical  : {theoretical_voltage:.4f} V")
        print(f"   Offset error : {(measured_voltage - theoretical_voltage)*1000:.2f} mV")
        print("="*60)
        
        return measured_voltage
    
    @staticmethod
    def _adc_to_voltage(adc_value):
        """Helper: Convert ADC raw to voltage"""
        return (adc_value / 65535.0) * ACS712_VCC
    
    @staticmethod
    def save_calibration(zero_voltage):
        """
        Save calibration values to file for persistence across reboots.
        
        Args:
            zero_voltage (float): Measured zero-current voltage
            
        Returns:
            dict: Saved calibration data
        """
        calibration_data = {
            "zero_voltage": round(zero_voltage, 4),
            "theoretical_zero": round(ACS712_VCC * ACS712_THEORETICAL_OFFSET, 4),
            "timestamp": datetime.now().isoformat(),
            "vcc": ACS712_VCC,
            "offset_ratio": ACS712_THEORETICAL_OFFSET
        }
        
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(calibration_data, f, indent=2)
        
        print(f"✓ Calibration saved to {CALIBRATION_FILE}")
        return calibration_data
    
    @staticmethod
    def load_calibration():
        """
        Load previously saved calibration values.
        
        Returns:
            dict or None: Calibration data if file exists, None otherwise
        """
        if os.path.exists(CALIBRATION_FILE):
            with open(CALIBRATION_FILE, 'r') as f:
                data = json.load(f)
            print(f"✓ Loaded calibration from {CALIBRATION_FILE}")
            print(f"   Zero voltage: {data['zero_voltage']} V")
            print(f"   Date: {data.get('timestamp', 'unknown')}")
            return data
        else:
            print("ℹ️  No calibration file found. Using theoretical values.")
            print("   Run --calibrate to perform calibration.")
            return None
    
    @staticmethod
    def get_calibrated_zero_voltage():
        """
        Convenience function to get calibrated zero voltage.
        
        Returns:
            float: Calibrated zero voltage, or theoretical if no calibration exists
        """
        cal_data = Calibration.load_calibration()
        if cal_data:
            return cal_data['zero_voltage']
        else:
            return ACS712_VCC * ACS712_THEORETICAL_OFFSET
    
    @staticmethod
    def clear_calibration():
        """Delete the calibration file"""
        if os.path.exists(CALIBRATION_FILE):
            os.remove(CALIBRATION_FILE)
            print("✓ Calibration file deleted")
        else:
            print("ℹ️ No calibration file to delete")


# ========================= STANDALONE CALIBRATION SCRIPT =========================

def run_calibration(channel):
    """Run calibration routine and save results"""
    zero_v = Calibration.measure_zero_voltage(channel)
    Calibration.save_calibration(zero_v)
    print("\n✓ Calibration complete! You can now run the main program.")
    return zero_v


# ========================= TEST FUNCTION =========================

def verify_calibration(channel):
    """
    Verify if calibration is still accurate.
    
    Args:
        channel: MCP3008 analog input channel
        
    Returns:
        bool: True if calibration is still valid, False otherwise
    """
    cal_data = Calibration.load_calibration()
    if not cal_data:
        print("✗ No calibration to verify")
        return False
    
    print("\n🔍 Verifying calibration...")
    print("Ensure NO current flowing through sensor...")
    time.sleep(2)
    
    # Take quick measurement
    total = 0
    for _ in range(50):
        total += channel.value
        time.sleep(0.001)
    
    current_voltage = Calibration._adc_to_voltage(total / 50)
    saved_zero = cal_data['zero_voltage']
    error = abs(current_voltage - saved_zero) * 1000  # in mV
    
    print(f"   Saved zero: {saved_zero:.4f} V")
    print(f"   Current    : {current_voltage:.4f} V")
    print(f"   Drift      : {error:.2f} mV")
    
    if error < 50:  # Less than 50mV drift is acceptable
        print("✓ Calibration is still valid")
        return True
    else:
        print("⚠️ Calibration drift detected! Consider recalibrating.")
        return False


# ========================= MAIN (when run directly) =========================

if __name__ == "__main__":
    print("Calibration module - Import this into your main program")
    print("\nUsage example:")
    print("  from calibration import Calibration")
    print("  cal_data = Calibration.load_calibration()")
    print("  zero_voltage = cal_data['zero_voltage']")