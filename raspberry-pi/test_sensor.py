#!/usr/bin/env python3
"""fast way to test sensor reading functions without waiting for the main loop"""

from main import (
    init_mcp3008, read_adc_raw, adc_to_voltage,
    voltage_to_current, calculate_power, read_power_data
)

print("🧪 ACS712 Sensor Test\n")

# 初始化
mcp = init_mcp3008()
if not mcp:
    exit(1)

print("\n1️⃣ ADC raw value...")
adc = read_adc_raw(mcp)
print(f"   ADC value: {adc} / 65535" if adc else "   ✗ failed")

print("\n2️⃣ voltage conversion...")
voltage = adc_to_voltage(adc) if adc else None
print(f"   voltage: {voltage}V" if voltage else "   ✗ failed")

print("\n3️⃣ current calculation...")
current = voltage_to_current(voltage) if voltage else None
print(f"   current: {current}A" if current is not None else "   ✗ failed")

print("\n4️⃣ power calculation...")
power = calculate_power(current) if current is not None else None
print(f"   power: {power}W" if power is not None else "   ✗ failed")

print("\n5️⃣ read power data...")
power_data = read_power_data(mcp)
if power_data:
    print(f"   ✓ success")
    print(f"   ADC: {power_data['adc_value']}")
    print(f"   current: {power_data['current_a']}A")
    print(f"   power: {power_data['power_w']}W")
else:
    print(f"   ✗ failed")