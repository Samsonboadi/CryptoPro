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