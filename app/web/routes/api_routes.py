"""
Complete REST API Routes
Handles all REST API endpoints for the trading bot web interface.
"""

from flask import Flask, jsonify, request
import logging
import time
from typing import Optional
import traceback

logger = logging.getLogger(__name__)

def create_api_routes(app: Flask, bot=None):
    """
    Create comprehensive API routes for the Flask application
    
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
                    'message': 'Bot not initialized',
                    'totalPnl': 0,
                    'totalTrades': 0,
                    'winRate': 0,
                    'openPositions': 0,
                    'dailyVolume': 0,
                    'accountBalance': 0,
                    'availableBalance': 0
                })
            
            # Get real performance data from bot
            performance = bot.get_performance_metrics()
            balance = bot.get_account_balance()
            
            return jsonify({
                'status': 'success',
                'running': bot.running,
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
                'message': f'Status error: {str(e)}',
                'totalPnl': 0,
                'totalTrades': 0,
                'winRate': 0,
                'openPositions': 0,
                'dailyVolume': 0,
                'accountBalance': 0,
                'availableBalance': 0
            }), 500

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

    @app.route('/api/market-data/all', methods=['GET'])
    def get_all_market_data():
        """Get market data for all trading pairs"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            market_data = bot.get_all_market_data()
            return jsonify({
                'status': 'success',
                'data': market_data
            })
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/market-data/<instrument>', methods=['GET'])
    def get_market_data(instrument):
        """Get market data for specific instrument"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            if instrument in bot.market_data:
                data = bot.market_data[instrument]
                return jsonify({
                    'status': 'success',
                    'data': {
                        'instrument': instrument,
                        'price': data.close,
                        'volume': data.volume,
                        'timestamp': data.timestamp,
                        'bid': data.bid,
                        'ask': data.ask
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': f'No data for {instrument}'})
                
        except Exception as e:
            logger.error(f"Error getting market data for {instrument}: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/account/balance', methods=['GET'])
    def get_account_balance():
        """Get account balance"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            balance = bot.get_account_balance()
            return jsonify({
                'status': 'success',
                'balance': balance
            })
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/account/holdings', methods=['GET'])
    def get_account_holdings():
        """Get account holdings for portfolio display"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            holdings = bot.get_account_holdings()
            return jsonify({
                'status': 'success',
                'holdings': holdings
            })
            
        except Exception as e:
            logger.error(f"Error getting account holdings: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/positions', methods=['GET'])
    def get_positions():
        """Get current positions"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            positions = bot.get_positions()
            return jsonify({
                'status': 'success',
                'positions': positions
            })
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/strategies', methods=['GET'])
    def get_strategies():
        """Get all trading strategies"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            strategies = bot.get_strategies_info()
            return jsonify({
                'status': 'success',
                'strategies': strategies
            })
            
        except Exception as e:
            logger.error(f"Error getting strategies: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/strategies/enable', methods=['POST'])
    def enable_strategy():
        """Enable a trading strategy"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            data = request.get_json()
            strategy_id = data.get('strategy_id')
            strategy_name = data.get('strategy_name')
            
            # For now, use strategy_name (in real app, map ID to name)
            if strategy_name:
                bot.enable_strategy(strategy_name)
                return jsonify({'status': 'success', 'message': f'Enabled {strategy_name}'})
            else:
                return jsonify({'status': 'error', 'message': 'Strategy name required'})
                
        except Exception as e:
            logger.error(f"Error enabling strategy: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/strategies/disable', methods=['POST'])
    def disable_strategy():
        """Disable a trading strategy"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            data = request.get_json()
            strategy_id = data.get('strategy_id')
            strategy_name = data.get('strategy_name')
            
            # For now, use strategy_name (in real app, map ID to name)
            if strategy_name:
                bot.disable_strategy(strategy_name)
                return jsonify({'status': 'success', 'message': f'Disabled {strategy_name}'})
            else:
                return jsonify({'status': 'error', 'message': 'Strategy name required'})
                
        except Exception as e:
            logger.error(f"Error disabling strategy: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/orders', methods=['POST'])
    def place_order():
        """Place a trading order"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            data = request.get_json()
            
            # Extract order parameters
            symbol = data.get('symbol')
            side = data.get('side')
            order_type = data.get('type', 'market')
            quantity = float(data.get('quantity', 0))
            price = float(data.get('price', 0)) if data.get('price') else None
            
            # Validate required fields
            if not symbol or not side or quantity <= 0:
                return jsonify({
                    'status': 'error', 
                    'message': 'Missing required fields: symbol, side, quantity'
                })
            
            # For demo mode, simulate order placement
            if bot.config.api.sandbox:
                logger.info(f"DEMO ORDER: {side} {quantity} {symbol} @ {price or 'market'}")
                return jsonify({
                    'status': 'success',
                    'message': f'Demo order placed: {side} {quantity} {symbol}',
                    'order_id': f'demo_{int(time.time())}'
                })
            else:
                # Real order placement would go here
                from ..api.crypto_com_api import OrderRequest, OrderSide, OrderType
                
                order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
                order_type_enum = OrderType.LIMIT if order_type == 'limit' else OrderType.MARKET
                
                order_request = OrderRequest(
                    instrument_name=symbol,
                    side=order_side,
                    order_type=order_type_enum,
                    quantity=str(quantity),
                    price=str(price) if price else None
                )
                
                result = bot.api.create_order(order_request)
                
                if result.get('code') == 0:
                    return jsonify({
                        'status': 'success',
                        'message': 'Order placed successfully',
                        'order_id': result.get('result', {}).get('order_id')
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': result.get('message', 'Order placement failed')
                    })
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            logger.error(traceback.format_exc())
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/orders/<order_id>', methods=['DELETE'])
    def cancel_order(order_id):
        """Cancel a trading order"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            if bot.config.api.sandbox:
                return jsonify({
                    'status': 'success',
                    'message': f'Demo order {order_id} cancelled'
                })
            else:
                result = bot.api.cancel_order(order_id=order_id)
                
                if result.get('code') == 0:
                    return jsonify({
                        'status': 'success',
                        'message': 'Order cancelled successfully'
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': result.get('message', 'Order cancellation failed')
                    })
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current bot configuration"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            config_dict = bot.config.to_dict()
            
            # Remove sensitive information
            if 'api' in config_dict:
                config_dict['api']['api_key'] = '***' if config_dict['api']['api_key'] else ''
                config_dict['api']['secret_key'] = '***' if config_dict['api']['secret_key'] else ''
            
            return jsonify({
                'status': 'success',
                'config': config_dict
            })
            
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/config', methods=['POST'])
    def update_config():
        """Update bot configuration"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            data = request.get_json()
            
            # Update configuration safely
            if 'maxPositionSize' in data:
                bot.config.risk.max_position_size = float(data['maxPositionSize'])
            
            if 'stopLoss' in data:
                bot.config.risk.default_stop_loss = float(data['stopLoss'])
            
            if 'takeProfit' in data:
                bot.config.risk.default_take_profit = float(data['takeProfit'])
            
            if 'tradingMode' in data:
                # Update sandbox mode based on trading mode
                bot.config.api.sandbox = data['tradingMode'] != 'live'
            
            # Save configuration
            bot.config.save_config()
            
            return jsonify({
                'status': 'success',
                'message': 'Configuration updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/test-connection', methods=['POST'])
    def test_connection():
        """Test API connection"""
        try:
            data = request.get_json()
            
            # For demo purposes, always return success for sandbox
            if data.get('exchange') == 'crypto_com':
                if bot and bot.config.api.sandbox:
                    return jsonify({
                        'status': 'success',
                        'message': 'Connection test successful (sandbox mode)'
                    })
                elif bot:
                    # Test real connection
                    try:
                        result = bot.api.get_instruments()
                        if result.get('code') == 0:
                            return jsonify({
                                'status': 'success',
                                'message': 'Connection test successful'
                            })
                        else:
                            return jsonify({
                                'status': 'error',
                                'message': f'API Error: {result.get("message", "Unknown error")}'
                            })
                    except Exception as api_error:
                        return jsonify({
                            'status': 'error',
                            'message': f'Connection failed: {str(api_error)}'
                        })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Bot not available'
                    })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Exchange {data.get("exchange")} not supported yet'
                })
            
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/performance', methods=['GET'])
    def get_performance():
        """Get detailed performance metrics"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            performance = bot.get_performance_metrics()
            
            # Add additional calculated metrics
            if performance.get('total_trades', 0) > 0:
                performance['loss_rate'] = 100 - performance.get('win_rate', 0)
                performance['avg_trade'] = performance.get('total_pnl', 0) / performance['total_trades']
            
            return jsonify({
                'status': 'success',
                'performance': performance
            })
            
        except Exception as e:
            logger.error(f"Error getting performance: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/history/trades', methods=['GET'])
    def get_trade_history():
        """Get trading history"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            # Get recent trades from bot's trading history
            trades = getattr(bot, 'trading_history', [])
            
            # Format trades for frontend
            formatted_trades = []
            for trade in trades[-50:]:  # Last 50 trades
                formatted_trades.append({
                    'id': trade.get('timestamp').strftime('%Y%m%d%H%M%S') if hasattr(trade.get('timestamp'), 'strftime') else str(int(time.time())),
                    'timestamp': trade.get('timestamp').isoformat() if hasattr(trade.get('timestamp'), 'isoformat') else str(trade.get('timestamp')),
                    'instrument': trade.get('instrument'),
                    'side': trade.get('side'),
                    'quantity': trade.get('quantity'),
                    'price': trade.get('price'),
                    'volume': trade.get('volume'),
                    'pnl': trade.get('pnl', 0),
                    'strategy': trade.get('strategy')
                })
            
            return jsonify({
                'status': 'success',
                'trades': formatted_trades
            })
            
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            status = {
                'status': 'healthy',
                'timestamp': time.time(),
                'bot_running': bot.running if bot else False,
                'api_connected': True if bot and bot.api else False
            }
            
            return jsonify(status)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }), 500

    @app.route('/api/orderbook/<instrument>', methods=['GET'])
    def get_orderbook(instrument):
        """Get order book for specific instrument"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            # Get depth parameter
            depth = request.args.get('depth', 10, type=int)
            
            if bot.config.api.sandbox:
                # Generate demo order book data
                current_price = bot.market_data.get(instrument).close if instrument in bot.market_data else 100000
                
                asks = []
                bids = []
                
                for i in range(depth):
                    # Generate asks (selling orders) above current price
                    ask_price = current_price + (i + 1) * (current_price * 0.0001)
                    ask_quantity = 0.1 + (i * 0.05)
                    asks.append({'price': round(ask_price, 2), 'quantity': round(ask_quantity, 4)})
                    
                    # Generate bids (buying orders) below current price
                    bid_price = current_price - (i + 1) * (current_price * 0.0001)
                    bid_quantity = 0.1 + (i * 0.05)
                    bids.append({'price': round(bid_price, 2), 'quantity': round(bid_quantity, 4)})
                
                return jsonify({
                    'status': 'success',
                    'orderbook': {
                        'asks': asks,
                        'bids': bids,
                        'instrument': instrument
                    }
                })
            else:
                # Get real order book from API
                result = bot.api.get_orderbook(instrument, depth)
                
                if result.get('code') == 0:
                    orderbook_data = result.get('result', {}).get('data', {})
                    return jsonify({
                        'status': 'success',
                        'orderbook': orderbook_data
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': result.get('message', 'Failed to get orderbook')
                    })
            
        except Exception as e:
            logger.error(f"Error getting orderbook for {instrument}: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/trades/<instrument>', methods=['GET'])
    def get_recent_trades(instrument):
        """Get recent trades for specific instrument"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            count = request.args.get('count', 25, type=int)
            
            if bot.config.api.sandbox:
                # Generate demo trade data
                import random
                from datetime import datetime, timedelta
                
                trades = []
                current_price = bot.market_data.get(instrument).close if instrument in bot.market_data else 100000
                
                for i in range(count):
                    # Generate realistic trade data
                    price_variation = current_price * random.uniform(-0.001, 0.001)
                    trade_price = current_price + price_variation
                    trade_quantity = random.uniform(0.01, 1.0)
                    trade_side = random.choice(['BUY', 'SELL'])
                    trade_time = (datetime.now() - timedelta(minutes=i)).strftime('%H:%M:%S')
                    
                    trades.append({
                        'id': f'demo_{i}',
                        'price': round(trade_price, 2),
                        'quantity': round(trade_quantity, 4),
                        'side': trade_side,
                        'time': trade_time
                    })
                
                return jsonify({
                    'status': 'success',
                    'trades': trades
                })
            else:
                # Get real trades from API
                result = bot.api.get_trades(instrument, count)
                
                if result.get('code') == 0:
                    trades_data = result.get('result', {}).get('data', [])
                    return jsonify({
                        'status': 'success',
                        'trades': trades_data
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': result.get('message', 'Failed to get trades')
                    })
            
        except Exception as e:
            logger.error(f"Error getting trades for {instrument}: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/candlestick/<instrument>', methods=['GET'])
    def get_candlestick_data(instrument):
        """Get candlestick data for charting"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            timeframe = request.args.get('timeframe', '1h')
            count = request.args.get('count', 100, type=int)
            
            if bot.config.api.sandbox:
                # Generate demo candlestick data
                import random
                from datetime import datetime, timedelta
                
                candlesticks = []
                base_price = bot.market_data.get(instrument).close if instrument in bot.market_data else 100000
                
                for i in range(count):
                    # Generate OHLCV data
                    time_offset = count - i
                    if timeframe == '1m':
                        candle_time = datetime.now() - timedelta(minutes=time_offset)
                    elif timeframe == '1h':
                        candle_time = datetime.now() - timedelta(hours=time_offset)
                    elif timeframe == '1d':
                        candle_time = datetime.now() - timedelta(days=time_offset)
                    else:
                        candle_time = datetime.now() - timedelta(hours=time_offset)
                    
                    # Generate realistic price movement
                    price_change = random.uniform(-0.02, 0.02)  # ±2% change
                    open_price = base_price * (1 + price_change)
                    
                    high_change = random.uniform(0, 0.01)  # Up to 1% higher
                    low_change = random.uniform(-0.01, 0)  # Up to 1% lower
                    close_change = random.uniform(-0.005, 0.005)  # ±0.5% from open
                    
                    high_price = open_price * (1 + high_change)
                    low_price = open_price * (1 + low_change)
                    close_price = open_price * (1 + close_change)
                    
                    # Ensure OHLC logic (high >= max(open, close), low <= min(open, close))
                    high_price = max(high_price, open_price, close_price)
                    low_price = min(low_price, open_price, close_price)
                    
                    volume = random.uniform(1000, 10000)
                    
                    candlesticks.append({
                        'timestamp': int(candle_time.timestamp() * 1000),
                        'open': round(open_price, 2),
                        'high': round(high_price, 2),
                        'low': round(low_price, 2),
                        'close': round(close_price, 2),
                        'volume': round(volume, 2)
                    })
                    
                    base_price = close_price  # Use close as next base
                
                return jsonify({
                    'status': 'success',
                    'candlesticks': candlesticks,
                    'instrument': instrument,
                    'timeframe': timeframe
                })
            else:
                # Get real candlestick data from API
                result = bot.api.get_candlestick(instrument, timeframe, count)
                
                if result.get('code') == 0:
                    candlestick_data = result.get('result', {}).get('data', [])
                    return jsonify({
                        'status': 'success',
                        'candlesticks': candlestick_data,
                        'instrument': instrument,
                        'timeframe': timeframe
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': result.get('message', 'Failed to get candlestick data')
                    })
            
        except Exception as e:
            logger.error(f"Error getting candlestick data for {instrument}: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/strategy/<strategy_name>/signals', methods=['GET'])
    def get_strategy_signals(strategy_name):
        """Get recent signals from a specific strategy"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            if strategy_name not in bot.strategies:
                return jsonify({
                    'status': 'error', 
                    'message': f'Strategy {strategy_name} not found'
                })
            
            strategy = bot.strategies[strategy_name]
            days = request.args.get('days', 7, type=int)
            
            # Get signal history if strategy supports it
            if hasattr(strategy, 'get_signal_history'):
                signals = strategy.get_signal_history(bot.config.trading.trading_pairs[0], days)
                return jsonify({
                    'status': 'success',
                    'signals': signals,
                    'strategy': strategy_name
                })
            else:
                return jsonify({
                    'status': 'success',
                    'signals': [],
                    'message': 'Strategy does not support signal history'
                })
            
        except Exception as e:
            logger.error(f"Error getting signals for {strategy_name}: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/strategy/<strategy_name>/optimize', methods=['POST'])
    def optimize_strategy(strategy_name):
        """Optimize strategy parameters"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            if strategy_name not in bot.strategies:
                return jsonify({
                    'status': 'error',
                    'message': f'Strategy {strategy_name} not found'
                })
            
            strategy = bot.strategies[strategy_name]
            data = request.get_json()
            lookback_days = data.get('lookback_days', 30)
            
            # Optimize parameters if strategy supports it
            if hasattr(strategy, 'optimize_parameters'):
                optimized_config = strategy.optimize_parameters(
                    bot.config.trading.trading_pairs[0], 
                    lookback_days
                )
                
                return jsonify({
                    'status': 'success',
                    'optimized_config': optimized_config,
                    'strategy': strategy_name
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Strategy does not support optimization'
                })
            
        except Exception as e:
            logger.error(f"Error optimizing {strategy_name}: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/risk/metrics', methods=['GET'])
    def get_risk_metrics():
        """Get current risk metrics"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            # Calculate portfolio risk metrics
            positions = bot.get_positions()
            balance = bot.get_account_balance()
            
            total_exposure = 0
            position_count = len(positions)
            
            for instrument, position in positions.items():
                current_price = bot.market_data.get(instrument).close if instrument in bot.market_data else 0
                exposure = position['quantity'] * current_price
                total_exposure += exposure
            
            # Calculate risk metrics
            risk_metrics = {
                'total_exposure': total_exposure,
                'available_balance': balance.get('available_balance', 0),
                'exposure_ratio': (total_exposure / balance.get('total_balance', 1)) * 100,
                'position_count': position_count,
                'max_positions': bot.config.risk.max_open_positions,
                'max_position_size': bot.config.risk.max_position_size,
                'daily_loss_limit': bot.config.risk.max_daily_loss,
                'leverage_used': total_exposure / max(balance.get('total_balance', 1), 1),
                'max_leverage': bot.config.risk.max_leverage
            }
            
            # Add strategy-specific risk metrics
            strategy_risks = {}
            for name, strategy in bot.strategies.items():
                if hasattr(strategy, 'get_risk_metrics'):
                    strategy_risks[name] = strategy.get_risk_metrics(
                        bot.config.trading.trading_pairs[0]
                    )
            
            return jsonify({
                'status': 'success',
                'portfolio_risk': risk_metrics,
                'strategy_risks': strategy_risks
            })
            
        except Exception as e:
            logger.error(f"Error getting risk metrics: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/notifications', methods=['GET'])
    def get_notifications():
        """Get recent notifications/alerts"""
        try:
            # This would typically come from a notification service
            # For now, return demo notifications
            notifications = [
                {
                    'id': 1,
                    'type': 'trade',
                    'message': 'BUY order executed: 0.1 BTCUSD-PERP @ $100,000',
                    'timestamp': int(time.time() - 3600),
                    'severity': 'info'
                },
                {
                    'id': 2,
                    'type': 'pnl',
                    'message': 'Daily PnL target reached: +2.5%',
                    'timestamp': int(time.time() - 7200),
                    'severity': 'success'
                },
                {
                    'id': 3,
                    'type': 'risk',
                    'message': 'Position size approaching limit',
                    'timestamp': int(time.time() - 10800),
                    'severity': 'warning'
                }
            ]
            
            return jsonify({
                'status': 'success',
                'notifications': notifications
            })
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/backup/export', methods=['GET'])
    def export_data():
        """Export trading data for backup"""
        try:
            if not bot:
                return jsonify({'status': 'error', 'message': 'Bot not available'})
            
            export_data = {
                'config': bot.config.to_dict(),
                'trading_history': getattr(bot, 'trading_history', []),
                'performance': bot.get_performance_metrics(),
                'strategies': bot.get_strategies_info(),
                'export_timestamp': time.time()
            }
            
            # Remove sensitive data
            if 'api' in export_data['config']:
                export_data['config']['api']['api_key'] = '[REDACTED]'
                export_data['config']['api']['secret_key'] = '[REDACTED]'
            
            return jsonify({
                'status': 'success',
                'data': export_data
            })
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/system/stats', methods=['GET'])
    def get_system_stats():
        """Get system performance statistics"""
        try:
            import psutil
            import os
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process metrics
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            
            stats = {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_gb': memory.used / (1024**3),
                    'memory_total_gb': memory.total / (1024**3),
                    'disk_percent': (disk.used / disk.total) * 100,
                    'disk_free_gb': disk.free / (1024**3)
                },
                'process': {
                    'memory_mb': process_memory.rss / (1024**2),
                    'threads': process.num_threads(),
                    'uptime_seconds': time.time() - process.create_time()
                },
                'bot': {
                    'running': bot.running if bot else False,
                    'total_trades': getattr(bot, 'total_trades', 0),
                    'active_strategies': len(getattr(bot, 'active_strategies', [])),
                    'market_data_points': len(getattr(bot, 'market_data', {}))
                }
            }
            
            return jsonify({
                'status': 'success',
                'stats': stats
            })
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found',
            'code': 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'code': 500
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'message': 'Bad request',
            'code': 400
        }), 400

    logger.info("Complete API routes created successfully with all endpoints")