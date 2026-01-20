from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()


class CopyTradeConfig(Base):
    """Configuration for copy trading a specific trader"""
    __tablename__ = 'copy_trade_configs'

    id = Column(Integer, primary_key=True)
    trader_address = Column(String, nullable=False)
    trader_name = Column(String)
    allocation = Column(Float, default=100.0)  # USD amount allocated
    allocation_type = Column(String, default='fixed')  # 'fixed' or 'percentage'
    percentage = Column(Float, default=10.0)  # Percentage of portfolio (if percentage-based)
    max_position = Column(Float, default=1000.0)  # Max position size in USD
    stop_loss = Column(Float, default=0.0)  # Stop loss percentage (0 = disabled)
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class CopyTradePerformance(Base):
    """Track performance of copy trades"""
    __tablename__ = 'copy_trade_performance'

    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, nullable=False)  # FK to CopyTradeConfig
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    total_volume = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    best_trade_pnl = Column(Float, default=0.0)
    worst_trade_pnl = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class TrackedAccount(Base):
    __tablename__ = 'tracked_accounts'

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    username = Column(String)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    total_volume = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    is_tracked = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    account_address = Column(String, nullable=False)
    trade_id = Column(String, unique=True)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # 'long' or 'short'
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    size = Column(Float, nullable=False)
    pnl = Column(Float)
    is_winner = Column(Boolean)
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime)
    is_copied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CopiedTrade(Base):
    __tablename__ = 'copied_trades'

    id = Column(Integer, primary_key=True)
    original_trade_id = Column(String, nullable=False)
    source_account = Column(String, nullable=False)
    our_trade_id = Column(String)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    size = Column(Float, nullable=False)
    pnl = Column(Float)
    status = Column(String, default='open')  # open, closed, failed
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_tracked_account(self, account_data):
        account = TrackedAccount(**account_data)
        self.session.merge(account)
        self.session.commit()
        return account

    def update_account_stats(self, address, stats):
        account = self.session.query(TrackedAccount).filter_by(address=address).first()
        if account:
            for key, value in stats.items():
                setattr(account, key, value)
            account.last_updated = datetime.utcnow()
            self.session.commit()

    def get_top_accounts(self, limit=10, min_win_rate=0.6, min_trades=50):
        return self.session.query(TrackedAccount).filter(
            TrackedAccount.win_rate >= min_win_rate,
            TrackedAccount.total_trades >= min_trades
        ).order_by(TrackedAccount.roi.desc()).limit(limit).all()

    def add_trade(self, trade_data):
        trade = Trade(**trade_data)
        self.session.add(trade)
        self.session.commit()
        return trade

    def add_copied_trade(self, trade_data):
        copied_trade = CopiedTrade(**trade_data)
        self.session.add(copied_trade)
        self.session.commit()
        return copied_trade

    def get_account_trades(self, address, limit=100):
        return self.session.query(Trade).filter_by(
            account_address=address
        ).order_by(Trade.opened_at.desc()).limit(limit).all()

    # =====================================================
    # COPY TRADE CONFIG METHODS
    # =====================================================

    def create_copy_trade_config(self, config_data):
        """Create a new copy trade configuration"""
        config = CopyTradeConfig(**config_data)
        self.session.add(config)
        self.session.commit()

        # Also create initial performance record
        perf = CopyTradePerformance(config_id=config.id)
        self.session.add(perf)
        self.session.commit()

        return config

    def update_copy_trade_config(self, config_id, updates):
        """Update a copy trade configuration"""
        config = self.session.query(CopyTradeConfig).filter_by(id=config_id).first()
        if config:
            for key, value in updates.items():
                setattr(config, key, value)
            self.session.commit()
        return config

    def stop_copy_trade_by_address(self, trader_address):
        """Stop all copy trades for a specific trader address"""
        configs = self.session.query(CopyTradeConfig).filter_by(
            trader_address=trader_address,
            is_active=True
        ).all()
        for config in configs:
            config.is_active = False
            config.stopped_at = datetime.utcnow()
        self.session.commit()

    def get_all_copy_trade_configs(self, active_only=False):
        """Get all copy trade configurations"""
        query = self.session.query(CopyTradeConfig)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(CopyTradeConfig.created_at.desc()).all()

    def get_copy_trade_config(self, config_id):
        """Get a specific copy trade configuration"""
        return self.session.query(CopyTradeConfig).filter_by(id=config_id).first()

    def get_copy_trade_config_by_address(self, trader_address):
        """Get active copy trade config for a trader"""
        return self.session.query(CopyTradeConfig).filter_by(
            trader_address=trader_address,
            is_active=True
        ).first()

    # =====================================================
    # COPY TRADE PERFORMANCE METHODS
    # =====================================================

    def get_copy_trade_performance(self, config_id):
        """Get performance data for a copy trade config"""
        perf = self.session.query(CopyTradePerformance).filter_by(config_id=config_id).first()
        if perf:
            return {
                'total_trades': perf.total_trades,
                'winning_trades': perf.winning_trades,
                'total_pnl': perf.total_pnl,
                'total_volume': perf.total_volume,
                'roi': perf.roi,
                'max_drawdown': perf.max_drawdown,
                'best_trade_pnl': perf.best_trade_pnl,
                'worst_trade_pnl': perf.worst_trade_pnl,
                'win_rate': (perf.winning_trades / perf.total_trades * 100) if perf.total_trades > 0 else 0,
                'last_updated': perf.last_updated.isoformat() if perf.last_updated else None
            }
        return None

    def update_copy_trade_performance(self, config_id, trade_pnl, trade_volume):
        """Update performance after a copy trade"""
        perf = self.session.query(CopyTradePerformance).filter_by(config_id=config_id).first()
        config = self.get_copy_trade_config(config_id)

        if perf and config:
            perf.total_trades += 1
            perf.total_pnl += trade_pnl
            perf.total_volume += trade_volume

            if trade_pnl > 0:
                perf.winning_trades += 1

            if trade_pnl > perf.best_trade_pnl:
                perf.best_trade_pnl = trade_pnl

            if trade_pnl < perf.worst_trade_pnl:
                perf.worst_trade_pnl = trade_pnl

            # Calculate ROI based on allocation
            if config.allocation > 0:
                perf.roi = (perf.total_pnl / config.allocation) * 100

            perf.last_updated = datetime.utcnow()
            self.session.commit()

        return perf

    def close(self):
        self.session.close()
