import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    HYPERLIQUID_API_KEY = os.getenv('HYPERLIQUID_API_KEY', '')
    HYPERLIQUID_SECRET = os.getenv('HYPERLIQUID_SECRET', '')
    HYPERLIQUID_WALLET_ADDRESS = os.getenv('HYPERLIQUID_WALLET_ADDRESS', '')

    # Tracked Addresses
    TRACKED_ADDRESSES = [addr.strip() for addr in os.getenv('TRACKED_ADDRESSES', '').split(',') if addr.strip()]

    # Hyperliquid API endpoints
    MAINNET_API_URL = "https://api.hyperliquid.xyz"
    TESTNET_API_URL = "https://api.hyperliquid-testnet.xyz"

    # Trading Configuration
    COPY_TRADE_ENABLED = os.getenv('COPY_TRADE_ENABLED', 'false').lower() == 'true'
    POSITION_SIZE_MULTIPLIER = float(os.getenv('POSITION_SIZE_MULTIPLIER', '0.1'))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '1000'))
    MIN_WIN_RATE = float(os.getenv('MIN_WIN_RATE', '0.6'))
    MIN_TRADES = int(os.getenv('MIN_TRADES', '50'))

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///hyperliquid_tracker.db')

    # Tracking Configuration
    TOP_ACCOUNTS_LIMIT = 100
    REFRESH_INTERVAL = 300  # seconds

    # Risk Management
    MAX_SLIPPAGE = 0.005  # 0.5%
    STOP_LOSS_PERCENTAGE = 0.02  # 2%
