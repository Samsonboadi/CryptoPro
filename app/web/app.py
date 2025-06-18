"""
Flask Application Factory - Simple Version Without Problematic Charts
"""

from flask import Flask, render_template_string
from flask_socketio import SocketIO
import logging
from typing import Optional

from ..utils.config import Config

# Import routes with absolute paths
from app.web.routes.api_routes import create_api_routes
from app.web.routes.websocket_routes import create_websocket_routes

logger = logging.getLogger(__name__)

def create_app(config: Config, bot=None) -> Flask:
    """Create and configure Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure Flask
    app.config['SECRET_KEY'] = config.web.secret_key
    app.config['DEBUG'] = config.web.debug
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Store config and bot in app context
    app.config['BOT_CONFIG'] = config
    app.config['BOT_INSTANCE'] = bot
    app.config['SOCKETIO'] = socketio
    
    # Register routes
    create_api_routes(app, bot)
    create_websocket_routes(socketio, bot)
    
    # Main dashboard route
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        return render_template_string(get_simple_dashboard_html())
    
    logger.info("Flask application created successfully")
    return app

def get_simple_dashboard_html() -> str:
    """Return a simple dashboard HTML without problematic charts"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoBot Pro - Trading Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.3.2/socket.io.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .tab-active { @apply bg-blue-600 text-white; }
        .tab-inactive { @apply bg-gray-700 text-gray-300 hover:bg-gray-600; }
        .crypto-card { transition: all 0.3s ease; }
        .crypto-card:hover { transform: translateY(-2px); }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div x-data="simpleTradingApp()" class="min-h-screen">
        <!-- Navigation -->
        <nav class="bg-gray-800 border-b border-gray-700 px-6 py-4">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold gradient-bg bg-clip-text text-transparent">CryptoBot Pro</h1>
                
                <!-- Bot Status & Controls -->
                <div class="flex items-center space-x-4">
                    <div class="flex items-center space-x-2">
                        <div :class="botStatus === 'running' ? 'bg-green-500' : 'bg-red-500'" 
                             class="w-3 h-3 rounded-full animate-pulse"></div>
                        <span class="text-sm" x-text="botStatus === 'running' ? 'Bot Active' : 'Bot Stopped'"></span>
                    </div>
                    <button @click="toggleBot()" 
                            :class="botStatus === 'running' ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'"
                            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        <span x-text="botStatus === 'running' ? 'Stop Bot' : 'Start Bot'"></span>
                    </button>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="container mx-auto px-6 py-8">
            <!-- Performance Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-lg font-semibold mb-2 text-gray-300">Total PnL</h3>
                    <div class="text-3xl font-bold" :class="(performance.totalPnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'"
                         x-text="'$' + (performance.totalPnl || 0).toFixed(2)"></div>
                    <div class="text-sm text-gray-400 mt-1">All Time</div>
                </div>
                
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-lg font-semibold mb-2 text-gray-300">Total Trades</h3>
                    <div class="text-3xl font-bold text-white" x-text="performance.totalTrades || 0"></div>
                    <div class="text-sm text-gray-400 mt-1">Executed</div>
                </div>
                
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-lg font-semibold mb-2 text-gray-300">Win Rate</h3>
                    <div class="text-3xl font-bold text-blue-400" x-text="(performance.winRate || 0).toFixed(1) + '%'"></div>
                    <div class="text-sm text-gray-400 mt-1">Success Rate</div>
                </div>
                
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-lg font-semibold mb-2 text-gray-300">Account Balance</h3>
                    <div class="text-3xl font-bold text-green-400" x-text="'$' + (accountBalance || 0).toLocaleString()"></div>
                    <div class="text-sm text-gray-400 mt-1">Available: $<span x-text="(availableBalance || 0).toLocaleString()"></span></div>
                </div>
            </div>

            <!-- Market Data -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <!-- Market Overview -->
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-xl font-semibold mb-4">Market Overview</h3>
                    <div class="space-y-3">
                        <template x-for="(data, symbol) in allMarketData" :key="symbol">
                            <div class="flex justify-between items-center py-3 border-b border-gray-700">
                                <div>
                                    <div class="font-semibold" x-text="symbol.replace('-PERP', '')"></div>
                                    <div class="text-sm text-gray-400" x-text="'Volume: ' + (data.volume || 0).toLocaleString()"></div>
                                </div>
                                <div class="text-right">
                                    <div class="font-semibold text-lg" x-text="'$' + (data.price || 0).toFixed(2)"></div>
                                    <div :class="(data.change || 0) >= 0 ? 'text-green-400' : 'text-red-400'" 
                                         class="text-sm"
                                         x-text="((data.change || 0) >= 0 ? '+' : '') + (data.change || 0).toFixed(2) + '%'"></div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Bot Status -->
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-xl font-semibold mb-4">Bot Status</h3>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-300">Status:</span>
                            <span :class="botStatus === 'running' ? 'text-green-400' : 'text-red-400'" 
                                  class="font-semibold" x-text="botStatus === 'running' ? 'Running' : 'Stopped'"></span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-300">Open Positions:</span>
                            <span class="font-semibold text-purple-400" x-text="Object.keys(positions).length"></span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-300">Active Strategies:</span>
                            <span class="font-semibold text-blue-400">RSI Strategy</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-300">Last Update:</span>
                            <span class="font-semibold text-gray-400" x-text="new Date().toLocaleTimeString()"></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Recent Trades -->
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-xl font-semibold mb-4">Recent Trades</h3>
                    <div class="space-y-3">
                        <template x-for="trade in recentTrades.slice(0, 5)" :key="trade.id">
                            <div class="flex justify-between items-center py-2 border-b border-gray-700">
                                <div>
                                    <div class="font-medium" x-text="trade.symbol"></div>
                                    <div class="text-sm text-gray-400" x-text="trade.time"></div>
                                </div>
                                <div class="text-right">
                                    <div :class="trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'" 
                                         class="font-medium"
                                         x-text="trade.side + ' ' + trade.quantity"></div>
                                    <div class="text-sm" x-text="'$' + trade.price.toFixed(2)"></div>
                                </div>
                            </div>
                        </template>
                        <div x-show="recentTrades.length === 0" class="text-center py-4 text-gray-400">
                            No recent trades
                        </div>
                    </div>
                </div>

                <!-- Active Positions -->
                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <h3 class="text-xl font-semibold mb-4">Active Positions</h3>
                    <div class="space-y-3">
                        <template x-for="(position, symbol) in positions" :key="symbol">
                            <div class="flex justify-between items-center py-2 border-b border-gray-700">
                                <div>
                                    <div class="font-medium" x-text="symbol"></div>
                                    <div class="text-sm text-gray-400" x-text="position.strategy || 'Manual'"></div>
                                </div>
                                <div class="text-right">
                                    <div :class="(position.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'" 
                                         class="font-medium"
                                         x-text="'$' + (position.unrealized_pnl || 0).toFixed(2)"></div>
                                    <div class="text-sm" x-text="(position.quantity || 0).toFixed(4)"></div>
                                </div>
                            </div>
                        </template>
                        <div x-show="Object.keys(positions).length === 0" class="text-center py-4 text-gray-400">
                            No active positions
                        </div>
                    </div>
                </div>
            </div>

            <!-- Info Message -->
            <div class="mt-8 bg-blue-900/50 border border-blue-700 rounded-xl p-4">
                <div class="flex items-center space-x-2">
                    <div class="text-blue-400">ℹ️</div>
                    <div class="text-blue-200">
                        <strong>Note:</strong> Charts temporarily disabled for stability. Core trading functionality remains active.
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function simpleTradingApp() {
            return {
                botStatus: 'stopped',
                
                // Performance Data
                performance: {
                    totalPnl: 0,
                    totalTrades: 0,
                    winRate: 0,
                    openPositions: 0,
                    dailyVolume: 0
                },
                
                // Account Data
                accountBalance: 50000,
                availableBalance: 45000,
                
                // Market Data
                allMarketData: {
                    'BTCUSD-PERP': { price: 100000, change: 2.5, volume: 1234567 },
                    'ETHUSD-PERP': { price: 2630, change: -1.2, volume: 987654 },
                    'ADAUSD-PERP': { price: 0.45, change: 3.1, volume: 456789 },
                    'SOLUSD-PERP': { price: 185.50, change: -0.8, volume: 234567 }
                },
                
                // Trading Data
                positions: {},
                
                // Recent Activity
                recentTrades: [
                    { id: 1, symbol: 'BTCUSD-PERP', side: 'BUY', quantity: 0.1, price: 100000, time: '14:30:25' },
                    { id: 2, symbol: 'ETHUSD-PERP', side: 'SELL', quantity: 2.5, price: 2630, time: '14:28:15' },
                    { id: 3, symbol: 'ADAUSD-PERP', side: 'BUY', quantity: 1000, price: 0.45, time: '14:25:10' }
                ],
                
                socket: null,

                init() {
                    this.connectWebSocket();
                    this.loadInitialData();
                    // Update data every 5 seconds
                    setInterval(() => {
                        this.updateMarketData();
                    }, 5000);
                },

                connectWebSocket() {
                    try {
                        this.socket = io();
                        
                        this.socket.on('connect', () => {
                            console.log('✅ Connected to server');
                        });
                        
                        this.socket.on('bot_status', (data) => {
                            this.performance = { ...this.performance, ...data };
                            this.botStatus = data.running ? 'running' : 'stopped';
                        });
                        
                        this.socket.on('positions_update', (data) => {
                            this.positions = data || {};
                        });
                        
                        this.socket.on('market_data', (data) => {
                            this.allMarketData = { ...this.allMarketData, ...data };
                        });
                    } catch (error) {
                        console.log('WebSocket connection failed, using polling');
                    }
                },

                async loadInitialData() {
                    try {
                        // Load bot status
                        const statusResponse = await fetch('/api/status');
                        if (statusResponse.ok) {
                            const status = await statusResponse.json();
                            this.performance = {
                                totalPnl: status.totalPnl || 0,
                                totalTrades: status.totalTrades || 0,
                                winRate: status.winRate || 0,
                                openPositions: status.openPositions || 0,
                                dailyVolume: status.dailyVolume || 0
                            };
                            
                            this.accountBalance = status.accountBalance || 50000;
                            this.availableBalance = status.availableBalance || 45000;
                            this.botStatus = status.running ? 'running' : 'stopped';
                        }
                        
                        // Load market data
                        const marketResponse = await fetch('/api/market-data/all');
                        if (marketResponse.ok) {
                            const marketResult = await marketResponse.json();
                            if (marketResult.status === 'success') {
                                this.allMarketData = marketResult.data;
                            }
                        }
                        
                        // Load positions
                        const positionsResponse = await fetch('/api/positions');
                        if (positionsResponse.ok) {
                            const positionsResult = await positionsResponse.json();
                            if (positionsResult.status === 'success') {
                                this.positions = positionsResult.positions || {};
                            }
                        }
                        
                    } catch (error) {
                        console.log('Using demo data:', error);
                    }
                },

                updateMarketData() {
                    // Simulate market data updates
                    Object.keys(this.allMarketData).forEach(symbol => {
                        const data = this.allMarketData[symbol];
                        // Small random price movements
                        const change = (Math.random() - 0.5) * 0.02; // ±1%
                        data.price = data.price * (1 + change);
                        data.change = change * 100;
                    });
                },

                async toggleBot() {
                    try {
                        const endpoint = this.botStatus === 'running' ? '/api/stop' : '/api/start';
                        const response = await fetch(endpoint, { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            this.botStatus = this.botStatus === 'running' ? 'stopped' : 'running';
                            console.log('Bot status changed to:', this.botStatus);
                        } else {
                            console.error('Failed to toggle bot:', result.message);
                        }
                    } catch (error) {
                        console.error('Error toggling bot:', error);
                    }
                }
            }
        }
    </script>
</body>
</html>
    """