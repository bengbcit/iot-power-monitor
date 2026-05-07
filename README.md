# IoT Power Monitor - ACS712 Current Monitoring System
```bash
*Updated 2026/5/7*

Raspberry Pi + ACS712 Current Sensor + MCP3008 ADC + Claude API intelligent power monitoring system

---

## 📋 Table of Contents

- [Hardware Requirements](#hardware-requirements)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Hardware Wiring](#hardware-wiring)
- [Quick Start](#quick-start)
- [Calibration](#calibration)
- [Overcurrent Protection](#overcurrent-protection)
- [File Structure](#file-structure)
- [Troubleshooting](#troubleshooting)
- [Project Goal](#project-goal)
- [System Architecture](#system-architecture)
- [Core Features](#core-features)
- [Learning Path](#learning-path)
- [Development Progress](#development-progress)

---

## Hardware Requirements

- Raspberry Pi 4 (4GB+)
- ACS712-20A Current Sensor ×2
- MCP3008 8-channel ADC Converter
- Breadboard + Jumper Wires

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Hardware Interface | SPI (MCP3008) |
| Sensor | ACS712 20A (100mV/A) |
| Data Acquisition | Adafruit CircuitPython |
| AI Analysis | Claude 3.5 Sonnet API |
| Database | Supabase PostgreSQL |
| Web Dashboard | Next.js Dashboard |

---

## Features

- ✅ Real-time current acquisition (via MCP3008 ADC)
- ✅ Automatic power calculation (W)
- ✅ Zero-point calibration for accuracy
- ✅ Overcurrent protection (Warning/Critical thresholds)
- ✅ Claude AI anomaly detection
- ✅ Persistent data storage
- ✅ Multi-language support

---

## Hardware Wiring / ハードウェア配線

### MCP3008 to Raspberry Pi / MCP3008 から Raspberry Pi へ

| MCP3008 Pin | Function | Raspberry Pi (BOARD) | Raspberry Pi (BCM) |
|-------------|----------|----------------------|--------------------|
| Pin 16      | VDD      | Pin 2 (5V)           | -                  |
| Pin 15      | VREF     | Pin 2 (5V)           | -                  |
| Pin 14      | AGND     | Pin 6 (GND)          | -                  |
| Pin 9       | DGND     | Pin 6 (GND)          | -                  |
| Pin 13      | CLK      | Pin 23               | GPIO 11            |
| Pin 12      | DOUT     | Pin 21               | GPIO 9             |
| Pin 11      | DIN      | Pin 19               | GPIO 10            |
| Pin 10      | CS       | Pin 24               | GPIO 8             |
| Pin 1       | CH0      | -                    | ACS712 VOUT        |

### ACS712 Connections / ACS712 接続

| ACS712 Pin | Connection |
|------------|------------|
| VCC | External 5V Power Supply (+) |
| GND | External 5V Power Supply (-) + Raspberry Pi GND |
| VOUT | MCP3008 CH0 |
| IP+ | Power Supply (+) → Load (+) |
| IP- | Load (-) → Power Supply (-) |

⚠️ **Important / 重要**: External power supply GND must connect to Raspberry Pi GND for common ground reference.
外部電源のGNDは、共通グランド基準のためにRaspberry PiのGNDに接続する必要があります。

---

## Quick Start

### 1. Hardware Wiring
Connect MCP3008 and ACS712 according to the wiring table above.

### 2. Install Dependencies
see requirements.txt

### 3. Run Scripts
# Test mode (fast readings for debugging)
python3 sensor_reader.py --test

# Normal operation
python3 sensor_reader.py

# Run calibration only
python3 sensor_reader.py --calibrate

Calibration / キャリブレーション
Before first use, calibrate the sensor with no load connected:
# Disconnect load from IP+ and IP- (no current flowing)
python3 sensor_reader.py --calibrate

Calibration File Example:
    {
    "zero_voltage": 2.5719,
    "theoretical_zero": 2.5000,
    "timestamp": "2026-05-06T17:24:12.883663",
    "vcc": 5.0
    }

Overcurrent Protection / 過電流保護
The system includes configurable warning and critical thresholds:

Level	Threshold	Behavior
Normal	< 15.0A	Normal operation
Warning	15.0A - 18.0A	Log alert, continue monitoring
Critical	≥ 18.0A	Emergency stop, raise exception

Configuration
Edit the thresholds in sensor_reader.py:

    WARNING_THRESHOLD = 15.0       # Warning at 15A
    CRITICAL_THRESHOLD = 18.0      # Critical at 18A
    AUTO_SHUTDOWN = True           # Enable emergency stop

Disable Protection (Testing Only)
    python3 sensor_reader.py --no-protection

Overcurrent Log
    When overcurrent occurs, events are logged to overcurrent_log.txt:
        text
        [2026-05-06 17:31:31] WARNING: 15.50A
        [2026-05-06 17:31:33] CRITICAL: 18.20A

File Structure / ファイル構成
    iot-power-monitor/
    ├── sensor_reader.py              # Main program (integrates all modules)
    ├── ACS712_Calibration.py       # Zero-point calibration module
    ├── ACS712_Overcurrent.py       # Overcurrent protection module
    ├── test_calibration.py  # Calibration test script
    ├── test_sensor.py       # Sensor reading test ACS712 script
    └── README.md            # This file\
    ├── analyzer.py          # Claude API analysis module
    architecture/
    ├── requirements.txt     # Python dependencies

Troubleshooting / トラブルシューティング
    Issue 1: Voltage reads ~3.78V with no load
    Cause: MCP3008 VREF connected to 3.3V instead of 5V
    Solution: Connect VREF to Raspberry Pi Pin 2 (5V)

        Before: VREF → Pin 1 (3.3V) ❌
        After:  VREF → Pin 2 (5V)  ✅

    Issue 2: Negative current reading
    Cause: IP+ and IP- connections reversed
    Solution: Swap IP+ and IP- wiring, or use abs(current) in code

    Issue 3: Large offset error (>100mV) after calibration
    Cause: Load was connected during calibration
    Solution: Disconnect load and re-run calibration

        python3 sensor_reader.py --calibrate

    Issue 4: SPI communication fails
        Checklist:
            SPI enabled: sudo raspi-config → Interface Options → SPI → Enable
            Wiring matches the table above
            Reboot after enabling SPI: sudo reboot

    Issue 5: No readings or all zeros
    Check:
        MCP3008 VDD and VREF have 5V power
        MCP3008 GND connected to Raspberry Pi GND
        ACS712 VOUT connected to MCP3008 CH0

```



