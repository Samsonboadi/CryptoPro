"""
RSI Trading Strategy
Relative Strength Index based trading strategy with overbought/oversold signals.
"""

import numpy as np
from typing import Dict
import logging

from .base_strategy import BaseStrategy, TradingSignal, SignalType
from ..utils.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

class RSIStrategy(BaseStrategy):
    """RSI-based trading strategy"""
    
    def __init__(self, config: Dict = None):
        default_config = {
            'rsi_period': 14,
            'oversold_threshold': 30,
            'overbought_threshold': 70,
            'min_confidence': 0.6,
            'risk_percentage': 2.0,
            'stop_loss': 2.0,
            'take_profit': 6.0
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("RSI Strategy", default_config)
        self.indicators = TechnicalIndicators()
    
    def calculate_rsi(self, prices: np.array) -> np.array:
        """Calculate RSI indicator using pure Python implementation"""
        try:
            return self.indicators.rsi(prices, self.config['rsi_period'])
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return np.array([])
    
    def analyze(self, instrument: str) -> TradingSignal:
        """Analyze market data and generate RSI-based trading signal"""
        if not self.has_sufficient_data(instrument):
            return TradingSignal(
                signal_type=SignalType.HOLD,
                confidence=0.0,
                price=0.0,
                reason="Insufficient data"
            )
        
        df = self.get_dataframe(instrument)
        if df.empty:
            return TradingSignal(
                signal_type=SignalType.HOLD,
                confidence=0.0,
                price=0.0,
                reason="No data available"
            )
        
        prices = df['close'].values
        current_price = prices[-1]
        
        # Calculate RSI
        rsi_values = self.calculate_rsi(prices)
        
        if len(rsi_values) < 2:
            return TradingSignal(
                signal_type=SignalType.HOLD,
                confidence=0.0,
                price=current_price,
                reason="Insufficient RSI data"
            )
        
        # Get current and previous RSI (skip NaN values)
        valid_rsi = rsi_values[~np.isnan(rsi_values)]
        if len(valid_rsi) < 2:
            return TradingSignal(
                signal_type=SignalType.HOLD,
                confidence=0.0,
                price=current_price,
                reason="Insufficient valid RSI data"
            )
        
        current_rsi = valid_rsi[-1]
        previous_rsi = valid_rsi[-2]
        
        # Generate signals
        signal_type = SignalType.HOLD
        confidence = 0.0
        reason = "No clear signal"
        
        oversold = self.config['oversold_threshold']
        overbought = self.config['overbought_threshold']
        
        # Buy signal: RSI crosses above oversold level
        if previous_rsi <= oversold and current_rsi > oversold:
            signal_type = SignalType.BUY
            # Confidence based on how oversold it was
            confidence = min(1.0, (oversold - min(previous_rsi, 20)) / 20)
            reason = f"RSI crossed above oversold level ({current_rsi:.1f})"
            
        # Sell signal: RSI crosses below overbought level
        elif previous_rsi >= overbought and current_rsi < overbought:
            signal_type = SignalType.SELL
            # Confidence based on how overbought it was
            confidence = min(1.0, (max(previous_rsi, 80) - overbought) / 20)
            reason = f"RSI crossed below overbought level ({current_rsi:.1f})"
        
        # Additional confirmation signals
        if signal_type != SignalType.HOLD:
            # Volume confirmation
            if len(df) >= 2:
                volume_ratio = df['volume'].iloc[-1] / df['volume'].iloc[-2]
                if volume_ratio > 1.2:  # 20% higher volume
                    confidence *= 1.1
                    reason += " with volume confirmation"
            
            # Trend confirmation
            if len(prices) >= 5:
                recent_trend = np.mean(prices[-5:]) - np.mean(prices[-10:-5])
                if signal_type == SignalType.BUY and recent_trend > 0:
                    confidence *= 1.05
                elif signal_type == SignalType.SELL and recent_trend < 0:
                    confidence *= 1.05
        
        # Cap confidence at 1.0
        confidence = min(1.0, confidence)
        
        # Only return signal if confidence meets minimum threshold
        if confidence < self.config['min_confidence']:
            signal_type = SignalType.HOLD
            reason = f"Low confidence signal ({confidence:.2f})"
        
        return TradingSignal(
            signal_type=signal_type,
            confidence=confidence,
            price=current_price,
            reason=reason,
            metadata={
                'rsi': current_rsi,
                'previous_rsi': previous_rsi,
                'oversold_threshold': oversold,
                'overbought_threshold': overbought
            }
        )
    
    def get_support_resistance_levels(self, instrument: str) -> Dict:
        """Calculate support and resistance levels based on RSI"""
        if not self.has_sufficient_data(instrument):
            return {}
        
        df = self.get_dataframe(instrument)
        if df.empty:
            return {}
        
        prices = df['close'].values
        rsi_values = self.calculate_rsi(prices)
        
        if len(rsi_values) < 20:
            return {}
        
        # Find levels where RSI was oversold/overbought
        oversold_prices = []
        overbought_prices = []
        
        valid_indices = ~np.isnan(rsi_values)
        valid_rsi = rsi_values[valid_indices]
        valid_prices = prices[valid_indices]
        
        for i in range(len(valid_rsi)):
            if valid_rsi[i] <= self.config['oversold_threshold']:
                oversold_prices.append(valid_prices[i])
            elif valid_rsi[i] >= self.config['overbought_threshold']:
                overbought_prices.append(valid_prices[i])
        
        support_level = np.mean(oversold_prices) if oversold_prices else None
        resistance_level = np.mean(overbought_prices) if overbought_prices else None
        
        return {
            'support': support_level,
            'resistance': resistance_level,
            'oversold_touches': len(oversold_prices),
            'overbought_touches': len(overbought_prices)
        }