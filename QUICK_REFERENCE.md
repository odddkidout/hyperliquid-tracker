# Quick Reference Card

## 🚀 Most Important Command

```bash
source venv/bin/activate
python leaderboard_analyzer.py --timeframe all --limit 50 --export
```

This analyzes ALL 28,953+ Hyperliquid traders across all timeframes!

---

## 📋 Common Commands

### Leaderboard Analysis

```bash
# Top 20 for the week (7 days)
python leaderboard_analyzer.py --timeframe week --limit 20

# Top 50 for 30 days
python leaderboard_analyzer.py --timeframe month --limit 50

# All-time top performers
python leaderboard_analyzer.py --timeframe allTime --limit 100

# Complete analysis (all timeframes)
python leaderboard_analyzer.py --timeframe all --limit 50
```

### Export & Save

```bash
# Export to JSON
python leaderboard_analyzer.py --timeframe all --export

# Save to database
python leaderboard_analyzer.py --timeframe all --save-db

# Both
python leaderboard_analyzer.py --timeframe all --export --save-db
```

### Find Best Traders

```bash
# By PnL
python leaderboard_analyzer.py --timeframe week --metric pnl --limit 30

# By ROI
python leaderboard_analyzer.py --timeframe month --metric roi --limit 30

# By Volume
python leaderboard_analyzer.py --timeframe allTime --metric volume --limit 30

# Consistent winners (>10% ROI across all periods)
python leaderboard_analyzer.py --min-roi 0.10 --export
```

---

## 📁 Key Files

### Main Tools

| File | Purpose |
|------|---------|
| `leaderboard_analyzer.py` | ⭐ Analyze ALL leaderboard accounts |
| `enhanced_tracker.py` | Deep analysis of specific accounts |
| `main.py` | Main system entry point |

### Run Commands

```bash
# Full leaderboard analysis
python leaderboard_analyzer.py --timeframe all --limit 50

# Deep individual analysis
python main.py --mode enhanced --addresses 0xAddr1,0xAddr2

# Copy trading (simulation)
python main.py --mode copytrade --testnet
```

---

## 📊 What You Get

### Leaderboard Data

- **28,953+ accounts** from Hyperliquid
- **4 timeframes**: Day, Week, Month, All-Time
- **3 rankings**: PnL, ROI, Volume
- **Instant results** (single API call)

### Metrics Per Account

- Address & display name
- Account value
- PnL (profit/loss)
- ROI (return %)
- Trading volume

---

## 🎯 Quick Workflows

### Find Top Performers

```bash
# 1. Get weekly top 50
python leaderboard_analyzer.py --timeframe week --limit 50 --export

# 2. Review JSON file
cat leaderboard_analysis_*.json | less

# 3. Note promising addresses
```

### Deep Analysis

```bash
# 1. Pick addresses from leaderboard
ADDRS="0xAddr1,0xAddr2,0xAddr3"

# 2. Deep analyze
python main.py --mode enhanced --addresses $ADDRS

# 3. Review detailed metrics
```

### Setup Copy Trading

```bash
# 1. Add to .env
echo "TRACKED_ADDRESSES=0xAddr1,0xAddr2,0xAddr3" >> .env

# 2. Test in simulation
python main.py --mode copytrade --testnet

# 3. Enable for real (when ready)
# Set COPY_TRADE_ENABLED=true in .env
python main.py --mode copytrade
```

---

## 📖 Documentation

| File | What's Inside |
|------|---------------|
| `FINAL_SUMMARY.md` | Complete overview |
| `LEADERBOARD_GUIDE.md` | Detailed leaderboard guide |
| `ENHANCED_ANALYSIS_GUIDE.md` | Deep analysis guide |
| `QUICK_START.md` | Basic setup |
| `PROJECT_SUMMARY.md` | Full system features |

---

## ⚡ One-Liners

```bash
# Quick weekly snapshot
python leaderboard_analyzer.py --timeframe week --limit 10

# Export top 100
python leaderboard_analyzer.py --timeframe all --limit 100 --export

# Find 20%+ ROI traders
python leaderboard_analyzer.py --min-roi 0.20

# Save everything to database
python leaderboard_analyzer.py --timeframe all --save-db
```

---

## 🔥 Pro Tips

1. **Start with week timeframe** - Good balance of data
2. **Export data** - Keep historical snapshots
3. **Compare timeframes** - Look for consistency
4. **Check volume** - Avoid market makers (too high)
5. **Use database** - Track changes over time

---

## 📈 Example Output

```
LEADERBOARD - 7 DAYS - RANKED BY PnL
══════════════════════════════════════════════════════════════════
Rank  Address          Name    PnL            ROI      Volume
──────────────────────────────────────────────────────────────────
1     0xb317...83ae    -       $16,493,176    7.46%    $66M
2     0xa312...ad1e    -       $4,499,176     16.53%   $16M
3     0x35d1...acb1    -       $3,369,408     13.17%   $22M
...
```

---

## ⚙️ System Status

✅ **28,953+ accounts** analyzed
✅ **4 timeframes** (Day, Week, Month, All-Time)
✅ **3 metrics** (PnL, ROI, Volume)
✅ **JSON export** available
✅ **Database storage** working
✅ **Copy trading** ready

---

## 🆘 Quick Help

**Can't find addresses?**
→ Use the leaderboard analyzer!

**Want detailed analysis?**
→ Use enhanced mode with specific addresses

**Ready to copy trade?**
→ Add addresses to `.env` and run copy trader

**Need historical data?**
→ Use `--export` and save JSON files

---

**Ready to start?**

```bash
source venv/bin/activate
python leaderboard_analyzer.py --timeframe all --limit 50
```

🚀 **Happy trading!**
