#!/usr/bin/env python3
"""
CryptoBot Pro - Main Application Entry Point
Advanced cryptocurrency trading bot with machine learning and risk management.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# DO NOT add app directory to Python path - use proper imports instead
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))  # ❌ REMOVE THIS

from app.web.app import create_app
from app.core.bot import TradingBot
from app.utils.config import Config
from app.utils.logger import setup_logging

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='CryptoBot Pro Trading Bot')
    parser.add_argument('--config', '-c', 
                       default='config/config.yaml',
                       help='Configuration file path')
    parser.add_argument('--debug', '-d', 
                       action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--port', '-p', 
                       type=int, default=5000,
                       help='Web interface port')
    parser.add_argument('--host', 
                       default='0.0.0.0',
                       help='Web interface host')
    parser.add_argument('--no-web', 
                       action='store_true',
                       help='Run bot without web interface')
    return parser.parse_args()

def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting CryptoBot Pro...")
    
    try:
        # Load configuration
        config = Config(args.config)
        
        # Initialize trading bot
        bot = TradingBot(config)
        
        # Create Flask app with bot instance
        app = create_app(config, bot)
        
        # Start the bot
        bot.start()
        
        if not args.no_web:
            logger.info(f"Starting web interface on http://{args.host}:{args.port}")
            app.run(host=args.host, port=args.port, debug=args.debug)
        else:
            logger.info("Running in headless mode (no web interface)")
            # Keep the bot running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        if 'bot' in locals():
            bot.stop()
        logger.info("CryptoBot Pro stopped.")

if __name__ == "__main__":
    main()