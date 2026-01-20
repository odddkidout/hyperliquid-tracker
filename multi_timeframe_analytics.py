import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

class MultiTimeframeAnalytics:
    """Enhanced analytics supporting multiple timeframes (7d, 30d, lifetime)"""

    def __init__(self):
        self.timeframes = {
            '7d': 7,
            '30d': 30,
            'lifetime': None  # No time limit
        }

    def filter_fills_by_timeframe(self, fills: List[Dict], days: int = None) -> List[Dict]:
        """Filter fills by timeframe"""
        if days is None:
            return fills  # Return all for lifetime

        cutoff_time = (datetime.now() - timedelta(days=days)).timestamp() * 1000
        return [f for f in fills if f.get('time', 0) >= cutoff_time]

    def calculate_pnl_metrics(self, fills: List[Dict]) -> Dict:
        """Calculate comprehensive PnL metrics"""
        if not fills:
            return self._empty_pnl_metrics()

        # Extract all PnL data
        realized_pnls = []
        trades_by_coin = defaultdict(list)
        total_volume = 0
        total_fees = 0

        for fill in fills:
            pnl = float(fill.get('closedPnl', 0))
            if pnl != 0:  # Only count closed positions
                realized_pnls.append(pnl)
                coin = fill.get('coin', 'UNKNOWN')
                trades_by_coin[coin].append(pnl)

            # Calculate volume
            px = float(fill.get('px', 0))
            sz = abs(float(fill.get('sz', 0)))
            total_volume += px * sz

            # Sum fees
            fee = float(fill.get('fee', 0))
            total_fees += abs(fee)

        # Calculate metrics
        total_pnl = sum(realized_pnls)
        gross_profit = sum(p for p in realized_pnls if p > 0)
        gross_loss = sum(p for p in realized_pnls if p < 0)

        num_trades = len(realized_pnls)
        winning_trades = sum(1 for p in realized_pnls if p > 0)
        losing_trades = sum(1 for p in realized_pnls if p < 0)

        win_rate = winning_trades / num_trades if num_trades > 0 else 0
        avg_win = gross_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = abs(gross_loss / losing_trades) if losing_trades > 0 else 0

        # Profit factor
        profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else (float('inf') if gross_profit > 0 else 0)

        # ROI (using volume as capital estimate)
        estimated_capital = total_volume / 10 if total_volume > 0 else 1
        roi = (total_pnl / estimated_capital) if estimated_capital > 0 else 0

        # Net profit after fees
        net_pnl = total_pnl - total_fees

        # Calculate risk-reward ratio
        risk_reward = avg_win / avg_loss if avg_loss > 0 else 0

        # Largest win and loss
        largest_win = max(realized_pnls) if realized_pnls else 0
        largest_loss = min(realized_pnls) if realized_pnls else 0

        # Best and worst coin
        coin_pnls = {coin: sum(pnls) for coin, pnls in trades_by_coin.items()}
        best_coin = max(coin_pnls.items(), key=lambda x: x[1]) if coin_pnls else ("N/A", 0)
        worst_coin = min(coin_pnls.items(), key=lambda x: x[1]) if coin_pnls else ("N/A", 0)

        return {
            'total_pnl': total_pnl,
            'net_pnl': net_pnl,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'total_volume': total_volume,
            'total_fees': total_fees,
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'roi': roi,
            'risk_reward': risk_reward,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'best_coin': best_coin,
            'worst_coin': worst_coin,
            'coins_traded': list(trades_by_coin.keys()),
            'num_coins': len(trades_by_coin)
        }

    def calculate_roi_metrics(self, fills: List[Dict], account_value: float = None) -> Dict:
        """Calculate detailed ROI metrics"""
        if not fills:
            return {}

        pnl_metrics = self.calculate_pnl_metrics(fills)

        # If account value provided, use it for ROI calculation
        if account_value and account_value > 0:
            roi = pnl_metrics['total_pnl'] / account_value
            roi_net = pnl_metrics['net_pnl'] / account_value
        else:
            roi = pnl_metrics['roi']
            roi_net = pnl_metrics['net_pnl'] / (pnl_metrics['total_volume'] / 10) if pnl_metrics['total_volume'] > 0 else 0

        return {
            'roi': roi,
            'roi_net': roi_net,
            'roi_annualized': self._annualize_roi(roi, fills),
            'total_pnl': pnl_metrics['total_pnl'],
            'net_pnl': pnl_metrics['net_pnl']
        }

    def _annualize_roi(self, roi: float, fills: List[Dict]) -> float:
        """Annualize ROI based on data timeframe"""
        if not fills or len(fills) < 2:
            return 0

        # Get time span in days
        times = [f.get('time', 0) for f in fills]
        time_span_days = (max(times) - min(times)) / (1000 * 60 * 60 * 24)

        if time_span_days <= 0:
            return 0

        # Annualize
        annualized = roi * (365 / time_span_days)
        return annualized

    def analyze_multi_timeframe(self, fills: List[Dict], account_value: float = None) -> Dict:
        """Analyze account across all timeframes"""
        results = {}

        for timeframe, days in self.timeframes.items():
            # Filter fills
            timeframe_fills = self.filter_fills_by_timeframe(fills, days)

            if not timeframe_fills:
                results[timeframe] = self._empty_timeframe_result()
                continue

            # Calculate metrics
            pnl_metrics = self.calculate_pnl_metrics(timeframe_fills)
            roi_metrics = self.calculate_roi_metrics(timeframe_fills, account_value)

            # Calculate time-specific metrics
            first_trade = min(f.get('time', 0) for f in timeframe_fills)
            last_trade = max(f.get('time', 0) for f in timeframe_fills)
            trading_days = (last_trade - first_trade) / (1000 * 60 * 60 * 24)
            trades_per_day = pnl_metrics['num_trades'] / trading_days if trading_days > 0 else 0

            results[timeframe] = {
                **pnl_metrics,
                **roi_metrics,
                'trading_days': trading_days,
                'trades_per_day': trades_per_day,
                'first_trade_time': datetime.fromtimestamp(first_trade / 1000),
                'last_trade_time': datetime.fromtimestamp(last_trade / 1000)
            }

        return results

    def rank_by_pnl(self, accounts: List[Dict], timeframe: str = '30d') -> List[Dict]:
        """Rank accounts by PnL for a specific timeframe"""
        return sorted(accounts, key=lambda x: x.get(timeframe, {}).get('total_pnl', 0), reverse=True)

    def rank_by_roi(self, accounts: List[Dict], timeframe: str = '30d') -> List[Dict]:
        """Rank accounts by ROI for a specific timeframe"""
        return sorted(accounts, key=lambda x: x.get(timeframe, {}).get('roi', 0), reverse=True)

    def _empty_pnl_metrics(self) -> Dict:
        """Return empty PnL metrics structure"""
        return {
            'total_pnl': 0,
            'net_pnl': 0,
            'gross_profit': 0,
            'gross_loss': 0,
            'total_volume': 0,
            'total_fees': 0,
            'num_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'roi': 0,
            'risk_reward': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'best_coin': ("N/A", 0),
            'worst_coin': ("N/A", 0),
            'coins_traded': [],
            'num_coins': 0
        }

    def _empty_timeframe_result(self) -> Dict:
        """Return empty timeframe result"""
        return {
            **self._empty_pnl_metrics(),
            'roi': 0,
            'roi_net': 0,
            'roi_annualized': 0,
            'trading_days': 0,
            'trades_per_day': 0
        }

    def generate_comparison_table(self, account_results: Dict) -> str:
        """Generate a formatted comparison table across timeframes"""
        timeframes = ['7d', '30d', 'lifetime']

        output = []
        output.append("\n" + "="*100)
        output.append("MULTI-TIMEFRAME ANALYSIS")
        output.append("="*100)
        output.append(f"{'Metric':<25} {'7 Days':<25} {'30 Days':<25} {'Lifetime':<25}")
        output.append("-"*100)

        metrics_to_show = [
            ('Total PnL', 'total_pnl', '$'),
            ('Net PnL', 'net_pnl', '$'),
            ('ROI', 'roi', '%'),
            ('Win Rate', 'win_rate', '%'),
            ('Profit Factor', 'profit_factor', 'x'),
            ('Total Trades', 'num_trades', ''),
            ('Winning Trades', 'winning_trades', ''),
            ('Total Volume', 'total_volume', '$'),
            ('Trades/Day', 'trades_per_day', ''),
        ]

        for label, key, fmt in metrics_to_show:
            values = []
            for tf in timeframes:
                val = account_results.get(tf, {}).get(key, 0)
                if fmt == '$':
                    values.append(f"${val:,.2f}")
                elif fmt == '%':
                    values.append(f"{val:.2%}")
                elif fmt == 'x':
                    values.append(f"{val:.2f}x")
                else:
                    values.append(f"{val:.0f}" if isinstance(val, (int, float)) else str(val))

            output.append(f"{label:<25} {values[0]:<25} {values[1]:<25} {values[2]:<25}")

        output.append("="*100)
        return "\n".join(output)
