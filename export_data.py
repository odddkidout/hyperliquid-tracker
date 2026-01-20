#!/usr/bin/env python3
"""
Export tracked data to CSV for external analysis
"""

import csv
from datetime import datetime
from database import Database, TrackedAccount, Trade, CopiedTrade
import argparse

class DataExporter:
    def __init__(self):
        self.db = Database()

    def export_tracked_accounts(self, filename='tracked_accounts.csv'):
        """Export tracked accounts to CSV"""
        accounts = self.db.session.query(TrackedAccount).all()

        if not accounts:
            print("No tracked accounts found.")
            return

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'address', 'username', 'total_trades', 'winning_trades',
                'win_rate', 'total_pnl', 'total_volume', 'roi',
                'sharpe_ratio', 'max_drawdown', 'last_updated', 'created_at'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for account in accounts:
                writer.writerow({
                    'address': account.address,
                    'username': account.username or '',
                    'total_trades': account.total_trades,
                    'winning_trades': account.winning_trades,
                    'win_rate': account.win_rate,
                    'total_pnl': account.total_pnl,
                    'total_volume': account.total_volume,
                    'roi': account.roi,
                    'sharpe_ratio': account.sharpe_ratio,
                    'max_drawdown': account.max_drawdown,
                    'last_updated': account.last_updated,
                    'created_at': account.created_at
                })

        print(f"✓ Exported {len(accounts)} accounts to {filename}")

    def export_trades(self, filename='trades.csv', address=None):
        """Export trades to CSV"""
        query = self.db.session.query(Trade)

        if address:
            query = query.filter_by(account_address=address)

        trades = query.all()

        if not trades:
            print("No trades found.")
            return

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'account_address', 'trade_id', 'symbol', 'side',
                'entry_price', 'exit_price', 'size', 'pnl',
                'is_winner', 'opened_at', 'closed_at'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for trade in trades:
                writer.writerow({
                    'account_address': trade.account_address,
                    'trade_id': trade.trade_id,
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price or '',
                    'size': trade.size,
                    'pnl': trade.pnl or '',
                    'is_winner': trade.is_winner or '',
                    'opened_at': trade.opened_at,
                    'closed_at': trade.closed_at or ''
                })

        print(f"✓ Exported {len(trades)} trades to {filename}")

    def export_copied_trades(self, filename='copied_trades.csv'):
        """Export copied trades to CSV"""
        copied_trades = self.db.session.query(CopiedTrade).all()

        if not copied_trades:
            print("No copied trades found.")
            return

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'original_trade_id', 'source_account', 'symbol', 'side',
                'entry_price', 'exit_price', 'size', 'pnl',
                'status', 'opened_at', 'closed_at'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for trade in copied_trades:
                writer.writerow({
                    'original_trade_id': trade.original_trade_id,
                    'source_account': trade.source_account,
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price or '',
                    'size': trade.size,
                    'pnl': trade.pnl or '',
                    'status': trade.status,
                    'opened_at': trade.opened_at,
                    'closed_at': trade.closed_at or ''
                })

        print(f"✓ Exported {len(copied_trades)} copied trades to {filename}")

    def export_summary_report(self, filename='summary_report.txt'):
        """Export a text summary report"""
        from config import Config

        accounts = self.db.get_top_accounts(
            limit=100,
            min_win_rate=Config.MIN_WIN_RATE,
            min_trades=Config.MIN_TRADES
        )

        with open(filename, 'w') as f:
            f.write("HYPERLIQUID TRACKER - SUMMARY REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"Total Qualifying Accounts: {len(accounts)}\n")
            f.write(f"Minimum Win Rate: {Config.MIN_WIN_RATE:.1%}\n")
            f.write(f"Minimum Trades: {Config.MIN_TRADES}\n\n")

            if accounts:
                f.write("TOP 20 PERFORMERS:\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'Rank':<6} {'Address':<45} {'Win Rate':<12} {'ROI':<12} {'Trades':<10}\n")
                f.write("-" * 80 + "\n")

                for i, account in enumerate(accounts[:20], 1):
                    f.write(f"{i:<6} {account.address:<45} {account.win_rate:>10.2%}  "
                           f"{account.roi:>10.2%}  {account.total_trades:>8}\n")

                f.write("\n" + "=" * 80 + "\n")

                # Statistics
                avg_win_rate = sum(a.win_rate for a in accounts) / len(accounts)
                avg_roi = sum(a.roi for a in accounts) / len(accounts)
                avg_trades = sum(a.total_trades for a in accounts) / len(accounts)

                f.write("\nAVERAGE STATISTICS:\n")
                f.write(f"Average Win Rate: {avg_win_rate:.2%}\n")
                f.write(f"Average ROI: {avg_roi:.2%}\n")
                f.write(f"Average Trades: {avg_trades:.0f}\n")

        print(f"✓ Exported summary report to {filename}")

    def export_all(self):
        """Export all data"""
        print("\nExporting all data...\n")
        self.export_tracked_accounts()
        self.export_trades()
        self.export_copied_trades()
        self.export_summary_report()
        print("\n✓ All data exported successfully!")

def main():
    parser = argparse.ArgumentParser(description='Export Hyperliquid Tracker data')

    parser.add_argument(
        '--type',
        choices=['accounts', 'trades', 'copied', 'summary', 'all'],
        default='all',
        help='Type of data to export'
    )

    parser.add_argument(
        '--address',
        type=str,
        help='Filter trades by account address'
    )

    args = parser.parse_args()

    exporter = DataExporter()

    if args.type == 'accounts':
        exporter.export_tracked_accounts()
    elif args.type == 'trades':
        exporter.export_trades(address=args.address)
    elif args.type == 'copied':
        exporter.export_copied_trades()
    elif args.type == 'summary':
        exporter.export_summary_report()
    elif args.type == 'all':
        exporter.export_all()

    exporter.db.close()

if __name__ == '__main__':
    main()
