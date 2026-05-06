# IoT Power Monitor - ACS712 Current Monitoring System

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
- [ ] Week 3-4: Claude API Integration / Claude API統合
- [ ] ...
```