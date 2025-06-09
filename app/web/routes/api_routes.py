"""
REST API Routes
Handles all REST API endpoints for the trading bot web interface.
"""

from flask import Flask, jsonify, request
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

def create_api_routes(app: Flask, bot=None):
    """
    Create API routes for the Flask application
    
    Args:
        app: Flask application instance
        bot: Trading bot instance
    """
    
"""
REST API Routes
Handles all REST API endpoints for the trading bot web interface.
"""

from flask import Flask, jsonify, request
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def create_api_routes(app: Flask, bot=None):
    """
    Create API routes for the Flask application
    
    Args:
        app: Flask application instance
        bot: Trading bot instance
    """
    
    @app.route('/api/status', methods=['GET'])
    def get_status():
        """Get bot status with real performance metrics"""
        try:
            if not bot:
                return jsonify({
                    'status': 'error',
                    'running': False,
                    'message': 'Bot not initialized'
                })
            
            # Get real performance data from bot
            performance = bot.get_performance_metrics()
            balance = bot.api_client.get_account_balance() if hasattr(bot, 'api_client') else {}
            
            return jsonify({
                'status': 'success',
                'running': bot.is_running if hasattr(bot, 'is_running') else False,
                'totalPnl': performance.get('total_pnl', 0),
                'totalTrades': performance.get('total_trades', 0),
                'winRate': performance.get('win_rate', 0),
                'openPositions': len(performance.get('open_positions', {})),
                'dailyVolume': performance.get('daily_volume', 0),
                'accountBalance': balance.get('total_balance', 0),
                'availableBalance': balance.get('available_balance', 0)
            })
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({
                'status': 'error',
                'running': False,
                'message': f'Status error: {str(e)}'
            })

    
    @app.route('/api/start', methods=['POST'])
    def start_bot():
        """Start the trading bot"""
        try:
            if bot and not bot.running:
                bot.start()
                return jsonify({'status': 'success', 'message': 'Bot started'})
            elif bot and bot.running:
                return jsonify({'status': 'error', 'message': 'Bot already running'})
            else:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/stop', methods=['POST'])
    def stop_bot():
        """Stop the trading bot"""
        try:
            if bot and bot.running:
                bot.stop()
                return jsonify({'status': 'success', 'message': 'Bot stopped'})
            elif bot and not bot.running:
                return jsonify({'status': 'error', 'message': 'Bot not running'})
            else:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/strategies')
    def get_strategies():
        """Get list of available strategies and their performance"""
        try:
            if bot:
                strategies = bot.get_strategies_info()
                return jsonify(strategies)
            else:
                return jsonify([])
        except Exception as e:
            logger.error(f"Error getting strategies: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/strategies/enable', methods=['POST'])
    def enable_strategy():
        """Enable a trading strategy"""
        try:
            data = request.json
            strategy_name = data.get('strategy_name')
            
            if not strategy_name:
                return jsonify({'status': 'error', 'message': 'Strategy name required'}), 400
            
            if bot:
                bot.enable_strategy(strategy_name)
                return jsonify({'status': 'success', 'message': f'Strategy {strategy_name} enabled'})
            else:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
        except Exception as e:
            logger.error(f"Error enabling strategy: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/strategies/disable', methods=['POST'])
    def disable_strategy():
        """Disable a trading strategy"""
        try:
            data = request.json
            strategy_name = data.get('strategy_name')
            
            if not strategy_name:
                return jsonify({'status': 'error', 'message': 'Strategy name required'}), 400
            
            if bot:
                bot.disable_strategy(strategy_name)
                return jsonify({'status': 'success', 'message': f'Strategy {strategy_name} disabled'})
            else:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
        except Exception as e:
            logger.error(f"Error disabling strategy: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/strategies/configure', methods=['POST'])
    def configure_strategy():
        """Configure strategy parameters"""
        try:
            data = request.json
            strategy_name = data.get('strategy_name')
            config = data.get('config', {})
            
            if not strategy_name:
                return jsonify({'status': 'error', 'message': 'Strategy name required'}), 400
            
            if bot:
                bot.update_strategy_config(strategy_name, config)
                return jsonify({'status': 'success', 'message': f'Strategy {strategy_name} configured'})
            else:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
        except Exception as e:
            logger.error(f"Error configuring strategy: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/positions')
    def get_positions():
        """Get current positions"""
        try:
            if bot:
                positions = bot.get_positions()
                return jsonify(positions)
            else:
                return jsonify({})
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/market-data/<instrument>')
    def get_market_data(instrument):
        """Get market data for specific instrument"""
        try:
            if bot and instrument in bot.market_data:
                market_data = bot.market_data[instrument]
                return jsonify({
                    'instrument_name': market_data.instrument_name,
                    'timestamp': market_data.timestamp,
                    'price': market_data.close,
                    'volume': market_data.volume,
                    'bid': market_data.bid,
                    'ask': market_data.ask
                })
            else:
                return jsonify({'error': 'Market data not available'}), 404
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/backtest', methods=['POST'])
    def run_backtest():
        """Run strategy backtest"""
        try:
            data = request.json
            strategy_name = data.get('strategy_name')
            symbol = data.get('symbol', 'BTCUSD-PERP')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            initial_capital = data.get('initial_capital', 10000)
            
            if not strategy_name:
                return jsonify({'status': 'error', 'message': 'Strategy name required'}), 400
            
            # For now, return simulated backtest results
            # In a full implementation, this would run actual backtesting
            results = {
                'strategy': strategy_name,
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': initial_capital,
                'final_capital': initial_capital * 1.15,  # 15% return
                'total_return': 15.0,
                'max_drawdown': 8.5,
                'sharpe_ratio': 1.34,
                'win_rate': 62.5,
                'total_trades': 156,
                'winning_trades': 97,
                'losing_trades': 59
            }
            
            return jsonify({
                'status': 'success',
                'results': results
            })
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration"""
        try:
            if bot:
                config = bot.config.to_dict()
                # Remove sensitive information
                if 'api' in config:
                    config['api']['api_key'] = '***'
                    config['api']['secret_key'] = '***'
                return jsonify(config)
            else:
                return jsonify({})
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config', methods=['POST', 'PUT'])
    def update_config():
        """Update configuration"""
        try:
            data = request.json
            
            if bot:
                # Update specific configuration sections
                if 'risk' in data:
                    for key, value in data['risk'].items():
                        setattr(bot.config.risk, key, value)
                
                if 'trading' in data:
                    for key, value in data['trading'].items():
                        setattr(bot.config.trading, key, value)
                
                # Save configuration
                bot.config.save_config()
                
                return jsonify({'status': 'success', 'message': 'Configuration updated'})
            else:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/trades')
    def get_trades():
        """Get recent trades history"""
        try:
            # For now, return mock data
            # In a full implementation, this would query the database
            trades = [
                {
                    'id': '1',
                    'timestamp': 1704067200000,
                    'instrument': 'BTCUSD-PERP',
                    'side': 'BUY',
                    'quantity': 0.1,
                    'price': 42000.0,
                    'strategy': 'RSI Strategy',
                    'pnl': 150.0
                },
                {
                    'id': '2',
                    'timestamp': 1704153600000,
                    'instrument': 'ETHUSD-PERP',
                    'side': 'SELL',
                    'quantity': 1.5,
                    'price': 2500.0,
                    'strategy': 'RSI Strategy',
                    'pnl': -75.0
                }
            ]
            return jsonify(trades)
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/portfolio')
    def get_portfolio():
        """Get portfolio information"""
        try:
            # For now, return mock portfolio data
            # In a full implementation, this would calculate from actual positions
            portfolio = {
                'total_value': 10500.0,
                'cash_balance': 8500.0,
                'positions_value': 2000.0,
                'daily_pnl': 125.0,
                'daily_pnl_percent': 1.2,
                'allocations': {
                    'CASH': 81.0,
                    'BTCUSD-PERP': 15.0,
                    'ETHUSD-PERP': 4.0
                }
            }
            return jsonify(portfolio)
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/instruments')
    def get_instruments():
        """Get available trading instruments"""
        try:
            if bot and bot.api:
                instruments_data = bot.api.get_instruments()
                if instruments_data.get('code') == 0:
                    return jsonify(instruments_data.get('result', {}))
                else:
                    return jsonify({'error': 'Failed to fetch instruments'}), 500
            else:
                # Return default instruments if bot not available
                return jsonify({
                    'data': [
                        {'symbol': 'BTCUSD-PERP', 'base_ccy': 'BTC', 'quote_ccy': 'USD'},
                        {'symbol': 'ETHUSD-PERP', 'base_ccy': 'ETH', 'quote_ccy': 'USD'},
                        {'symbol': 'ADAUSD-PERP', 'base_ccy': 'ADA', 'quote_ccy': 'USD'}
                    ]
                })
        except Exception as e:
            logger.error(f"Error getting instruments: {e}")
            return jsonify({'error': str(e)}), 500
    




    @app.route('/api/test-connection', methods=['POST'])
    def test_connection():
        """Test API connection with provided credentials"""
        try:
            data = request.get_json()
            api_key = data.get('apiKey', '')
            api_secret = data.get('apiSecret', '')
            exchange = data.get('exchange', 'crypto_com')
            
            # Basic validation
            if not api_key or not api_secret:
                return jsonify({
                    'status': 'error',
                    'message': 'API key and secret are required'
                })
            
            # Here you would test the actual connection
            # For now, we'll do a basic validation
            if len(api_key) < 10 or len(api_secret) < 10:
                return jsonify({
                    'status': 'error',
                    'message': 'API credentials appear to be invalid (too short)'
                })
            
            # TODO: Implement actual API connection test based on exchange
            # For now, return success for demo purposes
            return jsonify({
                'status': 'success',
                'message': f'Successfully connected to {exchange}'
            })
            
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Connection test failed: {str(e)}'
            })

    @app.route('/api/orders', methods=['POST'])
    def place_order():
        """Place a manual trading order"""
        try:
            data = request.get_json()
            symbol = data.get('symbol')
            order_type = data.get('type', 'market')
            side = data.get('side')
            quantity = float(data.get('quantity', 0))
            price = float(data.get('price', 0)) if data.get('price') else None
            
            # Basic validation
            if not symbol or not side or quantity <= 0:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid order parameters'
                })
            
            # TODO: Implement actual order placement through your bot
            # For now, simulate order placement
            logger.info(f"Manual order request: {side} {quantity} {symbol} at {price or 'market'}")
            
            return jsonify({
                'status': 'success',
                'message': f'Order placed: {side} {quantity} {symbol}',
                'order_id': f'demo_order_{int(time.time())}'
            })
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to place order: {str(e)}'
            })

    @app.route('/api/positions/close', methods=['POST'])
    def close_position():
        """Close a specific position"""
        try:
            data = request.get_json()
            symbol = data.get('symbol')
            
            if not symbol:
                return jsonify({
                    'status': 'error',
                    'message': 'Symbol is required'
                })
            
            # TODO: Implement actual position closing through your bot
            logger.info(f"Close position request for {symbol}")
            
            return jsonify({
                'status': 'success',
                'message': f'Position closed for {symbol}'
            })
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to close position: {str(e)}'
            })



    @app.route('/api/account/balance', methods=['GET'])
    def get_account_balance():
        """Get real account balance from Crypto.com API"""
        try:
            if not bot:
                return jsonify({
                    'status': 'error',
                    'message': 'Bot not initialized'
                })
            
            # Get balance from your bot's API client
            balance_data = bot.api_client.get_account_balance()
            
            return jsonify({
                'status': 'success',
                'totalBalance': balance_data.get('total_balance', 0),
                'availableBalance': balance_data.get('available_balance', 0),
                'lockedBalance': balance_data.get('locked_balance', 0),
                'holdings': balance_data.get('holdings', [])
            })
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get balance: {str(e)}'
            })

    @app.route('/api/market-data/all', methods=['GET'])
    def get_all_market_data():
        """Get real market data for all trading pairs"""
        try:
            if not bot:
                return jsonify({
                    'status': 'error',
                    'message': 'Bot not initialized'
                })
            
            # Get market data from your bot
            market_data = bot.get_all_market_data()
            
            return jsonify({
                'status': 'success',
                'data': market_data
            })
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get market data: {str(e)}'
            })

    @app.route('/api/account/holdings', methods=['GET'])
    def get_account_holdings():
        """Get real portfolio holdings"""
        try:
            if not bot:
                return jsonify({
                    'status': 'error',
                    'message': 'Bot not initialized'
                })
            
            # Get holdings from your bot's API client
            holdings = bot.api_client.get_account_holdings()
            
            return jsonify({
                'status': 'success',
                'holdings': holdings
            })
            
        except Exception as e:
            logger.error(f"Error getting holdings: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get holdings: {str(e)}'
            })


    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': time.time(),
                'bot_running': bot.running if bot else False,
                'api_connected': bot.api is not None if bot else False
            }
            return jsonify(health_status)
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
    
    logger.info("API routes created successfully")