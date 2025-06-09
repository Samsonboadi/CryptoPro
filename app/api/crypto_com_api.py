"""
Crypto.com Exchange API Client
Handles authentication, REST requests, and WebSocket connections.
"""

import hmac
import hashlib
import time
import json
import requests
import websocket
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"

class TimeInForce(Enum):
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"
    FILL_OR_KILL = "FILL_OR_KILL"

@dataclass
class OrderRequest:
    instrument_name: str
    side: OrderSide
    order_type: OrderType
    quantity: str
    price: Optional[str] = None
    client_oid: Optional[str] = None
    time_in_force: Optional[TimeInForce] = None

class CryptoComAPI:
    """Crypto.com Exchange API Client"""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.sandbox = sandbox
        
        # API Endpoints
        if sandbox:
            self.rest_url = "https://uat-api.3ona.co/exchange/v1"
            self.ws_user_url = "wss://uat-stream.3ona.co/exchange/v1/user"
            self.ws_market_url = "wss://uat-stream.3ona.co/exchange/v1/market"
        else:
            self.rest_url = "https://api.crypto.com/exchange/v1"
            self.ws_user_url = "wss://stream.crypto.com/exchange/v1/user"
            self.ws_market_url = "wss://stream.crypto.com/exchange/v1/market"
        
        self.ws_user = None
        self.ws_market = None
        self.request_id = 1
        self._session = requests.Session()
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests
    
    def _generate_signature(self, method: str, params: Dict) -> str:
        """Generate HMAC-SHA256 signature for authenticated requests"""
        param_str = ""
        if params:
            param_str = self._params_to_str(params, 0)
        
        nonce = int(time.time() * 1000)
        payload_str = f"{method}{self.request_id}{self.api_key}{param_str}{nonce}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, nonce
    
    def _params_to_str(self, obj, level, max_level=3):
        """Convert parameters to string for signature generation"""
        if level >= max_level:
            return str(obj)
        
        return_str = ""
        for key in sorted(obj):
            return_str += key
            if obj[key] is None:
                return_str += 'null'
            elif isinstance(obj[key], list):
                for sub_obj in obj[key]:
                    return_str += self._params_to_str(sub_obj, level + 1, max_level)
            else:
                return_str += str(obj[key])
        return return_str
    
    def _rate_limit(self):
        """Implement rate limiting"""
        now = time.time()
        time_since_last = now - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = time.time()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, auth: bool = False) -> Dict:
        """Make REST API request"""
        self._rate_limit()
        
        url = f"{self.rest_url}/{endpoint}"
        
        payload = {
            "id": self.request_id,
            "method": method
        }
        
        if params:
            payload["params"] = params
        
        if auth:
            payload["api_key"] = self.api_key
            signature, nonce = self._generate_signature(method, params or {})
            payload["sig"] = signature
            payload["nonce"] = nonce
        
        self.request_id += 1
        
        try:
            if method.startswith("public/"):
                # GET request for public endpoints
                response = self._session.get(url, params=payload.get("params", {}))
            else:
                # POST request for private endpoints
                response = self._session.post(
                    url, 
                    json=payload, 
                    headers={"Content-Type": "application/json"}
                )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                logger.warning(f"API warning: {result.get('message', 'Unknown error')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    # Market Data Methods
    def get_instruments(self) -> Dict:
        """Get all available trading instruments"""
        return self._make_request("public/get-instruments", "public/get-instruments")
    
    def get_ticker(self, instrument_name: str = None) -> Dict:
        """Get ticker information"""
        params = {"instrument_name": instrument_name} if instrument_name else {}
        return self._make_request("public/get-tickers", "public/get-tickers", params)
    
    def get_orderbook(self, instrument_name: str, depth: int = 10) -> Dict:
        """Get order book for instrument"""
        params = {"instrument_name": instrument_name, "depth": str(depth)}
        return self._make_request("public/get-book", "public/get-book", params)
    
    def get_trades(self, instrument_name: str, count: int = 25) -> Dict:
        """Get recent trades for instrument"""
        params = {"instrument_name": instrument_name, "count": count}
        return self._make_request("public/get-trades", "public/get-trades", params)
    
    def get_candlestick(self, instrument_name: str, timeframe: str = "1m", count: int = 25) -> Dict:
        """Get candlestick data"""
        params = {
            "instrument_name": instrument_name,
            "timeframe": timeframe,
            "count": count
        }
        return self._make_request("public/get-candlestick", "public/get-candlestick", params)
    
    # Account Methods (Authenticated)
    def get_balance(self) -> Dict:
        """Get account balance"""
        return self._make_request("private/user-balance", "private/user-balance", {}, auth=True)
    
    def get_positions(self, instrument_name: str = None) -> Dict:
        """Get positions"""
        params = {"instrument_name": instrument_name} if instrument_name else {}
        return self._make_request("private/get-positions", "private/get-positions", params, auth=True)
    
    def get_open_orders(self, instrument_name: str = None) -> Dict:
        """Get open orders"""
        params = {"instrument_name": instrument_name} if instrument_name else {}
        return self._make_request("private/get-open-orders", "private/get-open-orders", params, auth=True)
    
    # Trading Methods (Authenticated)
    def create_order(self, order: OrderRequest) -> Dict:
        """Create a new order"""
        params = {
            "instrument_name": order.instrument_name,
            "side": order.side.value,
            "type": order.order_type.value,
            "quantity": order.quantity
        }
        
        if order.price:
            params["price"] = order.price
        if order.client_oid:
            params["client_oid"] = order.client_oid
        if order.time_in_force:
            params["time_in_force"] = order.time_in_force.value
        
        return self._make_request("private/create-order", "private/create-order", params, auth=True)
    
    def cancel_order(self, order_id: str = None, client_oid: str = None) -> Dict:
        """Cancel an order"""
        params = {}
        if order_id:
            params["order_id"] = order_id
        if client_oid:
            params["client_oid"] = client_oid
        
        return self._make_request("private/cancel-order", "private/cancel-order", params, auth=True)
    
    def cancel_all_orders(self, instrument_name: str = None) -> Dict:
        """Cancel all orders for instrument"""
        params = {"instrument_name": instrument_name} if instrument_name else {}
        return self._make_request("private/cancel-all-orders", "private/cancel-all-orders", params, auth=True)
    
    def get_order_detail(self, order_id: str = None, client_oid: str = None) -> Dict:
        """Get order details"""
        params = {}
        if order_id:
            params["order_id"] = order_id
        if client_oid:
            params["client_oid"] = client_oid
        
        return self._make_request("private/get-order-detail", "private/get-order-detail", params, auth=True)
    
    def close(self):
        """Close API connections"""
        if self.ws_user:
            self.ws_user.close()
        if self.ws_market:
            self.ws_market.close()
        self._session.close()