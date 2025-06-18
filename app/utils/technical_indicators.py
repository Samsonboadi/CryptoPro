"""
Technical Indicators using pandas_ta - Fixed Version
All deprecated fillna methods replaced with modern equivalents
"""

import numpy as np
import pandas as pd
import pandas_ta as ta
from typing import Tuple, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Technical indicators using pandas_ta library - fixed version"""
    
    @staticmethod
    def rsi(prices: Union[np.array, pd.Series], period: int = 14) -> np.array:
        """
        Calculate Relative Strength Index (RSI) using pandas_ta
        
        Args:
            prices: Array or Series of prices
            period: RSI period (default 14)
            
        Returns:
            Array of RSI values
        """
        try:
            # Convert to pandas Series if numpy array
            if isinstance(prices, np.ndarray):
                prices = pd.Series(prices)
            
            # Calculate RSI using pandas_ta
            rsi_values = ta.rsi(prices, length=period)
            
            # Return as numpy array, handling NaN values
            return rsi_values.bfill().fillna(50).values
            
        except Exception as e:
            logger.error(f"Error calculating RSI with pandas_ta: {e}")
            # Fallback to simple RSI calculation
            return TechnicalIndicators._simple_rsi(prices.values if hasattr(prices, 'values') else prices, period)
    
    @staticmethod
    def _simple_rsi(prices: np.array, period: int = 14) -> np.array:
        """
        Fallback simple RSI calculation
        """
        try:
            if len(prices) < period + 1:
                return np.full(len(prices), 50.0)
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            # Calculate initial averages
            avg_gains = np.zeros(len(prices))
            avg_losses = np.zeros(len(prices))
            
            avg_gains[period] = np.mean(gains[:period])
            avg_losses[period] = np.mean(losses[:period])
            
            # Calculate smoothed averages
            for i in range(period + 1, len(prices)):
                avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
                avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
            
            # Calculate RSI
            rsi = np.full(len(prices), 50.0)
            for i in range(period, len(prices)):
                if avg_losses[i] == 0:
                    rsi[i] = 100
                else:
                    rs = avg_gains[i] / avg_losses[i]
                    rsi[i] = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error in simple RSI calculation: {e}")
            return np.full(len(prices), 50.0)
    
    @staticmethod
    def sma(prices: Union[np.array, pd.Series], period: int) -> np.array:
        """
        Calculate Simple Moving Average using pandas_ta
        """
        try:
            if isinstance(prices, np.ndarray):
                prices = pd.Series(prices)
            
            sma_values = ta.sma(prices, length=period)
            return sma_values.bfill().fillna(prices.iloc[0]).values
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            # Fallback calculation
            if isinstance(prices, pd.Series):
                return prices.rolling(window=period, min_periods=1).mean().values
            else:
                return pd.Series(prices).rolling(window=period, min_periods=1).mean().values
    
    @staticmethod
    def ema(prices: Union[np.array, pd.Series], period: int) -> np.array:
        """
        Calculate Exponential Moving Average using pandas_ta
        """
        try:
            if isinstance(prices, np.ndarray):
                prices = pd.Series(prices)
            
            ema_values = ta.ema(prices, length=period)
            return ema_values.bfill().fillna(prices.iloc[0]).values
            
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            # Fallback calculation
            if isinstance(prices, pd.Series):
                return prices.ewm(span=period, adjust=False).mean().values
            else:
                return pd.Series(prices).ewm(span=period, adjust=False).mean().values
    
    @staticmethod
    def bollinger_bands(prices: Union[np.array, pd.Series], period: int = 20, std_dev: float = 2.0) -> Tuple[np.array, np.array, np.array]:
        """
        Calculate Bollinger Bands using pandas_ta
        """
        try:
            if isinstance(prices, np.ndarray):
                prices = pd.Series(prices)
            
            # Calculate Bollinger Bands
            bb_result = ta.bbands(prices, length=period, std=std_dev)
            
            if bb_result is not None and len(bb_result.columns) >= 3:
                # Extract bands (lower, middle, upper)
                lower_band = bb_result.iloc[:, 0].bfill().fillna(prices.iloc[0]).values
                middle_band = bb_result.iloc[:, 1].bfill().fillna(prices.iloc[0]).values  
                upper_band = bb_result.iloc[:, 2].bfill().fillna(prices.iloc[0]).values
                
                return upper_band, middle_band, lower_band
            else:
                raise ValueError("Bollinger Bands calculation failed")
                
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            # Fallback calculation
            sma_values = TechnicalIndicators.sma(prices, period)
            std_values = pd.Series(prices).rolling(window=period).std().bfill().fillna(0).values
            
            upper_band = sma_values + (std_values * std_dev)
            lower_band = sma_values - (std_values * std_dev)
            
            return upper_band, sma_values, lower_band
    
    @staticmethod
    def macd(prices: Union[np.array, pd.Series], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.array, np.array, np.array]:
        """
        Calculate MACD using pandas_ta
        """
        try:
            if isinstance(prices, np.ndarray):
                prices = pd.Series(prices)
            
            # Calculate MACD
            macd_result = ta.macd(prices, fast=fast, slow=slow, signal=signal)
            
            if macd_result is not None and len(macd_result.columns) >= 3:
                macd_line = macd_result.iloc[:, 0].fillna(0).values
                macd_histogram = macd_result.iloc[:, 1].fillna(0).values
                macd_signal = macd_result.iloc[:, 2].fillna(0).values
                
                return macd_line, macd_signal, macd_histogram
            else:
                raise ValueError("MACD calculation failed")
                
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            # Fallback calculation
            ema_fast = TechnicalIndicators.ema(prices, fast)
            ema_slow = TechnicalIndicators.ema(prices, slow)
            macd_line = ema_fast - ema_slow
            
            # Signal line
            macd_series = pd.Series(macd_line)
            signal_line = macd_series.ewm(span=signal, adjust=False).mean().fillna(0).values
            
            # Histogram
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
    
    @staticmethod
    def stochastic(high: Union[np.array, pd.Series], low: Union[np.array, pd.Series], 
                  close: Union[np.array, pd.Series], k_period: int = 14, d_period: int = 3) -> Tuple[np.array, np.array]:
        """
        Calculate Stochastic Oscillator using pandas_ta
        """
        try:
            # Convert to pandas Series if needed
            if isinstance(high, np.ndarray):
                high = pd.Series(high)
            if isinstance(low, np.ndarray):
                low = pd.Series(low)
            if isinstance(close, np.ndarray):
                close = pd.Series(close)
            
            # Calculate Stochastic
            stoch_result = ta.stoch(high=high, low=low, close=close, k=k_period, d=d_period)
            
            if stoch_result is not None and len(stoch_result.columns) >= 2:
                k_percent = stoch_result.iloc[:, 0].fillna(50).values  # %K
                d_percent = stoch_result.iloc[:, 1].fillna(50).values  # %D
                
                return k_percent, d_percent
            else:
                raise ValueError("Stochastic calculation failed")
                
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            # Fallback calculation
            k_percent = np.full(len(close), 50.0)
            d_percent = np.full(len(close), 50.0)
            
            for i in range(k_period-1, len(close)):
                highest_high = np.max(high[i-k_period+1:i+1])
                lowest_low = np.min(low[i-k_period+1:i+1])
                
                if highest_high != lowest_low:
                    k_percent[i] = ((close[i] - lowest_low) / (highest_high - lowest_low)) * 100
            
            # Calculate %D as SMA of %K
            k_series = pd.Series(k_percent)
            d_percent = k_series.rolling(window=d_period, min_periods=1).mean().values
            
            return k_percent, d_percent
    
    @staticmethod
    def atr(high: Union[np.array, pd.Series], low: Union[np.array, pd.Series], 
           close: Union[np.array, pd.Series], period: int = 14) -> np.array:
        """
        Calculate Average True Range using pandas_ta
        """
        try:
            # Convert to pandas Series if needed
            if isinstance(high, np.ndarray):
                high = pd.Series(high)
            if isinstance(low, np.ndarray):
                low = pd.Series(low)
            if isinstance(close, np.ndarray):
                close = pd.Series(close)
            
            # Calculate ATR
            atr_values = ta.atr(high=high, low=low, close=close, length=period)
            
            if atr_values is not None:
                return atr_values.bfill().fillna(1.0).values
            else:
                raise ValueError("ATR calculation failed")
                
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            # Fallback calculation
            tr1 = high - low
            tr2 = np.abs(high - close.shift(1))
            tr3 = np.abs(low - close.shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period, min_periods=1).mean()
            
            return atr.bfill().fillna(1.0).values
    
    @staticmethod
    def williams_r(high: Union[np.array, pd.Series], low: Union[np.array, pd.Series], 
                  close: Union[np.array, pd.Series], period: int = 14) -> np.array:
        """
        Calculate Williams %R using pandas_ta
        """
        try:
            # Convert to pandas Series if needed
            if isinstance(high, np.ndarray):
                high = pd.Series(high)
            if isinstance(low, np.ndarray):
                low = pd.Series(low)
            if isinstance(close, np.ndarray):
                close = pd.Series(close)
            
            # Calculate Williams %R
            willr_values = ta.willr(high=high, low=low, close=close, length=period)
            
            if willr_values is not None:
                return willr_values.fillna(-50).values
            else:
                raise ValueError("Williams %R calculation failed")
                
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            # Fallback calculation
            williams_r = np.full(len(close), -50.0)
            
            for i in range(period-1, len(close)):
                highest_high = np.max(high[i-period+1:i+1])
                lowest_low = np.min(low[i-period+1:i+1])
                
                if highest_high != lowest_low:
                    williams_r[i] = ((highest_high - close[i]) / (highest_high - lowest_low)) * -100
            
            return williams_r
    
    @staticmethod
    def adx(high: Union[np.array, pd.Series], low: Union[np.array, pd.Series], 
           close: Union[np.array, pd.Series], period: int = 14) -> np.array:
        """
        Calculate Average Directional Index (ADX) using pandas_ta
        """
        try:
            # Convert to pandas Series if needed
            if isinstance(high, np.ndarray):
                high = pd.Series(high)
            if isinstance(low, np.ndarray):
                low = pd.Series(low)
            if isinstance(close, np.ndarray):
                close = pd.Series(close)
            
            # Calculate ADX
            adx_result = ta.adx(high=high, low=low, close=close, length=period)
            
            if adx_result is not None and f'ADX_{period}' in adx_result.columns:
                return adx_result[f'ADX_{period}'].fillna(25).values
            else:
                raise ValueError("ADX calculation failed")
                
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return np.full(len(close), 25.0)  # Neutral ADX value
    
    @staticmethod
    def obv(close: Union[np.array, pd.Series], volume: Union[np.array, pd.Series]) -> np.array:
        """
        Calculate On-Balance Volume (OBV) using pandas_ta
        """
        try:
            # Convert to pandas Series if needed
            if isinstance(close, np.ndarray):
                close = pd.Series(close)
            if isinstance(volume, np.ndarray):
                volume = pd.Series(volume)
            
            # Calculate OBV
            obv_values = ta.obv(close=close, volume=volume)
            
            if obv_values is not None:
                return obv_values.fillna(0).values
            else:
                raise ValueError("OBV calculation failed")
                
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            # Simple fallback
            direction = np.where(close.diff() > 0, 1, np.where(close.diff() < 0, -1, 0))
            return np.cumsum(direction * volume).fillna(0)

# Convenience function for DataFrame operations
def add_all_indicators(df: pd.DataFrame, 
                      high_col: str = 'high',
                      low_col: str = 'low', 
                      close_col: str = 'close',
                      volume_col: str = 'volume') -> pd.DataFrame:
    """
    Add all common technical indicators to a DataFrame
    
    Args:
        df: DataFrame with OHLCV data
        high_col: Name of high price column
        low_col: Name of low price column  
        close_col: Name of close price column
        volume_col: Name of volume column
        
    Returns:
        DataFrame with added indicator columns
    """
    try:
        indicators = TechnicalIndicators()
        
        # Basic indicators
        df['sma_20'] = indicators.sma(df[close_col], 20)
        df['ema_20'] = indicators.ema(df[close_col], 20)
        df['rsi'] = indicators.rsi(df[close_col], 14)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = indicators.bollinger_bands(df[close_col], 20, 2.0)
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower
        
        # MACD
        macd_line, macd_signal, macd_histogram = indicators.macd(df[close_col])
        df['macd'] = macd_line
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = macd_histogram
        
        # Stochastic
        stoch_k, stoch_d = indicators.stochastic(df[high_col], df[low_col], df[close_col])
        df['stoch_k'] = stoch_k
        df['stoch_d'] = stoch_d
        
        # ATR
        df['atr'] = indicators.atr(df[high_col], df[low_col], df[close_col])
        
        # Williams %R
        df['williams_r'] = indicators.williams_r(df[high_col], df[low_col], df[close_col])
        
        # ADX
        df['adx'] = indicators.adx(df[high_col], df[low_col], df[close_col])
        
        # OBV
        if volume_col in df.columns:
            df['obv'] = indicators.obv(df[close_col], df[volume_col])
        
        logger.info("Successfully added all technical indicators to DataFrame")
        return df
        
    except Exception as e:
        logger.error(f"Error adding indicators to DataFrame: {e}")
        return df