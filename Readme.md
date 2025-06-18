# CryptoBot Pro 🚀

**Advanced Cryptocurrency Trading Bot with Machine Learning and Professional Web Interface**

CryptoBot Pro is a sophisticated trading bot built with Python that integrates with Crypto.com Exchange API. It features advanced technical analysis using `pandas_ta` (instead of TA-Lib for better compatibility), multiple trading strategies, risk management, and a beautiful web dashboard.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## ✨ Key Features

### 🤖 Trading Engine
- **Multi-Strategy Support**: RSI, MACD, Bollinger Bands, Moving Averages
- **Real-time Market Data**: Live price feeds and order book data
- **Advanced Risk Management**: Position sizing, stop-loss, take-profit
- **Paper Trading**: Test strategies without real money
- **Portfolio Management**: Track positions and performance

### 📊 Technical Analysis
- **pandas_ta Integration**: Reliable technical indicators without compilation issues
- **50+ Technical Indicators**: RSI, MACD, Bollinger Bands, Stochastic, ADX, Williams %R
- **Custom Strategy Development**: Easy-to-extend strategy framework
- **Backtesting Support**: Test strategies on historical data

### 🌐 Professional Web Interface
- **Real-time Dashboard**: Live market data and bot status
- **Interactive Charts**: TradingView-style price charts
- **Portfolio Management**: Track holdings and performance
- **Strategy Configuration**: Enable/disable and configure strategies
- **Order Management**: Place and manage trades through web UI

### 🔧 Technical Features
- **WebSocket Support**: Real-time data streaming
- **RESTful API**: Complete API for external integrations
- **Comprehensive Logging**: Detailed trading and system logs
- **Configuration Management**: YAML and environment variable support
- **Database Integration**: SQLite with optional PostgreSQL support

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **pip package manager**
- **Crypto.com Exchange account** (for live trading)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/cryptobot-pro.git
cd cryptobot-pro
```

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a virtual environment
- Install all dependencies including `pandas_ta`
- Create configuration templates
- Set up directory structure
- Test the installation

### 3. Configure API Keys

Edit the `.env` file with your API credentials:

```bash
# Crypto.com API Configuration
CRYPTO_COM_API_KEY=your_actual_api_key
CRYPTO_COM_SECRET_KEY=your_actual_secret_key
CRYPTO_COM_SANDBOX=true  # Set to false for live trading

# Web Interface
WEB_SECRET_KEY=your-secure-secret-key
```

### 4. Start the Application

```bash
./start.sh
```

### 5. Access Web Interface

Open your browser to: **http://localhost:5000**

## 📁 Project Structure

```
cryptobot-pro/
├── app/
│   ├── api/                    # Exchange API clients
│   │   └── crypto_com_api.py   # Crypto.com API implementation
│   ├── core/                   # Core trading engine
│   │   └── bot.py              # Main trading bot orchestrator
│   ├── strategies/             # Trading strategies
│   │   ├── base_strategy.py    # Abstract strategy base class
│   │   └── rsi_strategy.py     # RSI trading strategy
│   ├── utils/                  # Utilities and helpers
│   │   ├── config.py           # Configuration management
│   │   ├── logger.py           # Logging setup
│   │   └── technical_indicators.py  # pandas_ta indicators
│   └── web/                    # Web interface
│       ├── app.py              # Flask application factory
│       └── routes/             # API and WebSocket routes
├── config/
│   └── config.yaml             # Main configuration file
├── data/
│   └── logs/                   # Application logs
├── requirements.txt            # Python dependencies
├── main.py                     # Application entry point
├── setup.sh                    # Setup script
├── start.sh                    # Startup script
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# API Configuration
CRYPTO_COM_API_KEY=your_api_key
CRYPTO_COM_SECRET_KEY=your_secret_key
CRYPTO_COM_SANDBOX=true

# Web Interface
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_SECRET_KEY=your-secret-key

# Trading Settings
TRADING_MODE=paper
MAX_POSITION_SIZE=10
STOP_LOSS=2.0
TAKE_PROFIT=5.0
```

### YAML Configuration

The `config/config.yaml` file contains detailed settings:

```yaml
api:
  api_key: ${CRYPTO_COM_API_KEY}
  secret_key: ${CRYPTO_COM_SECRET_KEY}
  sandbox: true

trading:
  enabled_strategies:
    - RSI Strategy
  trading_pairs:
    - BTCUSD-PERP
    - ETHUSD-PERP
  min_trade_amount: 10.0
  max_trade_amount: 1000.0

risk:
  max_daily_loss: 5.0
  max_position_size: 10.0
  max_open_positions: 5
  default_stop_loss: 2.0
  default_take_profit: 5.0

strategies:
  RSI Strategy:
    rsi_period: 14
    oversold_threshold: 30
    overbought_threshold: 70
    min_confidence: 0.6
