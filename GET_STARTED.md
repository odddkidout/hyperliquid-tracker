# 🚀 Get Started in 5 Minutes

## Quick Start Guide

### Step 1: Install Dependencies (1 minute)
```bash
cd hyperliquid
pip install -r requirements.txt
```

### Step 2: Configure Settings (1 minute)
```bash
# Copy the example config
cp .env.example .env

# Edit if needed (optional - API keys NOT required for tracking)
nano .env
```

### Step 3: Test Connection (1 minute)
```bash
# Verify everything works
python test_connection.py
```

### Step 4: Start Tracking (2 minutes)
```bash
# Track top accounts
python main.py --mode track

# OR use the interactive menu
./quickstart.sh
```

That's it! You're now tracking top Hyperliquid traders.

---

## What to Do Next?

### Option A: Just Track & Analyze (No Trading)
```bash
# Let it run for a few days to collect data
python main.py --mode track --continuous

# Then analyze the results
python main.py --mode analytics --details
```

### Option B: Test Copy Trading (Simulation - Safe!)
```bash
# Monitor copy trade opportunities (won't execute)
python main.py --mode copytrade --testnet
```

### Option C: View Live Dashboard
```bash
# Open a nice real-time dashboard
python dashboard.py
```

---

## Important Notes

✅ **Safe by Default**
- Copy trading is DISABLED by default
- No API keys required for tracking
- Everything runs locally on your machine

⚠️ **Before Live Trading**
- Collect data for at least 1-2 weeks
- Test extensively on testnet
- Start with TINY position sizes
- Understand the risks

📚 **Documentation**
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Architecture diagrams
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete overview

---

## File Overview

| File | Purpose |
|------|---------|
| `main.py` | Main entry point - run tracking, copy trading, analytics |
| `dashboard.py` | Real-time dashboard with auto-refresh |
| `quickstart.sh` | Interactive setup and launcher |
| `test_connection.py` | Test API and system functionality |
| `export_data.py` | Export data to CSV for analysis |

---

## Common Commands

```bash
# Track once
python main.py --mode track

# Track continuously (every 5 min)
python main.py --mode track --continuous --interval 300

# View top performers
python main.py --mode analytics

# Copy trading (simulation)
python main.py --mode copytrade --testnet

# Export data
python export_data.py --type all

# Live dashboard
python dashboard.py
```

---

## Need Help?

1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
2. Check [EXAMPLES.md](EXAMPLES.md) for usage examples
3. Review [VISUAL_GUIDE.md](VISUAL_GUIDE.md) for architecture

---

## Safety Reminder

⚠️ **This is NOT financial advice**
- Trading involves substantial risk
- Only trade with money you can afford to lose
- Past performance doesn't guarantee future results
- Always start with simulation mode

**Use at your own risk!**

---

Ready to start? Run:
```bash
./quickstart.sh
```

Or jump straight to tracking:
```bash
python main.py --mode track
```

Happy tracking! 📊
