#!/usr/bin/env python3
"""
Enhanced Account Tracker with Multi-Timeframe Analysis
Focuses on PnL and ROI across 7d, 30d, and lifetime
"""

import time
import json
from datetime import datetime
from typing import List, Dict
from hyperliquid_api import HyperliquidAPI
from multi_timeframe_analytics import MultiTimeframeAnalytics
from database import Database

class EnhancedTracker:
    def __init__(self, use_testnet=False):
        self.api = HyperliquidAPI(use_testnet=use_testnet)
        self.analytics = MultiTimeframeAnalytics()
        self.db = Database()

    def analyze_account_comprehensive(self, address: str) -> Dict:
        """Perform comprehensive multi-timeframe analysis of an account"""
        print(f"\n{'='*100}")
        print(f"Analyzing: {address}")
        print(f"{'='*100}")

        # Get ALL fills (lifetime)
        print("Fetching trade history...")
        all_fills = self.api.get_user_fills(address)

        if not all_fills:
            print(f"❌ No trading history found for {address}")
            return None

        print(f"✓ Found {len(all_fills)} total fills")

        # Get account state
        state = self.api.get_user_state(address)
        account_value = self._extract_account_value(state)

        # Perform multi-timeframe analysis
        print("Calculating metrics across timeframes...")
        results = self.analytics.analyze_multi_timeframe(all_fills, account_value)

        # Add address and metadata
        results['address'] = address
        results['account_value'] = account_value
        results['analysis_time'] = datetime.now()
        results['total_fills'] = len(all_fills)

        # Print comparison table
        print(self.analytics.generate_comparison_table(results))

        # Print highlights
        self._print_highlights(results)

        return results

    def analyze_multiple_accounts(self, addresses: List[str], rate_limit_delay: float = 1.0) -> List[Dict]:
        """Analyze multiple accounts"""
        results = []

        print(f"\n{'#'*100}")
        print(f"STARTING MULTI-ACCOUNT ANALYSIS - {len(addresses)} accounts")
        print(f"{'#'*100}\n")

        for i, address in enumerate(addresses, 1):
            print(f"\n[{i}/{len(addresses)}] Processing {address}...")

            try:
                result = self.analyze_account_comprehensive(address)
                if result:
                    results.append(result)
                    self._save_to_database(result)

                # Rate limiting
                if i < len(addresses):
                    print(f"\nWaiting {rate_limit_delay}s before next account...")
                    time.sleep(rate_limit_delay)

            except Exception as e:
                print(f"❌ Error analyzing {address}: {e}")
                continue

        return results

    def generate_leaderboard_report(self, results: List[Dict], timeframe: str = '30d'):
        """Generate leaderboard report for a specific timeframe"""
        if not results:
            print("\n❌ No results to report")
            return

        print(f"\n{'#'*100}")
        print(f"LEADERBOARD - {timeframe.upper()} TIMEFRAME")
        print(f"{'#'*100}\n")

        # Rank by PnL
        print("="*100)
        print(f"TOP PERFORMERS BY PnL ({timeframe})")
        print("="*100)
        print(f"{'Rank':<6} {'Address':<45} {'PnL':<15} {'ROI':<12} {'Win Rate':<12} {'Trades':<10}")
        print("-"*100)

        pnl_ranked = self.analytics.rank_by_pnl(results, timeframe)
        for i, account in enumerate(pnl_ranked[:20], 1):
            tf_data = account.get(timeframe, {})
            address = account.get('address', 'Unknown')[:42]
            pnl = tf_data.get('total_pnl', 0)
            roi = tf_data.get('roi', 0)
            win_rate = tf_data.get('win_rate', 0)
            trades = tf_data.get('num_trades', 0)

            print(f"{i:<6} {address:<45} ${pnl:>12,.2f}  {roi:>10.2%}  {win_rate:>10.2%}  {trades:>8}")

        # Rank by ROI
        print("\n" + "="*100)
        print(f"TOP PERFORMERS BY ROI ({timeframe})")
        print("="*100)
        print(f"{'Rank':<6} {'Address':<45} {'ROI':<12} {'PnL':<15} {'Win Rate':<12} {'Trades':<10}")
        print("-"*100)

        roi_ranked = self.analytics.rank_by_roi(results, timeframe)
        for i, account in enumerate(roi_ranked[:20], 1):
            tf_data = account.get(timeframe, {})
            address = account.get('address', 'Unknown')[:42]
            roi = tf_data.get('roi', 0)
            pnl = tf_data.get('total_pnl', 0)
            win_rate = tf_data.get('win_rate', 0)
            trades = tf_data.get('num_trades', 0)

            print(f"{i:<6} {address:<45} {roi:>10.2%}  ${pnl:>12,.2f}  {win_rate:>10.2%}  {trades:>8}")

        print("="*100)

    def export_results(self, results: List[Dict], filename: str = None):
        """Export results to JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'hyperliquid_analysis_{timestamp}.json'

        # Convert datetime objects to strings
        export_data = []
        for result in results:
            export_result = {**result}
            if 'analysis_time' in export_result:
                export_result['analysis_time'] = export_result['analysis_time'].isoformat()
            for tf in ['7d', '30d', 'lifetime']:
                if tf in export_result:
                    if 'first_trade_time' in export_result[tf]:
                        export_result[tf]['first_trade_time'] = export_result[tf]['first_trade_time'].isoformat()
                    if 'last_trade_time' in export_result[tf]:
                        export_result[tf]['last_trade_time'] = export_result[tf]['last_trade_time'].isoformat()
            export_data.append(export_result)

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n✓ Results exported to {filename}")

    def _extract_account_value(self, state: Dict) -> float:
        """Extract account value from state"""
        try:
            if 'marginSummary' in state:
                return float(state['marginSummary'].get('accountValue', 0))
            return 0
        except:
            return 0

    def _print_highlights(self, results: Dict):
        """Print key highlights from analysis"""
        print(f"\n{'='*100}")
        print("KEY HIGHLIGHTS")
        print(f"{'='*100}")

        for tf in ['7d', '30d', 'lifetime']:
            tf_data = results.get(tf, {})
            if tf_data.get('num_trades', 0) > 0:
                print(f"\n{tf.upper()}:")
                print(f"  Total PnL: ${tf_data.get('total_pnl', 0):,.2f}")
                print(f"  ROI: {tf_data.get('roi', 0):.2%}")
                print(f"  Win Rate: {tf_data.get('win_rate', 0):.2%}")
                print(f"  Profit Factor: {tf_data.get('profit_factor', 0):.2f}x")
                print(f"  Total Trades: {tf_data.get('num_trades', 0)}")
                print(f"  Best Coin: {tf_data.get('best_coin', ['N/A', 0])[0]} (${tf_data.get('best_coin', ['N/A', 0])[1]:,.2f})")

    def _save_to_database(self, result: Dict):
        """Save results to database"""
        try:
            # Save 30d metrics to main tracked_accounts table
            tf_data = result.get('30d', {})
            account_data = {
                'address': result['address'],
                'total_trades': tf_data.get('num_trades', 0),
                'winning_trades': tf_data.get('winning_trades', 0),
                'win_rate': tf_data.get('win_rate', 0),
                'total_pnl': tf_data.get('total_pnl', 0),
                'total_volume': tf_data.get('total_volume', 0),
                'roi': tf_data.get('roi', 0),
                'sharpe_ratio': 0,  # Calculate separately if needed
                'max_drawdown': 0,  # Calculate separately if needed
                'last_updated': datetime.utcnow()
            }
            self.db.add_tracked_account(account_data)
        except Exception as e:
            print(f"Warning: Could not save to database: {e}")


def main():
    """Main function for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python enhanced_tracker.py <address1> [address2] ...")
        print("Example: python enhanced_tracker.py 0x010461C14e146ac35Fe42271BDC1134EE31C703a")
        sys.exit(1)

    addresses = sys.argv[1:]
    tracker = EnhancedTracker()

    # Analyze all accounts
    results = tracker.analyze_multiple_accounts(addresses)

    # Generate reports for all timeframes
    for timeframe in ['7d', '30d', 'lifetime']:
        tracker.generate_leaderboard_report(results, timeframe)

    # Export results
    tracker.export_results(results)

    print("\n✓ Analysis complete!")


if __name__ == '__main__':
    main()
