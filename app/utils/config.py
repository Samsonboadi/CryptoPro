"""
Configuration Management
Handles loading and managing application configuration from various sources.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API configuration"""
    api_key: str = ""
    secret_key: str = ""
    sandbox: bool = True
    base_url: str = ""
    websocket_url: str = ""

@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_daily_loss: float = 5.0
    max_position_size: float = 10.0
    max_open_positions: int = 5
    default_stop_loss: float = 2.0
    default_take_profit: float = 5.0
    max_correlation: float = 0.7
    max_leverage: float = 3.0

@dataclass
class TradingConfig:
    """Trading configuration"""
    enabled_strategies: list = None
    trading_pairs: list = None
    min_trade_amount: float = 10.0
    max_trade_amount: float = 1000.0
    trade_frequency: int = 10  # seconds between trade checks

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///data/trading_bot.db"
    echo: bool = False
    pool_size: int = 5

@dataclass
class WebConfig:
    """Web interface configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: str = "dev-secret-key"

class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "config/config.yaml"
        self.config_data = {}
        
        # Initialize with defaults
        self.api = APIConfig()
        self.risk = RiskConfig()
        self.trading = TradingConfig()
        self.database = DatabaseConfig()
        self.web = WebConfig()
        
        # Load environment variables FIRST
        self.load_environment()
        
        # Then load configuration file (can override env vars)
        self.load_config()
    
    def load_environment(self):
        """Load configuration from environment variables - ENHANCED"""
        logger.info("Loading environment variables...")
        
        # API configuration from environment
        env_api_key = os.getenv('CRYPTO_COM_API_KEY') or os.getenv('API_KEY') or os.getenv('CRYPTOBOT_API_KEY')
        env_secret_key = os.getenv('CRYPTO_COM_SECRET_KEY') or os.getenv('SECRET_KEY') or os.getenv('CRYPTOBOT_SECRET_KEY')
        env_sandbox = os.getenv('CRYPTO_COM_SANDBOX') or os.getenv('SANDBOX_MODE') or os.getenv('CRYPTOBOT_SANDBOX')
        
        if env_api_key:
            self.api.api_key = env_api_key
            logger.info("✓ API key loaded from environment")
        else:
            logger.warning("⚠️ No API key found in environment variables")
            
        if env_secret_key:
            self.api.secret_key = env_secret_key
            logger.info("✓ Secret key loaded from environment")
        else:
            logger.warning("⚠️ No secret key found in environment variables")
            
        if env_sandbox:
            self.api.sandbox = env_sandbox.lower() in ('true', '1', 'yes', 'on')
            logger.info(f"✓ Sandbox mode from environment: {self.api.sandbox}")
        
        # Web configuration
        if os.getenv('WEB_HOST'):
            self.web.host = os.getenv('WEB_HOST')
        if os.getenv('WEB_PORT'):
            self.web.port = int(os.getenv('WEB_PORT'))
        if os.getenv('WEB_SECRET_KEY'):
            self.web.secret_key = os.getenv('WEB_SECRET_KEY')
        if os.getenv('DEBUG'):
            self.web.debug = os.getenv('DEBUG').lower() == 'true'
        
        # Database configuration
        if os.getenv('DATABASE_URL'):
            self.database.url = os.getenv('DATABASE_URL')
        
        logger.info("Environment variables loaded")
    
    def load_config(self):
        """Load configuration from file"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            logger.warning(f"Config file {self.config_file} not found, creating default")
            self._create_default_config()
            return
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                    self.config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    self.config_data = json.load(f)
                else:
                    logger.error(f"Unsupported config file format: {config_path.suffix}")
                    return
            
            # Update configuration objects (but don't override env vars if they exist)
            self._update_from_dict()
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            self._create_default_config()
    
    def _update_from_dict(self):
        """Update configuration objects from loaded data"""
        if 'api' in self.config_data:
            api_config = self.config_data['api']
            
            # Only update from file if not already set by environment
            if not self.api.api_key or self.api.api_key == "":
                self.api.api_key = api_config.get('api_key', self.api.api_key)
            if not self.api.secret_key or self.api.secret_key == "":
                self.api.secret_key = api_config.get('secret_key', self.api.secret_key)
                
            # Other API settings can be overridden
            self.api.base_url = api_config.get('base_url', self.api.base_url)
            self.api.websocket_url = api_config.get('websocket_url', self.api.websocket_url)
            
            # Sandbox mode: environment takes precedence
            if 'sandbox' in api_config and not os.getenv('CRYPTO_COM_SANDBOX'):
                self.api.sandbox = api_config.get('sandbox', self.api.sandbox)
        
        if 'risk' in self.config_data:
            risk_config = self.config_data['risk']
            self.risk.max_daily_loss = risk_config.get('max_daily_loss', self.risk.max_daily_loss)
            self.risk.max_position_size = risk_config.get('max_position_size', self.risk.max_position_size)
            self.risk.max_open_positions = risk_config.get('max_open_positions', self.risk.max_open_positions)
            self.risk.default_stop_loss = risk_config.get('default_stop_loss', self.risk.default_stop_loss)
            self.risk.default_take_profit = risk_config.get('default_take_profit', self.risk.default_take_profit)
            self.risk.max_correlation = risk_config.get('max_correlation', self.risk.max_correlation)
            self.risk.max_leverage = risk_config.get('max_leverage', self.risk.max_leverage)
        
        if 'trading' in self.config_data:
            trading_config = self.config_data['trading']
            self.trading.enabled_strategies = trading_config.get('enabled_strategies', ['RSI Strategy'])
            self.trading.trading_pairs = trading_config.get('trading_pairs', ['BTCUSD-PERP', 'ETHUSD-PERP'])
            self.trading.min_trade_amount = trading_config.get('min_trade_amount', self.trading.min_trade_amount)
            self.trading.max_trade_amount = trading_config.get('max_trade_amount', self.trading.max_trade_amount)
            self.trading.trade_frequency = trading_config.get('trade_frequency', self.trading.trade_frequency)
        
        if 'database' in self.config_data:
            db_config = self.config_data['database']
            self.database.url = db_config.get('url', self.database.url)
            self.database.echo = db_config.get('echo', self.database.echo)
            self.database.pool_size = db_config.get('pool_size', self.database.pool_size)
        
        if 'web' in self.config_data:
            web_config = self.config_data['web']
            self.web.host = web_config.get('host', self.web.host)
            self.web.port = web_config.get('port', self.web.port)
            self.web.debug = web_config.get('debug', self.web.debug)
            if not os.getenv('WEB_SECRET_KEY'):
                self.web.secret_key = web_config.get('secret_key', self.web.secret_key)
    
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            'api': {
                'api_key': 'your_crypto_com_api_key_here',
                'secret_key': 'your_crypto_com_secret_key_here',
                'sandbox': True
            },
            'risk': asdict(self.risk),
            'trading': {
                'enabled_strategies': ['RSI Strategy'],
                'trading_pairs': ['BTCUSD-PERP', 'ETHUSD-PERP'],
                'min_trade_amount': 10.0,
                'max_trade_amount': 1000.0,
                'trade_frequency': 10
            },
            'database': asdict(self.database),
            'web': asdict(self.web)
        }
        
        # Create config directory if it doesn't exist
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            logger.info(f"Default configuration created at {self.config_file}")
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """Get configuration for a specific strategy"""
        strategies_config = self.config_data.get('strategies', {})
        return strategies_config.get(strategy_name, {})
    
    def update_strategy_config(self, strategy_name: str, config: Dict[str, Any]):
        """Update configuration for a specific strategy"""
        if 'strategies' not in self.config_data:
            self.config_data['strategies'] = {}
        
        self.config_data['strategies'][strategy_name] = config
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        config_path = Path(self.config_file)
        
        # Update config_data with current objects
        self.config_data.update({
            'api': asdict(self.api),
            'risk': asdict(self.risk),
            'trading': asdict(self.trading),
            'database': asdict(self.database),
            'web': asdict(self.web)
        })
        
        try:
            with open(config_path, 'w') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
                elif config_path.suffix.lower() == '.json':
                    json.dump(self.config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # API validation - more lenient for demo mode
        if not self.api.api_key or self.api.api_key in ['your_crypto_com_api_key_here', 'your_api_key_here', '']:
            if not self.api.sandbox:
                errors.append("API key not configured for production mode")
            else:
                logger.warning("No API key configured - will use demo data")
        
        if not self.api.secret_key or self.api.secret_key in ['your_crypto_com_secret_key_here', 'your_secret_key_here', '']:
            if not self.api.sandbox:
                errors.append("Secret key not configured for production mode")
            else:
                logger.warning("No secret key configured - will use demo data")
        
        # Validate risk limits
        if self.risk.max_daily_loss <= 0 or self.risk.max_daily_loss > 50:
            errors.append("Invalid max daily loss (should be 0-50%)")
        
        if self.risk.max_position_size <= 0 or self.risk.max_position_size > 100:
            errors.append("Invalid max position size (should be 0-100%)")
        
        # Validate trading configuration
        if not self.trading.trading_pairs:
            errors.append("No trading pairs configured")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info("Configuration validation passed")
        self.print_config_summary()
        return True
    
    def print_config_summary(self):
        """Print configuration summary"""
        logger.info("=== Configuration Summary ===")
        logger.info(f"API Key: {'✓ Set' if self.api.api_key and self.api.api_key != 'your_crypto_com_api_key_here' else '✗ Not set'}")
        logger.info(f"Secret Key: {'✓ Set' if self.api.secret_key and self.api.secret_key != 'your_crypto_com_secret_key_here' else '✗ Not set'}")
        logger.info(f"Sandbox Mode: {self.api.sandbox}")
        logger.info(f"Trading Pairs: {', '.join(self.trading.trading_pairs or [])}")
        logger.info(f"Enabled Strategies: {', '.join(self.trading.enabled_strategies or [])}")
        logger.info("=============================")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'api': asdict(self.api),
            'risk': asdict(self.risk),
            'trading': asdict(self.trading),
            'database': asdict(self.database),
            'web': asdict(self.web),
            'strategies': self.config_data.get('strategies', {})
        }