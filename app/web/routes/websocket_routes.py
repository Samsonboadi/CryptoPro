"""
WebSocket Routes
Handles real-time WebSocket communication for live updates.
"""

from flask_socketio import SocketIO, emit, disconnect
import threading
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def create_websocket_routes(socketio: SocketIO, bot=None):
    """
    Create WebSocket event handlers
    
    Args:
        socketio: SocketIO instance
        bot: Trading bot instance
    """
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info('Client connected to WebSocket')
        emit('status', {'connected': True})
        
        # Send initial data
        if bot:
            try:
                # Send bot status
                status = bot.get_status()
                emit('bot_status', status)
                
                # Send strategies
                strategies = bot.get_strategies_info()
                emit('strategies_update', strategies)
                
                # Send positions
                positions = bot.get_positions()
                emit('positions_update', positions)
                
            except Exception as e:
                logger.error(f"Error sending initial data: {e}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info('Client disconnected from WebSocket')
    
    @socketio.on('subscribe_updates')
    def handle_subscribe_updates(data):
        """Handle subscription to real-time updates"""
        try:
            update_types = data.get('types', ['status', 'positions', 'strategies'])
            logger.info(f'Client subscribed to updates: {update_types}')
            
            # Start sending updates for this client
            # In a real implementation, you'd track client subscriptions
            emit('subscription_confirmed', {'types': update_types})
            
        except Exception as e:
            logger.error(f"Error handling subscription: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('get_market_data')
    def handle_get_market_data(data):
        """Handle market data request"""
        try:
            instrument = data.get('instrument')
            
            if bot and instrument in bot.market_data:
                market_data = bot.market_data[instrument]
                emit('market_data', {
                    'instrument': instrument,
                    'timestamp': market_data.timestamp,
                    'price': market_data.close,
                    'volume': market_data.volume,
                    'bid': market_data.bid,
                    'ask': market_data.ask
                })
            else:
                emit('error', {'message': f'No market data for {instrument}'})
                
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('bot_command')
    def handle_bot_command(data):
        """Handle bot control commands"""
        try:
            command = data.get('command')
            
            if not bot:
                emit('error', {'message': 'Bot not available'})
                return
            
            if command == 'start':
                if not bot.running:
                    bot.start()
                    emit('command_result', {'command': 'start', 'success': True})
                else:
                    emit('command_result', {'command': 'start', 'success': False, 'message': 'Already running'})
                    
            elif command == 'stop':
                if bot.running:
                    bot.stop()
                    emit('command_result', {'command': 'stop', 'success': True})
                else:
                    emit('command_result', {'command': 'stop', 'success': False, 'message': 'Not running'})
                    
            else:
                emit('error', {'message': f'Unknown command: {command}'})
                
        except Exception as e:
            logger.error(f"Error handling bot command: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('strategy_command')
    def handle_strategy_command(data):
        """Handle strategy control commands"""
        try:
            command = data.get('command')
            strategy_name = data.get('strategy_name')
            
            if not bot:
                emit('error', {'message': 'Bot not available'})
                return
            
            if not strategy_name:
                emit('error', {'message': 'Strategy name required'})
                return
            
            if command == 'enable':
                bot.enable_strategy(strategy_name)
                emit('command_result', {'command': 'enable', 'strategy': strategy_name, 'success': True})
                
            elif command == 'disable':
                bot.disable_strategy(strategy_name)
                emit('command_result', {'command': 'disable', 'strategy': strategy_name, 'success': True})
                
            elif command == 'configure':
                config = data.get('config', {})
                bot.update_strategy_config(strategy_name, config)
                emit('command_result', {'command': 'configure', 'strategy': strategy_name, 'success': True})
                
            else:
                emit('error', {'message': f'Unknown strategy command: {command}'})
            
            # Send updated strategies info
            strategies = bot.get_strategies_info()
            emit('strategies_update', strategies)
            
        except Exception as e:
            logger.error(f"Error handling strategy command: {e}")
            emit('error', {'message': str(e)})
    
    def start_real_time_updates():
        """Start broadcasting real-time updates to all connected clients"""
        def update_loop():
            while True:
                try:
                    if bot and bot.running:
                        # Broadcast bot status
                        status = bot.get_status()
                        socketio.emit('bot_status', status)
                        
                        # Broadcast positions
                        positions = bot.get_positions()
                        socketio.emit('positions_update', positions)
                        
                        # Broadcast market data
                        for instrument, market_data in bot.market_data.items():
                            socketio.emit('market_data_update', {
                                'instrument': instrument,
                                'timestamp': market_data.timestamp,
                                'price': market_data.close,
                                'volume': market_data.volume
                            })
                    
                    time.sleep(2)  # Update every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Error in real-time update loop: {e}")
                    time.sleep(5)
        
        # Start update thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        logger.info("Real-time updates started")
    
    # Start real-time updates when WebSocket routes are created
    start_real_time_updates()
    
    logger.info("WebSocket routes created successfully")