# Hyperliquid Leaderboard Analysis Guide

## 🎉 Complete Leaderboard Integration!

Your system now analyzes **ALL 28,953+ accounts** from the real Hyperliquid leaderboard across multiple timeframes with PnL and ROI metrics.

## Quick Start

```bash
source venv/bin/activate

# Analyze entire leaderboard (all timeframes)
python leaderboard_analyzer.py --timeframe all --limit 50

# Export to JSON
python leaderboard_analyzer.py --timeframe all --limit 100 --export

# Save to database
python leaderboard_analyzer.py --timeframe all --save-db
```

## What You Get

### Comprehensive Multi-Timeframe Analysis

The system fetches and analyzes:
- **28,953+ traders** from the official Hyperliquid leaderboard
- **4 timeframes**: Day, Week (7d), Month (30d), All-Time (lifetime)
- **3 key metrics**: PnL, ROI, Trading Volume

### Leaderboard Rankings

#### 1. Top Performers by PnL
Shows accounts with highest absolute profits across timeframes.

Example (7-day PnL leaders):
```
Rank  Address                      Name      PnL             ROI      Volume          Acct Value
1     0xb317...83ae                -         $16,493,176     7.46%    $66M            $237M
2     0xa312...ad1e                -         $4,499,176      16.53%   $16M            $27M
3     0x35d1...acb1                -         $3,369,408      13.17%   $22M            $22M
```

#### 2. Top Performers by ROI
Shows accounts with highest percentage returns.

#### 3. Highest Volume Traders
Shows most active traders by trading volume.

### Data for Each Account

- **Address**: Ethereum address
- **Display Name**: Username (if set)
- **Account Value**: Current portfolio value
- **PnL**: Profit/Loss in USDC
- **ROI**: Return on Investment (%)
- **Volume**: Total trading volume

## Command Options

### Basic Commands

```bash
# Show top 20 traders for specific timeframe
python leaderboard_analyzer.py --timeframe week --limit 20

# Show top 50 by ROI for 30 days
python leaderboard_analyzer.py --timeframe month --metric roi --limit 50

# Analyze entire leaderboard (all timeframes)
python leaderboard_analyzer.py --timeframe all --limit 100
```

### Timeframe Options

- `day` - Last 24 hours
- `week` - Last 7 days
- `month` - Last 30 days
- `allTime` - Complete history
- `all` - Show all timeframes (comprehensive report)

### Metric Options

- `pnl` - Rank by profit/loss
- `roi` - Rank by ROI percentage
- `volume` - Rank by trading volume

### Advanced Filters

```bash
# Find consistent performers (>10% ROI in all timeframes)
python leaderboard_analyzer.py --min-roi 0.1

# Top 100 traders, export to JSON
python leaderboard_analyzer.py --limit 100 --export

# Save all leaderboard data to database
python leaderboard_analyzer.py --save-db
```

## Real Analysis Results

### Top 7-Day PnL Leaders

| Rank | Address | PnL | ROI | Account Value |
|------|---------|-----|-----|---------------|
| 1 | 0xb317...83ae | $16.5M | 7.46% | $237.5M |
| 2 | 0xa312...ad1e | $4.5M | 16.53% | $27.1M |
| 3 | 0x35d1...acb1 | $3.4M | 13.17% | $22.3M |

### Top All-Time Volume

| Rank | Address | Volume | PnL | ROI |
|------|---------|--------|-----|-----|
| 1 | ABC | $575.7B | $26.9M | 47.15% |
| 2 | 0x87f9...2cf | $369.9B | $20.0M | 18.41% |
| 3 | Auros | $219.3B | $64.7M | 384.15% |

## Output Files

### JSON Export

When using `--export`, creates a file like:
```
leaderboard_analysis_20260119_201303.json
```

Contains full data for all analyzed accounts:
```json
[
  {
    "address": "0x87f9cd15f5050a9283b8896300f7c8cf69ece2cf",
    "display_name": null,
    "account_value": 77281757.52,
    "day": {
      "pnl": 3311930.43,
      "roi": 0.054,
      "volume": 762239261.91
    },
    "week": {
      "pnl": 1497248.80,
      "roi": 0.024,
      "volume": 6695841380.29
    },
    ...
  }
]
```

### Database Storage

When using `--save-db`, saves all accounts to SQLite database for later analysis.

## Use Cases

### 1. Find Top Performers

```bash
# Top 50 traders by 30-day ROI
python leaderboard_analyzer.py --timeframe month --metric roi --limit 50
```

### 2. Identify Copy Trade Candidates

```bash
# Consistent performers with >15% ROI across all periods
python leaderboard_analyzer.py --min-roi 0.15 --export
```

Then review the exported JSON to find addresses for copy trading.

### 3. Market Analysis

```bash
# See highest volume traders (market makers)
python leaderboard_analyzer.py --timeframe month --metric volume --limit 30
```

