# Hyperliquid Tracker & Copy Trading System - Setup Guide

## Overview

This system provides:
1. **Account Tracking**: Monitor top Hyperliquid traders and analyze their performance
2. **Performance Analytics**: Calculate win rates, ROI, Sharpe ratios, and other metrics
3. **Copy Trading**: Automatically replicate trades from successful accounts (with safety controls)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
# If you plan to execute trades (NOT just track), add your credentials:
HYPERLIQUID_API_KEY=your_api_key_here
HYPERLIQUID_SECRET=your_secret_here
HYPERLIQUID_WALLET_ADDRESS=your_wallet_address_here

# Copy trading settings
COPY_TRADE_ENABLED=false  # Set to 'true' to enable actual trade execution
POSITION_SIZE_MULTIPLIER=0.1  # Copy trades at 10% of original size
MAX_POSITION_SIZE=1000  # Maximum position size in USD
MIN_WIN_RATE=0.6  # Only copy traders with 60%+ win rate
MIN_TRADES=50  # Only copy traders with 50+ trades
```

## Usage

### Track Top Accounts

Track top performers from the leaderboard:

```bash
python main.py --mode track
```

Track specific addresses:

```bash
python main.py --mode track --addresses 0x1234...,0x5678...
```

Continuous tracking (updates every 5 minutes):

```bash
python main.py --mode track --continuous --interval 300
```

### View Analytics

View top performers and their statistics:

```bash
python main.py --mode analytics --limit 20
```

View detailed statistics:

```bash
python main.py --mode analytics --details
```

### Copy Trading

**IMPORTANT**: Copy trading is disabled by default and runs in simulation mode.

Start monitoring for copy trade opportunities:

```bash
python main.py --mode copytrade
```

This will:
1. Identify top performers based on your criteria
2. Monitor their trades in real-time
3. Log copy trade signals (simulated by default)

To enable ACTUAL trade execution:
1. Set `COPY_TRADE_ENABLED=true` in `.env`
2. Add your API credentials
3. **Start with testnet**: `python main.py --mode copytrade --testnet`
4. Monitor carefully before using mainnet

## Architecture

```
hyperliquid/
├── main.py                 # Entry point
├── config.py              # Configuration management
├── database.py            # SQLite database models
├── hyperliquid_api.py     # Hyperliquid API wrapper
├── account_tracker.py     # Account tracking logic
├── analytics.py           # Performance analytics
├── copy_trader.py         # Copy trading engine
└── requirements.txt       # Python dependencies
```

## Database Schema

The system uses SQLite with three main tables:

1. **tracked_accounts**: Stores trader statistics
2. **trades**: Historical trade data
3. **copied_trades**: Your copy trading history

## Safety Features

1. **Position Size Limits**: Configurable maximum position size
2. **Performance Filters**: Only copy traders meeting minimum criteria
3. **Simulation Mode**: Test without risking capital
4. **Testnet Support**: Practice on testnet first
5. **Rate Limiting**: Prevents API abuse

## Performance Metrics

The system calculates:

- **Win Rate**: Percentage of profitable trades
- **ROI**: Return on investment
- **Total PnL**: Profit and loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Profit Factor**: Ratio of gross profit to gross loss
- **Average Win/Loss**: Average size of winning vs losing trades

## Filtering Criteria

Top accounts are selected based on:

1. Minimum win rate (default: 60%)
2. Minimum number of trades (default: 50)
3. Sorted by ROI (highest first)

Adjust these in `.env`:
```bash
MIN_WIN_RATE=0.65
MIN_TRADES=100
```

## Copy Trading Strategy

When a tracked account opens a position:

1. **Verify Account**: Confirm account still meets criteria
2. **Calculate Size**: Apply position size multiplier
3. **Check Limits**: Ensure within max position size
4. **Execute Trade**: Place order (if enabled)
5. **Track Position**: Monitor for exit signals

## Risk Management

**CRITICAL**: Copy trading involves significant risk. Always:

- ✅ Start with testnet
- ✅ Use small position sizes (0.1x or less)
- ✅ Set maximum position limits
- ✅ Monitor the system constantly
- ✅ Have stop-loss strategies
- ✅ Only risk capital you can afford to lose
- ❌ Never blindly trust any trader
- ❌ Never risk more than you can afford

## Troubleshooting

### No accounts found
- The leaderboard might be empty or unavailable
- Try providing specific addresses with `--addresses`

### API errors
- Check your internet connection
- Verify API endpoints are accessible
- Check rate limits

### Database errors
- Delete `hyperliquid_tracker.db` to reset
- Check file permissions

## Advanced Configuration

Edit `config.py` for advanced settings:

```python
# Tracking
TOP_ACCOUNTS_LIMIT = 100
REFRESH_INTERVAL = 300

# Risk Management
MAX_SLIPPAGE = 0.005
STOP_LOSS_PERCENTAGE = 0.02
```

## Example Workflow

1. **Day 1**: Track accounts to build database
   ```bash
   python main.py --mode track
   ```

2. **Day 2-7**: Continue tracking to gather data
   ```bash
   python main.py --mode track --continuous
   ```

3. **Day 8**: Analyze performance
   ```bash
   python main.py --mode analytics --details
   ```

4. **Day 9**: Test copy trading (simulation)
   ```bash
   python main.py --mode copytrade --testnet
   ```

5. **Day 10+**: Enable if satisfied (start small!)

## Support

For issues or questions:
1. Check this guide thoroughly
2. Review the code comments
3. Test on testnet first
4. Start with small positions

## Disclaimer

This software is provided "as is" without warranty. Trading cryptocurrencies involves substantial risk of loss. You are solely responsible for your trading decisions and any losses incurred.

**Use at your own risk.**
