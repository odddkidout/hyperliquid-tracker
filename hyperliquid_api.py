import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import Config

try:
    from hyperliquid.info import Info
    HYPERLIQUID_SDK_AVAILABLE = True
except ImportError:
    HYPERLIQUID_SDK_AVAILABLE = False

class HyperliquidAPI:
    def __init__(self, use_testnet=False):
        self.base_url = Config.TESTNET_API_URL if use_testnet else Config.MAINNET_API_URL
        self.info_url = f"{self.base_url}/info"

        # Initialize official SDK if available
        if HYPERLIQUID_SDK_AVAILABLE:
            try:
                self.info = Info(skip_ws=True)
            except:
                self.info = None
        else:
            self.info = None

    def _post(self, endpoint: str, data: Dict) -> Dict:
        """Make a POST request to the Hyperliquid API"""
        url = f"{self.info_url}"
        try:
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return {}

    def get_user_state(self, address: str) -> Dict:
        """Get current state for a user address"""
        data = {
            "type": "clearinghouseState",
            "user": address
        }
        return self._post("clearinghouseState", data)

    def get_user_fills(self, address: str, start_time: Optional[int] = None) -> List[Dict]:
        """Get fill history for a user"""
        data = {
            "type": "userFills",
            "user": address
        }
        if start_time:
            data["startTime"] = start_time

        result = self._post("userFills", data)
        return result if isinstance(result, list) else []

    def get_user_funding(self, address: str, start_time: Optional[int] = None) -> List[Dict]:
        """Get funding payment history for a user"""
        data = {
            "type": "userFunding",
            "user": address
        }
        if start_time:
            data["startTime"] = start_time

        result = self._post("userFunding", data)
        return result if isinstance(result, list) else []

    def get_user_non_funding_ledger_updates(self, address: str, start_time: Optional[int] = None) -> List[Dict]:
        """Get non-funding ledger updates (deposits, withdrawals, etc.)"""
        data = {
            "type": "userNonFundingLedgerUpdates",
            "user": address
        }
        if start_time:
            data["startTime"] = start_time

        result = self._post("userNonFundingLedgerUpdates", data)
        return result if isinstance(result, list) else []

    def get_meta(self) -> Dict:
        """Get exchange metadata including available assets"""
        data = {"type": "meta"}
        return self._post("meta", data)

    def get_all_mids(self) -> Dict:
        """Get current mid prices for all assets"""
        data = {"type": "allMids"}
        return self._post("allMids", data)

    def get_user_token_balances(self, address: str) -> Dict:
        """Get token balances for a user"""
        data = {
            "type": "spotClearinghouseState",
            "user": address
        }
        return self._post("spotClearinghouseState", data)

    def get_leaderboard(self) -> List[Dict]:
        """Get the real Hyperliquid leaderboard from stats API

        Returns list of traders with PnL, ROI, and volume across timeframes
        """
        leaderboard_url = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"

        try:
            response = requests.get(leaderboard_url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'leaderboardRows' in data:
                leaderboard_rows = data['leaderboardRows']
                print(f"✓ Fetched {len(leaderboard_rows)} traders from leaderboard")
                return leaderboard_rows
            else:
                print("❌ Unexpected leaderboard format")
                return []

        except Exception as e:
            print(f"❌ Error fetching leaderboard: {e}")
            return []

    def parse_leaderboard_entry(self, entry: Dict) -> Dict:
        """Parse a leaderboard entry into a standardized format"""
        address = entry.get('ethAddress', '')
        account_value = float(entry.get('accountValue', 0))
        display_name = entry.get('displayName')

        # Parse window performances
        performances = {}
        for window_data in entry.get('windowPerformances', []):
            if len(window_data) == 2:
                timeframe, metrics = window_data
                performances[timeframe] = {
                    'pnl': float(metrics.get('pnl', 0)),
                    'roi': float(metrics.get('roi', 0)),
                    'volume': float(metrics.get('vlm', 0))
                }

        return {
            'address': address,
            'display_name': display_name,
            'account_value': account_value,
            'day': performances.get('day', {}),
            'week': performances.get('week', {}),
            'month': performances.get('month', {}),
            'allTime': performances.get('allTime', {}),
            'raw': entry
        }

    def get_user_fills_by_time(self, address: str, hours: int = 24) -> List[Dict]:
        """Get recent fills for a user within specified hours"""
        start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
        return self.get_user_fills(address, start_time)

    def get_funding_history(self, coin: str, start_time: Optional[int] = None) -> List[Dict]:
        """Get funding rate history for a coin"""
        data = {
            "type": "fundingHistory",
            "coin": coin
        }
        if start_time:
            data["startTime"] = start_time

        result = self._post("fundingHistory", data)
        return result if isinstance(result, list) else []

    def get_candles_snapshot(self, coin: str, interval: str, start_time: int, end_time: int) -> List[Dict]:
        """Get historical candles"""
        data = {
            "type": "candleSnapshot",
            "req": {
                "coin": coin,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time
            }
        }
        result = self._post("candleSnapshot", data)
        return result if isinstance(result, list) else []