### 4. Complete Research

```bash
# Generate full report across all timeframes
python leaderboard_analyzer.py --timeframe all --limit 100 --export --save-db
```

This gives you:
- Comprehensive leaderboards for all timeframes
- JSON export for further analysis
- Database storage for tracking over time

## Integration with Main System

The leaderboard analyzer integrates with the main system:

```bash
# Option 1: Use standalone leaderboard analyzer (RECOMMENDED)
python leaderboard_analyzer.py --timeframe all --limit 50

# Option 2: Use main.py with enhanced mode
# (This fetches individual trade history - slower but more detailed)
ADDRESSES=$(python leaderboard_analyzer.py --timeframe week --limit 10 2>/dev/null | grep "0x" | awk '{print $2}' | head -10 | tr '\n' ',')
python main.py --mode enhanced --addresses $ADDRESSES
```

## Performance Notes

- **Fast**: Analyzes 28,953 accounts in seconds (uses pre-calculated leaderboard data)
- **Efficient**: Single API call fetches all leaderboard data
- **Comprehensive**: No need to fetch individual trade histories
- **Real-time**: Data is current from Hyperliquid's stats API

## Finding Copy Trade Candidates

### Step 1: Run Full Analysis

```bash
python leaderboard_analyzer.py --timeframe all --limit 100 --export
```

### Step 2: Review Results

Look for accounts with:
- **Consistent positive ROI** across timeframes
- **Reasonable trading volume** (not too high = institutional)
- **Sustainable PnL** (not one-off wins)

### Step 3: Extract Addresses

From the leaderboard output or JSON file, collect addresses of top performers.

### Step 4: Set Up Copy Trading

Add addresses to `.env`:
```
TRACKED_ADDRESSES=0xAddr1,0xAddr2,0xAddr3
```

Then start copy trading:
```bash
python main.py --mode copytrade
```

## Example Workflows

### Workflow 1: Daily Top Traders Report

```bash
#!/bin/bash
# daily_report.sh

source venv/bin/activate

DATE=$(date +%Y%m%d)

# Generate daily report
python leaderboard_analyzer.py \
  --timeframe day \
  --limit 20 \
  --export > reports/daily_$DATE.txt

echo "Report saved to reports/daily_$DATE.txt"
```

### Workflow 2: Find Consistent Winners

```bash
# Get traders with >20% ROI in all timeframes
python leaderboard_analyzer.py --min-roi 0.20 --export

# Review the consistent_performers section
# Extract addresses for copy trading
```

### Workflow 3: Weekly Leaderboard Update

```bash
#!/bin/bash
# weekly_update.sh

source venv/bin/activate

# Full analysis with database update
python leaderboard_analyzer.py \
  --timeframe all \
  --limit 100 \
  --export \
  --save-db

# This updates your local database with latest stats
echo "Weekly leaderboard update complete!"
```

## Tips

1. **Start with "week" timeframe** - Good balance of data and relevance
2. **Look at multiple metrics** - Don't just focus on PnL or ROI alone
3. **Check consistency** - Compare performance across timeframes
4. **Watch volume** - Very high volume = likely market maker
5. **Export data** - Keep historical snapshots for comparison
6. **Use database** - Track changes over time

## Comparison: Leaderboard vs Enhanced Analysis

### Leaderboard Analyzer (leaderboard_analyzer.py)
✅ Analyzes ALL 28,953 accounts instantly
✅ Pre-calculated PnL, ROI, Volume from Hyperliquid
✅ Fast and efficient
✅ Great for discovering traders
❌ No individual trade details
❌ No win rate or trade count

### Enhanced Tracker (enhanced_tracker.py / main.py --mode enhanced)
✅ Detailed trade-by-trade analysis
✅ Win rate, profit factor, risk metrics
✅ Trade history with best/worst coins
❌ Slower (fetches each account's fills)
❌ Better for analyzing specific accounts

**Recommended Approach:**
1. Use `leaderboard_analyzer.py` to find top performers
2. Use `enhanced_tracker.py` to deeply analyze selected accounts

## Troubleshooting

### "Failed to fetch leaderboard"
- Check internet connection
- Hyperliquid API may be temporarily down
- Try again in a few minutes

### Output too long
- Reduce `--limit` parameter
- Use specific timeframe instead of `all`
- Redirect to file: `python leaderboard_analyzer.py --timeframe week > output.txt`

### Want to analyze specific accounts only
Use the enhanced tracker instead:
```bash
python main.py --mode enhanced --addresses 0xAddr1,0xAddr2
```

## Next Steps

1. ✅ Run full leaderboard analysis
2. 📊 Review top performers across timeframes
3. 🎯 Identify candidates for copy trading
4. 📈 Track changes over time with weekly updates
5. 🤖 Set up automated copy trading

Happy trading! 🚀
