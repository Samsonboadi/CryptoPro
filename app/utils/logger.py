"""
Logging Configuration
Centralized logging setup for the trading bot application.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import colorlog

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_dir: str = "data/logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
):
    """
    Setup comprehensive logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional specific log file name
        log_dir: Directory for log files
        max_bytes: Maximum size per log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
    """
    
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler with colors
    if console_output:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        color_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s - %(blue)s%(name)s%(reset)s - %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(color_formatter)
        root_logger.addHandler(console_handler)
    
    # Main application log file
    app_log_file = log_path / (log_file or "app.log")
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_handler)
    
    # Trading-specific log file
    trading_log_file = log_path / "trading.log"
    trading_handler = logging.handlers.RotatingFileHandler(
        trading_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    trading_handler.setLevel(logging.INFO)
    trading_handler.setFormatter(detailed_formatter)
    
    # Only log trading-related messages to trading.log
    trading_logger = logging.getLogger('app.strategies')
    trading_logger.addHandler(trading_handler)
    
    bot_logger = logging.getLogger('app.core.bot')
    bot_logger.addHandler(trading_handler)
    
    # Error log file (ERROR and CRITICAL only)
    error_log_file = log_path / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Performance log file (for metrics and performance data)
    performance_log_file = log_path / "performance.log"
    performance_handler = logging.handlers.RotatingFileHandler(
        performance_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(simple_formatter)
    
    # Create performance logger
    performance_logger = logging.getLogger('performance')
    performance_logger.addHandler(performance_handler)
    performance_logger.setLevel(logging.INFO)
    performance_logger.propagate = False  # Don't propagate to root logger
    
    # Set specific logger levels
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('websocket').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    
    # Create custom loggers for different components
    create_component_loggers()
    
    logging.info("Logging configuration completed")

def create_component_loggers():
    """Create specialized loggers for different components"""
    
    # API Logger
    api_logger = logging.getLogger('app.api')
    api_logger.setLevel(logging.INFO)
    
    # Strategy Logger
    strategy_logger = logging.getLogger('app.strategies')
    strategy_logger.setLevel(logging.INFO)
    
    # Risk Management Logger
    risk_logger = logging.getLogger('app.risk')
    risk_logger.setLevel(logging.INFO)
    
    # ML Logger
    ml_logger = logging.getLogger('app.ml')
    ml_logger.setLevel(logging.INFO)
    
    # Backtesting Logger
    backtest_logger = logging.getLogger('app.backtesting')
    backtest_logger.setLevel(logging.INFO)
    
    # Portfolio Logger
    portfolio_logger = logging.getLogger('app.portfolio')
    portfolio_logger.setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

def log_trade(symbol: str, side: str, quantity: float, price: float, strategy: str):
    """Log trading activity"""
    trade_logger = logging.getLogger('app.core.bot')
    trade_logger.info(f"TRADE: {side} {quantity} {symbol} @ {price} using {strategy}")

def log_performance(metric: str, value: float, symbol: str = None):
    """Log performance metrics"""
    performance_logger = logging.getLogger('performance')
    symbol_str = f" [{symbol}]" if symbol else ""
    performance_logger.info(f"{metric}{symbol_str}: {value}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None):
    """Log error with additional context"""
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    logger.error(error_msg, exc_info=True)

class TradingLogger:
    """Specialized logger for trading activities"""
    
    def __init__(self, strategy_name: str):
        self.logger = logging.getLogger(f'app.strategies.{strategy_name.lower().replace(" ", "_")}')
        self.strategy_name = strategy_name
    
    def signal(self, symbol: str, signal_type: str, confidence: float, reason: str):
        """Log trading signal"""
        self.logger.info(f"SIGNAL: {signal_type} {symbol} (confidence: {confidence:.2f}) - {reason}")
    
    def position_opened(self, symbol: str, side: str, quantity: float, price: float):
        """Log position opening"""
        self.logger.info(f"POSITION_OPEN: {side} {quantity} {symbol} @ ${price:.2f}")
    
    def position_closed(self, symbol: str, side: str, quantity: float, price: float, pnl: float):
        """Log position closing"""
        pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
        self.logger.info(f"POSITION_CLOSE: {side} {quantity} {symbol} @ ${price:.2f} | PnL: {pnl_str}")
    
    def error(self, message: str, error: Exception = None):
        """Log strategy error"""
        if error:
            self.logger.error(f"{message}: {str(error)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def warning(self, message: str):
        """Log strategy warning"""
        self.logger.warning(message)
    
    def info(self, message: str):
        """Log strategy info"""
        self.logger.info(message)

class APILogger:
    """Specialized logger for API activities"""
    
    def __init__(self):
        self.logger = logging.getLogger('app.api.crypto_com_api')
    
    def request(self, method: str, endpoint: str, params: dict = None):
        """Log API request"""
        param_str = f" with params: {params}" if params else ""
        self.logger.debug(f"API Request: {method} {endpoint}{param_str}")
    
    def response(self, method: str, endpoint: str, status_code: int, response_time: float):
        """Log API response"""
        self.logger.debug(f"API Response: {method} {endpoint} | Status: {status_code} | Time: {response_time:.3f}s")
    
    def error(self, method: str, endpoint: str, error: Exception):
        """Log API error"""
        self.logger.error(f"API Error: {method} {endpoint} | Error: {str(error)}")
    
    def rate_limit(self, wait_time: float):
        """Log rate limiting"""
        self.logger.warning(f"Rate limit hit, waiting {wait_time:.2f}s")

# Example usage function
def demo_logging():
    """Demonstrate logging capabilities"""
    setup_logging(level=logging.DEBUG)
    
    logger = get_logger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Trading logger demo
    trading_logger = TradingLogger("RSI Strategy")
    trading_logger.signal("BTCUSD-PERP", "BUY", 0.85, "RSI oversold")
    trading_logger.position_opened("BTCUSD-PERP", "BUY", 0.1, 35000.0)
    
    # Performance logging demo
    log_performance("win_rate", 68.5, "BTCUSD-PERP")
    log_performance("total_pnl", 1250.75)

if __name__ == "__main__":
    demo_logging()