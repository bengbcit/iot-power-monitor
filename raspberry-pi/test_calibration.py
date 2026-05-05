# test_calibration.py - 测试校准模块

import board
import busio
import digitalio
import time

# 导入校准模块
from ACS712_Calibration import Calibration

# 初始化 MCP3008
def init_mcp3008():
    spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.D8)
    
    import adafruit_mcp3xxx.mcp3008 as MCP
    from adafruit_mcp3xxx.analog_in import AnalogIn
    
    mcp = MCP.MCP3008(spi, cs)
    channel = AnalogIn(mcp, MCP.P0)
    return channel

# 主程序
print("="*50)
print("ACS712 Calibration Test")
print("="*50)

# 初始化硬件
channel = init_mcp3008()
print("✓ MCP3008 initialized")

# 尝试加载已有的校准
cal_data = Calibration.load_calibration()

if cal_data:
    print(f"\n✓ 已有校准文件:")
    print(f"   零点电压: {cal_data['zero_voltage']} V")
    print(f"   校准时间: {cal_data['timestamp']}")
    
    # 验证当前零点（需要断开负载）
    print("\n🔍 验证校准（请确保无负载）...")
    time.sleep(2)
    
    # 读取当前电压
    total = 0
    for _ in range(100):
        total += channel.value
        time.sleep(0.001)
    current_voltage = (total / 100 / 65535.0) * 5.0
    
    print(f"   当前电压: {current_voltage:.4f} V")
    print(f"   保存零点: {cal_data['zero_voltage']:.4f} V")
    print(f"   偏差: {(current_voltage - cal_data['zero_voltage'])*1000:.2f} mV")
    
else:
    print("\n⚠️ 没有找到校准文件")
    print("请先运行校准:")
    print("  1. 断开负载（确保 ACS712 无电流）")
    print("  2. 运行以下代码进行校准")
    
    input("\n按 Enter 开始校准...")
    
    # 执行校准
    zero_v = Calibration.measure_zero_voltage(channel)
    Calibration.save_calibration(zero_v)
    print(f"\n✓ 校准完成！零点电压: {zero_v:.4f} V")
