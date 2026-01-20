# Visual Guide - System Architecture & Workflow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HYPERLIQUID TRACKER                         │
│                      Copy Trading System v1.0                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   main.py    │  │dashboard.py  │  │quickstart.sh │            │
│  │              │  │              │  │              │            │
│  │  CLI Entry   │  │ Real-time    │  │ Interactive  │            │
│  │  Point       │  │ Dashboard    │  │ Setup        │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         CORE MODULES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐        ┌──────────────────────┐         │
│  │  account_tracker.py  │        │  copy_trader.py      │         │
│  │                      │        │                      │         │
│  │  • Discover traders  │        │  • Monitor trades    │         │
│  │  • Analyze perf      │        │  • Execute copies    │         │
│  │  • Track history     │        │  • Manage positions  │         │
│  └──────────────────────┘        └──────────────────────┘         │
│                                                                     │
│  ┌──────────────────────┐        ┌──────────────────────┐         │
│  │    analytics.py      │        │  hyperliquid_api.py  │         │
│  │                      │        │                      │         │
│  │  • Calculate metrics │        │  • API wrapper       │         │
│  │  • Rank accounts     │        │  • Data fetching     │         │
│  │  • Performance stats │        │  • Rate limiting     │         │
│  └──────────────────────┘        └──────────────────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DATA & CONFIGURATION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   database.py    │  │    config.py     │  │  .env (config)   │ │
│  │                  │  │                  │  │                  │ │
│  │  SQLite DB       │  │  Settings mgmt   │  │  User settings   │ │
│  │  • Accounts      │  │  • API endpoints │  │  • API keys      │ │
│  │  • Trades        │  │  • Limits        │  │  • Thresholds    │ │
│  │  • Copied Trades │  │  • Filters       │  │  • Trading cfg   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│             ┌────────────────────────────────┐                     │
│             │   Hyperliquid API              │                     │
│             │                                │                     │
│             │  • Leaderboard                 │                     │
│             │  • User fills (trades)         │                     │
│             │  • Account states              │                     │
│             │  • Market data                 │                     │
│             └────────────────────────────────┘                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│ Hyperliquid  │
│ Leaderboard  │
└──────┬───────┘
       │
       │ Fetch top traders
       ▼
┌──────────────────┐
│ Account Tracker  │
│                  │
│ 1. Get addresses │
│ 2. Fetch fills   │
│ 3. Get state     │
└──────┬───────────┘
       │
       │ Raw trade data
       ▼
┌──────────────────┐
│   Analytics      │
│                  │
│ Calculate:       │
│ • Win rate       │
│ • ROI            │
│ • Sharpe ratio   │
│ • Drawdown       │
└──────┬───────────┘
       │
       │ Performance metrics
       ▼
┌──────────────────┐
│    Database      │
│                  │
│ Store:           │
│ • Account stats  │
│ • Trade history  │
│ • Timestamps     │
└──────┬───────────┘
       │
       │ Query top performers
       ▼
┌──────────────────┐
│  Copy Trader     │
│                  │
│ 1. Select traders│
│ 2. Monitor new   │
│    trades        │
│ 3. Apply filters │
│ 4. Calculate size│
│ 5. Execute copy  │
└──────┬───────────┘
       │
       │ Copy trades (if enabled)
       ▼
┌──────────────────┐
│  Your Account    │
│  (Hyperliquid)   │
└──────────────────┘
```

## Workflow Visualizations

### Basic Tracking Workflow

```
START
  │
  ├─→ Run: python main.py --mode track
  │
  ├─→ [Fetch Leaderboard]
  │        │
  │        ├─→ Get top 100 addresses
  │        │
  │        ▼
  │   [For Each Account]
  │        │
  │        ├─→ Fetch trade fills (30 days)
  │        ├─→ Fetch account state
  │        ├─→ Calculate performance
  │        ├─→ Store in database
  │        │
  │        ▼
  │   [Display Results]
  │        │
  │        └─→ Top 10 performers table
  │
  └─→ END
```

### Copy Trading Workflow

```
START (Copy Trading Enabled)
  │
  ├─→ Load Configuration
  │     │
  │     ├─→ MIN_WIN_RATE
  │     ├─→ MIN_TRADES
  │     └─→ POSITION_SIZE_MULTIPLIER
  │
  ├─→ [Query Database]
  │     │
  │     └─→ Get qualifying accounts
  │           (win_rate ≥ threshold)
  │           (trades ≥ minimum)
  │
  ├─→ [Monitoring Loop] ────────┐
  │                              │
  │     For each tracked account │
  │          │                   │
  │          ├─→ Fetch recent fills (last 5 min)
  │          │                   │
  │          ├─→ Detect new trades
  │          │                   │
  │          ▼                   │
  │     [New Trade Found?]       │
  │          │                   │
  │      YES │  NO               │
  │          │   └─→ Continue ───┘
  │          ▼
  │     [Apply Filters]
  │          │
  │          ├─→ Check account still qualifies
  │          ├─→ Check trade size reasonable
  │          ├─→ Verify within limits
  │          │
  │          ▼
  │     [Should Copy?]
  │          │
  │      YES │  NO
  │          │   └─→ Log & Skip
  │          ▼
  │     [Calculate Position Size]
  │          │
  │          ├─→ original_size × multiplier
  │          ├─→ Apply max limit
  │          │
  │          ▼
  │     [Execute Copy Trade]
  │          │
  │          ├─→ If ENABLED: Place order
  │          ├─→ If DISABLED: Simulate only
  │          ├─→ Store in database
  │          │
  │          ▼
  │     [Log Result] ────────────┘
  │
  └─→ Continue monitoring...
