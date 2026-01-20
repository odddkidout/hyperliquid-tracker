# Usage Examples

## Installation & Setup

### First Time Setup
```bash
# Clone or navigate to the project
cd hyperliquid

# Run the interactive setup
./quickstart.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Test Your Setup
```bash
# Verify API connection and functionality
python test_connection.py
```

## Basic Usage

### 1. Track Top Accounts (One Time)
```bash
# Track top 100 accounts from leaderboard
python main.py --mode track

# Output:
# Processing 1/100: 0xabc123...
# Account 0xabc123...: Win Rate: 65.00%, ROI: 125.50%, Total Trades: 156
# ...
# TOP 10 PERFORMERS
# Address                                          Win Rate      ROI          Trades     PnL
# 0xabc123...                                     65.00%        125.50%      156        $12,345.67
```

### 2. Track Specific Addresses
```bash
# Track only specific addresses you're interested in
python main.py --mode track --addresses 0x1234567890abcdef,0xfedcba0987654321

# Good for:
# - Following known successful traders
# - Tracking your own performance
# - Monitoring friends' accounts
```

### 3. Continuous Tracking
```bash
# Track continuously with 5-minute updates
python main.py --mode track --continuous --interval 300

# This will run indefinitely:
# - Fetches new data every 5 minutes
# - Updates database
# - Shows top performers after each cycle
# - Press Ctrl+C to stop
```

### 4. View Analytics
```bash
# Simple analytics view
python main.py --mode analytics

# Detailed analytics with top 20 accounts
python main.py --mode analytics --limit 20 --details

# Output includes:
# - Ranking of top performers
# - Win rates, ROI, trade counts
# - Detailed stats for #1 performer
```

### 5. Real-Time Dashboard
```bash
# Launch interactive dashboard (auto-refreshes every 5 seconds)
python dashboard.py

# Shows:
# - Configuration settings
# - Top 10 performers
# - Recent activity
# - Copy trading stats
```

## Advanced Usage

### Monitor Multiple Aspects Simultaneously

**Terminal 1 - Continuous Tracking:**
```bash
python main.py --mode track --continuous --interval 300
```

**Terminal 2 - Live Dashboard:**
```bash
python dashboard.py
```

**Terminal 3 - Copy Trading Monitor:**
```bash
python main.py --mode copytrade --testnet
```

### Copy Trading Examples

#### Example 1: Simulation Mode (Safe)
```bash
# In .env:
COPY_TRADE_ENABLED=false

# Run copy trader
python main.py --mode copytrade --testnet

# Output:
# Monitoring 5 accounts for copy trading...
#   - 0xabc123... (Win Rate: 65.00%, ROI: 125.50%)
#   - 0xdef456... (Win Rate: 70.00%, ROI: 95.20%)
# ...
# COPY TRADE SIGNAL
# Symbol: BTC
# Side: long
# Copy Size: 0.01
# Price: $50000
# Value: $500.00
# Status: SIMULATED (not executed)
```

#### Example 2: Testnet Trading
```bash
# In .env:
COPY_TRADE_ENABLED=true
POSITION_SIZE_MULTIPLIER=0.05  # 5% of original size
MAX_POSITION_SIZE=100          # Max $100 per trade

# Run on testnet
python main.py --mode copytrade --testnet

# This will actually execute trades on testnet
# Good for testing without risk
```

#### Example 3: Conservative Live Trading
```bash
# In .env:
COPY_TRADE_ENABLED=true
POSITION_SIZE_MULTIPLIER=0.05   # Very small positions
MAX_POSITION_SIZE=50            # Low maximum
MIN_WIN_RATE=0.75              # Only copy 75%+ win rate traders
MIN_TRADES=200                  # Require lots of history

# Run on mainnet (REAL MONEY - BE CAREFUL!)
python main.py --mode copytrade

# Only copies traders with:
# - 75%+ win rate
# - 200+ trades
# - Position sizes 5% of original
# - Max $50 per trade
```

## Data Export Examples

### Export All Data
```bash
# Export everything to CSV files
python export_data.py --type all

# Creates:
# - tracked_accounts.csv
# - trades.csv
# - copied_trades.csv
# - summary_report.txt
```

### Export Specific Data Types
```bash
# Just accounts
python export_data.py --type accounts

# Just trades
python export_data.py --type trades

# Trades from specific account
python export_data.py --type trades --address 0xabc123...

# Just copied trades
python export_data.py --type copied

# Just summary report
python export_data.py --type summary
```

### Analyze Exported Data
```bash
# Open in spreadsheet software
open tracked_accounts.csv

# Or use command line tools
cat summary_report.txt

# Or import into Python/Pandas
python
>>> import pandas as pd
>>> df = pd.read_csv('tracked_accounts.csv')
>>> df[df.win_rate > 0.7].sort_values('roi', ascending=False)
```

## Configuration Examples

### Conservative Settings (Recommended for Beginners)
```bash
# .env
COPY_TRADE_ENABLED=false
POSITION_SIZE_MULTIPLIER=0.05
MAX_POSITION_SIZE=100
MIN_WIN_RATE=0.70
MIN_TRADES=100
```

### Moderate Settings
```bash
# .env
COPY_TRADE_ENABLED=false  # Keep disabled until confident
POSITION_SIZE_MULTIPLIER=0.1
MAX_POSITION_SIZE=500
MIN_WIN_RATE=0.65
MIN_TRADES=75
```

### Aggressive Settings (Higher Risk!)
```bash
# .env
COPY_TRADE_ENABLED=true
POSITION_SIZE_MULTIPLIER=0.25
MAX_POSITION_SIZE=2000
MIN_WIN_RATE=0.60
MIN_TRADES=50
```

## Workflow Examples

### Workflow 1: Research Mode
**Goal:** Identify consistently profitable traders

```bash
# Day 1-3: Collect data
python main.py --mode track --continuous --interval 300

