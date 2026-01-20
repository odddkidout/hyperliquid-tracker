# Enhanced Multi-Timeframe Analysis Guide

## Overview

The enhanced analysis system provides comprehensive PnL and ROI tracking across multiple timeframes:
- **7 Days**: Short-term performance
- **30 Days**: Medium-term trends
- **Lifetime**: Complete trading history

## Quick Start

### Step 1: Activate Environment

```bash
source venv/bin/activate
```

### Step 2: Analyze Specific Addresses

```bash
# Single address
python main.py --mode enhanced --addresses 0x010461C14e146ac35Fe42271BDC1134EE31C703a

# Multiple addresses
python main.py --mode enhanced --addresses 0xAddr1,0xAddr2,0xAddr3
```

### Step 3: Export Results (Optional)

```bash
python main.py --mode enhanced --addresses 0xAddr1,0xAddr2 --export
```

This creates a JSON file with all analysis data.

## Getting Leaderboard Addresses

Since Hyperliquid doesn't have a public leaderboard API, you need to source addresses manually:

### Option 1: Community Sources

1. **Hyperliquid Discord**: https://discord.gg/hyperliquid
2. **Twitter**: Search #Hyperliquid or follow prominent traders
3. **Community Leaderboards**: Check third-party sites like Hypurrscan

### Option 2: Helper Script

Run the address fetcher:

```bash
python get_leaderboard_addresses.py
```

This will:
- Try to fetch from community APIs
- Provide a curated list
- Save addresses to `leaderboard_addresses.txt`

Then analyze them:

```bash
python main.py --mode enhanced --addresses $(cat leaderboard_addresses.txt | head -10 | tr '\n' ',' | sed 's/,$//')
```

### Option 3: Manual List

Create `leaderboard_addresses.txt` with one address per line:

```
0x010461C14e146ac35Fe42271BDC1134EE31C703a
0x00c7B18c0AE49a8330Fb4cf8753c0D9b6f50a800
0x563C175E6f11582f0F346d63E0D551d83191F5e0
```

## What Gets Analyzed

For each account and timeframe, the system calculates:

### PnL Metrics
- **Total PnL**: Gross profit/loss
- **Net PnL**: After fees
- **Gross Profit**: Sum of all winning trades
- **Gross Loss**: Sum of all losing trades
- **Largest Win/Loss**: Best and worst single trades
- **Best/Worst Coin**: Most profitable and unprofitable assets

### Trading Metrics
- **Number of Trades**: Total positions closed
- **Winning Trades**: Number of profitable trades
- **Losing Trades**: Number of unprofitable trades
- **Win Rate**: Percentage of winning trades
- **Average Win**: Mean profit per winning trade
- **Average Loss**: Mean loss per losing trade
- **Profit Factor**: Gross profit / gross loss ratio

### Performance Metrics
- **ROI**: Return on investment (%)
- **ROI (Net)**: ROI after fees
- **ROI (Annualized)**: Projected annual returns
- **Risk/Reward**: Average win / average loss ratio
- **Trades per Day**: Trading frequency
- **Total Volume**: Cumulative trading volume
- **Total Fees**: All fees paid

## Output Format

### Individual Account Analysis

For each account, you get:

```
================================================================================
Analyzing: 0x010461C14e146ac35Fe42271BDC1134EE31C703a
================================================================================
Fetching trade history...
✓ Found 2000 total fills
Calculating metrics across timeframes...

MULTI-TIMEFRAME ANALYSIS
================================================================================
Metric                    7 Days                    30 Days                   Lifetime
----------------------------------------------------------------------------------
Total PnL                 $-1,234.56               $-12,345.67               $-50,000.00
Net PnL                   $-1,345.67               $-13,456.78               $-52,000.00
ROI                       -5.23%                   -6.45%                    -5.73%
Win Rate                  22.50%                   23.35%                    25.00%
Profit Factor             0.85x                    0.89x                     0.92x
Total Trades              150                      650                       2000
Winning Trades            34                       152                       500
Total Volume              $23,456.78               $191,234.56               $874,567.89
Trades/Day                21                       22                        12
================================================================================

KEY HIGHLIGHTS
================================================================================

7D:
  Total PnL: $-1,234.56
  ROI: -5.23%
  Win Rate: 22.50%
  Profit Factor: 0.85x
  Total Trades: 150
  Best Coin: BTC ($150.25)

30D:
  Total PnL: $-12,345.67
  ROI: -6.45%
  Win Rate: 23.35%
  Profit Factor: 0.89x
  Total Trades: 650
  Best Coin: ETH ($1,234.56)

LIFETIME:
  Total PnL: $-50,000.00
  ROI: -5.73%
  Win Rate: 25.00%
  Profit Factor: 0.92x
  Total Trades: 2000
  Best Coin: SOL ($5,678.90)
```

### Leaderboard Rankings