```

## Configuration Impact Visualization

```
┌────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION SETTINGS                      │
└────────────────────────────────────────────────────────────────┘

MIN_WIN_RATE Setting:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0.50            0.60            0.70            0.80
├───────────────┼───────────────┼───────────────┼──────────────►
│               │               │               │
More traders    Balanced        Conservative    Very selective
Higher risk     Recommended     Lower risk      Minimal trades

MIN_TRADES Setting:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
20              50              100             200
├───────────────┼───────────────┼───────────────┼──────────────►
│               │               │               │
Less history    Recommended     More reliable   Very reliable
Newer traders   Good balance    Established     Proven track

POSITION_SIZE_MULTIPLIER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0.05            0.10            0.25            0.50
├───────────────┼───────────────┼───────────────┼──────────────►
│               │               │               │
Very small      Recommended     Moderate        Large
5% of original  10% of original 25% of original 50% of original
Safest          Good start      Higher risk     Highest risk

MAX_POSITION_SIZE ($):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
100             500             1000            5000
├───────────────┼───────────────┼───────────────┼──────────────►
│               │               │               │
Beginner        Intermediate    Advanced        Expert
Low risk        Moderate risk   Higher risk     High risk
```

## Database Schema Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                       tracked_accounts                          │
├─────────────────────────────────────────────────────────────────┤
│  PK  id                  INTEGER                                │
│  UNQ address             STRING                                 │
│      username            STRING                                 │
│      total_trades        INTEGER                                │
│      winning_trades      INTEGER                                │
│      win_rate            FLOAT    ◄── Calculated metric        │
│      total_pnl           FLOAT    ◄── Total profit/loss        │
│      total_volume        FLOAT                                  │
│      roi                 FLOAT    ◄── Return on investment     │
│      sharpe_ratio        FLOAT    ◄── Risk-adjusted return     │
│      max_drawdown        FLOAT    ◄── Largest decline          │
│      is_tracked          BOOLEAN  ◄── Currently monitoring?    │
│      last_updated        DATETIME                               │
│      created_at          DATETIME                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ FK: account_address
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                            trades                               │
├─────────────────────────────────────────────────────────────────┤
│  PK  id                  INTEGER                                │
│      account_address     STRING   ◄── Links to tracked_accounts│
│  UNQ trade_id            STRING                                 │
│      symbol              STRING   ◄── BTC, ETH, etc.           │
│      side                STRING   ◄── long or short            │
│      entry_price         FLOAT                                  │
│      exit_price          FLOAT                                  │
│      size                FLOAT                                  │
│      pnl                 FLOAT    ◄── Profit/loss for trade    │
│      is_winner           BOOLEAN                                │
│      opened_at           DATETIME                               │
│      closed_at           DATETIME                               │
│      is_copied           BOOLEAN  ◄── Did we copy this?        │
│      created_at          DATETIME                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Links to
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        copied_trades                            │
├─────────────────────────────────────────────────────────────────┤
│  PK  id                  INTEGER                                │
│      original_trade_id   STRING   ◄── Links to trades.trade_id │
│      source_account      STRING   ◄── Who we copied from       │
│      our_trade_id        STRING   ◄── Our trade ID             │
│      symbol              STRING                                 │
│      side                STRING                                 │
│      entry_price         FLOAT                                  │
│      exit_price          FLOAT                                  │
│      size                FLOAT    ◄── Adjusted by multiplier   │
│      pnl                 FLOAT    ◄── Our profit/loss          │
│      status              STRING   ◄── open, closed, failed     │
│      opened_at           DATETIME                               │
│      closed_at           DATETIME                               │
│      created_at          DATETIME                               │
└─────────────────────────────────────────────────────────────────┘
```

## Performance Metrics Calculation

