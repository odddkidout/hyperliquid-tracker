#!/usr/bin/env python3
"""
Hyperliquid Leaderboard Analyzer
Analyzes all accounts on the leaderboard across multiple timeframes
"""

import json
from datetime import datetime
from typing import List, Dict
from hyperliquid_api import HyperliquidAPI
from database import Database

class LeaderboardAnalyzer:
    def __init__(self):
        self.api = HyperliquidAPI()
        self.db = Database()

    def fetch_and_analyze_leaderboard(self) -> List[Dict]:
        """Fetch leaderboard and analyze all accounts"""
        print("\n" + "="*100)
        print("FETCHING HYPERLIQUID LEADERBOARD")
        print("="*100 + "\n")

        # Fetch leaderboard
        leaderboard = self.api.get_leaderboard()

        if not leaderboard:
            print("❌ Failed to fetch leaderboard")
            return []

        print(f"✓ Found {len(leaderboard)} accounts on leaderboard")
        print("\nProcessing accounts...")

        # Parse all entries
        analyzed_accounts = []
        for i, entry in enumerate(leaderboard, 1):
            parsed = self.api.parse_leaderboard_entry(entry)
            analyzed_accounts.append(parsed)

            if i % 10 == 0:
                print(f"  Processed {i}/{len(leaderboard)} accounts...", end='\r')

        print(f"\n✓ Processed all {len(analyzed_accounts)} accounts\n")

        return analyzed_accounts

    def generate_leaderboard_report(self, accounts: List[Dict],
                                   timeframe: str = 'week',
                                   metric: str = 'pnl',
                                   limit: int = 50):
        """Generate leaderboard report for specific timeframe and metric"""

        # Map our timeframes to API timeframes
        timeframe_map = {
            '7d': 'week',
            '30d': 'month',
            'lifetime': 'allTime',
            'day': 'day',
            'week': 'week',
            'month': 'month',
            'allTime': 'allTime'
        }

        api_timeframe = timeframe_map.get(timeframe, timeframe)

        # Filter accounts that have data for this timeframe
        valid_accounts = [
            acc for acc in accounts
            if api_timeframe in acc and acc[api_timeframe].get(metric) is not None
        ]

        if not valid_accounts:
            print(f"❌ No data available for timeframe: {timeframe}")
            return

        # Sort by metric
        sorted_accounts = sorted(
            valid_accounts,
            key=lambda x: x[api_timeframe].get(metric, 0),
            reverse=True
        )

        # Display report
        self._print_report(sorted_accounts[:limit], api_timeframe, metric)

    def _print_report(self, accounts: List[Dict], timeframe: str, metric: str):
        """Print formatted leaderboard report"""

        # Timeframe display names
        tf_names = {
            'day': '1 DAY',
            'week': '7 DAYS',
            'month': '30 DAYS',
            'allTime': 'ALL TIME'
        }

        metric_names = {
            'pnl': 'PnL',
            'roi': 'ROI',
            'volume': 'Volume'
        }

        print("\n" + "="*120)
        print(f"LEADERBOARD - {tf_names.get(timeframe, timeframe.upper())} - RANKED BY {metric_names.get(metric, metric.upper())}")
        print("="*120)
        print(f"{'Rank':<6} {'Address':<45} {'Name':<15} {'PnL':<18} {'ROI':<12} {'Volume':<18} {'Acct Value':<18}")
        print("-"*120)

        for i, account in enumerate(accounts, 1):
            address = account.get('address', 'Unknown')[:42]
            name = account.get('display_name') or '-'
            name = name[:13] if len(name) > 13 else name

            tf_data = account.get(timeframe, {})
            pnl = tf_data.get('pnl', 0)
            roi = tf_data.get('roi', 0)
            volume = tf_data.get('volume', 0)
            account_value = account.get('account_value', 0)

            # Format values
            pnl_str = f"${pnl:,.2f}" if pnl >= 0 else f"-${abs(pnl):,.2f}"
            roi_str = f"{roi*100:.2f}%"
            volume_str = f"${volume:,.0f}"
            acct_str = f"${account_value:,.2f}"

            print(f"{i:<6} {address:<45} {name:<15} {pnl_str:>16}  {roi_str:>10}  {volume_str:>16}  {acct_str:>16}")

        print("="*120 + "\n")

    def generate_multi_timeframe_report(self, accounts: List[Dict], limit: int = 20):
        """Generate reports for all timeframes"""

        print("\n" + "#"*120)
        print(f"COMPREHENSIVE LEADERBOARD ANALYSIS - TOP {limit} TRADERS")
        print("#"*120)

        # PnL rankings for each timeframe
        print("\n" + "="*120)
        print("SECTION 1: TOP PERFORMERS BY PnL")
        print("="*120)

        for timeframe in ['day', 'week', 'month', 'allTime']:
            self.generate_leaderboard_report(accounts, timeframe, 'pnl', limit)

        # ROI rankings for each timeframe
        print("\n" + "="*120)
        print("SECTION 2: TOP PERFORMERS BY ROI")
        print("="*120)

        for timeframe in ['day', 'week', 'month', 'allTime']:
            self.generate_leaderboard_report(accounts, timeframe, 'roi', limit)

        # Volume rankings
        print("\n" + "="*120)
        print("SECTION 3: HIGHEST VOLUME TRADERS")
        print("="*120)

        for timeframe in ['week', 'month', 'allTime']:
            self.generate_leaderboard_report(accounts, timeframe, 'volume', limit)

    def get_top_performers(self, accounts: List[Dict],
                          timeframe: str = 'week',
                          min_roi: float = 0.0,
                          min_pnl: float = 0.0,
                          limit: int = 10) -> List[Dict]:
        """Filter top performers by criteria"""

        filtered = []
        for account in accounts:
            tf_data = account.get(timeframe, {})
            roi = tf_data.get('roi', 0)
            pnl = tf_data.get('pnl', 0)

            if roi >= min_roi and pnl >= min_pnl:
                filtered.append(account)

        # Sort by PnL descending
        filtered.sort(key=lambda x: x.get(timeframe, {}).get('pnl', 0), reverse=True)

        return filtered[:limit]

    def export_results(self, accounts: List[Dict], filename: str = None):
        """Export leaderboard data to JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'leaderboard_analysis_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(accounts, f, indent=2)

        print(f"✓ Exported {len(accounts)} accounts to {filename}")

    def save_to_database(self, accounts: List[Dict]):
        """Save leaderboard data to database"""
        print("\nSaving to database...")

        saved = 0
        for account in accounts:
            try:
                # Use 30-day (month) data for database
                month_data = account.get('month', {})

                account_data = {
                    'address': account['address'],
                    'username': account.get('display_name'),
                    'total_trades': 0,  # Not available in leaderboard data
                    'winning_trades': 0,  # Not available
                    'win_rate': 0,  # Not available
                    'total_pnl': month_data.get('pnl', 0),
                    'total_volume': month_data.get('volume', 0),
                    'roi': month_data.get('roi', 0),
                    'sharpe_ratio': 0,
                    'max_drawdown': 0,
                    'last_updated': datetime.utcnow()
                }

                self.db.add_tracked_account(account_data)
                saved += 1

            except Exception as e:
                # Skip if already exists
                continue

        print(f"✓ Saved {saved} accounts to database")

    def find_consistent_performers(self, accounts: List[Dict],
                                   min_roi_all_periods: float = 0.1) -> List[Dict]:
        """Find traders who are consistently profitable across all timeframes"""

        consistent = []
        for account in accounts:
            # Check if profitable in all timeframes
            day_roi = account.get('day', {}).get('roi', -999)
            week_roi = account.get('week', {}).get('roi', -999)
            month_roi = account.get('month', {}).get('roi', -999)
            all_roi = account.get('allTime', {}).get('roi', -999)

            if (day_roi > min_roi_all_periods and
                week_roi > min_roi_all_periods and
                month_roi > min_roi_all_periods and
                all_roi > min_roi_all_periods):
                consistent.append(account)

        return consistent


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze Hyperliquid Leaderboard')
    parser.add_argument('--limit', type=int, default=50, help='Number of top traders to show')
    parser.add_argument('--timeframe', type=str, default='all',
                       choices=['day', 'week', 'month', 'allTime', 'all'],
                       help='Timeframe to analyze')
    parser.add_argument('--metric', type=str, default='pnl',
                       choices=['pnl', 'roi', 'volume'],
                       help='Metric to rank by')
    parser.add_argument('--export', action='store_true', help='Export to JSON')
    parser.add_argument('--save-db', action='store_true', help='Save to database')
    parser.add_argument('--min-roi', type=float, default=0.0,
                       help='Minimum ROI filter (e.g., 0.1 for 10%%)')

    args = parser.parse_args()

    analyzer = LeaderboardAnalyzer()

    # Fetch leaderboard
    accounts = analyzer.fetch_and_analyze_leaderboard()

    if not accounts:
        print("❌ No accounts to analyze")
        return

    # Generate reports
    if args.timeframe == 'all':
        analyzer.generate_multi_timeframe_report(accounts, args.limit)
    else:
        analyzer.generate_leaderboard_report(accounts, args.timeframe, args.metric, args.limit)

    # Find consistent performers
    if args.min_roi > 0:
        print("\n" + "="*120)
        print(f"CONSISTENT PERFORMERS (>{args.min_roi*100:.0f}% ROI in ALL timeframes)")
        print("="*120)
        consistent = analyzer.find_consistent_performers(accounts, args.min_roi)
        print(f"Found {len(consistent)} consistent performers\n")

        if consistent:
            analyzer.generate_leaderboard_report(consistent, 'week', 'pnl', min(20, len(consistent)))

    # Export if requested
    if args.export:
        analyzer.export_results(accounts)

    # Save to database if requested
    if args.save_db:
        analyzer.save_to_database(accounts)

    print("\n✓ Analysis complete!")


if __name__ == '__main__':
    main()
