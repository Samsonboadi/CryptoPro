"""
Flask Application Factory
Creates and configures the Flask web application with all routes and features.
"""

from flask import Flask, render_template_string
from flask_socketio import SocketIO
import logging
from typing import Optional

from ..utils.config import Config

# Import routes with absolute paths - this fixes the import issue
from app.web.routes.api_routes import create_api_routes
from app.web.routes.websocket_routes import create_websocket_routes

logger = logging.getLogger(__name__)

# Global bot instance (will be set when app is created)
bot_instance = None

def create_app(config: Config, bot=None) -> Flask:
    """
    Create and configure Flask application
    
    Args:
        config: Application configuration
        bot: Trading bot instance
        
    Returns:
        Configured Flask application
    """
    global bot_instance
    bot_instance = bot
    
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
        return render_template_string(get_dashboard_html())
    
    logger.info("Flask application created successfully")
    return app

def get_dashboard_html() -> str:
    """
    Return the complete dashboard HTML
    This is a simplified version - in a real app, this would be in templates/
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoBot Pro - Professional Trading Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
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
        .chart-container { position: relative; height: 300px; }
        .sidebar { min-height: calc(100vh - 80px); }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div x-data="tradingApp()" class="min-h-screen">
        <!-- Navigation -->
        <nav class="bg-gray-800 border-b border-gray-700 px-6 py-4 sticky top-0 z-50">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold gradient-bg bg-clip-text text-transparent">CryptoBot Pro</h1>
                
                <!-- Main Navigation -->
                <div class="flex space-x-2">
                    <button @click="activeTab = 'dashboard'" 
                            :class="activeTab === 'dashboard' ? 'tab-active' : 'tab-inactive'"
                            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        📊 Dashboard
                    </button>
                    <button @click="activeTab = 'trading'" 
                            :class="activeTab === 'trading' ? 'tab-active' : 'tab-inactive'"
                            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        💹 Trading
                    </button>
                    <button @click="activeTab = 'portfolio'" 
                            :class="activeTab === 'portfolio' ? 'tab-active' : 'tab-inactive'"
                            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        💼 Portfolio
                    </button>
                    <button @click="activeTab = 'strategies'" 
                            :class="activeTab === 'strategies' ? 'tab-active' : 'tab-inactive'"
                            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        🤖 Strategies
                    </button>
                    <button @click="activeTab = 'settings'" 
                            :class="activeTab === 'settings' ? 'tab-active' : 'tab-inactive'"
                            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        ⚙️ Settings
                    </button>
                </div>
                
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

        <div class="flex">
            <!-- Sidebar - Market Data -->
            <div class="w-80 bg-gray-800 border-r border-gray-700 sidebar overflow-y-auto">
                <div class="p-4">
                    <h3 class="text-lg font-semibold mb-4">🔥 Market Overview</h3>
                    
                    <!-- Account Balance -->
                    <div class="bg-gray-700 rounded-lg p-4 mb-4">
                        <h4 class="text-sm font-medium text-gray-300 mb-2">Account Balance</h4>
                        <div class="text-2xl font-bold text-green-400" x-text="'$' + (accountBalance || 0).toLocaleString()"></div>
                        <div class="text-sm text-gray-400">
                            <span>Available: </span>
                            <span class="text-white" x-text="'$' + (availableBalance || 0).toLocaleString()"></span>
                        </div>
                    </div>
                    
                    <!-- Market Data List -->
                    <div class="space-y-2">
                        <template x-for="(data, symbol) in allMarketData" :key="symbol">
                            <div @click="selectPair(symbol)" 
                                 :class="selectedPair === symbol ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'"
                                 class="crypto-card rounded-lg p-3 cursor-pointer transition-all">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <div class="font-semibold" x-text="symbol.replace('-PERP', '')"></div>
                                        <div class="text-xs text-gray-400" x-text="'Vol: ' + (data.volume || 0).toLocaleString()"></div>
                                    </div>
                                    <div class="text-right">
                                        <div class="font-semibold" x-text="'$' + (data.price || 0).toFixed(2)"></div>
                                        <div :class="(data.change || 0) >= 0 ? 'text-green-400' : 'text-red-400'" 
                                             class="text-xs"
                                             x-text="((data.change || 0) >= 0 ? '+' : '') + (data.change || 0).toFixed(2) + '%'"></div>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>

            <!-- Main Content Area -->
            <div class="flex-1">
                <!-- Dashboard Tab -->
                <div x-show="activeTab === 'dashboard'" class="p-6">
                    <!-- Performance Cards -->
                    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-lg font-semibold mb-2">Total PnL</h3>
                            <div class="text-3xl font-bold" :class="(performance.totalPnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'"
                                 x-text="'$' + (performance.totalPnl || 0).toFixed(2)"></div>
                            <div class="text-sm text-gray-400 mt-1">24h Change</div>
                        </div>
                        
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-lg font-semibold mb-2">Total Trades</h3>
                            <div class="text-3xl font-bold text-white" x-text="performance.totalTrades || 0"></div>
                            <div class="text-sm text-gray-400 mt-1">All Time</div>
                        </div>
                        
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-lg font-semibold mb-2">Win Rate</h3>
                            <div class="text-3xl font-bold text-blue-400" x-text="(performance.winRate || 0).toFixed(1) + '%'"></div>
                            <div class="text-sm text-gray-400 mt-1">Success Rate</div>
                        </div>
                        
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-lg font-semibold mb-2">Open Positions</h3>
                            <div class="text-3xl font-bold text-purple-400" x-text="performance.openPositions || 0"></div>
                            <div class="text-sm text-gray-400 mt-1">Active Now</div>
                        </div>
                        
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-lg font-semibold mb-2">Daily Volume</h3>
                            <div class="text-3xl font-bold text-yellow-400" x-text="'$' + (performance.dailyVolume || 0).toLocaleString()"></div>
                            <div class="text-sm text-gray-400 mt-1">24h Trading</div>
                        </div>
                    </div>

                    <!-- Price Chart -->
                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-8">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-xl font-semibold" x-text="selectedPair + ' Price Chart'"></h3>
                            <div class="flex space-x-2">
                                <button @click="changeTimeframe('1h')" 
                                        :class="timeframe === '1h' ? 'bg-blue-600' : 'bg-gray-700'"
                                        class="px-3 py-1 rounded text-sm">1H</button>
                                <button @click="changeTimeframe('4h')" 
                                        :class="timeframe === '4h' ? 'bg-blue-600' : 'bg-gray-700'"
                                        class="px-3 py-1 rounded text-sm">4H</button>
                                <button @click="changeTimeframe('1d')" 
                                        :class="timeframe === '1d' ? 'bg-blue-600' : 'bg-gray-700'"
                                        class="px-3 py-1 rounded text-sm">1D</button>
                            </div>
                        </div>
                        <div class="chart-container">
                            <canvas id="priceChart"></canvas>
                        </div>
                    </div>

                    <!-- Recent Activity -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Recent Trades -->
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-xl font-semibold mb-4">Recent Trades</h3>
                            <div class="space-y-3">
                                <template x-for="trade in recentTrades" :key="trade.id">
                                    <div class="flex justify-between items-center py-2 border-b border-gray-700">
                                        <div>
                                            <div class="font-medium" x-text="trade.symbol"></div>
                                            <div class="text-sm text-gray-400" x-text="trade.time"></div>
                                        </div>
                                        <div class="text-right">
                                            <div :class="trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'" 
                                                 x-text="trade.side + ' ' + trade.quantity"></div>
                                            <div class="text-sm" x-text="'$' + trade.price.toFixed(2)"></div>
                                        </div>
                                    </div>
                                </template>
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
                </div>

                <!-- Trading Tab -->
                <div x-show="activeTab === 'trading'" class="p-6">
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <!-- Order Form -->
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-xl font-semibold mb-4">Place Order</h3>
                            
                            <form @submit.prevent="placeOrder()" class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium mb-2">Trading Pair</label>
                                    <select x-model="orderForm.symbol" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                        <template x-for="(data, symbol) in allMarketData" :key="symbol">
                                            <option :value="symbol" x-text="symbol"></option>
                                        </template>
                                    </select>
                                </div>
                                
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Order Type</label>
                                        <select x-model="orderForm.type" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                            <option value="market">Market</option>
                                            <option value="limit">Limit</option>
                                            <option value="stop">Stop Loss</option>
                                            <option value="take_profit">Take Profit</option>
                                        </select>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Side</label>
                                        <select x-model="orderForm.side" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                            <option value="BUY">Buy</option>
                                            <option value="SELL">Sell</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium mb-2">Quantity</label>
                                    <input type="number" x-model="orderForm.quantity" step="0.0001" 
                                           class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
                                           placeholder="0.0000">
                                    <div class="text-xs text-gray-400 mt-1">
                                        Max: <span x-text="calculateMaxQuantity()"></span>
                                    </div>
                                </div>
                                
                                <div x-show="orderForm.type !== 'market'">
                                    <label class="block text-sm font-medium mb-2">Price</label>
                                    <input type="number" x-model="orderForm.price" step="0.01" 
                                           class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
                                           placeholder="0.00">
                                </div>
                                
                                <!-- Quick Amount Buttons -->
                                <div class="grid grid-cols-4 gap-2">
                                    <button type="button" @click="setPercentage(25)" class="bg-gray-700 hover:bg-gray-600 py-1 rounded text-sm">25%</button>
                                    <button type="button" @click="setPercentage(50)" class="bg-gray-700 hover:bg-gray-600 py-1 rounded text-sm">50%</button>
                                    <button type="button" @click="setPercentage(75)" class="bg-gray-700 hover:bg-gray-600 py-1 rounded text-sm">75%</button>
                                    <button type="button" @click="setPercentage(100)" class="bg-gray-700 hover:bg-gray-600 py-1 rounded text-sm">100%</button>
                                </div>
                                
                                <div class="flex space-x-2">
                                    <button type="submit" 
                                            :class="orderForm.side === 'BUY' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'"
                                            class="flex-1 py-3 rounded-lg font-medium transition-colors">
                                        <span x-text="orderForm.side === 'BUY' ? 'Place Buy Order' : 'Place Sell Order'"></span>
                                    </button>
                                </div>
                            </form>
                        </div>
                        
                        <!-- Order Book -->
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-xl font-semibold mb-4">Order Book</h3>
                            
                            <!-- Asks (Sell Orders) -->
                            <div class="mb-4">
                                <div class="text-sm text-gray-400 mb-2">Asks (Sellers)</div>
                                <div class="space-y-1">
                                    <template x-for="ask in orderBook.asks" :key="ask.price">
                                        <div class="flex justify-between text-sm">
                                            <span class="text-red-400" x-text="ask.price.toFixed(2)"></span>
                                            <span x-text="ask.quantity.toFixed(4)"></span>
                                        </div>
                                    </template>
                                </div>
                            </div>
                            
                            <!-- Current Price -->
                            <div class="text-center py-2 border-t border-b border-gray-600 mb-4">
                                <div class="text-lg font-bold" x-text="'$' + (allMarketData[selectedPair]?.price || 0).toFixed(2)"></div>
                                <div class="text-sm text-gray-400">Last Price</div>
                            </div>
                            
                            <!-- Bids (Buy Orders) -->
                            <div>
                                <div class="text-sm text-gray-400 mb-2">Bids (Buyers)</div>
                                <div class="space-y-1">
                                    <template x-for="bid in orderBook.bids" :key="bid.price">
                                        <div class="flex justify-between text-sm">
                                            <span class="text-green-400" x-text="bid.price.toFixed(2)"></span>
                                            <span x-text="bid.quantity.toFixed(4)"></span>
                                        </div>
                                    </template>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Trade History -->
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-xl font-semibold mb-4">Recent Trades</h3>
                            <div class="space-y-2">
                                <template x-for="trade in tradeHistory" :key="trade.id">
                                    <div class="flex justify-between items-center text-sm">
                                        <span :class="trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'" 
                                              x-text="trade.price.toFixed(2)"></span>
                                        <span x-text="trade.quantity.toFixed(4)"></span>
                                        <span class="text-gray-400" x-text="trade.time"></span>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Portfolio Tab -->
                <div x-show="activeTab === 'portfolio'" class="p-6">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                        <!-- Portfolio Overview -->
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-xl font-semibold mb-4">Portfolio Overview</h3>
                            <div class="space-y-4">
                                <div class="flex justify-between">
                                    <span>Total Balance:</span>
                                    <span class="font-bold text-2xl" x-text="'$' + (accountBalance || 0).toLocaleString()"></span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Available:</span>
                                    <span class="text-green-400" x-text="'$' + (availableBalance || 0).toLocaleString()"></span>
                                </div>
                                <div class="flex justify-between">
                                    <span>In Orders:</span>
                                    <span class="text-yellow-400" x-text="'$' + (lockedBalance || 0).toLocaleString()"></span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Total PnL:</span>
                                    <span :class="(performance.totalPnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'" 
                                          x-text="'$' + (performance.totalPnl || 0).toFixed(2)"></span>
                                </div>
                            </div>
                        </div>

                        <!-- Asset Allocation -->
                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-xl font-semibold mb-4">Asset Allocation</h3>
                            <div class="chart-container">
                                <canvas id="allocationChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Holdings Table -->
                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                        <h3 class="text-xl font-semibold mb-4">Holdings</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full">
                                <thead>
                                    <tr class="border-b border-gray-700">
                                        <th class="text-left py-3">Asset</th>
                                        <th class="text-left py-3">Balance</th>
                                        <th class="text-left py-3">Value (USD)</th>
                                        <th class="text-left py-3">24h Change</th>
                                        <th class="text-left py-3">Allocation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template x-for="holding in holdings" :key="holding.asset">
                                        <tr class="border-b border-gray-700">
                                            <td class="py-3 font-medium" x-text="holding.asset"></td>
                                            <td class="py-3" x-text="holding.balance.toFixed(4)"></td>
                                            <td class="py-3" x-text="'$' + holding.value.toFixed(2)"></td>
                                            <td class="py-3" :class="holding.change >= 0 ? 'text-green-400' : 'text-red-400'"
                                                x-text="(holding.change >= 0 ? '+' : '') + holding.change.toFixed(2) + '%'"></td>
                                            <td class="py-3" x-text="holding.allocation.toFixed(1) + '%'"></td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Strategies Tab -->
                <div x-show="activeTab === 'strategies'" class="p-6">
                    <div class="mb-6 flex justify-between items-center">
                        <h2 class="text-2xl font-bold">Trading Strategies</h2>
                        <button @click="showAddStrategy = true" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg">
                            + Add Strategy
                        </button>
                    </div>

                    <!-- Strategy Cards -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                        <template x-for="strategy in allStrategies" :key="strategy.id">
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                                <div class="flex justify-between items-center mb-4">
                                    <h3 class="text-lg font-semibold" x-text="strategy.name"></h3>
                                    <button @click="toggleStrategy(strategy.id)" 
                                            :class="strategy.enabled ? 'bg-green-600' : 'bg-gray-600'"
                                            class="w-12 h-6 rounded-full relative transition-colors">
                                        <div :class="strategy.enabled ? 'translate-x-6' : 'translate-x-0'"
                                             class="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5 transition-transform"></div>
                                    </button>
                                </div>
                                
                                <p class="text-gray-400 text-sm mb-4" x-text="strategy.description"></p>
                                
                                <div class="space-y-2 text-sm">
                                    <div class="flex justify-between">
                                        <span>Type:</span>
                                        <span x-text="strategy.type"></span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span>Risk Level:</span>
                                        <span :class="strategy.riskLevel === 'Low' ? 'text-green-400' : strategy.riskLevel === 'Medium' ? 'text-yellow-400' : 'text-red-400'"
                                              x-text="strategy.riskLevel"></span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span>Performance:</span>
                                        <span :class="(strategy.performance?.totalReturn || 0) >= 0 ? 'text-green-400' : 'text-red-400'"
                                              x-text="((strategy.performance?.totalReturn || 0) >= 0 ? '+' : '') + (strategy.performance?.totalReturn || 0).toFixed(2) + '%'"></span>
                                    </div>
                                </div>
                                
                                <div class="mt-4 flex space-x-2">
                                    <button @click="configureStrategy(strategy)" 
                                            class="flex-1 bg-blue-600 hover:bg-blue-700 py-2 rounded text-sm">
                                        Configure
                                    </button>
                                    <button @click="viewStrategyDetails(strategy)" 
                                            class="flex-1 bg-gray-600 hover:bg-gray-700 py-2 rounded text-sm">
                                        Details
                                    </button>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Settings Tab -->
                <div x-show="activeTab === 'settings'" class="p-6">
                    <div class="max-w-4xl mx-auto">
                        <h2 class="text-2xl font-bold mb-6">Settings</h2>
                        
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <!-- Bot Configuration -->
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                                <h3 class="text-xl font-semibold mb-4">Bot Configuration</h3>
                                
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Trading Mode</label>
                                        <select x-model="settings.tradingMode" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                            <option value="live">Live Trading</option>
                                            <option value="paper">Paper Trading</option>
                                            <option value="backtest">Backtest Only</option>
                                        </select>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Max Position Size (%)</label>
                                        <input type="number" x-model="settings.maxPositionSize" min="1" max="100" 
                                               class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Stop Loss (%)</label>
                                        <input type="number" x-model="settings.stopLoss" min="0.1" max="50" step="0.1"
                                               class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Take Profit (%)</label>
                                        <input type="number" x-model="settings.takeProfit" min="0.1" max="100" step="0.1"
                                               class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Risk Management</label>
                                        <select x-model="settings.riskLevel" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                            <option value="conservative">Conservative</option>
                                            <option value="moderate">Moderate</option>
                                            <option value="aggressive">Aggressive</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- API Configuration -->
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                                <h3 class="text-xl font-semibold mb-4">API Configuration</h3>
                                
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Exchange</label>
                                        <select x-model="settings.exchange" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                                            <option value="crypto_com">Crypto.com</option>
                                            <option value="binance">Binance</option>
                                            <option value="coinbase">Coinbase Pro</option>
                                            <option value="kraken">Kraken</option>
                                            <option value="ftx">FTX</option>
                                        </select>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">API Key</label>
                                        <input type="password" x-model="settings.apiKey" 
                                               class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
                                               placeholder="Enter API key">
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">API Secret</label>
                                        <input type="password" x-model="settings.apiSecret" 
                                               class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
                                               placeholder="Enter API secret">
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium mb-2">Sandbox Mode</label>
                                        <label class="flex items-center">
                                            <input type="checkbox" x-model="settings.sandboxMode" 
                                                   class="mr-2 bg-gray-700 border border-gray-600 rounded">
                                            <span class="text-sm">Use sandbox/testnet environment</span>
                                        </label>
                                    </div>
                                    
                                    <button @click="testConnection()" 
                                            class="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg font-medium transition-colors">
                                        Test Connection
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Notification Settings -->
                        <div class="mt-8 bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h3 class="text-xl font-semibold mb-4">Notification Settings</h3>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div class="space-y-4">
                                    <div class="flex items-center justify-between">
                                        <span>Trade Notifications</span>
                                        <input type="checkbox" x-model="settings.notifications.trades" 
                                               class="bg-gray-700 border border-gray-600 rounded">
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <span>PnL Alerts</span>
                                        <input type="checkbox" x-model="settings.notifications.pnl" 
                                               class="bg-gray-700 border border-gray-600 rounded">
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <span>Strategy Performance</span>
                                        <input type="checkbox" x-model="settings.notifications.strategies" 
                                               class="bg-gray-700 border border-gray-600 rounded">
                                    </div>
                                </div>
                                
                                <div class="space-y-4">
                                    <div class="flex items-center justify-between">
                                        <span>Error Alerts</span>
                                        <input type="checkbox" x-model="settings.notifications.errors" 
                                               class="bg-gray-700 border border-gray-600 rounded">
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <span>Market Updates</span>
                                        <input type="checkbox" x-model="settings.notifications.market" 
                                               class="bg-gray-700 border border-gray-600 rounded">
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <span>Daily Reports</span>
                                        <input type="checkbox" x-model="settings.notifications.reports" 
                                               class="bg-gray-700 border border-gray-600 rounded">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-8 flex justify-end space-x-4">
                            <button @click="resetSettings()" 
                                    class="px-6 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg font-medium transition-colors">
                                Reset to Defaults
                            </button>
                            <button @click="saveSettings()" 
                                    class="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors">
                                Save Settings
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function tradingApp() {
            return {
                activeTab: 'dashboard',
                selectedPair: 'BTCUSD-PERP',
                timeframe: '1h',
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
                lockedBalance: 5000,
                
                // Market Data
                allMarketData: {
                    'BTCUSD-PERP': { price: 100000, change: 2.5, volume: 1234567 },
                    'ETHUSD-PERP': { price: 2630, change: -1.2, volume: 987654 },
                    'ADAUSD-PERP': { price: 0.45, change: 3.1, volume: 456789 },
                    'SOLUSD-PERP': { price: 185.50, change: -0.8, volume: 234567 },
                    'DOTUSD-PERP': { price: 7.25, change: 1.5, volume: 123456 },
                    'LINKUSD-PERP': { price: 15.80, change: -2.1, volume: 789012 },
                    'AVAXUSD-PERP': { price: 42.30, change: 4.2, volume: 345678 },
                    'MATICUSD-PERP': { price: 0.85, change: 0.7, volume: 567890 }
                },
                
                // Trading Data
                strategies: [],
                positions: {},
                orderForm: {
                    symbol: 'BTCUSD-PERP',
                    type: 'market',
                    side: 'BUY',
                    quantity: 0,
                    price: 0
                },
                
                // Order Book
                orderBook: {
                    asks: [
                        { price: 100050, quantity: 0.5 },
                        { price: 100025, quantity: 1.2 },
                        { price: 100010, quantity: 2.1 }
                    ],
                    bids: [
                        { price: 99990, quantity: 1.8 },
                        { price: 99975, quantity: 0.9 },
                        { price: 99950, quantity: 2.5 }
                    ]
                },
                
                // Recent Activity
                recentTrades: [
                    { id: 1, symbol: 'BTCUSD-PERP', side: 'BUY', quantity: 0.1, price: 100000, time: '14:30:25' },
                    { id: 2, symbol: 'ETHUSD-PERP', side: 'SELL', quantity: 2.5, price: 2630, time: '14:28:15' },
                    { id: 3, symbol: 'ADAUSD-PERP', side: 'BUY', quantity: 1000, price: 0.45, time: '14:25:10' }
                ],
                
                tradeHistory: [
                    { id: 1, side: 'BUY', price: 100000, quantity: 0.1, time: '14:30' },
                    { id: 2, side: 'SELL', price: 99995, quantity: 0.2, time: '14:29' },
                    { id: 3, side: 'BUY', price: 99990, quantity: 0.15, time: '14:28' }
                ],
                
                // Portfolio
                holdings: [
                    { asset: 'USD', balance: 45000, value: 45000, change: 0, allocation: 90 },
                    { asset: 'BTC', balance: 0.05, value: 5000, change: 2.5, allocation: 10 }
                ],
                
                // Strategies
                allStrategies: [
                    {
                        id: 1,
                        name: 'RSI Strategy',
                        description: 'Buy when RSI < 30, sell when RSI > 70',
                        type: 'Technical Analysis',
                        riskLevel: 'Medium',
                        enabled: true,
                        performance: { totalReturn: 12.5, trades: 45, winRate: 68 }
                    },
                    {
                        id: 2,
                        name: 'Moving Average Crossover',
                        description: 'EMA 20/50 crossover strategy',
                        type: 'Trend Following',
                        riskLevel: 'Low',
                        enabled: false,
                        performance: { totalReturn: 8.3, trades: 23, winRate: 74 }
                    },
                    {
                        id: 3,
                        name: 'Bollinger Bands',
                        description: 'Mean reversion using Bollinger Bands',
                        type: 'Mean Reversion',
                        riskLevel: 'High',
                        enabled: false,
                        performance: { totalReturn: -2.1, trades: 67, winRate: 45 }
                    }
                ],
                
                // Settings
                settings: {
                    tradingMode: 'paper',
                    maxPositionSize: 10,
                    stopLoss: 2.0,
                    takeProfit: 5.0,
                    riskLevel: 'moderate',
                    apiKey: '',
                    apiSecret: '',
                    exchange: 'crypto_com',
                    sandboxMode: true,
                    notifications: {
                        trades: true,
                        pnl: true,
                        strategies: false,
                        errors: true,
                        market: false,
                        reports: true
                    }
                },
                
                socket: null,
                priceChart: null,
                allocationChart: null,

                init() {
                    this.connectWebSocket();
                    this.loadInitialData();
                    this.initCharts();
                },

                connectWebSocket() {
                    this.socket = io();
                    
                    this.socket.on('connect', () => {
                        console.log('Connected to server');
                    });
                    
                    this.socket.on('bot_status', (data) => {
                        this.performance = { ...this.performance, ...data };
                        this.botStatus = data.running ? 'running' : 'stopped';
                    });
                    
                    this.socket.on('strategies_update', (data) => {
                        this.strategies = data;
                    });
                    
                    this.socket.on('positions_update', (data) => {
                        this.positions = data;
                    });
                    
                    this.socket.on('market_data', (data) => {
                        this.allMarketData = { ...this.allMarketData, ...data };
                        this.updatePriceChart();
                    });
                },

                async loadInitialData() {
                    try {
                        // Load real bot status and performance
                        const statusResponse = await fetch('/api/status');
                        if (statusResponse.ok) {
                            const status = await statusResponse.json();
                            this.performance = {
                                totalPnl: status.totalPnl || 0,
                                totalTrades: status.totalTrades || 0,
                                winRate: status.winRate || 0,
                                openPositions: status.openPositions || 0,
                                dailyVolume: status.dailyVolume || 0,
                                running: status.running || false
                            };
                            
                            // Update account balance with real data
                            this.accountBalance = status.accountBalance || 0;
                            this.availableBalance = status.availableBalance || 0;
                            this.lockedBalance = this.accountBalance - this.availableBalance;
                            
                            this.botStatus = status.running ? 'running' : 'stopped';
                        }
                        
                        // Load real market data
                        const marketResponse = await fetch('/api/market-data/all');
                        if (marketResponse.ok) {
                            const marketResult = await marketResponse.json();
                            if (marketResult.status === 'success') {
                                this.allMarketData = marketResult.data;
                            }
                        }
                        
                        // Load real account holdings
                        const holdingsResponse = await fetch('/api/account/holdings');
                        if (holdingsResponse.ok) {
                            const holdingsResult = await holdingsResponse.json();
                            if (holdingsResult.status === 'success') {
                                this.holdings = holdingsResult.holdings;
                                // Update allocation chart with real data
                                if (this.allocationChart) {
                                    this.allocationChart.data.labels = this.holdings.map(h => h.asset);
                                    this.allocationChart.data.datasets[0].data = this.holdings.map(h => h.allocation);
                                    this.allocationChart.update('none');
                                }
                            }
                        }
                        
                        // Load strategies
                        const strategiesResponse = await fetch('/api/strategies');
                        if (strategiesResponse.ok) {
                            this.strategies = await strategiesResponse.json();
                        }
                        
                        // Load positions
                        const positionsResponse = await fetch('/api/positions');
                        if (positionsResponse.ok) {
                            this.positions = await positionsResponse.json();
                        }
                        
                    } catch (error) {
                        console.error('Error loading data:', error);
                        // Keep demo data as fallback
                        console.log('Using demo data as fallback');
                    }
                },

initCharts() {
                    // Add delay to ensure DOM is ready
                    setTimeout(() => {
                        // Price Chart
                        const priceCtx = document.getElementById('priceChart');
                        if (priceCtx) {
                            try {
                                // Destroy existing chart if it exists
                                if (this.priceChart) {
                                    this.priceChart.destroy();
                                }
                                
                                this.priceChart = new Chart(priceCtx, {
                                    type: 'line',
                                    data: {
                                        labels: [],
                                        datasets: [{
                                            label: 'Price',
                                            data: [],
                                            borderColor: '#3B82F6',
                                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                            fill: true,
                                            tension: 0.1
                                        }]
                                    },
                                    options: {
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        animation: false, // Disable animations to prevent stack overflow
                                        interaction: {
                                            intersect: false,
                                            mode: 'index'
                                        },
                                        plugins: {
                                            legend: { display: false }
                                        },
                                        scales: {
                                            x: { 
                                                grid: { color: '#374151' },
                                                ticks: { color: '#9CA3AF' }
                                            },
                                            y: { 
                                                grid: { color: '#374151' },
                                                ticks: { color: '#9CA3AF' }
                                            }
                                        }
                                    }
                                });
                                this.updatePriceChart();
                            } catch (error) {
                                console.error('Price chart initialization error:', error);
                            }
                        }

                        // Allocation Chart
                        const allocationCtx = document.getElementById('allocationChart');
                        if (allocationCtx) {
                            try {
                                // Destroy existing chart if it exists
                                if (this.allocationChart) {
                                    this.allocationChart.destroy();
                                }
                                
                                this.allocationChart = new Chart(allocationCtx, {
                                    type: 'doughnut',
                                    data: {
                                        labels: this.holdings.map(h => h.asset),
                                        datasets: [{
                                            data: this.holdings.map(h => h.allocation),
                                            backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
                                        }]
                                    },
                                    options: {
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        animation: false, // Disable animations
                                        plugins: {
                                            legend: { 
                                                position: 'bottom',
                                                labels: { color: '#9CA3AF' }
                                            }
                                        }
                                    }
                                });
                            } catch (error) {
                                console.error('Allocation chart initialization error:', error);
                            }
                        }
                    }, 100);
                },

                updatePriceChart() {
                    if (!this.priceChart) return;
                    
                    try {
                        // Generate sample price data
                        const now = new Date();
                        const labels = [];
                        const data = [];
                        const basePrice = this.allMarketData[this.selectedPair]?.price || 100000;
                        
                        for (let i = 23; i >= 0; i--) {
                            const time = new Date(now - i * 60 * 60 * 1000);
                            labels.push(time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
                            data.push(basePrice + (Math.random() - 0.5) * 1000);
                        }
                        
                        // Update chart data without animation
                        this.priceChart.data.labels = labels;
                        this.priceChart.data.datasets[0].data = data;
                        this.priceChart.update('none'); // 'none' disables all animations
                    } catch (error) {
                        console.error('Chart update error:', error);
                        // If chart update fails, try to recreate it
                        setTimeout(() => {
                            if (this.priceChart) {
                                this.priceChart.destroy();
                                this.priceChart = null;
                            }
                            this.initCharts();
                        }, 1000);
                    }
                },



                selectPair(symbol) {
                    this.selectedPair = symbol;
                    this.orderForm.symbol = symbol;
                    this.updatePriceChart();
                },

                changeTimeframe(tf) {
                    this.timeframe = tf;
                    this.updatePriceChart();
                },

                calculateMaxQuantity() {
                    const price = this.allMarketData[this.orderForm.symbol]?.price || 0;
                    if (price === 0) return '0.0000';
                    return (this.availableBalance / price).toFixed(4);
                },

                setPercentage(percent) {
                    const maxQty = parseFloat(this.calculateMaxQuantity());
                    this.orderForm.quantity = (maxQty * percent / 100).toFixed(4);
                },

                async toggleBot() {
                    try {
                        const endpoint = this.botStatus === 'running' ? '/api/stop' : '/api/start';
                        const response = await fetch(endpoint, { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            this.botStatus = this.botStatus === 'running' ? 'stopped' : 'running';
                        }
                    } catch (error) {
                        console.error('Error toggling bot:', error);
                    }
                },

                async placeOrder() {
                    try {
                        const response = await fetch('/api/orders', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(this.orderForm)
                        });
                        
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            alert('Order placed successfully!');
                            this.orderForm.quantity = 0;
                            this.orderForm.price = 0;
                        } else {
                            alert('Error placing order: ' + result.message);
                        }
                    } catch (error) {
                        console.error('Error placing order:', error);
                        alert('Error placing order: ' + error.message);
                    }
                },

                async toggleStrategy(strategyId) {
                    const strategy = this.allStrategies.find(s => s.id === strategyId);
                    if (strategy) {
                        strategy.enabled = !strategy.enabled;
                        
                        try {
                            const endpoint = strategy.enabled ? '/api/strategies/enable' : '/api/strategies/disable';
                            await fetch(endpoint, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ strategy_id: strategyId })
                            });
                        } catch (error) {
                            console.error('Error toggling strategy:', error);
                        }
                    }
                },

                configureStrategy(strategy) {
                    alert('Configure strategy: ' + strategy.name);
                },

                viewStrategyDetails(strategy) {
                    alert('Strategy details: ' + strategy.name);
                },

                async testConnection() {
                    try {
                        const response = await fetch('/api/test-connection', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                apiKey: this.settings.apiKey,
                                apiSecret: this.settings.apiSecret,
                                exchange: this.settings.exchange
                            })
                        });
                        
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            alert('Connection successful!');
                        } else {
                            alert('Connection failed: ' + result.message);
                        }
                    } catch (error) {
                        alert('Connection test failed: ' + error.message);
                    }
                },

                async saveSettings() {
                    try {
                        const response = await fetch('/api/config', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(this.settings)
                        });
                        
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            alert('Settings saved successfully!');
                        } else {
                            alert('Error saving settings: ' + result.message);
                        }
                    } catch (error) {
                        console.error('Error saving settings:', error);
                    }
                },

                resetSettings() {
                    if (!confirm('Reset all settings to defaults?')) return;
                    
                    this.settings = {
                        tradingMode: 'paper',
                        maxPositionSize: 10,
                        stopLoss: 2.0,
                        takeProfit: 5.0,
                        riskLevel: 'moderate',
                        apiKey: '',
                        apiSecret: '',
                        exchange: 'crypto_com',
                        sandboxMode: true,
                        notifications: {
                            trades: true,
                            pnl: true,
                            strategies: false,
                            errors: true,
                            market: false,
                            reports: true
                        }
                    };
                }
            }
        }
    </script>
</body>
</html>
    """