# Day 4: Analyze
python main.py --mode analytics --limit 50 --details

# Export for detailed analysis
python export_data.py --type all

# Review in spreadsheet
open tracked_accounts.csv
```

### Workflow 2: Testing Copy Trading
**Goal:** Test copy trading strategy without risk

```bash
# Step 1: Build database (several days)
python main.py --mode track --continuous

# Step 2: Configure conservative settings
nano .env
# Set COPY_TRADE_ENABLED=false
# Set MIN_WIN_RATE=0.70
# Set POSITION_SIZE_MULTIPLIER=0.05

# Step 3: Monitor in simulation
python main.py --mode copytrade --testnet

# Step 4: Analyze results
python main.py --mode analytics
python export_data.py --type copied
```

### Workflow 3: Live Copy Trading (Advanced)
**Goal:** Actively copy trade with real money

```bash
# Prerequisites:
# - Several weeks of data collection
# - Thoroughly tested on testnet
# - Comfortable with risks

# Terminal 1: Keep data fresh
python main.py --mode track --continuous --interval 600

# Terminal 2: Monitor performance
python dashboard.py

# Terminal 3: Execute copy trades
python main.py --mode copytrade

# Regularly check performance
python main.py --mode analytics --details
python export_data.py --type copied
```

## Common Scenarios

### Scenario: Find Best Trader for a Specific Asset
```bash
# Track accounts
python main.py --mode track

# Export all trades
python export_data.py --type trades

# Analyze in Python
python
>>> import pandas as pd
>>> trades = pd.read_csv('trades.csv')
>>> btc_traders = trades[trades.symbol == 'BTC'].groupby('account_address')
>>> btc_stats = btc_traders.agg({
...     'pnl': 'sum',
...     'is_winner': 'mean'
... }).sort_values('pnl', ascending=False)
>>> print(btc_stats.head())
```

### Scenario: Monitor Your Copy Trading Performance
```bash
# While copy trading is running
# Terminal 1: Run copy trader
python main.py --mode copytrade

# Terminal 2: Monitor dashboard
python dashboard.py

# Terminal 3: Check periodically
watch -n 60 'python export_data.py --type copied && tail -20 copied_trades.csv'
```

### Scenario: Backtest a Trader's Strategy
```bash
# Export their trades
python export_data.py --type trades --address 0xTRADER_ADDRESS

# Analyze in spreadsheet or Python
# Calculate metrics:
# - Win rate over time
# - Profitability by asset
# - Best/worst periods
# - Drawdown periods
```

## Troubleshooting Examples

### Problem: No Data Showing Up
```bash
# Check API connection
python test_connection.py

# Check if database has data
python
>>> from database import Database
>>> db = Database()
>>> accounts = db.session.query(db.TrackedAccount).count()
>>> print(f"Total accounts: {accounts}")

# If zero, run tracker
python main.py --mode track
```

### Problem: Copy Trading Not Working
```bash
# Verify settings
cat .env | grep COPY_TRADE

# Check if any accounts qualify
python main.py --mode analytics

# If none qualify, lower thresholds
nano .env
# Reduce MIN_WIN_RATE or MIN_TRADES
```

### Problem: Database Issues
```bash
# Backup current database
cp hyperliquid_tracker.db hyperliquid_tracker.db.backup

# Reset database
rm hyperliquid_tracker.db

# Rebuild
python main.py --mode track
```

## Integration Examples

### Send Telegram Notifications
```python
# Add to copy_trader.py
import telegram_send

def execute_copy_trade(self, fill, source_account):
    # ... existing code ...

    message = f"📊 Copy Trade Executed\n" \
              f"Symbol: {coin}\n" \
              f"Side: {side}\n" \
              f"Size: {copy_size}\n" \
              f"Price: ${original_price}"

    telegram_send.send(messages=[message])
```

### Export to Google Sheets
```python
# Install: pip install gspread oauth2client
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def export_to_sheets():
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('Hyperliquid Tracker').sheet1

    # Export data
    from database import Database
    db = Database()
    accounts = db.get_top_accounts(limit=100)

    for i, acc in enumerate(accounts, start=2):
        sheet.update_cell(i, 1, acc.address)
        sheet.update_cell(i, 2, acc.win_rate)
        sheet.update_cell(i, 3, acc.roi)
```

### Create Discord Bot
```python
# Install: pip install discord.py
import discord
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix='!')

@tasks.loop(hours=1)
async def post_top_performers():
    channel = bot.get_channel(YOUR_CHANNEL_ID)
    accounts = db.get_top_accounts(limit=5)

    message = "🏆 **Top 5 Performers**\n"
    for i, acc in enumerate(accounts, 1):
        message += f"{i}. {acc.address[:10]}... - Win Rate: {acc.win_rate:.1%}\n"

    await channel.send(message)

@bot.command()
async def top(ctx):
    accounts = db.get_top_accounts(limit=10)
    # Format and send...

bot.run('YOUR_BOT_TOKEN')
```

## Tips & Tricks

### Reduce API Calls
```bash
# Use longer intervals
python main.py --mode track --continuous --interval 600  # 10 minutes

# Track fewer accounts
python main.py --mode track --addresses 0xONLY_BEST_TRADER
```

### Find Emerging Talents
```bash
# Lower minimum trades to find newer profitable traders
nano .env
# Set MIN_TRADES=20

python main.py --mode analytics --limit 50
```

### Focus on Specific Assets
```python
# Modify account_tracker.py
def get_best_performers(self, symbol='BTC'):
    # Filter accounts that primarily trade specific asset
    pass
```

---

**Remember:** Always start with simulation mode and testnet before risking real capital!
