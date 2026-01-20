#!/usr/bin/env python3
"""
Simple CLI Dashboard for Hyperliquid Tracker
Displays real-time statistics and tracked accounts
"""

import time
import os
from datetime import datetime
from database import Database
from config import Config

class Dashboard:
    def __init__(self):
        self.db = Database()

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        """Print dashboard header"""
        print("╔" + "═" * 98 + "╗")
        print("║" + " " * 30 + "HYPERLIQUID TRACKER DASHBOARD" + " " * 38 + "║")
        print("║" + f" Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " " * 60 + "║")
        print("╚" + "═" * 98 + "╝")
        print()

    def print_config(self):
        """Print current configuration"""
        print("┌─ Configuration " + "─" * 82 + "┐")
        print(f"│ Copy Trading: {'ENABLED' if Config.COPY_TRADE_ENABLED else 'DISABLED':<15} │ "
              f"Position Multiplier: {Config.POSITION_SIZE_MULTIPLIER:<10} │ "
              f"Max Size: ${Config.MAX_POSITION_SIZE:<15,.0f} │")
        print(f"│ Min Win Rate: {Config.MIN_WIN_RATE:<15.1%} │ "
              f"Min Trades: {Config.MIN_TRADES:<15} │ "
              f"                            │")
        print("└" + "─" * 98 + "┘")
        print()

    def print_summary_stats(self):
        """Print summary statistics"""
        # Get total accounts tracked
        total_accounts = self.db.session.query(Database.TrackedAccount).count()
        qualifying_accounts = len(self.db.get_top_accounts(
            limit=1000,
            min_win_rate=Config.MIN_WIN_RATE,
            min_trades=Config.MIN_TRADES
        ))

        print("┌─ Summary " + "─" * 88 + "┐")
        print(f"│ Total Accounts Tracked: {total_accounts:<20} │ "
              f"Qualifying Accounts: {qualifying_accounts:<30} │")
        print("└" + "─" * 98 + "┘")
        print()

    def print_top_accounts(self, limit=10):
        """Print top performing accounts"""
        top_accounts = self.db.get_top_accounts(
            limit=limit,
            min_win_rate=Config.MIN_WIN_RATE,
            min_trades=Config.MIN_TRADES
        )

        print("┌─ Top Performers " + "─" * 81 + "┐")
        print("│ " + f"{'Rank':<6} {'Address':<45} {'Win Rate':<12} {'ROI':<12} {'Trades':<10}" + " │")
        print("├" + "─" * 98 + "┤")

        for i, account in enumerate(top_accounts, 1):
            addr_short = account.address[:10] + "..." + account.address[-8:]
            print(f"│ {i:<6} {addr_short:<45} {account.win_rate:>10.2%}  "
                  f"{account.roi:>10.2%}  {account.total_trades:>8}   │")

        if len(top_accounts) < limit:
            for _ in range(limit - len(top_accounts)):
                print("│" + " " * 98 + "│")

        print("└" + "─" * 98 + "┘")
        print()

    def print_recent_activity(self):
        """Print recent trading activity"""
        # Get recent trades
        from database import Trade
        recent_trades = self.db.session.query(Trade).order_by(
            Trade.created_at.desc()
        ).limit(5).all()

        print("┌─ Recent Activity " + "─" * 80 + "┐")

        if not recent_trades:
            print("│ No recent activity" + " " * 76 + "│")
        else:
            for trade in recent_trades:
                addr_short = trade.account_address[:8] + "..."
                time_str = trade.opened_at.strftime('%H:%M:%S')
                pnl_str = f"${trade.pnl:+,.2f}" if trade.pnl else "Open"
                status = "✓" if trade.pnl and trade.pnl > 0 else "✗" if trade.pnl else "•"

                info = f"{status} {time_str} │ {addr_short} │ {trade.symbol:<8} │ {trade.side:<6} │ {pnl_str}"
                print(f"│ {info:<97}│")

        print("└" + "─" * 98 + "┘")
        print()

    def print_copy_trades(self):
        """Print copy trading statistics"""
        from database import CopiedTrade
        copied_trades = self.db.session.query(CopiedTrade).all()

        total_copied = len(copied_trades)
        total_pnl = sum(t.pnl for t in copied_trades if t.pnl)
        open_trades = sum(1 for t in copied_trades if t.status == 'open')

        print("┌─ Copy Trading Stats " + "─" * 77 + "┐")
        print(f"│ Total Copied: {total_copied:<15} │ "
              f"Open Positions: {open_trades:<15} │ "
              f"Total PnL: ${total_pnl:>15,.2f}  │")
        print("└" + "─" * 98 + "┘")
        print()

    def print_controls(self):
        """Print control instructions"""
        print("Press Ctrl+C to exit")

    def run(self, refresh_interval=5):
        """Run the dashboard with auto-refresh"""
        try:
            while True:
                self.clear_screen()
                self.print_header()
                self.print_config()
                self.print_summary_stats()
                self.print_top_accounts(limit=10)
                self.print_recent_activity()
                self.print_copy_trades()
                self.print_controls()

                time.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")
            self.db.close()

if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.run(refresh_interval=5)
