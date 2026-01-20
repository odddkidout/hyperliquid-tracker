# Quick Start Guide

## ✅ System is Ready!

Your Hyperliquid tracker is installed and working. Here's how to use it:

## Option 1: Track Specific Addresses (Recommended)

### Step 1: Add addresses to track

Edit the `.env` file and add Hyperliquid wallet addresses:

```bash
TRACKED_ADDRESSES=0xYourAddress1,0xYourAddress2,0xYourAddress3
```

### Step 2: Run the tracker

```bash
source venv/bin/activate
python main.py --mode track
```

## Option 2: Track via Command Line

```bash
source venv/bin/activate
python main.py --mode track --addresses 0xAddress1,0xAddress2
```

## Option 3: View Current Data

```bash
source venv/bin/activate
python main.py --mode analytics
```

## Finding Addresses to Track

To find successful Hyperliquid traders to track:

1. **Community Resources**: Check Hyperliquid Discord, Twitter, or forums for shared addresses
2. **Leaderboard Sites**: Use third-party leaderboard websites
3. **Known Traders**: Track addresses of traders you follow
4. **Your Own Analysis**: Monitor addresses from on-chain data

## Adjusting Criteria

The system filters for traders with:
- Win rate ≥ 60% (MIN_WIN_RATE)
- Total trades ≥ 50 (MIN_TRADES)

To adjust these, edit `.env`:

```bash
MIN_WIN_RATE=0.5    # 50% win rate minimum
MIN_TRADES=20       # 20 trades minimum
```

## Example Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Track specific addresses
python main.py --mode track --addresses 0x010461C14e146ac35Fe42271BDC1134EE31C703a

# View analytics (after tracking)
python main.py --mode analytics --details

# Continuous tracking (every 5 minutes)
python main.py --mode track --continuous --interval 300
```

## What Just Happened?

The tracker successfully analyzed:
- ✅ Account 1: 2000 trades, 23.35% win rate, -5.73% ROI
- ⏭️  Account 2: No recent activity
- ⏭️  Account 3: No recent activity

The first account was tracked but didn't meet the 60% win rate threshold, so it didn't show in "TOP PERFORMERS".

## Next Steps

1. **Add real addresses** you want to track to `.env`
2. **Lower the thresholds** if you want to see more accounts:
   ```
   MIN_WIN_RATE=0.2
   MIN_TRADES=10
   ```
3. **Run continuous tracking** to build up a database over time
4. **Analyze results** after collecting data

## Important Notes

- ⚠️ The system tracks the last 30 days of trading activity
- ⚠️ Copy trading is DISABLED by default (safe)
- ⚠️ You need to find and add addresses manually
- ✅ No API keys required for tracking
- ✅ All data stored locally

## Getting Help

- Check `SETUP_GUIDE.md` for detailed setup
- See `EXAMPLES.md` for more usage examples
- Read `PROJECT_SUMMARY.md` for full features

Happy tracking! 📊
