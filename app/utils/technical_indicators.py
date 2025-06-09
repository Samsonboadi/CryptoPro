"""
Pure Python Technical Indicators
Alternative to TA-Lib that doesn't require compilation
"""

import numpy as np
import pandas as pd
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Pure Python implementation of technical indicators"""
    
    @staticmethod
    def rsi(prices: np.array, period: int = 14) -> np.array:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Array of prices
            period: RSI period (default 14)
            
        Returns:
            Array of RSI values
        """
        try:
            if len(prices) < period + 1:
                return np.array([])
            
            # Calculate price changes
            deltas = np.diff(prices)
            
            # Separate gains and losses
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            # Calculate average gains and losses
            avg_gains = np.zeros_like(prices)
            avg_losses = np.zeros_like(prices)
            
            # Initial averages (simple average for first period)
            avg_gains[period] = np.mean(gains[:period])
            avg_losses[period] = np.mean(losses[:period])
            
            # Calculate smoothed averages for subsequent periods
            for i in range(period + 1, len(prices)):
                avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
                avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
            
            # Calculate RSI
            rsi = np.zeros_like(prices)
            rsi[:period] = np.nan
            
            for i in range(period, len(prices)):
                if avg_losses[i] == 0:
                    rsi[i] = 100
                else:
                    rs = avg_gains[i] / avg_losses[i]
                    rsi[i] = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return np.array([])
    
    @staticmethod
    def sma(prices: np.array, period: int) -> np.array:
        """
        Calculate Simple Moving Average
        
        Args:
            prices: Array of prices
            period: Moving average period
            
        Returns:
            Array of SMA values
        """
        try:
            if len(prices) < period:
                return np.array([])
            
            sma = np.zeros_like(prices)
            sma[:period-1] = np.nan
            
            for i in range(period-1, len(prices)):
                sma[i] = np.mean(prices[i-period+1:i+1])
            
            return sma
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return np.array([])
    
    @staticmethod
    def ema(prices: np.array, period: int) -> np.array:
        """
        Calculate Exponential Moving Average
        
        Args:
            prices: Array of prices
            period: EMA period
            
        Returns:
            Array of EMA values
        """
        try:
            if len(prices) < period:
                return np.array([])
            
            alpha = 2.0 / (period + 1)
            ema = np.zeros_like(prices)
            ema[:period-1] = np.nan
            
            # First EMA value is SMA
            ema[period-1] = np.mean(prices[:period])
            
            # Calculate subsequent EMA values
            for i in range(period, len(prices)):
                ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
            
            return ema
            
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return np.array([])
    
    @staticmethod
    def bollinger_bands(prices: np.array, period: int = 20, std_dev: float = 2.0) -> Tuple[np.array, np.array, np.array]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: Array of prices
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        try:
            if len(prices) < period:
                return np.array([]), np.array([]), np.array([])
            
            # Calculate middle band (SMA)
            middle_band = TechnicalIndicators.sma(prices, period)
            
            # Calculate standard deviation
            std = np.zeros_like(prices)
            std[:period-1] = np.nan
            
            for i in range(period-1, len(prices)):
                std[i] = np.std(prices[i-period+1:i+1])
            
            # Calculate upper and lower bands
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return upper_band, middle_band, lower_band
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return np.array([]), np.array([]), np.array([])
    
    @staticmethod
    def macd(prices: np.array, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.array, np.array, np.array]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Array of prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        try:
            if len(prices) < slow:
                return np.array([]), np.array([]), np.array([])
            
            # Calculate EMAs
            ema_fast = TechnicalIndicators.ema(prices, fast)
            ema_slow = TechnicalIndicators.ema(prices, slow)
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line (EMA of MACD line)
            # Remove NaN values for signal calculation
            macd_clean = macd_line[~np.isnan(macd_line)]
            if len(macd_clean) >= signal:
                signal_ema = TechnicalIndicators.ema(macd_clean, signal)
                
                # Align signal line with original array
                signal_line = np.full_like(macd_line, np.nan)
                start_idx = len(macd_line) - len(signal_ema)
                signal_line[start_idx:] = signal_ema
            else:
                signal_line = np.full_like(macd_line, np.nan)
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return np.array([]), np.array([]), np.array([])
    
    @staticmethod
    def stochastic(high: np.array, low: np.array, close: np.array, k_period: int = 14, d_period: int = 3) -> Tuple[np.array, np.array]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of close prices
            k_period: %K period
            d_period: %D period
            
        Returns:
            Tuple of (%K, %D)
        """
        try:
            if len(close) < k_period:
                return np.array([]), np.array([])
            
            k_percent = np.zeros_like(close)
            k_percent[:k_period-1] = np.nan
            
            for i in range(k_period-1, len(close)):
                highest_high = np.max(high[i-k_period+1:i+1])
                lowest_low = np.min(low[i-k_period+1:i+1])
                
                if highest_high == lowest_low:
                    k_percent[i] = 50  # Avoid division by zero
                else:
                    k_percent[i] = ((close[i] - lowest_low) / (highest_high - lowest_low)) * 100
            
            # Calculate %D (SMA of %K)
            k_clean = k_percent[~np.isnan(k_percent)]
            if len(k_clean) >= d_period:
                d_percent_clean = TechnicalIndicators.sma(k_clean, d_period)
                
                # Align %D with original array
                d_percent = np.full_like(k_percent, np.nan)
                start_idx = len(k_percent) - len(d_percent_clean)
                d_percent[start_idx:] = d_percent_clean
            else:
                d_percent = np.full_like(k_percent, np.nan)
            
            return k_percent, d_percent
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return np.array([]), np.array([])
    
    @staticmethod
    def atr(high: np.array, low: np.array, close: np.array, period: int = 14) -> np.array:
        """
        Calculate Average True Range
        
        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of close prices
            period: ATR period
            
        Returns:
            Array of ATR values
        """
        try:
            if len(close) < 2:
                return np.array([])
            
            # Calculate True Range
            tr1 = high - low
            tr2 = np.abs(high - np.roll(close, 1))
            tr3 = np.abs(low - np.roll(close, 1))
            
            # Set first values (no previous close)
            tr2[0] = high[0] - low[0]
            tr3[0] = high[0] - low[0]
            
            true_range = np.maximum(tr1, np.maximum(tr2, tr3))
            
            # Calculate ATR using SMA
            atr = TechnicalIndicators.sma(true_range, period)
            
            return atr
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return np.array([])
    
    @staticmethod
    def williams_r(high: np.array, low: np.array, close: np.array, period: int = 14) -> np.array:
        """
        Calculate Williams %R
        
        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of close prices
            period: Period for calculation
            
        Returns:
            Array of Williams %R values
        """
        try:
            if len(close) < period:
                return np.array([])
            
            williams_r = np.zeros_like(close)
            williams_r[:period-1] = np.nan
            
            for i in range(period-1, len(close)):
                highest_high = np.max(high[i-period+1:i+1])
                lowest_low = np.min(low[i-period+1:i+1])
                
                if highest_high == lowest_low:
                    williams_r[i] = -50  # Avoid division by zero
                else:
                    williams_r[i] = ((highest_high - close[i]) / (highest_high - lowest_low)) * -100
            
            return williams_r
            
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return np.array([])