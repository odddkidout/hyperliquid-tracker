import time
from datetime import datetime, timedelta
from typing import List, Dict
from hyperliquid_api import HyperliquidAPI
from database import Database
from analytics import PerformanceAnalytics

class AccountTracker:
    def __init__(self, use_testnet=False):
        self.api = HyperliquidAPI(use_testnet=use_testnet)
        self.db = Database()
        self.analytics = PerformanceAnalytics()

    def discover_top_accounts(self) -> List[str]:
        """Discover top trading accounts from leaderboard or config"""
        from config import Config

        # First, check if user provided custom addresses in .env
        if Config.TRACKED_ADDRESSES:
            print(f"Using {len(Config.TRACKED_ADDRESSES)} addresses from configuration...")
            return Config.TRACKED_ADDRESSES

        # Otherwise, try to fetch from API
        print("Fetching accounts to track...")
        leaderboard = self.api.get_leaderboard()

        if not leaderboard:
            print("\n⚠️  No addresses found to track!")
            print("\nTo track specific addresses, add them to your .env file:")
            print("TRACKED_ADDRESSES=0xYourAddress1,0xYourAddress2,0xYourAddress3")
            print("\nOr pass addresses directly: python main.py --mode track --addresses 0x...")
            return []

        top_addresses = []
        for entry in leaderboard[:100]:  # Top 100
            if 'user' in entry:
                top_addresses.append(entry['user'])
            elif 'address' in entry:
                top_addresses.append(entry['address'])

        print(f"Found {len(top_addresses)} accounts to track")
        return top_addresses

    def analyze_account(self, address: str) -> Dict:
        """Analyze a single account's trading performance"""
        print(f"Analyzing account: {address}")

        # Get user state
        state = self.api.get_user_state(address)

        # Get fill history (last 30 days)
        thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        fills = self.api.get_user_fills(address, start_time=thirty_days_ago)

        if not fills:
            print(f"No fills found for {address}")
            return None

        # Analyze performance
        performance = self.analytics.calculate_performance(fills, state)

        # Store trades in database
        for fill in fills:
            trade_data = {
                'account_address': address,
                'trade_id': fill.get('tid', ''),
                'symbol': fill.get('coin', ''),
                'side': fill.get('side', ''),
                'entry_price': float(fill.get('px', 0)),
                'size': float(fill.get('sz', 0)),
                'opened_at': datetime.fromtimestamp(fill.get('time', 0) / 1000),
            }
            try:
                self.db.add_trade(trade_data)
            except:
                pass  # Skip duplicates

        # Update account stats
        account_data = {
            'address': address,
            'total_trades': performance['total_trades'],
            'winning_trades': performance['winning_trades'],
            'win_rate': performance['win_rate'],
            'total_pnl': performance['total_pnl'],
            'total_volume': performance['total_volume'],
            'roi': performance['roi'],
            'sharpe_ratio': performance.get('sharpe_ratio', 0),
            'max_drawdown': performance.get('max_drawdown', 0),
            'last_updated': datetime.utcnow()
        }

        self.db.add_tracked_account(account_data)

        print(f"Account {address}: Win Rate: {performance['win_rate']:.2%}, ROI: {performance['roi']:.2%}, Total Trades: {performance['total_trades']}")

        return performance

    def track_accounts(self, addresses: List[str] = None):
        """Track multiple accounts"""
        if not addresses:
            addresses = self.discover_top_accounts()

        for i, address in enumerate(addresses):
            try:
                print(f"\n[{i+1}/{len(addresses)}] Processing {address}...")
                self.analyze_account(address)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error analyzing {address}: {e}")
                continue

    def get_best_performers(self, limit=10):
        """Get the best performing accounts based on criteria"""
        from config import Config

        top_accounts = self.db.get_top_accounts(
            limit=limit,
            min_win_rate=Config.MIN_WIN_RATE,
            min_trades=Config.MIN_TRADES
        )

        print(f"\n{'='*80}")
        print(f"TOP {len(top_accounts)} PERFORMERS")
        print(f"{'='*80}")
        print(f"{'Address':<45} {'Win Rate':<12} {'ROI':<12} {'Trades':<10} {'PnL':<15}")
        print(f"{'-'*80}")

        for account in top_accounts:
            print(f"{account.address:<45} {account.win_rate:>10.2%}  {account.roi:>10.2%}  {account.total_trades:>8}  ${account.total_pnl:>12,.2f}")

        return top_accounts

    def continuous_tracking(self, interval=300):
        """Continuously track accounts at specified interval"""
        print(f"Starting continuous tracking (interval: {interval}s)...")

        while True:
            try:
                print(f"\n{'='*80}")
                print(f"Tracking cycle started at {datetime.now()}")
                print(f"{'='*80}")

                self.track_accounts()
                self.get_best_performers()

                print(f"\nSleeping for {interval} seconds...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopping tracker...")
                break
            except Exception as e:
                print(f"Error in tracking cycle: {e}")
                time.sleep(interval)
