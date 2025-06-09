"""
Main Trading Bot Orchestrator
Coordinates all trading activities, strategies, and risk management.
"""

import time
import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from ..api.crypto_com_api import CryptoComAPI, OrderRequest, OrderSide, OrderType
from ..strategies.base_strategy import BaseStrategy, MarketData, SignalType
from ..strategies.rsi_strategy import RSIStrategy
from ..utils.config import Config
from ..utils.logger import TradingLogger

logger = logging.getLogger(__name__)

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.running = False
        self.api = None
        self.strategies = {}
        self.active_strategies = []
        self.positions = {}
        self.market_data = {}
        
        # Threading
        self.trading_thread = None
        self.market_data_thread = None
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        
        # Logging
        self.trade_logger = TradingLogger("TradingBot")
        
        # Initialize components
        self._initialize_api()
        self._initialize_strategies()
    
    def _initialize_api(self):
        """Initialize the API client"""
        try:
            self.api = CryptoComAPI(
                api_key=self.config.api.api_key,
                secret_key=self.config.api.secret_key,
                sandbox=self.config.api.sandbox
            )
            logger.info("API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API client: {e}")
            raise
    
    def _initialize_strategies(self):
        """Initialize trading strategies"""
        try:
            # Load strategy configurations
            rsi_config = self.config.get_strategy_config("RSI Strategy")
            
            # Initialize strategies
            self.strategies = {
                "RSI Strategy": RSIStrategy(rsi_config)
            }
            
            # Set active strategies based on config
            enabled_strategies = self.config.trading.enabled_strategies or ["RSI Strategy"]
            self.active_strategies = [
                self.strategies[name] for name in enabled_strategies 
                if name in self.strategies
            ]
            
            logger.info(f"Initialized {len(self.strategies)} strategies, {len(self.active_strategies)} active")
            
        except Exception as e:
            logger.error(f"Failed to initialize strategies: {e}")
            raise
    
    def start(self):
        """Start the trading bot"""
        if self.running:
            logger.warning("Bot is already running")
            return
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration")
        
        self.running = True
        logger.info("Starting CryptoBot Pro...")
        
        # Start market data feed
        self.market_data_thread = threading.Thread(target=self._market_data_loop, daemon=True)
        self.market_data_thread.start()
        
        # Start trading loop
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        
        logger.info("CryptoBot Pro started successfully")
    
    def stop(self):
        """Stop the trading bot"""
        if not self.running:
            logger.warning("Bot is not running")
            return
        
        logger.info("Stopping CryptoBot Pro...")
        self.running = False
        
        # Wait for threads to finish
        if self.trading_thread and self.trading_thread.is_alive():
            self.trading_thread.join(timeout=5)
        
        if self.market_data_thread and self.market_data_thread.is_alive():
            self.market_data_thread.join(timeout=5)
        
        # Close API connections
        if self.api:
            self.api.close()
        
        logger.info("CryptoBot Pro stopped")
    
    def _market_data_loop(self):
        """Continuous market data updates"""
        trading_pairs = self.config.trading.trading_pairs or ["BTCUSD-PERP", "ETHUSD-PERP"]
        
        while self.running:
            try:
                for instrument in trading_pairs:
                    # Get ticker data
                    ticker_data = self.api.get_ticker(instrument)
                    
                    if ticker_data.get("code") == 0 and ticker_data.get("result", {}).get("data"):
                        ticker = ticker_data["result"]["data"][0]
                        
                        # Create market data object
                        market_data = MarketData(
                            instrument_name=instrument,
                            timestamp=int(time.time() * 1000),
                            open=float(ticker.get("a", 0)),
                            high=float(ticker.get("h", 0)),
                            low=float(ticker.get("l", 0)),
                            close=float(ticker.get("a", 0)),
                            volume=float(ticker.get("v", 0)),
                            bid=float(ticker.get("b", 0)) if ticker.get("b") else None,
                            ask=float(ticker.get("k", 0)) if ticker.get("k") else None
                        )
                        
                        # Store market data
                        self.market_data[instrument] = market_data
                        
                        # Update all strategies
                        for strategy in self.strategies.values():
                            strategy.update_market_data(market_data)
                        
                        logger.debug(f"Updated market data for {instrument}: ${market_data.close}")
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in market data loop: {e}")
                time.sleep(10)
    
    def _trading_loop(self):
        """Main trading logic loop"""
        while self.running:
            try:
                for instrument in self.market_data.keys():
                    current_price = self.market_data[instrument].close
                    
                    # Check each active strategy
                    for strategy in self.active_strategies:
                        # Check for buy signals
                        if instrument not in self.positions and strategy.should_buy(instrument):
                            signal = strategy.analyze(instrument)
                            
                            if signal.signal_type == SignalType.BUY and signal.confidence > 0.6:
                                self._execute_buy_signal(instrument, strategy, signal)
                        
                        # Check for sell signals
                        elif instrument in self.positions and strategy.should_sell(instrument):
                            signal = strategy.analyze(instrument)
                            
                            if signal.signal_type == SignalType.SELL and signal.confidence > 0.6:
                                self._execute_sell_signal(instrument, strategy, signal)
                
                time.sleep(self.config.trading.trade_frequency)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(30)
    
    def _execute_buy_signal(self, instrument: str, strategy: BaseStrategy, signal):
        """Execute buy signal"""
        try:
            # Get current balance
            balance_data = self.api.get_balance()
            if balance_data.get("code") != 0:
                logger.error("Failed to get account balance")
                return
            
            balance_info = balance_data.get("result", {}).get("data", [])
            if not balance_info:
                logger.error("No balance information available")
                return
            
            available_balance = float(balance_info[0].get("total_available_balance", 0))
            
            # Calculate position size
            position_size = strategy.calculate_position_size(instrument, available_balance)
            
            if position_size <= 0:
                logger.warning(f"Position size too small for {instrument}")
                return
            
            # Check minimum trade amount
            trade_value = position_size * signal.price
            if trade_value < self.config.trading.min_trade_amount:
                logger.warning(f"Trade value ${trade_value:.2f} below minimum ${self.config.trading.min_trade_amount}")
                return
            
            # Execute buy order
            if self.config.api.sandbox:
                # Simulate order in sandbox mode
                success = self._simulate_order(instrument, OrderSide.BUY, position_size, signal.price)
            else:
                # Real order execution
                order_request = OrderRequest(
                    instrument_name=instrument,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=str(position_size)
                )
                
                result = self.api.create_order(order_request)
                success = result.get("code") == 0
            
            if success:
                # Record position
                self.positions[instrument] = {
                    'side': 'BUY',
                    'quantity': position_size,
                    'entry_price': signal.price,
                    'strategy': strategy.name,
                    'timestamp': time.time()
                }
                
                self.trade_logger.position_opened(instrument, "BUY", position_size, signal.price)
                logger.info(f"Opened BUY position: {position_size} {instrument} @ ${signal.price} using {strategy.name}")
                
        except Exception as e:
            logger.error(f"Error executing buy signal: {e}")
    
    def _execute_sell_signal(self, instrument: str, strategy: BaseStrategy, signal):
        """Execute sell signal"""
        try:
            if instrument not in self.positions:
                logger.warning(f"No position to sell for {instrument}")
                return
            
            position = self.positions[instrument]
            
            # Execute sell order
            if self.config.api.sandbox:
                # Simulate order in sandbox mode
                success = self._simulate_order(instrument, OrderSide.SELL, position['quantity'], signal.price)
            else:
                # Real order execution
                order_request = OrderRequest(
                    instrument_name=instrument,
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=str(position['quantity'])
                )
                
                result = self.api.create_order(order_request)
                success = result.get("code") == 0
            
            if success:
                # Calculate PnL
                entry_price = position['entry_price']
                exit_price = signal.price
                quantity = position['quantity']
                
                if position['side'] == 'BUY':
                    pnl = (exit_price - entry_price) * quantity
                else:
                    pnl = (entry_price - exit_price) * quantity
                
                # Update performance metrics
                self.total_trades += 1
                self.total_pnl += pnl
                
                if pnl > 0:
                    self.winning_trades += 1
                
                # Update strategy performance
                strategy.update_performance(pnl, pnl > 0)
                
                # Remove position
                del self.positions[instrument]
                
                self.trade_logger.position_closed(instrument, "SELL", quantity, exit_price, pnl)
                logger.info(f"Closed position: {instrument} @ ${exit_price} | PnL: ${pnl:.2f}")
                
        except Exception as e:
            logger.error(f"Error executing sell signal: {e}")
    
    def _simulate_order(self, instrument: str, side: OrderSide, quantity: float, price: float) -> bool:
        """Simulate order execution for sandbox mode"""
        logger.info(f"SIMULATED ORDER: {side.value} {quantity} {instrument} @ ${price}")
        return True
    
    def get_status(self) -> Dict:
        """Get bot status and performance metrics"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'running': self.running,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate,
            'total_pnl': self.total_pnl,
            'open_positions': len(self.positions),
            'active_strategies': [s.name for s in self.active_strategies],
            'last_update': datetime.now().isoformat()
        }
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        positions_with_unrealized_pnl = {}
        
        for instrument, position in self.positions.items():
            current_price = self.market_data.get(instrument, {}).close if instrument in self.market_data else 0
            
            if current_price > 0:
                entry_price = position['entry_price']
                quantity = position['quantity']
                
                if position['side'] == 'BUY':
                    unrealized_pnl = (current_price - entry_price) * quantity
                else:
                    unrealized_pnl = (entry_price - current_price) * quantity
                
                positions_with_unrealized_pnl[instrument] = {
                    **position,
                    'current_price': current_price,
                    'unrealized_pnl': unrealized_pnl
                }
        
        return positions_with_unrealized_pnl
    
    def get_strategies_info(self) -> List[Dict]:
        """Get information about all strategies"""
        return [strategy.get_strategy_info() for strategy in self.strategies.values()]
    
    def enable_strategy(self, strategy_name: str):
        """Enable a strategy"""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            strategy.enable()
            
            if strategy not in self.active_strategies:
                self.active_strategies.append(strategy)
            
            logger.info(f"Enabled strategy: {strategy_name}")
    
    def disable_strategy(self, strategy_name: str):
        """Disable a strategy"""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            strategy.disable()
            
            if strategy in self.active_strategies:
                self.active_strategies.remove(strategy)
            
            logger.info(f"Disabled strategy: {strategy_name}")
    
    def update_strategy_config(self, strategy_name: str, config: Dict):
        """Update strategy configuration"""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].update_config(config)
            logger.info(f"Updated config for strategy: {strategy_name}")





    def get_all_market_data(self):
        """Get market data for all supported trading pairs"""
        try:
            pairs = [
                'BTCUSD-PERP', 'ETHUSD-PERP', 'ADAUSD-PERP', 'SOLUSD-PERP',
                'DOTUSD-PERP', 'LINKUSD-PERP', 'AVAXUSD-PERP', 'MATICUSD-PERP'
            ]
            
            market_data = {}
            for pair in pairs:
                try:
                    # Get data from your API client
                    ticker = self.api_client.get_ticker(pair)
                    market_data[pair] = {
                        'price': float(ticker.get('last_price', 0)),
                        'change': float(ticker.get('price_change_24h', 0)),
                        'volume': float(ticker.get('volume_24h', 0))
                    }
                except Exception as e:
                    logger.warning(f"Failed to get data for {pair}: {e}")
                    # Fallback to cached data or default
                    market_data[pair] = {
                        'price': 0,
                        'change': 0,
                        'volume': 0
                    }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting all market data: {e}")
            return {}

    def get_performance_metrics(self):
        """Get real performance metrics from the bot"""
        try:
            # Calculate real metrics from your trading history
            metrics = {
                'total_pnl': 0,
                'total_trades': 0,
                'win_rate': 0,
                'daily_volume': 0,
                'open_positions': {}
            }
            
            # Get data from your trading history/database
            if hasattr(self, 'trading_history'):
                trades = self.trading_history
                metrics['total_trades'] = len(trades)
                
                if trades:
                    total_pnl = sum(trade.get('pnl', 0) for trade in trades)
                    winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
                    
                    metrics['total_pnl'] = total_pnl
                    metrics['win_rate'] = (winning_trades / len(trades)) * 100
                    
                    # Calculate daily volume (last 24h)
                    from datetime import datetime, timedelta
                    yesterday = datetime.now() - timedelta(days=1)
                    daily_trades = [t for t in trades if t.get('timestamp', datetime.min) > yesterday]
                    metrics['daily_volume'] = sum(trade.get('volume', 0) for trade in daily_trades)
            
            # Get open positions
            if hasattr(self, 'positions'):
                metrics['open_positions'] = self.positions
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                'total_pnl': 0,
                'total_trades': 0,
                'win_rate': 0,
                'daily_volume': 0,
                'open_positions': {}
            }