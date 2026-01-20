# Hyperliquid Tracker & Copy Trading System - Project Summary

## What You Got

A complete, production-ready system for tracking top Hyperliquid traders and optionally copying their trades.

## File Structure

```
hyperliquid/
├── main.py                    # Main entry point
├── quickstart.sh             # Interactive setup & launch script
├── dashboard.py              # Real-time CLI dashboard
├── test_connection.py        # API & system testing script
│
├── Core Modules:
├── config.py                 # Configuration management
├── database.py               # SQLite database & models
├── hyperliquid_api.py        # Hyperliquid API wrapper
├── account_tracker.py        # Account tracking & analysis
├── analytics.py              # Performance calculations
├── copy_trader.py            # Copy trading engine
│
├── Configuration:
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
│
└── Documentation:
    ├── README.md             # Project overview
    ├── SETUP_GUIDE.md        # Detailed setup instructions
    └── PROJECT_SUMMARY.md    # This file
```

## Key Features

### 1. Account Tracking
- Fetches top traders from Hyperliquid leaderboard
- Tracks custom addresses
- Stores historical trade data
- Continuous monitoring mode

### 2. Performance Analytics
- **Win Rate**: Percentage of profitable trades
- **ROI**: Return on investment
- **Total PnL**: Profit and loss tracking
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest decline from peak
- **Profit Factor**: Gross profit / gross loss ratio
- **Volume Analysis**: Total trading volume

### 3. Copy Trading Engine
- Monitors top performers in real-time
- Configurable position sizing
- Safety filters (min win rate, min trades)
- Maximum position limits
- **Simulation mode by default** (safe testing)
- Testnet support

### 4. Database Storage
- SQLite database for persistence
- Three main tables:
  - `tracked_accounts`: Trader statistics
  - `trades`: Historical trade records
  - `copied_trades`: Your copy trade history

### 5. Dashboard
- Real-time statistics display
- Top performers list
- Recent activity feed
- Copy trade performance
- Auto-refreshing interface

## Quick Start

### Option 1: Interactive (Recommended)
```bash
./quickstart.sh
```

### Option 2: Manual Commands

**Track top accounts:**
```bash
python main.py --mode track
```

**Continuous tracking:**
```bash
python main.py --mode track --continuous
```

**View analytics:**
```bash
python main.py --mode analytics --details
```

**Copy trading (simulation):**
```bash
python main.py --mode copytrade --testnet
```

**Real-time dashboard:**
```bash
python dashboard.py
```

## Configuration

Edit `.env` file:

```bash
# API credentials (optional for tracking)
HYPERLIQUID_API_KEY=your_key
HYPERLIQUID_SECRET=your_secret
HYPERLIQUID_WALLET_ADDRESS=your_address

# Copy trading settings
COPY_TRADE_ENABLED=false        # Set true to enable execution
POSITION_SIZE_MULTIPLIER=0.1    # Copy at 10% size
MAX_POSITION_SIZE=1000          # Max $1000 per position
MIN_WIN_RATE=0.6               # 60% minimum win rate
MIN_TRADES=50                   # 50+ trades minimum
```

## Safety Features

1. **Disabled by Default**: Copy trading requires explicit enabling
2. **Simulation Mode**: Test without risking capital
3. **Testnet Support**: Practice on testnet first
4. **Position Limits**: Configurable maximum sizes
5. **Performance Filters**: Only copy qualified traders
6. **Rate Limiting**: Prevents API abuse

## Workflow

### Phase 1: Discovery (Days 1-3)
```bash
# Track top accounts to build database
python main.py --mode track --continuous
```

### Phase 2: Analysis (Days 4-7)
```bash
# Analyze performance and identify best traders
python main.py --mode analytics --details
```

### Phase 3: Testing (Days 8-14)
```bash
# Test copy trading in simulation
python main.py --mode copytrade --testnet
```

### Phase 4: Live Trading (Optional)
```bash
# Enable in .env: COPY_TRADE_ENABLED=true
# Start with small positions!
python main.py --mode copytrade
```

## Advanced Usage

### Track Specific Addresses
```bash
python main.py --mode track --addresses 0xabc123,0xdef456
```

### Custom Refresh Interval
```bash
python main.py --mode track --continuous --interval 600
```

### View Top 50 Accounts
```bash
python main.py --mode analytics --limit 50
```

### Combined Monitoring
Terminal 1: Run tracker
```bash
python main.py --mode track --continuous
```

Terminal 2: Run dashboard
```bash
python dashboard.py
```

Terminal 3: Run copy trader
```bash
python main.py --mode copytrade
```

