#!/usr/bin/env python3
"""
Hyperliquid Web Dashboard
Beautiful UI-friendly web interface for leaderboard analysis and copy trading
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from hyperliquid_api import HyperliquidAPI
from database import Database, CopyTradeConfig, CopyTradePerformance
from config import Config
import json
from datetime import datetime, timedelta
import numpy as np

app = Flask(__name__)
CORS(app)

# Initialize API and Database
api = HyperliquidAPI()
db = Database()

# Cache for leaderboard data (to reduce API calls)
leaderboard_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 30  # Cache for 30 seconds
}

def get_cached_leaderboard():
    """Get leaderboard with caching"""
    now = datetime.now()
    if (leaderboard_cache['data'] is None or
        leaderboard_cache['timestamp'] is None or
        (now - leaderboard_cache['timestamp']).seconds > leaderboard_cache['ttl']):
        leaderboard_cache['data'] = api.get_leaderboard()
        leaderboard_cache['timestamp'] = now
    return leaderboard_cache['data']

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/leaderboard')
def get_leaderboard():
    """API endpoint to fetch leaderboard data"""
    try:
        # Get query parameters
        timeframe = request.args.get('timeframe', 'week')
        limit = int(request.args.get('limit', 100))
        metric = request.args.get('metric', 'pnl')

        # Fetch leaderboard
        leaderboard = api.get_leaderboard()

        if not leaderboard:
            return jsonify({'error': 'Failed to fetch leaderboard'}), 500

        # Parse entries
        parsed_accounts = []
        for entry in leaderboard[:limit]:
            parsed = api.parse_leaderboard_entry(entry)
            parsed_accounts.append(parsed)

        # Map timeframes
        timeframe_map = {
            'day': 'day',
            'week': 'week',
            'month': 'month',
            'lifetime': 'allTime'
        }
        api_timeframe = timeframe_map.get(timeframe, 'week')

        # Sort by metric
        if metric in ['pnl', 'roi', 'volume']:
            parsed_accounts.sort(
                key=lambda x: x.get(api_timeframe, {}).get(metric, 0),
                reverse=True
            )

        return jsonify({
            'success': True,
            'data': parsed_accounts,
            'timeframe': timeframe,
            'metric': metric,
            'total': len(leaderboard),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/account/<address>')
def get_account_detail(address):
    """Get detailed account information"""
    try:
        # Fetch leaderboard
        leaderboard = api.get_leaderboard()

        # Find account
        account = None
        for entry in leaderboard:
            if entry.get('ethAddress', '').lower() == address.lower():
                account = api.parse_leaderboard_entry(entry)
                break

        if not account:
            return jsonify({'error': 'Account not found'}), 404

        return jsonify({
            'success': True,
            'data': account
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_global_stats():
    """Get global statistics"""
    try:
        leaderboard = api.get_leaderboard()

        # Calculate stats
        total_accounts = len(leaderboard)

        # Parse all accounts for stats
        parsed = [api.parse_leaderboard_entry(e) for e in leaderboard]

        # Calculate averages and totals
        stats = {
            'total_accounts': total_accounts,
            'timeframes': {}
        }

        for tf in ['day', 'week', 'month', 'allTime']:
            accounts_with_data = [a for a in parsed if tf in a and a[tf].get('pnl') is not None]

            if accounts_with_data:
                total_pnl = sum(a[tf].get('pnl', 0) for a in accounts_with_data)
                total_volume = sum(a[tf].get('volume', 0) for a in accounts_with_data)
                avg_roi = sum(a[tf].get('roi', 0) for a in accounts_with_data) / len(accounts_with_data)

                profitable = len([a for a in accounts_with_data if a[tf].get('pnl', 0) > 0])

                stats['timeframes'][tf] = {
                    'total_pnl': total_pnl,
                    'total_volume': total_volume,
                    'avg_roi': avg_roi,
                    'profitable_accounts': profitable,
                    'loss_accounts': len(accounts_with_data) - profitable
                }

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top/<timeframe>/<metric>')
def get_top_performers(timeframe, metric):
    """Get top performers for specific timeframe and metric"""
    try:
        limit = int(request.args.get('limit', 10))

        leaderboard = api.get_leaderboard()
        parsed_accounts = [api.parse_leaderboard_entry(e) for e in leaderboard]

        # Map timeframes
        timeframe_map = {
            'day': 'day',
            'week': 'week',
            'month': 'month',
            'lifetime': 'allTime'
        }
        api_timeframe = timeframe_map.get(timeframe, 'week')

        # Filter and sort
        valid_accounts = [
            a for a in parsed_accounts
            if api_timeframe in a and a[api_timeframe].get(metric) is not None
        ]

        valid_accounts.sort(
            key=lambda x: x[api_timeframe].get(metric, 0),
            reverse=True
        )

        return jsonify({
            'success': True,
            'data': valid_accounts[:limit],
            'timeframe': timeframe,
            'metric': metric
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


# =====================================================
# TRADER DETAIL ENDPOINTS
# =====================================================

@app.route('/api/trader/<address>/details')
def get_trader_details(address):
    """Get comprehensive trader details including live data"""
    try:
        # Get leaderboard data for basic stats
        leaderboard = get_cached_leaderboard()
        account = None
        for entry in leaderboard:
            if entry.get('ethAddress', '').lower() == address.lower():
                account = api.parse_leaderboard_entry(entry)
                break

        if not account:
            return jsonify({'error': 'Account not found in leaderboard'}), 404

        # Get user state (positions, account value)
        user_state = api.get_user_state(address)

        # Get live positions
        positions = []
        if user_state and 'assetPositions' in user_state:
            for pos in user_state['assetPositions']:
                position_info = pos.get('position', {})
                if float(position_info.get('szi', 0)) != 0:
                    positions.append({
                        'coin': position_info.get('coin', ''),
                        'size': float(position_info.get('szi', 0)),
                        'entry_price': float(position_info.get('entryPx', 0)),
                        'unrealized_pnl': float(position_info.get('unrealizedPnl', 0)),
                        'return_on_equity': float(position_info.get('returnOnEquity', 0)),
                        'leverage': float(position_info.get('leverage', {}).get('value', 1)),
                        'liquidation_price': float(position_info.get('liquidationPx', 0) or 0),
                        'margin_used': float(position_info.get('marginUsed', 0)),
                    })

        # Get margin summary
        margin_summary = {}
        if user_state and 'marginSummary' in user_state:
            ms = user_state['marginSummary']
            margin_summary = {
                'account_value': float(ms.get('accountValue', 0)),
                'total_margin_used': float(ms.get('totalMarginUsed', 0)),
                'total_ntl_pos': float(ms.get('totalNtlPos', 0)),
                'total_raw_usd': float(ms.get('totalRawUsd', 0)),
            }

        return jsonify({
            'success': True,
            'data': {
                'address': address,
                'display_name': account.get('display_name'),
                'leaderboard_stats': account,
                'positions': positions,
                'margin_summary': margin_summary,
                'position_count': len(positions)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trader/<address>/trades')
def get_trader_trades(address):
    """Get recent trades (fills) for a trader"""
    try:
        hours = int(request.args.get('hours', 24))
        limit = int(request.args.get('limit', 100))

        fills = api.get_user_fills_by_time(address, hours=hours)

        # Parse and format fills
        trades = []
        for fill in fills[:limit]:
            trades.append({
                'trade_id': fill.get('tid', ''),
                'coin': fill.get('coin', ''),
                'side': fill.get('side', ''),
                'price': float(fill.get('px', 0)),
                'size': float(fill.get('sz', 0)),
                'value': float(fill.get('px', 0)) * float(fill.get('sz', 0)),
                'time': fill.get('time', ''),
                'fee': float(fill.get('fee', 0)),
                'start_position': fill.get('startPosition', ''),
                'direction': fill.get('dir', ''),
                'closed_pnl': float(fill.get('closedPnl', 0)),
            })

        return jsonify({
            'success': True,
            'data': trades,
            'count': len(trades),
            'hours': hours
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trader/<address>/orders')
def get_trader_orders(address):
    """Get open orders for a trader"""
    try:
        # Get user state which includes open orders
        user_state = api.get_user_state(address)

        orders = []
        if user_state and 'assetPositions' in user_state:
            # Note: Hyperliquid API doesn't directly expose open orders via clearinghouseState
            # We need to use a different endpoint or the SDK
            pass

        # Try to get open orders via the info API
        try:
            data = {"type": "openOrders", "user": address}
            result = api._post("openOrders", data)
            if isinstance(result, list):
                for order in result:
                    orders.append({
                        'order_id': order.get('oid', ''),
                        'coin': order.get('coin', ''),
                        'side': order.get('side', ''),
                        'limit_price': float(order.get('limitPx', 0)),
                        'size': float(order.get('sz', 0)),
                        'original_size': float(order.get('origSz', 0)),
                        'order_type': order.get('orderType', ''),
                        'reduce_only': order.get('reduceOnly', False),
                        'timestamp': order.get('timestamp', ''),
                    })
        except Exception as e:
            print(f"Error fetching open orders: {e}")

        return jsonify({
            'success': True,
            'data': orders,
            'count': len(orders)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trader/<address>/funding')
def get_trader_funding(address):
    """Get deposit and withdrawal history for a trader"""
    try:
        # Get non-funding ledger updates (deposits, withdrawals, etc.)
        ledger = api.get_user_non_funding_ledger_updates(address)

        deposits = []
        withdrawals = []
        total_deposited = 0
        total_withdrawn = 0

        for entry in ledger:
            delta = entry.get('delta', {})
            entry_type = delta.get('type', '')
            amount = float(delta.get('usdc', 0))
            time_str = entry.get('time', '')

            record = {
                'time': time_str,
                'amount': abs(amount),
                'type': entry_type,
                'hash': delta.get('hash', ''),
            }

            if entry_type == 'deposit':
                deposits.append(record)
                total_deposited += abs(amount)
            elif entry_type in ['withdraw', 'withdrawal']:
                withdrawals.append(record)
                total_withdrawn += abs(amount)

        return jsonify({
            'success': True,
            'data': {
                'deposits': deposits[:50],  # Last 50
                'withdrawals': withdrawals[:50],
                'total_deposited': total_deposited,
                'total_withdrawn': total_withdrawn,
                'net_deposits': total_deposited - total_withdrawn
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================
# COPY TRADING ENDPOINTS
# =====================================================

@app.route('/api/copy-trade/start', methods=['POST'])
def start_copy_trade():
    """Start copy trading a trader"""
    try:
        data = request.get_json()
        trader_address = data.get('trader_address')
        allocation = float(data.get('allocation', 100))  # USD amount
        allocation_type = data.get('allocation_type', 'fixed')  # 'fixed' or 'percentage'
        percentage = float(data.get('percentage', 10))  # If percentage-based
        max_position = float(data.get('max_position', 1000))
        stop_loss = float(data.get('stop_loss', 0))  # 0 = no stop loss

        if not trader_address:
            return jsonify({'error': 'trader_address is required'}), 400

        # Get trader info
        leaderboard = get_cached_leaderboard()
        trader_info = None
        for entry in leaderboard:
            if entry.get('ethAddress', '').lower() == trader_address.lower():
                trader_info = api.parse_leaderboard_entry(entry)
                break

        # Create copy trade config
        config = db.create_copy_trade_config({
            'trader_address': trader_address,
            'trader_name': trader_info.get('display_name') if trader_info else None,
            'allocation': allocation,
            'allocation_type': allocation_type,
            'percentage': percentage,
            'max_position': max_position,
            'stop_loss': stop_loss,
            'is_active': True,
            'started_at': datetime.utcnow()
        })

        return jsonify({
            'success': True,
            'message': f'Started copy trading {trader_address}',
            'config_id': config.id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/copy-trade/stop', methods=['POST'])
def stop_copy_trade():
    """Stop copy trading a trader"""
    try:
        data = request.get_json()
        config_id = data.get('config_id')
        trader_address = data.get('trader_address')

        if config_id:
            db.update_copy_trade_config(config_id, {'is_active': False, 'stopped_at': datetime.utcnow()})
        elif trader_address:
            db.stop_copy_trade_by_address(trader_address)
        else:
            return jsonify({'error': 'config_id or trader_address required'}), 400

        return jsonify({
            'success': True,
            'message': 'Copy trading stopped'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/copy-trade/pause', methods=['POST'])
def pause_copy_trade():
    """Pause copy trading (don't copy new trades but keep tracking)"""
    try:
        data = request.get_json()
        config_id = data.get('config_id')

        if not config_id:
            return jsonify({'error': 'config_id required'}), 400

        db.update_copy_trade_config(config_id, {'is_paused': True})

        return jsonify({
            'success': True,
            'message': 'Copy trading paused'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/copy-trade/resume', methods=['POST'])
def resume_copy_trade():
    """Resume paused copy trading"""
    try:
        data = request.get_json()
        config_id = data.get('config_id')

        if not config_id:
            return jsonify({'error': 'config_id required'}), 400

        db.update_copy_trade_config(config_id, {'is_paused': False})

        return jsonify({
            'success': True,
            'message': 'Copy trading resumed'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/copy-trade/list')
def list_copy_trades():
    """List all active and historical copy trades"""
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'

        configs = db.get_all_copy_trade_configs(active_only=active_only)

        result = []
        for config in configs:
            # Get current performance
            performance = db.get_copy_trade_performance(config.id)

            # Get trader's current leaderboard stats
            leaderboard = get_cached_leaderboard()
            trader_stats = None
            for entry in leaderboard:
                if entry.get('ethAddress', '').lower() == config.trader_address.lower():
                    trader_stats = api.parse_leaderboard_entry(entry)
                    break

            result.append({
                'config_id': config.id,
                'trader_address': config.trader_address,
                'trader_name': config.trader_name,
                'allocation': config.allocation,
                'allocation_type': config.allocation_type,
                'percentage': config.percentage,
                'max_position': config.max_position,
                'stop_loss': config.stop_loss,
                'is_active': config.is_active,
                'is_paused': config.is_paused,
                'started_at': config.started_at.isoformat() if config.started_at else None,
                'stopped_at': config.stopped_at.isoformat() if config.stopped_at else None,
                'performance': performance,
                'trader_stats': trader_stats
            })

        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/copy-trade/performance')
def get_copy_trading_performance():
    """Get overall copy trading portfolio performance"""
    try:
        # Get all active configs
        configs = db.get_all_copy_trade_configs(active_only=False)

        total_allocated = 0
        total_pnl = 0
        total_trades = 0
        winning_trades = 0

        trader_performances = []

        for config in configs:
            perf = db.get_copy_trade_performance(config.id)
            if perf:
                total_allocated += config.allocation
                total_pnl += perf.get('total_pnl', 0)
                total_trades += perf.get('total_trades', 0)
                winning_trades += perf.get('winning_trades', 0)

                trader_performances.append({
                    'trader_address': config.trader_address,
                    'trader_name': config.trader_name,
                    'allocation': config.allocation,
                    'pnl': perf.get('total_pnl', 0),
                    'roi': perf.get('roi', 0),
                    'trades': perf.get('total_trades', 0),
                    'win_rate': perf.get('win_rate', 0),
                    'is_active': config.is_active
                })

        overall_roi = (total_pnl / total_allocated * 100) if total_allocated > 0 else 0
        overall_win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        return jsonify({
            'success': True,
            'data': {
                'total_allocated': total_allocated,
                'total_pnl': total_pnl,
                'overall_roi': overall_roi,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'overall_win_rate': overall_win_rate,
                'trader_performances': trader_performances
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================
# AI TRADER RECOMMENDATION
# =====================================================

@app.route('/api/recommendations')
def get_trader_recommendations():
    """Get AI-powered trader recommendations for copy trading"""
    try:
        limit = int(request.args.get('limit', 10))

        leaderboard = get_cached_leaderboard()
        parsed_accounts = [api.parse_leaderboard_entry(e) for e in leaderboard]

        # Score each trader based on multiple factors
        scored_traders = []

        for account in parsed_accounts:
            score = 0
            reasons = []

            # Get multi-timeframe data
            day_data = account.get('day', {})
            week_data = account.get('week', {})
            month_data = account.get('month', {})
            all_time = account.get('allTime', {})

            # Factor 1: Consistency across timeframes (weight: 30%)
            # Traders who are profitable across multiple timeframes are more reliable
            timeframes_profitable = 0
            for tf_data in [day_data, week_data, month_data, all_time]:
                if tf_data.get('pnl', 0) > 0:
                    timeframes_profitable += 1

            consistency_score = (timeframes_profitable / 4) * 30
            score += consistency_score
            if timeframes_profitable >= 3:
                reasons.append(f"Profitable in {timeframes_profitable}/4 timeframes")

            # Factor 2: ROI performance (weight: 25%)
            # Higher weekly ROI with reasonable bounds (not too high = risky)
            week_roi = week_data.get('roi', 0)
            if 0.05 <= week_roi <= 0.5:  # 5-50% weekly ROI is sweet spot
                roi_score = 25
                reasons.append(f"Healthy weekly ROI: {week_roi*100:.1f}%")
            elif 0 < week_roi < 0.05:
                roi_score = 15
            elif week_roi > 0.5:
                roi_score = 10  # Too high might be too risky
            else:
                roi_score = 0
            score += roi_score

            # Factor 3: Account value / Capital (weight: 20%)
            # Prefer traders with substantial capital (more serious)
            account_value = account.get('account_value', 0)
            if account_value >= 100000:
                capital_score = 20
                reasons.append(f"Large account: ${account_value:,.0f}")
            elif account_value >= 50000:
                capital_score = 15
            elif account_value >= 10000:
                capital_score = 10
            else:
                capital_score = 5
            score += capital_score

            # Factor 4: Trading volume (weight: 15%)
            # Active traders are better to copy (more opportunities)
            week_volume = week_data.get('volume', 0)
            if week_volume >= 10000000:  # $10M+ weekly volume
                volume_score = 15
                reasons.append("High trading activity")
            elif week_volume >= 1000000:
                volume_score = 10
            elif week_volume >= 100000:
                volume_score = 5
            else:
                volume_score = 2
            score += volume_score

            # Factor 5: Risk-adjusted returns (weight: 10%)
            # Penalize negative PnL in any recent timeframe
            if day_data.get('pnl', 0) < 0:
                score -= 5
            if week_data.get('pnl', 0) < 0:
                score -= 10

            # Bonus: Long-term profitability
            if all_time.get('pnl', 0) > 0 and all_time.get('roi', 0) > 0:
                score += 10
                reasons.append("Long-term profitable")

            scored_traders.append({
                'address': account.get('address'),
                'display_name': account.get('display_name'),
                'score': round(score, 2),
                'reasons': reasons,
                'account_value': account_value,
                'stats': {
                    'day': day_data,
                    'week': week_data,
                    'month': month_data,
                    'allTime': all_time
                }
            })

        # Sort by score and return top recommendations
        scored_traders.sort(key=lambda x: x['score'], reverse=True)
        recommendations = scored_traders[:limit]

        # Add rank
        for i, rec in enumerate(recommendations):
            rec['rank'] = i + 1

        return jsonify({
            'success': True,
            'data': recommendations,
            'algorithm': 'Multi-factor scoring based on consistency, ROI, capital, volume, and risk',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        Hyperliquid Dashboard - Web Interface             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝

    Dashboard running at: http://localhost:8080

    Press Ctrl+C to stop the server
    """)

    app.run(debug=True, host='0.0.0.0', port=8080)