```
┌─────────────────────────────────────────────────────────────────┐
│                    METRICS CALCULATION FLOW                     │
└─────────────────────────────────────────────────────────────────┘

Input: List of Trades (fills)
         │
         ▼
    ┌────────────────┐
    │ Group by       │
    │ Position       │
    │                │
    │ Identify       │
    │ entry/exit     │
    └────────┬───────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Calculate Basic Metrics:           │
    │                                    │
    │ • Total Trades                     │
    │ • Winning Trades                   │
    │ • Losing Trades                    │
    │                                    │
    │   Win Rate = Wins / Total          │
    │                                    │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Calculate Financial Metrics:       │
    │                                    │
    │ • Total PnL = Σ(all pnls)         │
    │ • Total Volume = Σ(price × size)  │
    │ • Avg Win = mean(winning pnls)    │
    │ • Avg Loss = mean(losing pnls)    │
    │                                    │
    │   Profit Factor = Total Wins /     │
    │                   |Total Losses|   │
    │                                    │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Calculate ROI:                     │
    │                                    │
    │ Estimated Capital = Volume / 10    │
    │                                    │
    │   ROI = Total PnL /                │
    │         Estimated Capital          │
    │                                    │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Calculate Risk Metrics:            │
    │                                    │
    │ Sharpe Ratio:                      │
    │   σ = std(returns)                 │
    │   μ = mean(returns)                │
    │   Sharpe = μ / σ × √365           │
    │                                    │
    │ Max Drawdown:                      │
    │   cumulative_pnl = [...]           │
    │   peak = max(cumulative_pnl)       │
    │   for each value:                  │
    │     dd = (peak - value) / peak     │
    │   max_dd = max(all dds)            │
    │                                    │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Return Complete Performance Dict   │
    │                                    │
    │ {                                  │
    │   'total_trades': int,             │
    │   'win_rate': float,               │
    │   'total_pnl': float,              │
    │   'roi': float,                    │
    │   'sharpe_ratio': float,           │
    │   'max_drawdown': float,           │
    │   ...                              │
    │ }                                  │
    └────────────────────────────────────┘
```

## Decision Tree: Should I Copy This Trade?

```
                    [New Trade Detected]
                            │
                            ▼
                ┌───────────────────────┐
                │ Is account still in   │
                │ top performers list?  │
                └───────┬───────────────┘
                        │
                   YES  │   NO
                        │    └─→ [SKIP: Account no longer qualifies]
                        ▼
                ┌───────────────────────┐
                │ Win rate ≥            │
                │ MIN_WIN_RATE?         │
                └───────┬───────────────┘
                        │
                   YES  │   NO
                        │    └─→ [SKIP: Win rate too low]
                        ▼
                ┌───────────────────────┐
                │ Total trades ≥        │
                │ MIN_TRADES?           │
                └───────┬───────────────┘
                        │
                   YES  │   NO
                        │    └─→ [SKIP: Insufficient history]
                        ▼
                ┌───────────────────────┐
                │ Trade value           │
                │ ≥ $10?                │
                └───────┬───────────────┘
                        │
                   YES  │   NO
                        │    └─→ [SKIP: Trade too small]
                        ▼
                ┌───────────────────────┐
                │ Calculate copy size:  │
                │ original × multiplier │
                └───────┬───────────────┘
                        │
                        ▼
                ┌───────────────────────┐
                │ Copy size ≤           │
                │ MAX_POSITION_SIZE?    │
                └───────┬───────────────┘
                        │
                   YES  │   NO
                        │    └─→ [Adjust to MAX_POSITION_SIZE]
                        ▼
                ┌───────────────────────┐
                │ COPY_TRADE_ENABLED?   │
                └───────┬───────────────┘
                        │
                   YES  │   NO
                        │    └─→ [SIMULATE: Log but don't execute]
                        ▼
                ┌───────────────────────┐
                │ [EXECUTE COPY TRADE]  │
                │ • Place order         │
                │ • Store in database   │
                │ • Log result          │
                └───────────────────────┘
```

## Terminal Layout for Multi-Monitor Setup

```
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│  Terminal 1             │  Terminal 2             │  Terminal 3             │
│  CONTINUOUS TRACKER     │  LIVE DASHBOARD         │  COPY TRADER            │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│                         │                         │                         │
│ $ python main.py \      │ $ python dashboard.py   │ $ python main.py \      │
│   --mode track \        │                         │   --mode copytrade      │
│   --continuous          │ ┌─ DASHBOARD ──────┐   │                         │
│                         │ │ Top Performers    │   │ Monitoring 5 accounts   │
│ Tracking cycle 1/∞      │ │ 1. 0xabc... 75%   │   │                         │
│ Processing...           │ │ 2. 0xdef... 72%   │   │ [COPY TRADE SIGNAL]     │
│ [1/100] 0xabc123...     │ │ 3. 0x123... 68%   │   │ Symbol: BTC             │
│   Win Rate: 75.00%      │ │                   │   │ Side: long              │
│   ROI: 145.20%          │ │ Recent Activity   │   │ Size: 0.01              │
│                         │ │ • 19:45 BTC long  │   │ Value: $500             │
│ [2/100] 0xdef456...     │ │ • 19:42 ETH short │   │ Status: EXECUTED ✓      │
│   Win Rate: 72.00%      │ │ • 19:40 SOL long  │   │                         │
│   ROI: 132.10%          │ │                   │   │                         │
│                         │ │ Copy Stats        │   │                         │
│ ...                     │ │ Total: 12         │   │ Waiting for signals...  │
│                         │ │ PnL: +$1,234      │   │                         │
│                         │ └───────────────────┘   │                         │
│                         │                         │                         │
│ Sleeping 300s...        │ Auto-refresh: 5s        │ Monitoring...           │
│                         │                         │                         │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

This visual guide should help you understand how all the components work together!
