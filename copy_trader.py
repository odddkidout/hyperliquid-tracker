import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from hyperliquid_api import HyperliquidAPI
from database import Database
from config import Config

class CopyTrader:
    def __init__(self, use_testnet=True):
        """Initialize copy trader - defaults to testnet for safety"""
        self.api = HyperliquidAPI(use_testnet=use_testnet)
        self.db = Database()
        self.use_testnet = use_testnet
        self.tracked_positions = {}
        self.last_check = {}

        if not use_testnet:
            print("WARNING: Running on MAINNET with real money!")
            print("Make sure you understand the risks before proceeding.")

    def get_accounts_to_copy(self) -> List:
        """Get list of accounts that meet criteria for copying"""
        return self.db.get_top_accounts(
            limit=10,
            min_win_rate=Config.MIN_WIN_RATE,
            min_trades=Config.MIN_TRADES
        )

    def monitor_account_trades(self, address: str) -> List[Dict]:
        """Monitor an account for new trades"""
        # Get recent fills (last 5 minutes)
        five_min_ago = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)

        fills = self.api.get_user_fills(address, start_time=five_min_ago)

        new_trades = []
        for fill in fills:
            trade_id = fill.get('tid', '')

            # Check if we've already seen this trade
            if trade_id not in self.tracked_positions.get(address, set()):
                new_trades.append(fill)

                # Mark as seen
                if address not in self.tracked_positions:
                    self.tracked_positions[address] = set()
                self.tracked_positions[address].add(trade_id)

        return new_trades

    def calculate_copy_size(self, original_size: float, original_price: float) -> float:
        """Calculate position size for copy trade based on multiplier and limits"""
        position_value = original_size * original_price
        copy_value = position_value * Config.POSITION_SIZE_MULTIPLIER

        # Apply maximum position size limit
        if copy_value > Config.MAX_POSITION_SIZE:
            copy_value = Config.MAX_POSITION_SIZE

        copy_size = copy_value / original_price
        return copy_size

    def should_copy_trade(self, fill: Dict, account_stats: Dict) -> bool:
        """Determine if a trade should be copied based on criteria"""

        # Check if account meets minimum criteria
        if account_stats.win_rate < Config.MIN_WIN_RATE:
            return False

        if account_stats.total_trades < Config.MIN_TRADES:
            return False

        # Check if trade size is reasonable
        size = float(fill.get('sz', 0))
        price = float(fill.get('px', 0))
        trade_value = size * price

        if trade_value < 10:  # Ignore very small trades
            return False

        return True

    def execute_copy_trade(self, fill: Dict, source_account: str) -> Optional[Dict]:
        """Execute a copy trade (SIMULATION ONLY by default)"""

        coin = fill.get('coin', '')
        side = fill.get('side', '')
        original_price = float(fill.get('px', 0))
        original_size = float(fill.get('sz', 0))

        # Calculate copy size
        copy_size = self.calculate_copy_size(original_size, original_price)

        trade_data = {
            'original_trade_id': fill.get('tid', ''),
            'source_account': source_account,
            'symbol': coin,
            'side': side,
            'entry_price': original_price,
            'size': copy_size,
            'status': 'simulated',  # Change to 'open' for real trading
            'opened_at': datetime.now()
        }

        print(f"\n{'='*60}")
        print(f"COPY TRADE SIGNAL")
        print(f"{'='*60}")
        print(f"Source: {source_account[:10]}...")
        print(f"Symbol: {coin}")
        print(f"Side: {side}")
        print(f"Original Size: {original_size}")
        print(f"Copy Size: {copy_size}")
        print(f"Price: ${original_price}")
        print(f"Value: ${copy_size * original_price:.2f}")
        print(f"Status: SIMULATED (not executed)")
        print(f"{'='*60}\n")

        # Store in database
        copied_trade = self.db.add_copied_trade(trade_data)

        # TODO: Implement actual trade execution via Hyperliquid Exchange API
        # This requires:
        # 1. Wallet setup with private key
        # 2. Exchange API integration (different from Info API)
        # 3. Order placement logic
        # 4. Risk management checks

        return trade_data

    def monitor_and_copy(self):
        """Main loop to monitor accounts and execute copy trades"""

        if not Config.COPY_TRADE_ENABLED:
            print("Copy trading is DISABLED in config. Set COPY_TRADE_ENABLED=true to enable.")
            print("Running in monitoring mode only...")

        accounts_to_copy = self.get_accounts_to_copy()

        if not accounts_to_copy:
            print("No accounts found that meet the criteria for copying.")
            return

        print(f"\nMonitoring {len(accounts_to_copy)} accounts for copy trading...")
        for account in accounts_to_copy:
            print(f"  - {account.address} (Win Rate: {account.win_rate:.2%}, ROI: {account.roi:.2%})")

        while True:
            try:
                for account in accounts_to_copy:
                    # Monitor for new trades
                    new_trades = self.monitor_account_trades(account.address)

                    if new_trades:
                        print(f"\nDetected {len(new_trades)} new trade(s) from {account.address[:10]}...")

                        for fill in new_trades:
                            # Check if we should copy this trade
                            if self.should_copy_trade(fill, account):
                                if Config.COPY_TRADE_ENABLED:
                                    self.execute_copy_trade(fill, account.address)
                                else:
                                    print(f"Would copy trade: {fill.get('coin')} {fill.get('side')} (DISABLED)")

                    time.sleep(1)  # Rate limiting

                # Wait before next monitoring cycle
                time.sleep(10)

            except KeyboardInterrupt:
                print("\nStopping copy trader...")
                break
            except Exception as e:
                print(f"Error in copy trading loop: {e}")
                time.sleep(10)

    def get_copy_trade_performance(self) -> Dict:
        """Get performance statistics of copy trades"""
        # Query all copied trades from database
        # Calculate performance metrics
        # This is a placeholder for now
        return {
            'total_copied': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0
        }