## Performance Metrics Explained

### Win Rate
```
Win Rate = (Winning Trades / Total Trades) × 100%
```
Higher is better, but consider other metrics too.

### ROI (Return on Investment)
```
ROI = (Total PnL / Estimated Capital) × 100%
```
Estimated capital based on trading volume.

### Sharpe Ratio
```
Sharpe = (Average Return - Risk-free Rate) / Std Dev of Returns
```
Measures risk-adjusted returns. Higher is better.
- < 1: Poor
- 1-2: Good
- > 2: Excellent

### Max Drawdown
```
Max DD = (Peak Value - Trough Value) / Peak Value
```
Largest decline from peak. Lower is better.

### Profit Factor
```
Profit Factor = Gross Profit / Gross Loss
```
- < 1: Losing strategy
- 1-2: Break-even to good
- > 2: Strong strategy

## Risk Management

### Critical Safety Rules

1. **NEVER** risk more than you can afford to lose
2. **ALWAYS** start with testnet
3. **ALWAYS** use small position sizes (0.1x or less)
4. **NEVER** blindly trust any trader
5. **ALWAYS** monitor your positions
6. **ALWAYS** have stop-loss strategies
7. **NEVER** copy trade without understanding risks

### Recommended Settings for Beginners

```bash
COPY_TRADE_ENABLED=false        # Keep disabled initially
POSITION_SIZE_MULTIPLIER=0.05   # 5% of original size
MAX_POSITION_SIZE=100           # Max $100 per position
MIN_WIN_RATE=0.70              # 70% minimum (stricter)
MIN_TRADES=100                  # 100+ trades (more data)
```

## Troubleshooting

### Issue: "No accounts found"
**Solution**:
- Wait and run tracker multiple times to build database
- Try specific addresses: `--addresses 0x...`
- Check API connection: `python test_connection.py`

### Issue: API errors
**Solution**:
- Verify internet connection
- Check Hyperliquid API status
- Reduce request frequency

### Issue: Database locked
**Solution**:
- Close other instances of the program
- Delete `.db` file to reset (loses history)

### Issue: Import errors
**Solution**:
```bash
pip install -r requirements.txt
```

## Testing

Before going live:

```bash
# 1. Test API connection
python test_connection.py

# 2. Test tracking (one-time)
python main.py --mode track

# 3. Test analytics
python main.py --mode analytics

# 4. Test copy trading (simulation, testnet)
python main.py --mode copytrade --testnet
```

## Extending the System

### Add Custom Filters
Edit `account_tracker.py` in `get_best_performers()`:
```python
# Add custom criteria
custom_accounts = [a for a in top_accounts if a.sharpe_ratio > 2.0]
```

### Add Notifications
Install: `pip install telegram-send`
```python
# In copy_trader.py
import telegram_send
telegram_send.send(messages=[f"Copied trade: {symbol}"])
```

### Export Data
```python
# In analytics.py
import pandas as pd
df = pd.DataFrame([account.__dict__ for account in accounts])
df.to_csv('top_traders.csv')
```

## Performance Optimization

For large-scale tracking:

1. **Use PostgreSQL** instead of SQLite
   - Update `DATABASE_URL` in `.env`

2. **Add caching** for API calls
   - Implement Redis caching

3. **Parallelize tracking**
   - Use `asyncio` for concurrent API calls

4. **Add indexing**
   - Database indexes on frequently queried fields

## Legal & Compliance

- ⚠️ Check local regulations for automated trading
- ⚠️ Ensure compliance with Hyperliquid's Terms of Service
- ⚠️ Understand tax implications
- ⚠️ Keep detailed records for reporting

## Disclaimer

**THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.**

- Trading cryptocurrencies involves substantial risk
- Past performance does not guarantee future results
- You are solely responsible for your trading decisions
- The developers assume no liability for losses
- This is not financial advice

**USE AT YOUR OWN RISK.**

## Next Steps

1. ✅ Setup complete - You have a working system
2. 📊 Start tracking accounts
3. 📈 Analyze performance data
4. 🧪 Test in simulation
5. 💰 (Optional) Enable live trading with extreme caution

## Support & Development

- Read documentation thoroughly
- Test on testnet extensively
- Start with minimal positions
- Monitor closely
- Learn from results

## Notes

- API keys are **NOT required** for tracking only
- Database stores all historical data locally
- System runs entirely on your machine
- No third-party services or subscriptions needed
- Open source - modify as needed

---

**Built for the Hyperliquid community**
**Trade responsibly. Stay safe.**