# Updated 2026/5/6
```bash
Raspberry Pi + ACS712 Current Sensor + MCP3008 ADC + Claude API intelligent power monitoring system

## Hardware Requirements
- Raspberry Pi 4 (4GB+)
- ACS712-20A Current Sensor ×2
- MCP3008 8-channel ADC Converter
- Breadboard + Jumper Wires

## Tech Stack
- **Hardware Interface**: SPI (MCP3008)
- **Sensor**: ACS712 20A (100mV/A)
- **Data Acquisition**: Adafruit CircuitPython
- **AI Analysis**: Claude 3.5 Sonnet API
- **Database**: Supabase PostgreSQL
- **Web Dashboard**: Next.js Dashboard (Week 3)

## Features
- ✅ Real-time current acquisition (via MCP3008 ADC)
- ✅ Automatic power calculation (W)
- ✅ Claude AI anomaly detection
- ✅ Persistent data storage
- ✅ Multi-language support

## Quick Start

### 1. Hardware Wiring
Connect MCP3008 and ACS712 according to documentation

### 2. Install Dependencies
pip install -r requirements.txt
```


```bash
🎯 Project Goal / プロジェクト目標
Real-time power consumption monitoring using Raspberry Pi for data collection, Claude API for analysis, Supabase for storage, and Next.js dashboard for visualization.
ラズベリーパイを使用したリアルタイム電力消費モニタリング、データ収集、Claude APIによる分析、Supabaseによる保存、Next.jsダッシュボードによる可視化。

## 🏗️ System Architecture / システムアーキテクチャ
Raspberry Pi 4 (Temperature/Humidity/Power Sensors) / ラズベリーパイ4（温湿度/電力センサー）
↓ USB / Network / USB/ネットワーク
Python Script (Sensor Data Reading) / Pythonスクリプト（センサーデータ読み取り）
↓ REST API / REST API
Claude API (Data Analysis & Anomaly Detection) / Claude API（データ分析 & 異常検出）
↓ JSON Response / JSONレスポンス
Supabase (PostgreSQL Database) / Supabase（PostgreSQLデータベース）
↓ Real-time / リアルタイム
Next.js Dashboard (React Visualization) / Next.jsダッシュボード（React可視化）
↓
User Browser (Charts & Real-time Data) / ユーザーブラウザ（チャート & リアルタイムデータ）



## 📋 Core Features / コア機能

- [x] Raspberry Pi reads power sensor data / ラズベリーパイで電力センサーデータを読み取り
- [ ] Real-time analysis via Claude API / Claude APIによるリアルタイム分析
- [ ] Store to Supabase database / Supabaseデータベースに保存
- [ ] Display on Next.js dashboard / Next.jsダッシュボードで表示
- [ ] Anomaly alert system / 異常警報システム

## 🛠️ Tech Stack / 技術スタック

- **Hardware / ハードウェア**: Raspberry Pi 4 (4GB)
- **Sensor / センサー**: ACS712 Current Sensor / ACS712電流センサー
- **Backend / バックエンド**: Python + Claude API + Supabase
- **Frontend / フロントエンド**: Next.js + TypeScript + Tailwind CSS
- **Deployment / デプロイ**: Vercel (Frontend) + Supabase (Backend)

## 📚 Learning Path / 学習パス

- Week 1-2 / 第1-2週: Hardware Assembly + Python Basics / ハードウェア組立て + Python基礎 ✅
- Week 3-4 / 第3-4週: Claude API Integration / Claude API統合
- Week 5-6 / 第5-6週: Supabase Database / Supabaseデータベース
- Week 7-8 / 第7-8週: Next.js Dashboard / Next.jsダッシュボード

## 🚀 Development Progress / 開発進捗

- [x] Week 1 (4/23-4/27): Architecture Design 
- [x] Week 2 (4/28-5/4): Raspberry Pi OS Installation + Python Sensor Reading / Raspberry Pi OSインストール + Pythonセンサー読み取り
- [x] Week 3-4: Claude API Integration / Claude API統合
- [ ] Week 5-6: Supabase Database
- [ ] Week 7-8: Next.js Dashboard

📄 License
MIT License

```