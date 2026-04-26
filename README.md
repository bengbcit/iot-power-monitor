# IoT电力监控系统

## 🎯 项目目标
实时监控电力消耗，使用树莓派采集数据，通过Claude API进行数据分析，存储到Supabase，展示在Next.js仪表板。

## 🏗️ 系统架构

```
	Raspberry Pi 4 (温湿度/电力传感器)
	      ↓ USB / 网络
	   Python脚本 (读取传感器数据)
	      ↓ REST API
	   Claude API (数据分析 & 异常检测)
	      ↓ JSON响应
	   Supabase (PostgreSQL数据库)
	      ↓ Real-time
	   Next.js Dashboard (React可视化)
	      ↓
	   用户浏览器 (图表 & 实时数据)
```

## 📋 核心功能

- [ ] Raspberry Pi读取电力传感器数据
- [ ] 通过Claude API进行实时分析
- [ ] 存储到Supabase数据库
- [ ] Next.js仪表板展示
- [ ] 异常警告系统

## 🛠️ 技术栈

- **硬件**：Raspberry Pi 4 (4GB)
- **传感器**：ACS712电流传感器
- **后端**：Python + Claude API + Supabase
- **前端**：Next.js + TypeScript + Tailwind CSS
- **部署**：Vercel (前端) + Supabase (后端)

## 📚 学习路径

Week 1-2：硬件组装 + Python基础
Week 3-4：Claude API集成
Week 5-6：Supabase数据库
Week 7-8：Next.js仪表板

## 🚀 开发进度

- [ ] Week 1 (4/23-4/27)：架构设计 ← **现在**
- [ ] Week 2 (4/28-5/4)：Raspberry Pi OS安装 + Python传感器读取
- [ ] Week 3-4：Claude API集成
- [ ] ...
