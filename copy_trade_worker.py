#!/usr/bin/env python3
"""
Copy Trade Worker - Runs continuously to monitor and execute copy trades
This should run on an always-on server (Railway, Fly.io, Oracle Cloud, etc.)

Key Logic:
1. Monitor trader's fills (executed trades)
2. Detect if it's an ENTRY or EXIT based on position changes
3. For entries: place same order type (market/limit)
4. For exits (TP/SL): close our position proportionally
5. Track limit orders separately to copy them
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from hyperliquid_api import HyperliquidAPI
from database import Database, CopyTradeConfig, CopyTradePerformance
from config import Config

# Try to import exchange for real trading
try:
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils import constants
    import eth_account
    EXCHANGE_AVAILABLE = True
except ImportError:
    EXCHANGE_AVAILABLE = False
    print("⚠️  hyperliquid.exchange not available - running in simulation mode")


class CopyTradeWorker:
    def __init__(self, use_testnet=True):
        """Initialize the copy trade worker"""
        self.api = HyperliquidAPI(use_testnet=use_testnet)
        self.db = Database()
        self.use_testnet = use_testnet
        self.exchange = None

        # Initialize exchange if credentials available
        self._init_exchange()

        # Track trader states
        self.trader_positions = {}      # {trader_address: {coin: position_data}}
        self.trader_orders = {}         # {trader_address: {order_id: order_data}}
        self.last_seen_fills = {}       # {trader_address: set(fill_ids)}
        self.our_positions = {}         # {coin: position_data}

        # Polling interval in seconds
        self.poll_interval = 3  # Check every 3 seconds for faster response

        print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           Copy Trade Worker - {'TESTNET' if use_testnet else 'MAINNET'}                   ║
║           Exchange: {'ENABLED' if self.exchange else 'SIMULATION'}                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """)

        if not use_testnet:
            print("⚠️  WARNING: Running on MAINNET with real money!")
            print()

    def _init_exchange(self):
        """Initialize the Hyperliquid Exchange API for real trading"""
        if not EXCHANGE_AVAILABLE:
            return

        private_key = os.getenv('HYPERLIQUID_PRIVATE_KEY', '')
        if not private_key:
            print("⚠️  HYPERLIQUID_PRIVATE_KEY not set - running in simulation mode")
            return

        try:
            account = eth_account.Account.from_key(private_key)
            base_url = constants.TESTNET_API_URL if self.use_testnet else constants.MAINNET_API_URL
            self.exchange = Exchange(account, base_url)
            print(f"✅ Exchange initialized for wallet: {account.address}")
        except Exception as e:
            print(f"❌ Failed to initialize exchange: {e}")
            self.exchange = None

    def get_active_copy_configs(self) -> List[CopyTradeConfig]:
        """Get all active (not paused) copy trade configurations"""
        configs = self.db.get_all_copy_trade_configs(active_only=True)
        return [c for c in configs if not c.is_paused]

    def get_trader_positions(self, address: str) -> Dict[str, dict]:
        """Get current positions for a trader"""
        user_state = self.api.get_user_state(address)
        positions = {}

        if user_state and 'assetPositions' in user_state:
            for pos in user_state['assetPositions']:
                position_info = pos.get('position', {})
                size = float(position_info.get('szi', 0))
                if size != 0:
                    coin = position_info.get('coin', '')
                    positions[coin] = {
                        'size': size,
                        'entry_price': float(position_info.get('entryPx', 0)),
                        'unrealized_pnl': float(position_info.get('unrealizedPnl', 0)),
                        'leverage': float(position_info.get('leverage', {}).get('value', 1)),
                    }

        return positions

    def get_trader_open_orders(self, address: str) -> Dict[str, dict]:
        """Get open orders for a trader"""
        orders = {}
        try:
            data = {"type": "openOrders", "user": address}
            result = self.api._post("openOrders", data)
            if isinstance(result, list):
                for order in result:
                    oid = str(order.get('oid', ''))
                    orders[oid] = {
                        'oid': oid,
                        'coin': order.get('coin', ''),
                        'side': order.get('side', ''),
                        'price': float(order.get('limitPx', 0)),
                        'size': float(order.get('sz', 0)),
                        'order_type': order.get('orderType', ''),
                        'reduce_only': order.get('reduceOnly', False),
                    }
        except Exception as e:
            print(f"  ⚠️  Error fetching orders for {address[:10]}: {e}")

        return orders

    def get_recent_fills(self, address: str, minutes: int = 1) -> List[dict]:
        """Get recent fills for a trader"""
        start_time = int((datetime.now() - timedelta(minutes=minutes)).timestamp() * 1000)
        return self.api.get_user_fills(address, start_time=start_time)

    def analyze_fill(self, fill: dict, prev_positions: Dict[str, dict],
                     curr_positions: Dict[str, dict]) -> dict:
        """
        Analyze a fill to determine if it's an entry, exit, or position adjustment

        Returns:
            {
                'action': 'entry' | 'exit' | 'add' | 'reduce' | 'flip',
                'coin': str,
                'side': 'long' | 'short',
                'size': float,
                'price': float,
                'is_market': bool,
                'prev_size': float,
                'new_size': float,
            }
        """
        coin = fill.get('coin', '')
        fill_side = fill.get('side', '')  # 'B' = buy, 'A' = sell
        fill_size = float(fill.get('sz', 0))
        fill_price = float(fill.get('px', 0))
        direction = fill.get('dir', '')  # 'Open Long', 'Close Long', etc.

        prev_pos = prev_positions.get(coin, {})
        curr_pos = curr_positions.get(coin, {})

        prev_size = prev_pos.get('size', 0)
        curr_size = curr_pos.get('size', 0)

        # Determine action based on position change
        analysis = {
            'coin': coin,
            'fill_side': fill_side,
            'price': fill_price,
            'fill_size': fill_size,
            'prev_size': prev_size,
            'new_size': curr_size,
            'direction': direction,
        }

        # Determine the action type
        if prev_size == 0 and curr_size != 0:
            # New position opened
            analysis['action'] = 'entry'
            analysis['side'] = 'long' if curr_size > 0 else 'short'
            analysis['size'] = abs(curr_size)

        elif prev_size != 0 and curr_size == 0:
            # Position fully closed
            analysis['action'] = 'exit'
            analysis['side'] = 'long' if prev_size > 0 else 'short'
            analysis['size'] = abs(prev_size)

        elif prev_size > 0 and curr_size > 0:
            if curr_size > prev_size:
                # Added to long
                analysis['action'] = 'add'
                analysis['side'] = 'long'
                analysis['size'] = curr_size - prev_size
            else:
                # Reduced long (partial close)
                analysis['action'] = 'reduce'
                analysis['side'] = 'long'
                analysis['size'] = prev_size - curr_size

        elif prev_size < 0 and curr_size < 0:
            if curr_size < prev_size:
                # Added to short
                analysis['action'] = 'add'
                analysis['side'] = 'short'
                analysis['size'] = abs(curr_size) - abs(prev_size)
            else:
                # Reduced short (partial close)
                analysis['action'] = 'reduce'
                analysis['side'] = 'short'
                analysis['size'] = abs(prev_size) - abs(curr_size)

        elif (prev_size > 0 and curr_size < 0) or (prev_size < 0 and curr_size > 0):
            # Position flipped
            analysis['action'] = 'flip'
            analysis['side'] = 'long' if curr_size > 0 else 'short'
            analysis['size'] = abs(curr_size)

        else:
            analysis['action'] = 'unknown'
            analysis['side'] = 'unknown'
            analysis['size'] = fill_size

        return analysis

    def calculate_copy_size(self, config: CopyTradeConfig,
                           trader_size: float, trader_price: float,
                           trader_account_value: float = None) -> float:
        """
        Calculate the position size for our copy trade

        Logic:
        - If percentage mode: use same % of our allocation as trader uses of their account
        - If fixed mode: scale proportionally with max position limit
        """
        trade_value = abs(trader_size) * trader_price

        if config.allocation_type == 'percentage' and trader_account_value:
            # Calculate what % of their account this trade represents
            trader_pct = trade_value / trader_account_value
            # Use same % of our allocation
            our_value = config.allocation * trader_pct
        else:
            # Fixed allocation - use a portion based on trade significance
            # Scale: if they use $1000 on a $10000 account (10%), we use 10% of our allocation
            our_value = min(trade_value * 0.1, config.allocation * 0.2)

        # Apply max position limit
        if our_value > config.max_position:
            our_value = config.max_position

        # Minimum trade size ($10)
        if our_value < 10:
            return 0

        return our_value / trader_price

    def execute_market_order(self, coin: str, is_buy: bool, size: float,
                            reduce_only: bool = False) -> Optional[dict]:
        """Execute a market order"""
        if not self.exchange:
            print(f"  📝 [SIMULATED] Market {'BUY' if is_buy else 'SELL'} {size:.4f} {coin}")
            return {'simulated': True}

        try:
            # Get current price for slippage calculation
            mids = self.api.get_all_mids()
            if coin not in mids:
                print(f"  ❌ Cannot find price for {coin}")
                return None

            current_price = float(mids[coin])
            # Add 0.5% slippage for market orders
            slippage = 0.005
            if is_buy:
                limit_price = current_price * (1 + slippage)
            else:
                limit_price = current_price * (1 - slippage)

            result = self.exchange.market_open(
                coin=coin,
                is_buy=is_buy,
                sz=size,
                px=limit_price,
                reduce_only=reduce_only
            )
            print(f"  ✅ Market order executed: {result}")
            return result

        except Exception as e:
            print(f"  ❌ Market order failed: {e}")
            return None

    def execute_limit_order(self, coin: str, is_buy: bool, size: float,
                           price: float, reduce_only: bool = False) -> Optional[dict]:
        """Execute a limit order"""
        if not self.exchange:
            print(f"  📝 [SIMULATED] Limit {'BUY' if is_buy else 'SELL'} {size:.4f} {coin} @ ${price:.2f}")
            return {'simulated': True}

        try:
            result = self.exchange.order(
                coin=coin,
                is_buy=is_buy,
                sz=size,
                limit_px=price,
                reduce_only=reduce_only,
                order_type={"limit": {"tif": "Gtc"}}  # Good til cancelled
            )
            print(f"  ✅ Limit order placed: {result}")
            return result

        except Exception as e:
            print(f"  ❌ Limit order failed: {e}")
            return None

    def close_position(self, coin: str, size: float) -> Optional[dict]:
        """Close a position (full or partial)"""
        if not self.exchange:
            print(f"  📝 [SIMULATED] Close {size:.4f} {coin}")
            return {'simulated': True}

        try:
            # Determine direction based on our current position
            our_pos = self.our_positions.get(coin, {})
            our_size = our_pos.get('size', 0)

            if our_size == 0:
                print(f"  ⚠️  No position to close for {coin}")
                return None

            # If we're long, we sell to close. If short, we buy to close.
            is_buy = our_size < 0  # Buy to close short, sell to close long

            result = self.execute_market_order(
                coin=coin,
                is_buy=is_buy,
                size=min(abs(size), abs(our_size)),
                reduce_only=True
            )
            return result

        except Exception as e:
            print(f"  ❌ Close position failed: {e}")
            return None

    def handle_new_fill(self, config: CopyTradeConfig, fill: dict,
                       analysis: dict, trader_account_value: float):
        """Handle a new fill from the trader we're copying"""

        action = analysis['action']
        coin = analysis['coin']
        side = analysis['side']
        trader_size = analysis['size']
        price = analysis['price']

        print(f"""
╔═══════════════════════════════════════════════════════════╗
║  📋 COPY TRADE SIGNAL                                     ║
╠═══════════════════════════════════════════════════════════╣
║  Trader: {config.trader_name or config.trader_address[:15]}...
║  Action: {action.upper()}
║  Coin: {coin}
║  Side: {side.upper()}
║  Trader Size: {trader_size:.4f}
║  Price: ${price:,.2f}
║  Direction: {analysis.get('direction', 'N/A')}
╚═══════════════════════════════════════════════════════════╝
        """)

        # Calculate our copy size
        copy_size = self.calculate_copy_size(
            config, trader_size, price, trader_account_value
        )

        if copy_size == 0:
            print(f"  ⏭️  Trade too small to copy (min $10)")
            return

        print(f"  📊 Our copy size: {copy_size:.4f} (~${copy_size * price:.2f})")

        # Execute based on action type
        result = None

        if action == 'entry':
            # New position - enter with market order
            is_buy = (side == 'long')
            result = self.execute_market_order(coin, is_buy, copy_size)

        elif action == 'add':
            # Adding to position - market order
            is_buy = (side == 'long')
            result = self.execute_market_order(coin, is_buy, copy_size)

        elif action == 'exit':
            # Full exit - close position
            result = self.close_position(coin, copy_size)

        elif action == 'reduce':
            # Partial exit - reduce position
            result = self.close_position(coin, copy_size)

        elif action == 'flip':
            # Position flipped - close current and open opposite
            # First close any existing position
            self.close_position(coin, abs(self.our_positions.get(coin, {}).get('size', 0)))
            # Then open new position
            is_buy = (side == 'long')
            result = self.execute_market_order(coin, is_buy, copy_size)

        # Record the trade
        if result:
            trade_data = {
                'original_trade_id': fill.get('tid', ''),
                'source_account': config.trader_address,
                'symbol': coin,
                'side': side,
                'entry_price': price,
                'size': copy_size,
                'status': 'simulated' if not self.exchange else 'executed',
                'opened_at': datetime.now()
            }
            self.db.add_copied_trade(trade_data)

            # Update performance tracking
            trade_value = copy_size * price
            self.db.update_copy_trade_performance(config.id, 0, trade_value)

    def check_for_new_limit_orders(self, config: CopyTradeConfig,
                                   prev_orders: Dict[str, dict],
                                   curr_orders: Dict[str, dict],
                                   curr_positions: Dict[str, dict],
                                   trader_account_value: float):
        """
        Check for new limit orders placed by the trader

        Logic:
        - If new order is reduce_only or position exists in same direction → it's TP/SL
        - If new order has no matching position → it's an entry order
        """

        new_order_ids = set(curr_orders.keys()) - set(prev_orders.keys())

        for oid in new_order_ids:
            order = curr_orders[oid]
            coin = order['coin']
            is_buy = order['side'] == 'B'
            size = order['size']
            price = order['price']
            reduce_only = order['reduce_only']

            # Get current position for this coin
            position = curr_positions.get(coin, {})
            pos_size = position.get('size', 0)

            # Determine if this is TP/SL or entry
            is_tp_sl = False

            if reduce_only:
                is_tp_sl = True
            elif pos_size != 0:
                # Check if order would reduce position
                if pos_size > 0 and not is_buy:  # Long position, sell order
                    is_tp_sl = True
                elif pos_size < 0 and is_buy:  # Short position, buy order
                    is_tp_sl = True

            print(f"""
  📋 New Limit Order Detected:
     Coin: {coin}
     Side: {'BUY' if is_buy else 'SELL'}
     Size: {size:.4f}
     Price: ${price:,.2f}
     Type: {'TP/SL (Skip)' if is_tp_sl else 'Entry (Copy)'}
            """)

            if is_tp_sl:
                # Skip TP/SL orders - we'll handle exits when fills happen
                print(f"  ⏭️  Skipping TP/SL order")
                continue

            # This is an entry limit order - copy it
            copy_size = self.calculate_copy_size(
                config, size, price, trader_account_value
            )

            if copy_size > 0:
                self.execute_limit_order(coin, is_buy, copy_size, price)

    def update_our_positions(self):
        """Update our own position tracking"""
        if not self.exchange:
            return

        try:
            wallet_address = os.getenv('HYPERLIQUID_WALLET_ADDRESS', '')
            if wallet_address:
                self.our_positions = self.get_trader_positions(wallet_address)
        except Exception as e:
            print(f"  ⚠️  Error updating our positions: {e}")

    def monitor_trader(self, config: CopyTradeConfig) -> int:
        """
        Monitor a single trader for new activity

        Returns: number of new trades detected
        """
        address = config.trader_address
        new_trade_count = 0

        # Get current state
        curr_positions = self.get_trader_positions(address)
        curr_orders = self.get_trader_open_orders(address)
        curr_fills = self.get_recent_fills(address, minutes=2)

        # Get previous state (or initialize)
        prev_positions = self.trader_positions.get(address, {})
        prev_orders = self.trader_orders.get(address, {})

        if address not in self.last_seen_fills:
            self.last_seen_fills[address] = set()

        # Get trader's account value for proportional sizing
        user_state = self.api.get_user_state(address)
        trader_account_value = 0
        if user_state and 'marginSummary' in user_state:
            trader_account_value = float(user_state['marginSummary'].get('accountValue', 0))

        # Process new fills
        for fill in curr_fills:
            fill_id = fill.get('tid', '')

            if fill_id in self.last_seen_fills[address]:
                continue

            # New fill detected
            self.last_seen_fills[address].add(fill_id)
            new_trade_count += 1

            # Analyze the fill
            analysis = self.analyze_fill(fill, prev_positions, curr_positions)

            # Handle the trade
            self.handle_new_fill(config, fill, analysis, trader_account_value)

        # Check for new limit orders (entry orders only, not TP/SL)
        self.check_for_new_limit_orders(
            config, prev_orders, curr_orders,
            curr_positions, trader_account_value
        )

        # Update stored state
        self.trader_positions[address] = curr_positions
        self.trader_orders[address] = curr_orders

        # Cleanup old fill IDs (keep last 500)
        if len(self.last_seen_fills[address]) > 500:
            fills_list = list(self.last_seen_fills[address])
            self.last_seen_fills[address] = set(fills_list[-250:])

        return new_trade_count

    def initialize_trader_state(self, config: CopyTradeConfig):
        """Initialize state for a trader (positions, orders, recent fills)"""
        address = config.trader_address
        print(f"  📥 Initializing state for {config.trader_name or address[:15]}...")

        # Get current positions and orders
        self.trader_positions[address] = self.get_trader_positions(address)
        self.trader_orders[address] = self.get_trader_open_orders(address)

        # Load recent fills to avoid copying old trades
        fills = self.api.get_user_fills_by_time(address, hours=1)
        self.last_seen_fills[address] = set(f.get('tid', '') for f in fills)

        pos_count = len(self.trader_positions[address])
        order_count = len(self.trader_orders[address])
        fill_count = len(self.last_seen_fills[address])

        print(f"     Positions: {pos_count}, Orders: {order_count}, Recent fills: {fill_count}")

    def run(self):
        """Main monitoring loop"""
        print(f"🚀 Starting copy trade worker...")
        print(f"⏱️  Polling interval: {self.poll_interval} seconds")
        print()

        # Initialize state for all active traders
        configs = self.get_active_copy_configs()
        print(f"📥 Initializing state for {len(configs)} trader(s)...")
        for config in configs:
            self.initialize_trader_state(config)
        print()

        # Update our own positions
        self.update_our_positions()

        iteration = 0
        while True:
            try:
                iteration += 1

                # Refresh active configs periodically
                if iteration % 20 == 1:
                    configs = self.get_active_copy_configs()

                    # Initialize any new traders
                    for config in configs:
                        if config.trader_address not in self.trader_positions:
                            self.initialize_trader_state(config)

                if not configs:
                    if iteration % 100 == 1:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] No active copy trades configured")
                else:
                    # Monitor each trader
                    for config in configs:
                        new_trades = self.monitor_trader(config)

                        if new_trades > 0:
                            # Update our positions after executing trades
                            self.update_our_positions()

                # Status update every 2 minutes
                if iteration % 40 == 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💓 Worker alive - monitoring {len(configs)} trader(s)")

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                print("\n\n🛑 Stopping copy trade worker...")
                break
            except Exception as e:
                print(f"\n❌ Error in monitoring loop: {e}")
                import traceback
                traceback.print_exc()
                print("   Retrying in 10 seconds...")
                time.sleep(10)

        self.db.close()
        print("👋 Copy trade worker stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Hyperliquid Copy Trade Worker')
    parser.add_argument('--mainnet', action='store_true', help='Run on mainnet (default: testnet)')
    parser.add_argument('--interval', type=int, default=3, help='Polling interval in seconds (default: 3)')

    args = parser.parse_args()

    worker = CopyTradeWorker(use_testnet=not args.mainnet)
    worker.poll_interval = args.interval
    worker.run()


if __name__ == '__main__':
    main()
