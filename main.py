#!/usr/bin/env python3
"""
Hyperliquid Tracker & Copy Trading System
Main entry point for the application
"""

import argparse
import sys
from account_tracker import AccountTracker
from copy_trader import CopyTrader
from database import Database
from config import Config
from enhanced_tracker import EnhancedTracker

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        Hyperliquid Tracker & Copy Trading System         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def track_mode(args):
    """Run account tracking mode"""
    print("\n[TRACK MODE] Starting account tracker...\n")

    tracker = AccountTracker(use_testnet=args.testnet)

    if args.continuous:
        tracker.continuous_tracking(interval=args.interval)
    else:
        # One-time tracking
        if args.addresses:
            addresses = args.addresses.split(',')
            tracker.track_accounts(addresses)
        else:
            tracker.track_accounts()

        tracker.get_best_performers(limit=args.limit)

def copytrade_mode(args):
    """Run copy trading mode"""
    print("\n[COPY TRADE MODE] Starting copy trader...\n")

    if not Config.COPY_TRADE_ENABLED:
        print("⚠️  WARNING: Copy trading is DISABLED in .env config")
        print("Set COPY_TRADE_ENABLED=true to enable actual trade execution\n")

    trader = CopyTrader(use_testnet=args.testnet)
    trader.monitor_and_copy()

def enhanced_mode(args):
    """Run enhanced multi-timeframe analysis"""
    print("\n[ENHANCED MODE] Multi-timeframe PnL & ROI Analysis...\n")

    if not args.addresses:
        print("❌ Error: Enhanced mode requires addresses to analyze")
        print("\nUsage:")
        print("  python main.py --mode enhanced --addresses 0x123...,0x456...")
        print("\nOr get addresses first:")
        print("  python get_leaderboard_addresses.py")
        return

    addresses = args.addresses.split(',')
    tracker = EnhancedTracker(use_testnet=args.testnet)

    # Analyze all accounts
    results = tracker.analyze_multiple_accounts(addresses, rate_limit_delay=1.0)

    if not results:
        print("\n❌ No results to display")
        return

    # Generate leaderboards for all timeframes
    for timeframe in ['7d', '30d', 'lifetime']:
        tracker.generate_leaderboard_report(results, timeframe)

    # Export results
    if args.export:
        tracker.export_results(results)

    print("\n✓ Enhanced analysis complete!")

def analytics_mode(args):
    """Display analytics and statistics"""
    print("\n[ANALYTICS MODE] Displaying performance statistics...\n")

    db = Database()

    # Get top accounts
    top_accounts = db.get_top_accounts(
        limit=args.limit,
        min_win_rate=Config.MIN_WIN_RATE,
        min_trades=Config.MIN_TRADES
    )

    if not top_accounts:
        print("No tracked accounts found. Run tracker first with: python main.py --mode track")
        return

    print(f"{'='*100}")
    print(f"TOP {len(top_accounts)} PERFORMING ACCOUNTS")
    print(f"{'='*100}")
    print(f"{'Rank':<6} {'Address':<45} {'Win Rate':<12} {'ROI':<12} {'Trades':<10} {'Total PnL':<15}")
    print(f"{'-'*100}")

    for i, account in enumerate(top_accounts, 1):
        print(f"{i:<6} {account.address:<45} {account.win_rate:>10.2%}  {account.roi:>10.2%}  "
              f"{account.total_trades:>8}  ${account.total_pnl:>12,.2f}")

    print(f"{'='*100}\n")

    # Show detailed stats for top account if requested
    if args.details and top_accounts:
        top_account = top_accounts[0]
        print(f"\nDETAILED STATS - {top_account.address}")
        print(f"{'-'*60}")
        print(f"Total Trades:      {top_account.total_trades}")
        print(f"Winning Trades:    {top_account.winning_trades}")
        print(f"Win Rate:          {top_account.win_rate:.2%}")
        print(f"Total PnL:         ${top_account.total_pnl:,.2f}")
        print(f"ROI:               {top_account.roi:.2%}")
        print(f"Total Volume:      ${top_account.total_volume:,.2f}")
        print(f"Sharpe Ratio:      {top_account.sharpe_ratio:.2f}")
        print(f"Max Drawdown:      {top_account.max_drawdown:.2%}")
        print(f"Last Updated:      {top_account.last_updated}")
        print(f"{'-'*60}\n")

    db.close()

def main():
    parser = argparse.ArgumentParser(
        description='Hyperliquid Tracker & Copy Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Track top accounts once
  python main.py --mode track

  # Track specific addresses
  python main.py --mode track --addresses 0x123...,0x456...

  # Continuous tracking
  python main.py --mode track --continuous --interval 300

  # Start copy trading (simulation by default)
  python main.py --mode copytrade

  # View analytics
  python main.py --mode analytics --limit 20 --details
        """
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['track', 'copytrade', 'analytics', 'enhanced'],
        default='track',
        help='Operation mode (default: track)'
    )

    parser.add_argument(
        '--testnet',
        action='store_true',
        help='Use testnet instead of mainnet'
    )

    parser.add_argument(
        '--addresses',
        type=str,
        help='Comma-separated list of addresses to track'
    )

    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuous tracking'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Tracking interval in seconds (default: 300)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of top accounts to display (default: 10)'
    )

    parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed statistics'
    )

    parser.add_argument(
        '--export',
        action='store_true',
        help='Export results to JSON file'
    )

    args = parser.parse_args()

    print_banner()

    # Route to appropriate mode
    if args.mode == 'track':
        track_mode(args)
    elif args.mode == 'copytrade':
        copytrade_mode(args)
    elif args.mode == 'analytics':
        analytics_mode(args)
    elif args.mode == 'enhanced':
        enhanced_mode(args)

    print("\n✓ Done!\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