```

## 📈 Trading Strategies

### RSI Strategy

The RSI (Relative Strength Index) strategy identifies overbought and oversold conditions:

- **Buy Signal**: RSI crosses above oversold threshold (default: 30)
- **Sell Signal**: RSI crosses below overbought threshold (default: 70)
- **Confirmations**: Volume, trend, and momentum filters

### Custom Strategy Development

Create new strategies by extending the `BaseStrategy` class:

```python
from app.strategies.base_strategy import BaseStrategy, TradingSignal, SignalType

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config=None):
        super().__init__("My Custom Strategy", config)
    
    def analyze(self, instrument: str) -> TradingSignal:
        # Implement your trading logic here
        return TradingSignal(
            signal_type=SignalType.BUY,
            confidence=0.8,
            price=current_price,
            reason="Custom signal triggered"
        )
```

## 🌐 Web Dashboard

### Features

1. **Dashboard**: Real-time performance metrics and charts
2. **Trading**: Place orders and manage positions
3. **Portfolio**: View holdings and allocation
4. **Strategies**: Configure and monitor trading strategies
5. **Settings**: Update bot configuration and API settings

### API Endpoints

The web interface provides a comprehensive REST API:

```
GET  /api/status                 # Bot status and metrics
POST /api/start                  # Start trading bot
POST /api/stop                   # Stop trading bot
GET  /api/positions              # Current positions
GET  /api/market-data/all        # All market data
POST /api/orders                 # Place new order
GET  /api/strategies             # List strategies
```

## 🛠️ Development

### Running in Development Mode

```bash
# Start with debug mode
./start.sh --debug

# Start without web interface (headless)
./start.sh --no-web

# Start with custom config
./start.sh --config my-config.yaml
```

### Testing Dependencies

```bash
python3 test_setup.py
```

### Adding New Indicators

Using `pandas_ta` makes it easy to add new technical indicators:

```python
from app.utils.technical_indicators import TechnicalIndicators

# Use any pandas_ta indicator
indicators = TechnicalIndicators()
macd_line, macd_signal, macd_histogram = indicators.macd(prices)
bollinger_upper, bollinger_middle, bollinger_lower = indicators.bollinger_bands(prices)
```

## 🔒 Security

### API Key Management

- Store API keys in environment variables
- Never commit credentials to version control
- Use sandbox mode for testing
- Enable IP whitelisting on exchange

### Risk Management

- Set appropriate position size limits
- Use stop-loss orders
- Monitor daily loss limits
- Regular performance reviews

## 📊 Performance Monitoring

### Metrics Tracked

- **Total PnL**: Profit and loss across all trades
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Trade Frequency**: Number of trades per time period

### Logging

Comprehensive logging system with multiple log files:

- `app.log`: General application logs
- `trading.log`: Trading-specific activities
- `errors.log`: Error messages and exceptions
- `performance.log`: Performance metrics

## 🚨 Troubleshooting

### Common Issues

#### 1. pandas_ta Import Error

```bash
# Reinstall pandas_ta
pip uninstall pandas-ta
pip install pandas-ta>=0.3.14b
```

#### 2. API Connection Issues

- Check API credentials in `.env` file
- Verify sandbox mode setting
- Check network connectivity
- Review API rate limits

#### 3. WebSocket Connection Failed

```bash
# Check if port is available
netstat -an | grep 5000

# Try different port
WEB_PORT=8080 ./start.sh
```

#### 4. Technical Indicator Errors

```bash
# Test individual indicators
python3 -c "
from app.utils.technical_indicators import TechnicalIndicators
import numpy as np
ti = TechnicalIndicators()
prices = np.random.random(100) * 100
rsi = ti.rsi(prices)
print('RSI calculation successful:', len(rsi))
"
```

### Getting Help

1. Check the logs in `data/logs/`
2. Run `python3 test_setup.py` to verify installation
3. Review configuration in `config/config.yaml`
4. Check API credentials and permissions

## 🔄 Updates and Maintenance

### Updating Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade pandas-ta
```

### Backup Configuration

```bash
# Export current configuration
curl http://localhost:5000/api/backup/export > backup.json
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**Important**: This software is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss. Never trade with money you cannot afford to lose. The authors are not responsible for any financial losses incurred through the use of this software.

- Always test strategies thoroughly in paper trading mode
- Understand the risks of automated trading
- Monitor your bot's performance regularly
- Keep your API keys secure
- Use appropriate position sizing and risk management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🌟 Features Roadmap

- [ ] Additional exchange integrations (Binance, Coinbase Pro)
- [ ] Machine learning prediction models
- [ ] Advanced backtesting engine
- [ ] Social trading features
- [ ] Mobile app companion
- [ ] Telegram/Discord notifications
- [ ] Advanced portfolio analytics
- [ ] Multi-timeframe analysis

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/cryptobot-pro/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/cryptobot-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cryptobot-pro/discussions)

---

**Happy Trading! 📈🚀**

*Built with ❤️ by the CryptoBot Pro team*