After analyzing all accounts, you get ranked leaderboards:

#### By PnL
```
================================================================================
TOP PERFORMERS BY PnL (30D)
================================================================================
Rank   Address                                       PnL              ROI          Win Rate     Trades
------------------------------------------------------------------------------------------------------
1      0x123...                                      $125,456.78     145.23%      68.50%       345
2      0x456...                                      $89,234.56      92.45%       65.20%       287
3      0x789...                                      $67,890.12      78.90%       61.15%       412
```

#### By ROI
```
================================================================================
TOP PERFORMERS BY ROI (30D)
================================================================================
Rank   Address                                       ROI          PnL              Win Rate     Trades
------------------------------------------------------------------------------------------------------
1      0xabc...                                      245.67%      $45,678.90      72.30%       156
2      0xdef...                                      198.45%      $89,234.56      69.80%       234
3      0x123...                                      145.23%      $125,456.78     68.50%       345
```

## Example Workflows

### Workflow 1: Analyze Top 10 Known Traders

```bash
# 1. Get addresses (manually from community)
echo "0xAddr1
0xAddr2
0xAddr3
0xAddr4
0xAddr5
0xAddr6
0xAddr7
0xAddr8
0xAddr9
0xAddr10" > my_addresses.txt

# 2. Analyze them
source venv/bin/activate
ADDRESSES=$(cat my_addresses.txt | tr '\n' ',' | sed 's/,$//')
python main.py --mode enhanced --addresses $ADDRESSES --export

# 3. Results saved to JSON file
```

### Workflow 2: Compare Timeframes

```bash
# Analyze a single account comprehensively
python main.py --mode enhanced --addresses 0xYourAddress

# Look at the multi-timeframe table to see:
# - Recent performance (7d) vs historical (30d, lifetime)
# - Improvement or decline in metrics
# - Consistency across timeframes
```

### Workflow 3: Find Best Performers

```bash
# 1. Analyze many addresses
python main.py --mode enhanced --addresses 0xA1,0xA2,0xA3...0xA20 --export

# 2. Check the leaderboards for:
#    - Highest PnL (absolute profit)
#    - Highest ROI (percentage returns)
#    - Filter by win rate and trades

# 3. Copy trade the top performers
```

## Understanding the Metrics

### Win Rate
- **Good**: > 60%
- **Average**: 40-60%
- **Poor**: < 40%

Note: Win rate alone doesn't indicate profitability. A 30% win rate with 5:1 risk/reward can be very profitable.

### Profit Factor
- **Excellent**: > 2.0
- **Good**: 1.5 - 2.0
- **Breakeven**: ~1.0
- **Losing**: < 1.0

### ROI
- Highly dependent on timeframe
- Compare within the same timeframe
- Look for consistency across timeframes

### Risk/Reward Ratio
- **Conservative**: > 3:1 (make $3 for every $1 risked)
- **Balanced**: 2:1 to 3:1
- **Aggressive**: 1:1 to 2:1

## Tips for Analysis

1. **Look for Consistency**: Good traders show consistent metrics across all timeframes

2. **Recent Performance Matters**: Weight 7d and 30d more heavily than lifetime

3. **Volume Matters**: High volume traders have more reliable statistics

4. **Win Rate + Profit Factor**: Both must be considered together

5. **Ignore Outliers**: One massive win can skew metrics

6. **Check Trading Frequency**: Trades per day indicates activity level

7. **Best/Worst Coins**: Shows specialization or diversification

## Advanced: Batch Analysis

Create a script to analyze many addresses:

```bash
#!/bin/bash
# analyze_batch.sh

source venv/bin/activate

# Read from file or paste addresses
ADDRESSES="
0xAddr1
0xAddr2
0xAddr3
"

# Clean and convert
CLEAN_ADDR=$(echo "$ADDRESSES" | grep -E '^0x' | tr '\n' ',' | sed 's/,$//')

# Run analysis
python main.py --mode enhanced --addresses $CLEAN_ADDR --export

echo "Analysis complete! Check the JSON output file."
```

## Troubleshooting

### "No fills found"
- Account has no recent trading activity
- Try a different address
- Check the address is correct

### Rate Limiting
- System adds 1s delay between accounts
- For many addresses, expect longer runtime
- API calls are rate-limited by Hyperliquid

### Memory Issues
- Analyzing 50+ addresses at once may be slow
- Break into smaller batches
- Export and analyze results separately

## Next Steps

1. Collect addresses from community sources
2. Run initial analysis to identify top performers
3. Monitor their performance over time
4. Consider copy trading the most consistent performers
5. Re-analyze weekly to track changes

## Important Notes

- ⚠️ Past performance doesn't guarantee future results
- ⚠️ Always do your own research
- ⚠️ Start with paper trading / simulation
- ⚠️ Risk only what you can afford to lose

Happy analyzing! 📊
