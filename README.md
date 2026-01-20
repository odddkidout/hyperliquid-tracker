# Hyperliquid Tracker & Copy Trading System

A **professional-grade** system to track ALL 28,953+ Hyperliquid traders with **beautiful web dashboard** and powerful CLI tools.

## 🌟 Features

### 🌐 Web Dashboard (NEW!)
- **Beautiful UI** with interactive charts and tables
- **Real-time updates** every 60 seconds
- **Multi-timeframe analysis** (24h, 7d, 30d, All-time)
- **Sortable leaderboard** with search functionality
- **Responsive design** for all devices

### ⌨️ CLI Tools
- **Leaderboard Analysis**: Track ALL 28,953+ accounts
- **Performance Analytics**: PnL, ROI, Volume across timeframes
- **Enhanced Tracking**: Deep dive into specific accounts
- **Copy Trading**: Automatically replicate successful traders
- **Data Export**: JSON, CSV, Database storage

## 🚀 Quick Start

### Web Dashboard (Recommended)

```bash
# Start beautiful web interface
./start_dashboard.sh
```

Then open: **http://localhost:8080**

### CLI Analysis

```bash
# Activate environment
source venv/bin/activate

# Analyze entire leaderboard
python leaderboard_analyzer.py --timeframe all --limit 50
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start using immediately:
```bash
# Web Dashboard
./start_dashboard.sh

# OR CLI Tools
python leaderboard_analyzer.py --timeframe week --limit 20
```

## Configuration

Edit `.env` to configure:
- API credentials
- Minimum win rate threshold
- Position size multiplier for copy trading
- Risk management parameters

## Usage

### Track Top Accounts
```bash
python main.py --mode track
```

### Copy Trade
```bash
python main.py --mode copytrade
```

### View Analytics
```bash
python main.py --mode analytics
```

## Safety Warning

Copy trading involves significant risk. Always:
- Start with small position sizes
- Monitor the system closely
- Set appropriate stop losses
- Only trade with capital you can afford to lose
