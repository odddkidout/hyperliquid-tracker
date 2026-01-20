import numpy as np
from typing import Dict, List
from collections import defaultdict

class PerformanceAnalytics:
    def calculate_performance(self, fills: List[Dict], state: Dict = None) -> Dict:
        """Calculate comprehensive performance metrics from fill history"""

        if not fills:
            return self._empty_performance()

        # Group fills by position
        positions = self._group_fills_by_position(fills)

        # Calculate metrics
        total_trades = len(positions)
        winning_trades = sum(1 for p in positions if p['pnl'] > 0)
        losing_trades = sum(1 for p in positions if p['pnl'] < 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        total_pnl = sum(p['pnl'] for p in positions)
        total_volume = sum(abs(p['volume']) for p in positions)

        # Calculate average win/loss
        wins = [p['pnl'] for p in positions if p['pnl'] > 0]
        losses = [p['pnl'] for p in positions if p['pnl'] < 0]

        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        profit_factor = sum(wins) / abs(sum(losses)) if losses else float('inf')

        # Calculate ROI (assuming some initial capital)
        # We'll estimate based on volume
        estimated_capital = total_volume / 10 if total_volume > 0 else 1
        roi = (total_pnl / estimated_capital) if estimated_capital > 0 else 0

        # Calculate Sharpe Ratio
        returns = [p['pnl'] for p in positions]
        sharpe_ratio = self._calculate_sharpe_ratio(returns)

        # Calculate Maximum Drawdown
        max_drawdown = self._calculate_max_drawdown(positions)

        # Calculate consecutive wins/losses
        max_consecutive_wins = self._calculate_max_consecutive(positions, True)
        max_consecutive_losses = self._calculate_max_consecutive(positions, False)

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_volume': total_volume,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'roi': roi,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses
        }

    def _group_fills_by_position(self, fills: List[Dict]) -> List[Dict]:
        """Group fills into complete positions (entry + exit)"""
        positions = []
        position_tracker = defaultdict(list)

        for fill in fills:
            coin = fill.get('coin', '')
            side = fill.get('side', '')
            price = float(fill.get('px', 0))
            size = float(fill.get('sz', 0))
            time = fill.get('time', 0)

            # Determine if this is opening or closing
            # This is simplified - in reality, you'd need to track running position
            pnl = fill.get('closedPnl', 0)

            if pnl != 0:  # Position was closed
                positions.append({
                    'coin': coin,
                    'pnl': float(pnl),
                    'volume': price * size,
                    'time': time
                })

        return positions

    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe Ratio"""
        if not returns or len(returns) < 2:
            return 0.0

        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate

        if np.std(excess_returns) == 0:
            return 0.0

        sharpe = np.mean(excess_returns) / np.std(excess_returns)
        # Annualize (assuming daily returns)
        sharpe_annualized = sharpe * np.sqrt(365)

        return sharpe_annualized

    def _calculate_max_drawdown(self, positions: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if not positions:
            return 0.0

        # Sort by time
        sorted_positions = sorted(positions, key=lambda x: x['time'])

        # Calculate cumulative PnL
        cumulative_pnl = []
        running_pnl = 0

        for pos in sorted_positions:
            running_pnl += pos['pnl']
            cumulative_pnl.append(running_pnl)

        if not cumulative_pnl:
            return 0.0

        # Calculate drawdown
        peak = cumulative_pnl[0]
        max_dd = 0

        for value in cumulative_pnl:
            if value > peak:
                peak = value
            dd = (peak - value) / abs(peak) if peak != 0 else 0
            max_dd = max(max_dd, dd)

        return max_dd

    def _calculate_max_consecutive(self, positions: List[Dict], wins: bool) -> int:
        """Calculate maximum consecutive wins or losses"""
        if not positions:
            return 0

        max_consecutive = 0
        current_consecutive = 0

        sorted_positions = sorted(positions, key=lambda x: x['time'])

        for pos in sorted_positions:
            is_win = pos['pnl'] > 0

            if is_win == wins:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def _empty_performance(self) -> Dict:
        """Return empty performance metrics"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'total_volume': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
            'roi': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0
        }

    def rank_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """Rank accounts based on multiple criteria"""
        if not accounts:
            return []

        # Scoring weights
        weights = {
            'win_rate': 0.3,
            'roi': 0.3,
            'sharpe_ratio': 0.2,
            'profit_factor': 0.1,
            'total_trades': 0.1
        }

        scored_accounts = []

        for account in accounts:
            score = 0
            score += account.get('win_rate', 0) * weights['win_rate'] * 100
            score += min(account.get('roi', 0), 2) * weights['roi'] * 50  # Cap ROI at 200%
            score += min(max(account.get('sharpe_ratio', 0), 0), 3) * weights['sharpe_ratio'] * 33
            score += min(account.get('profit_factor', 0), 5) * weights['profit_factor'] * 20
            score += min(account.get('total_trades', 0) / 100, 1) * weights['total_trades'] * 100

            account['score'] = score
            scored_accounts.append(account)

        # Sort by score
        return sorted(scored_accounts, key=lambda x: x['score'], reverse=True)
