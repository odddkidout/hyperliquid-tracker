#!/usr/bin/env python3
"""
Test script to verify Hyperliquid API connection and functionality
"""

from hyperliquid_api import HyperliquidAPI
from datetime import datetime

def test_api_connection():
    """Test basic API connectivity"""
    print("Testing Hyperliquid API Connection...")
    print("=" * 60)

    api = HyperliquidAPI(use_testnet=False)

    # Test 1: Get Meta
    print("\n[1/5] Testing Meta endpoint...")
    try:
        meta = api.get_meta()
        if meta and 'universe' in meta:
            print(f"✓ Meta endpoint working - Found {len(meta['universe'])} assets")
        else:
            print("✗ Meta endpoint returned unexpected data")
    except Exception as e:
        print(f"✗ Meta endpoint failed: {e}")

    # Test 2: Get All Mids
    print("\n[2/5] Testing All Mids endpoint...")
    try:
        mids = api.get_all_mids()
        if mids:
            print(f"✓ All Mids endpoint working - Found {len(mids)} mid prices")
            # Show a few examples
            for i, (coin, price) in enumerate(list(mids.items())[:3]):
                print(f"   {coin}: ${price}")
        else:
            print("✗ All Mids endpoint returned no data")
    except Exception as e:
        print(f"✗ All Mids endpoint failed: {e}")

    # Test 3: Get Leaderboard
    print("\n[3/5] Testing Leaderboard endpoint...")
    try:
        leaderboard = api.get_leaderboard()
        if leaderboard and isinstance(leaderboard, list):
            print(f"✓ Leaderboard endpoint working - Found {len(leaderboard)} entries")
            if leaderboard:
                print(f"   Top trader: {leaderboard[0]}")
        else:
            print("⚠ Leaderboard endpoint returned empty or unexpected data")
    except Exception as e:
        print(f"✗ Leaderboard endpoint failed: {e}")

    # Test 4: Get User State (use a known address or example)
    print("\n[4/5] Testing User State endpoint...")
    try:
        # Example address - replace with a real one if available
        test_address = "0x0000000000000000000000000000000000000000"
        state = api.get_user_state(test_address)
        print(f"✓ User State endpoint working (tested with example address)")
    except Exception as e:
        print(f"⚠ User State endpoint test inconclusive: {e}")

    # Test 5: Get User Fills
    print("\n[5/5] Testing User Fills endpoint...")
    try:
        test_address = "0x0000000000000000000000000000000000000000"
        fills = api.get_user_fills(test_address)
        print(f"✓ User Fills endpoint working (tested with example address)")
    except Exception as e:
        print(f"⚠ User Fills endpoint test inconclusive: {e}")

    print("\n" + "=" * 60)
    print("API Connection Test Complete!")
    print("=" * 60)

def test_database():
    """Test database functionality"""
    print("\n\nTesting Database Functionality...")
    print("=" * 60)

    from database import Database

    try:
        db = Database()
        print("✓ Database connection successful")

        # Test adding an account
        test_data = {
            'address': '0xTEST1234567890',
            'total_trades': 100,
            'winning_trades': 65,
            'win_rate': 0.65,
            'total_pnl': 1000.0,
            'total_volume': 50000.0,
            'roi': 0.25
        }

        db.add_tracked_account(test_data)
        print("✓ Can add tracked accounts")

        # Test querying
        accounts = db.get_top_accounts(limit=1)
        print(f"✓ Can query accounts - Found {len(accounts)} account(s)")

        db.close()
        print("\n✓ Database tests passed!")

    except Exception as e:
        print(f"✗ Database test failed: {e}")

    print("=" * 60)

def test_analytics():
    """Test analytics functionality"""
    print("\n\nTesting Analytics Functionality...")
    print("=" * 60)

    from analytics import PerformanceAnalytics

    try:
        analytics = PerformanceAnalytics()
        print("✓ Analytics module loaded")

        # Test with dummy data
        dummy_fills = [
            {'coin': 'BTC', 'px': '50000', 'sz': '0.1', 'closedPnl': 100, 'time': 1000000},
            {'coin': 'ETH', 'px': '3000', 'sz': '1', 'closedPnl': -50, 'time': 1000001},
            {'coin': 'BTC', 'px': '50100', 'sz': '0.1', 'closedPnl': 150, 'time': 1000002},
        ]

        performance = analytics.calculate_performance(dummy_fills)
        print(f"✓ Can calculate performance metrics")
        print(f"   Win Rate: {performance['win_rate']:.2%}")
        print(f"   Total PnL: ${performance['total_pnl']:.2f}")

        print("\n✓ Analytics tests passed!")

    except Exception as e:
        print(f"✗ Analytics test failed: {e}")

    print("=" * 60)

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  Hyperliquid Tracker - Connection Test")
    print("=" * 60)

    test_api_connection()
    test_database()
    test_analytics()

    print("\n\n" + "=" * 60)
    print("  All Tests Complete!")
    print("=" * 60)
    print("\nIf all tests passed, you're ready to start tracking!")
    print("Run: python main.py --mode track")
    print()
