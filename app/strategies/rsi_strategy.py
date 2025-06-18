"""
RSI Trading Strategy
Relative Strength Index based trading strategy with overbought/oversold signals.
Enhanced with pure Python technical analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List  # Added List import
import logging

from .base_strategy import BaseStrategy, TradingSignal, SignalType
from ..utils.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

class RSIStrategy(BaseStrategy):
    """RSI-based trading strategy using pure Python implementation"""
    
    def __init__(self, config: Dict = None):
        default_config = {
            'rsi_period': 14,
            'oversold_threshold': 30,
            'overbought_threshold': 70,
            'min_confidence': 0.6,
            'risk_percentage': 2.0,
            'stop_loss': 2.0,
            'take_profit': 6.0,
            'volume_confirmation': True,
            'trend_confirmation': True,
            'min_data_points': 50,
            'max_lookback': 200
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("RSI Strategy", default_config)
        self.indicators = TechnicalIndicators()
    
    def calculate_rsi(self, prices: np.array) -> np.array:
        """Calculate RSI indicator using pure Python implementation"""
        try:
            # Use pure Python RSI calculation
            rsi_values = self.indicators.rsi(prices, self.config['rsi_period'])
            
            # Ensure we have valid RSI values
            if len(rsi_values) == 0 or np.all(np.isnan(rsi_values)):
                logger.warning("RSI calculation returned invalid values, using fallback")
                return self._fallback_rsi(prices)
            
            return rsi_values
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return self._fallback_rsi(prices)
    
    def _fallback_rsi(self, prices: np.array) -> np.array:
        """Fallback RSI calculation if main calculation fails"""
        try:
            period = self.config['rsi_period']
            if len(prices) < period + 1:
                return np.full(len(prices), np.nan)
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gains = np.zeros(len(prices))
            avg_losses = np.zeros(len(prices))
            
            # Initial averages
            avg_gains[period] = np.mean(gains[:period])
            avg_losses[period] = np.mean(losses[:period])
            
            # Smoothed averages
            for i in range(period + 1, len(prices)):
                avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
                avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
            
            # Calculate RSI
            rsi = np.full(len(prices), np.nan)
            for i in range(period, len(prices)):
                if avg_losses[i] == 0:
                    rsi[i] = 100
                else:
                    rs = avg_gains[i] / avg_losses[i]
                    rsi[i] = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Fallback RSI calculation failed: {e}")
            return np.full(len(prices), 50.0)  # Neutral RSI
    
    def analyze(self, instrument: str) -> TradingSignal:
        """Analyze market data and generate RSI-based trading signal"""
        if not self.has_sufficient_data(instrument):
            return TradingSignal(
                signal_type=SignalType.HOLD,
                confidence=0.0,
                price=0.0,
                reason="Insufficient data for analysis"
            )
        
        df = self.get_dataframe(instrument)
        if df.empty or len(df) < self.config['min_data_points']:
            return TradingSignal(
                signal_type=SignalType.HOLD,
                confidence=0.0,
                price=0.0,
                reason="No sufficient market data available"
            )
        
        try:
            # Get price data
            prices = df['close'].values
            current_price = prices[-1]
            
            # Calculate RSI
            rsi_values = self.calculate_rsi(prices)
            
            # Get valid RSI values (remove NaN)
            valid_indices = ~np.isnan(rsi_values)
            if np.sum(valid_indices) < 2:
                return TradingSignal(
                    signal_type=SignalType.HOLD,
                    confidence=0.0,
                    price=current_price,
                    reason="Insufficient valid RSI data points"
                )
            
            # Get current and previous valid RSI values
            valid_rsi = rsi_values[valid_indices]
            if len(valid_rsi) < 2:
                return TradingSignal(
                    signal_type=SignalType.HOLD,
                    confidence=0.0,
                    price=current_price,
                    reason="Need at least 2 valid RSI values"
                )
            
            current_rsi = valid_rsi[-1]
            previous_rsi = valid_rsi[-2]
            
            # Initialize signal parameters
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No clear RSI signal"
            
            oversold = self.config['oversold_threshold']
            overbought = self.config['overbought_threshold']
            
            # Generate RSI signals
            if self._is_buy_signal(previous_rsi, current_rsi, oversold):
                signal_type = SignalType.BUY
                confidence = self._calculate_buy_confidence(current_rsi, previous_rsi, oversold)
                reason = f"RSI buy signal: {current_rsi:.1f} (crossed above {oversold})"
                
            elif self._is_sell_signal(previous_rsi, current_rsi, overbought):
                signal_type = SignalType.SELL
                confidence = self._calculate_sell_confidence(current_rsi, previous_rsi, overbought)
                reason = f"RSI sell signal: {current_rsi:.1f} (crossed below {overbought})"
            
            # Apply confirmation filters
            if signal_type != SignalType.HOLD:
                confidence = self._apply_confirmations(df, signal_type, confidence, reason)
                
                # Check minimum confidence threshold
                if confidence < self.config['min_confidence']:
                    signal_type = SignalType.HOLD
                    reason = f"Signal confidence {confidence:.2f} below threshold {self.config['min_confidence']}"
            
            return TradingSignal(
                signal_type=signal_type,
                confidence=min(1.0, confidence),  # Cap at 1.0
                price=current_price,
                reason=reason,
                metadata={
                    'rsi_current': current_rsi,
                    'rsi_previous': previous_rsi,
                    'oversold_threshold': oversold,
                    'overbought_threshold': overbought,
                    'rsi_period': self.config['rsi_period'],
                    'data_points': len(df)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in RSI analysis for {instrument}: {e}")
            return TradingSignal(
                signal_type=SignalType.HOLD,
                confidence=0.0,
                price=df['close'].iloc[-1] if not df.empty else 0.0,
                reason=f"Analysis error: {str(e)}"
            )
    
    def _is_buy_signal(self, previous_rsi: float, current_rsi: float, oversold: float) -> bool:
        """Check if current conditions indicate a buy signal"""
        return previous_rsi <= oversold and current_rsi > oversold
    
    def _is_sell_signal(self, previous_rsi: float, current_rsi: float, overbought: float) -> bool:
        """Check if current conditions indicate a sell signal"""
        return previous_rsi >= overbought and current_rsi < overbought
    
    def _calculate_buy_confidence(self, current_rsi: float, previous_rsi: float, oversold: float) -> float:
        """Calculate confidence for buy signals"""
        # Base confidence on how oversold the asset was
        oversold_strength = max(0, (oversold - min(previous_rsi, 20)) / 20)
        
        # Additional confidence for strong reversal
        reversal_strength = min(1.0, (current_rsi - previous_rsi) / 10)
        
        # Combine factors
        confidence = (oversold_strength * 0.7) + (reversal_strength * 0.3)
        
        return max(0.1, min(0.9, confidence))  # Keep between 0.1 and 0.9
    
    def _calculate_sell_confidence(self, current_rsi: float, previous_rsi: float, overbought: float) -> float:
        """Calculate confidence for sell signals"""
        # Base confidence on how overbought the asset was
        overbought_strength = max(0, (max(previous_rsi, 80) - overbought) / 20)
        
        # Additional confidence for strong reversal
        reversal_strength = min(1.0, (previous_rsi - current_rsi) / 10)
        
        # Combine factors
        confidence = (overbought_strength * 0.7) + (reversal_strength * 0.3)
        
        return max(0.1, min(0.9, confidence))  # Keep between 0.1 and 0.9
    
    def _apply_confirmations(self, df: pd.DataFrame, signal_type: SignalType, 
                           base_confidence: float, reason: str) -> float:
        """Apply additional confirmation filters to improve signal quality"""
        confidence = base_confidence
        confirmations = []
        
        try:
            # Volume confirmation
            if self.config.get('volume_confirmation', True) and len(df) >= 2:
                recent_volume = df['volume'].iloc[-1]
                avg_volume = df['volume'].iloc[-5:].mean()  # 5-period average
                
                if recent_volume > avg_volume * 1.2:  # 20% above average
                    confidence *= 1.1
                    confirmations.append("high volume")
                elif recent_volume < avg_volume * 0.8:  # 20% below average
                    confidence *= 0.9
                    confirmations.append("low volume")
            
            # Trend confirmation using moving averages
            if self.config.get('trend_confirmation', True) and len(df) >= 20:
                prices = df['close'].values
                sma_short = self.indicators.sma(prices, 10)
                sma_long = self.indicators.sma(prices, 20)
                
                if len(sma_short) > 0 and len(sma_long) > 0:
                    current_short = sma_short[-1]
                    current_long = sma_long[-1]
                    
                    # For buy signals, prefer uptrend
                    if signal_type == SignalType.BUY and current_short > current_long:
                        confidence *= 1.05
                        confirmations.append("uptrend")
                    # For sell signals, prefer downtrend
                    elif signal_type == SignalType.SELL and current_short < current_long:
                        confidence *= 1.05
                        confirmations.append("downtrend")
            
            # Price momentum confirmation
            if len(df) >= 5:
                recent_prices = df['close'].iloc[-5:].values
                momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
                
                # Positive momentum for buy signals
                if signal_type == SignalType.BUY and momentum > 0:
                    confidence *= 1.03
                    confirmations.append("positive momentum")
                # Negative momentum for sell signals
                elif signal_type == SignalType.SELL and momentum < 0:
                    confidence *= 1.03
                    confirmations.append("negative momentum")
            
            # Add confirmations to reason if any were found
            if confirmations:
                reason += f" with {', '.join(confirmations)}"
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error applying confirmations: {e}")
            return base_confidence
    
    def get_support_resistance_levels(self, instrument: str) -> Dict:
        """Calculate support and resistance levels based on RSI extremes"""
        if not self.has_sufficient_data(instrument):
            return {}
        
        df = self.get_dataframe(instrument)
        if df.empty or len(df) < 20:
            return {}
        
        try:
            prices = df['close'].values
            rsi_values = self.calculate_rsi(prices)
            
            # Find prices where RSI was at extremes
            oversold_prices = []
            overbought_prices = []
            
            valid_indices = ~np.isnan(rsi_values)
            valid_rsi = rsi_values[valid_indices]
            valid_prices = prices[valid_indices]
            
            oversold_threshold = self.config['oversold_threshold']
            overbought_threshold = self.config['overbought_threshold']
            
            for i, rsi_val in enumerate(valid_rsi):
                if rsi_val <= oversold_threshold:
                    oversold_prices.append(valid_prices[i])
                elif rsi_val >= overbought_threshold:
                    overbought_prices.append(valid_prices[i])
            
            # Calculate levels
            support_level = np.mean(oversold_prices) if oversold_prices else None
            resistance_level = np.mean(overbought_prices) if overbought_prices else None
            
            return {
                'support': support_level,
                'resistance': resistance_level,
                'oversold_touches': len(oversold_prices),
                'overbought_touches': len(overbought_prices),
                'oversold_threshold': oversold_threshold,
                'overbought_threshold': overbought_threshold
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance levels: {e}")
            return {}
    
    def get_risk_metrics(self, instrument: str) -> Dict:
        """Calculate risk metrics for the strategy"""
        try:
            df = self.get_dataframe(instrument)
            if df.empty:
                return {}
            
            prices = df['close'].values
            returns = np.diff(prices) / prices[:-1]
            
            # Calculate volatility
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            
            # Calculate maximum drawdown
            cumulative = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = np.min(drawdown) * 100
            
            # Calculate current RSI level for risk assessment
            rsi_values = self.calculate_rsi(prices)
            current_rsi = rsi_values[-1] if len(rsi_values) > 0 and not np.isnan(rsi_values[-1]) else 50
            
            # Risk level based on RSI
            if current_rsi < 30 or current_rsi > 70:
                risk_level = "High"
            elif current_rsi < 40 or current_rsi > 60:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            return {
                'volatility': volatility,
                'max_drawdown': max_drawdown,
                'current_rsi': current_rsi,
                'risk_level': risk_level,
                'stop_loss_pct': self.config.get('stop_loss', 2.0),
                'take_profit_pct': self.config.get('take_profit', 6.0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def optimize_parameters(self, instrument: str, lookback_days: int = 30) -> Dict:
        """Suggest optimized parameters based on recent market behavior"""
        try:
            df = self.get_dataframe(instrument)
            if df.empty or len(df) < lookback_days:
                return self.config
            
            # Use recent data for optimization
            recent_df = df.tail(lookback_days)
            prices = recent_df['close'].values
            
            # Test different RSI periods
            best_period = self.config['rsi_period']
            best_score = 0
            
            for period in [10, 12, 14, 16, 18, 20]:
                try:
                    rsi_test = self.indicators.rsi(prices, period)
                    if len(rsi_test) > 0:
                        # Score based on signal quality (how often RSI reaches extremes)
                        extreme_signals = np.sum((rsi_test < 30) | (rsi_test > 70))
                        score = extreme_signals / len(rsi_test)
                        
                        if score > best_score:
                            best_score = score
                            best_period = period
                except:
                    continue
            
            # Optimize thresholds based on volatility
            volatility = np.std(np.diff(prices) / prices[:-1])
            
            if volatility > 0.03:  # High volatility
                suggested_oversold = 25
                suggested_overbought = 75
            elif volatility < 0.01:  # Low volatility
                suggested_oversold = 35
                suggested_overbought = 65
            else:  # Medium volatility
                suggested_oversold = 30
                suggested_overbought = 70
            
            optimized_config = self.config.copy()
            optimized_config.update({
                'rsi_period': best_period,
                'oversold_threshold': suggested_oversold,
                'overbought_threshold': suggested_overbought
            })
            
            return optimized_config
            
        except Exception as e:
            logger.error(f"Error optimizing parameters: {e}")
            return self.config
    
    def get_signal_history(self, instrument: str, days: int = 7) -> list[Dict]:
        """Get recent signal history for analysis"""
        try:
            df = self.get_dataframe(instrument)
            if df.empty:
                return []
            
            # Take recent data
            recent_df = df.tail(days * 24)  # Assuming hourly data
            signals = []
            
            for i in range(len(recent_df) - 1):
                # Analyze each point
                temp_df = recent_df.iloc[:i+2]
                if len(temp_df) < self.config['min_data_points']:
                    continue
                
                signal = self.analyze(instrument)
                if signal.signal_type != SignalType.HOLD:
                    signals.append({
                        'timestamp': recent_df.index[i],
                        'signal_type': signal.signal_type.value,
                        'confidence': signal.confidence,
                        'price': signal.price,
                        'reason': signal.reason,
                        'rsi': signal.metadata.get('rsi_current', 0)
                    })
            
            return signals[-10:]  # Return last 10 signals
            
        except Exception as e:
            logger.error(f"Error getting signal history: {e}")
            return []