"""
Base Strategy Class
Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class MarketData:
    instrument_name: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None

@dataclass
class TradingSignal:
    signal_type: SignalType
    confidence: float  # 0.0 to 1.0
    price: float
    quantity: Optional[float] = None
    reason: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass
class StrategyPerformance:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
        self.market_data = {}  # instrument_name -> List[MarketData]
        self.positions = {}    # instrument_name -> position_info
        self.performance = StrategyPerformance()
        self.enabled = True
        
        # Strategy parameters
        self.max_lookback = self.config.get('max_lookback', 200)
        self.min_data_points = self.config.get('min_data_points', 50)
        
    def update_market_data(self, data: MarketData):
        """Update market data for the strategy"""
        if not self.enabled:
            return
            
        instrument = data.instrument_name
        
        if instrument not in self.market_data:
            self.market_data[instrument] = []
        
        self.market_data[instrument].append(data)
        
        # Keep only max_lookback data points to manage memory
        if len(self.market_data[instrument]) > self.max_lookback:
            self.market_data[instrument] = self.market_data[instrument][-self.max_lookback:]
    
    def get_dataframe(self, instrument: str, periods: int = None) -> pd.DataFrame:
        """Convert market data to pandas DataFrame"""
        if instrument not in self.market_data:
            return pd.DataFrame()
        
        data_list = self.market_data[instrument]
        
        if periods:
            data_list = data_list[-periods:]
        
        if len(data_list) < self.min_data_points:
            return pd.DataFrame()
        
        df = pd.DataFrame([{
            'timestamp': d.timestamp,
            'open': d.open,
            'high': d.high,
            'low': d.low,
            'close': d.close,
            'volume': d.volume
        } for d in data_list])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def get_latest_price(self, instrument: str) -> Optional[float]:
        """Get the latest price for an instrument"""
        if instrument not in self.market_data or not self.market_data[instrument]:
            return None
        return self.market_data[instrument][-1].close
    
    def has_sufficient_data(self, instrument: str) -> bool:
        """Check if we have sufficient data for analysis"""
        return (instrument in self.market_data and 
                len(self.market_data[instrument]) >= self.min_data_points)
    
    @abstractmethod
    def analyze(self, instrument: str) -> TradingSignal:
        """
        Analyze market data and generate trading signal
        
        Args:
            instrument: Trading instrument (e.g., 'BTCUSD-PERP')
            
        Returns:
            TradingSignal with recommendation
        """
        pass
    
    def should_buy(self, instrument: str) -> bool:
        """Check if strategy recommends buying"""
        if not self.enabled or not self.has_sufficient_data(instrument):
            return False
        
        signal = self.analyze(instrument)
        return signal.signal_type == SignalType.BUY and signal.confidence > 0.5
    
    def should_sell(self, instrument: str) -> bool:
        """Check if strategy recommends selling"""
        if not self.enabled or not self.has_sufficient_data(instrument):
            return False
        
        signal = self.analyze(instrument)
        return signal.signal_type == SignalType.SELL and signal.confidence > 0.5
    
    def calculate_position_size(self, instrument: str, account_balance: float) -> float:
        """
        Calculate position size based on risk management
        
        Args:
            instrument: Trading instrument
            account_balance: Available account balance
            
        Returns:
            Position size in base currency
        """
        risk_percentage = self.config.get('risk_percentage', 1.0) / 100
        max_position_size = self.config.get('max_position_size', 10.0) / 100
        
        risk_amount = account_balance * risk_percentage
        max_amount = account_balance * max_position_size
        
        current_price = self.get_latest_price(instrument)
        if not current_price:
            return 0.0
        
        # Calculate position size based on risk
        stop_loss_pct = self.config.get('stop_loss', 2.0) / 100
        position_size = risk_amount / (current_price * stop_loss_pct)
        
        # Ensure position doesn't exceed maximum
        max_position_size_units = max_amount / current_price
        position_size = min(position_size, max_position_size_units)
        
        return max(0.0, position_size)
    
    def update_performance(self, trade_pnl: float, is_winning_trade: bool):
        """Update strategy performance metrics"""
        self.performance.total_trades += 1
        self.performance.total_pnl += trade_pnl
        
        if is_winning_trade:
            self.performance.winning_trades += 1
            if self.performance.winning_trades > 0:
                self.performance.avg_win = (
                    (self.performance.avg_win * (self.performance.winning_trades - 1) + trade_pnl) /
                    self.performance.winning_trades
                )
        else:
            self.performance.losing_trades += 1
            if self.performance.losing_trades > 0:
                self.performance.avg_loss = (
                    (self.performance.avg_loss * (self.performance.losing_trades - 1) + abs(trade_pnl)) /
                    self.performance.losing_trades
                )
        
        # Update win rate
        if self.performance.total_trades > 0:
            self.performance.win_rate = self.performance.winning_trades / self.performance.total_trades
    
    def get_strategy_info(self) -> Dict:
        """Get strategy information and performance"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'config': self.config,
            'performance': {
                'total_trades': self.performance.total_trades,
                'winning_trades': self.performance.winning_trades,
                'losing_trades': self.performance.losing_trades,
                'total_pnl': self.performance.total_pnl,
                'win_rate': self.performance.win_rate * 100,
                'avg_win': self.performance.avg_win,
                'avg_loss': self.performance.avg_loss,
                'max_drawdown': self.performance.max_drawdown,
                'sharpe_ratio': self.performance.sharpe_ratio
            }
        }
    
    def enable(self):
        """Enable the strategy"""
        self.enabled = True
        logger.info(f"Strategy {self.name} enabled")
    
    def disable(self):
        """Disable the strategy"""
        self.enabled = False
        logger.info(f"Strategy {self.name} disabled")
    
    def update_config(self, new_config: Dict):
        """Update strategy configuration"""
        self.config.update(new_config)
        logger.info(f"Strategy {self.name} configuration updated: {new_config}")
    
    def reset_performance(self):
        """Reset performance metrics"""
        self.performance = StrategyPerformance()
        logger.info(f"Strategy {self.name} performance metrics reset")