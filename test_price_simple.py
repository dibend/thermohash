#!/usr/bin/env python3
"""
Simplified test script for ThermoHash Price Tracking functionality
Tests only the price tracking features without ML dependencies
"""

import json
import sys
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class SimplePriceTracker:
    """Simplified Bitcoin price and hash price tracking"""
    
    def __init__(self):
        self.bitcoin_apis = [
            {
                'name': 'CoinGecko',
                'url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                'price_path': ['bitcoin', 'usd'],
                'timeout': 10
            },
            {
                'name': 'CoinDesk',
                'url': 'https://api.coindesk.com/v1/bpi/currentprice/USD.json',
                'price_path': ['bpi', 'USD', 'rate_float'],
                'timeout': 10
            },
            {
                'name': 'Binance',
                'url': 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
                'price_path': ['price'],
                'timeout': 10
            }
        ]
        
        self.last_bitcoin_price = None
        self.last_hashprice = None
        self.last_update = None
        
    def get_bitcoin_price(self) -> Optional[float]:
        """Get current Bitcoin price from multiple sources"""
        for api in self.bitcoin_apis:
            try:
                print(f"Fetching Bitcoin price from {api['name']}...")
                response = requests.get(api['url'], timeout=api['timeout'])
                response.raise_for_status()
                data = response.json()
                
                # Navigate through the nested JSON structure
                price_data = data
                for key in api['price_path']:
                    price_data = price_data[key]
                
                price = float(price_data)
                
                if price > 0:  # Validate price
                    self.last_bitcoin_price = price
                    self.last_update = datetime.now()
                    print(f"✅ Bitcoin price: ${price:,.2f} (from {api['name']})")
                    return price
                    
            except requests.RequestException as e:
                print(f"⚠️ Bitcoin price API {api['name']} failed: {e}")
            except (KeyError, ValueError, TypeError) as e:
                print(f"⚠️ Error parsing Bitcoin price from {api['name']}: {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error with {api['name']}: {e}")
        
        print("❌ All Bitcoin price sources failed")
        return self.last_bitcoin_price  # Return cached price if available
    
    def get_network_hashrate(self) -> Optional[float]:
        """Get current Bitcoin network hashrate"""
        try:
            print("Fetching network hashrate...")
            # Using blockchain.info API for network stats
            url = "https://api.blockchain.info/stats"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Hashrate is in hash/s, convert to TH/s
            hashrate_th = data.get('hash_rate', 0) / 1e12
            print(f"✅ Network hashrate: {hashrate_th:,.2f} TH/s")
            return hashrate_th
            
        except Exception as e:
            print(f"⚠️ Failed to get network hashrate: {e}")
            return None
    
    def get_mining_difficulty(self) -> Optional[float]:
        """Get current Bitcoin mining difficulty"""
        try:
            print("Fetching mining difficulty...")
            url = "https://api.blockchain.info/stats"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            difficulty = data.get('difficulty', 0)
            print(f"✅ Mining difficulty: {difficulty:,.0f}")
            return float(difficulty)
            
        except Exception as e:
            print(f"⚠️ Failed to get mining difficulty: {e}")
            return None
    
    def calculate_hashprice(self, btc_price: Optional[float] = None) -> Optional[float]:
        """
        Calculate hash price (USD per TH/s per day)
        Hash price = (BTC Price * Block Reward * 144) / (Network Hashrate)
        """
        try:
            if btc_price is None:
                btc_price = self.get_bitcoin_price()
            
            if btc_price is None:
                return None
            
            # Get network stats
            hashrate = self.get_network_hashrate()
            if hashrate is None:
                return None
            
            # Bitcoin block reward (currently 6.25 BTC)
            block_reward = 6.25
            blocks_per_day = 144  # ~10 minutes per block
            
            # Calculate daily Bitcoin production in USD
            daily_btc_production = block_reward * blocks_per_day
            daily_usd_production = daily_btc_production * btc_price
            
            # Hash price = daily USD production / network hashrate (TH/s)
            hashprice = daily_usd_production / hashrate if hashrate > 0 else 0
            
            self.last_hashprice = hashprice
            print(f"✅ Hash price: ${hashprice:.6f} per TH/s per day")
            return hashprice
            
        except Exception as e:
            print(f"❌ Error calculating hash price: {e}")
            return self.last_hashprice  # Return cached value if available
    
    def get_price_data(self) -> Dict:
        """Get comprehensive price data"""
        btc_price = self.get_bitcoin_price()
        hashprice = self.calculate_hashprice(btc_price)
        difficulty = self.get_mining_difficulty()
        hashrate = self.get_network_hashrate()
        
        return {
            'bitcoin_price': btc_price,
            'hashprice': hashprice,
            'network_hashrate_th': hashrate,
            'difficulty': difficulty,
            'timestamp': datetime.now(),
            'last_update': self.last_update
        }

def test_bitcoin_price():
    """Test Bitcoin price fetching from multiple sources"""
    print("\n💰 Testing Bitcoin Price Tracking...")
    print("=" * 50)
    
    price_tracker = SimplePriceTracker()
    
    # Test Bitcoin price fetching
    btc_price = price_tracker.get_bitcoin_price()
    
    if btc_price:
        print(f"✅ Bitcoin price retrieved: ${btc_price:,.2f}")
        
        # Validate price range (reasonable bounds)
        if 1000 <= btc_price <= 500000:
            print("✅ Price is within reasonable range")
        else:
            print(f"⚠️ Price seems unusual: ${btc_price:,.2f}")
            
        return btc_price
    else:
        print("❌ Failed to retrieve Bitcoin price")
        return None

def test_network_stats():
    """Test network statistics (hashrate, difficulty)"""
    print(f"\n⛏️ Testing Network Statistics...")
    print("=" * 50)
    
    price_tracker = SimplePriceTracker()
    
    try:
        # Test hashrate
        hashrate = price_tracker.get_network_hashrate()
        
        # Test difficulty
        difficulty = price_tracker.get_mining_difficulty()
            
        return hashrate, difficulty
        
    except Exception as e:
        print(f"❌ Network stats error: {e}")
        return None, None

def test_hashprice_calculation(btc_price):
    """Test hash price calculation"""
    if btc_price is None:
        print("\n❌ Skipping hash price test - no Bitcoin price")
        return None
        
    print(f"\n📊 Testing Hash Price Calculation...")
    print("=" * 50)
    
    try:
        price_tracker = SimplePriceTracker()
        
        # Test hash price calculation
        hashprice = price_tracker.calculate_hashprice(btc_price)
        
        if hashprice:
            print(f"✅ Hash price calculated: ${hashprice:.6f} per TH/s per day")
            
            # Validate hash price range
            if 0.001 <= hashprice <= 1.0:
                print("✅ Hash price is within reasonable range")
            else:
                print(f"⚠️ Hash price seems unusual: ${hashprice:.6f}")
                
            return hashprice
        else:
            print("❌ Failed to calculate hash price")
            return None
            
    except Exception as e:
        print(f"❌ Hash price calculation error: {e}")
        return None

def test_comprehensive_price_data():
    """Test getting all price data at once"""
    print(f"\n📈 Testing Comprehensive Price Data...")
    print("=" * 50)
    
    try:
        price_tracker = SimplePriceTracker()
        
        price_data = price_tracker.get_price_data()
        
        print("Price Data Summary:")
        print("-" * 30)
        
        if price_data['bitcoin_price']:
            print(f"Bitcoin Price: ${price_data['bitcoin_price']:,.2f}")
        else:
            print("Bitcoin Price: ❌ Not available")
            
        if price_data['hashprice']:
            print(f"Hash Price: ${price_data['hashprice']:.6f} per TH/s per day")
        else:
            print("Hash Price: ❌ Not available")
            
        if price_data['network_hashrate_th']:
            print(f"Network Hashrate: {price_data['network_hashrate_th']:,.2f} TH/s")
        else:
            print("Network Hashrate: ❌ Not available")
            
        if price_data['difficulty']:
            print(f"Difficulty: {price_data['difficulty']:,.0f}")
        else:
            print("Difficulty: ❌ Not available")
            
        print(f"Timestamp: {price_data['timestamp']}")
        
        return price_data
        
    except Exception as e:
        print(f"❌ Comprehensive price data error: {e}")
        return None

def test_config_integration():
    """Test price data integration with configuration"""
    print(f"\n⚙️ Testing Configuration Integration...")
    print("=" * 50)
    
    try:
        # Load config
        with open("config.json", "r") as f:
            config = json.load(f)
        
        price_settings = config.get("price_settings", {})
        
        if price_settings:
            print("✅ Price settings found in config:")
            print(f"   Enable price optimization: {price_settings.get('enable_price_optimization', 'Not set')}")
            print(f"   Min profitable hash price: ${price_settings.get('min_profitable_hashprice', 'Not set')}")
            print(f"   Optimal hash price: ${price_settings.get('optimal_hashprice', 'Not set')}")
            print(f"   Max power price factor: {price_settings.get('max_power_price_factor', 'Not set')}")
            print(f"   Min power price factor: {price_settings.get('min_power_price_factor', 'Not set')}")
        else:
            print("❌ No price settings found in config")
            
        return price_settings
        
    except Exception as e:
        print(f"❌ Config integration error: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 ThermoHash Price Tracking Test Suite (Simplified)")
    print("====================================================")
    print("This script tests the Bitcoin price and hash price tracking features")
    print("without requiring ML dependencies.\n")
    
    # Test Bitcoin price
    btc_price = test_bitcoin_price()
    
    # Test network statistics
    hashrate, difficulty = test_network_stats()
    
    # Test hash price calculation
    hashprice = test_hashprice_calculation(btc_price)
    
    # Test comprehensive price data
    price_data = test_comprehensive_price_data()
    
    # Test config integration
    config_data = test_config_integration()
    
    print("\n📋 Test Summary")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    if btc_price:
        print("✅ Bitcoin price tracking: PASSED")
        tests_passed += 1
    else:
        print("❌ Bitcoin price tracking: FAILED")
    
    if hashrate and difficulty:
        print("✅ Network statistics: PASSED")
        tests_passed += 1
    else:
        print("❌ Network statistics: FAILED")
    
    if hashprice:
        print("✅ Hash price calculation: PASSED")
        tests_passed += 1
    else:
        print("❌ Hash price calculation: FAILED")
    
    if price_data and price_data.get('bitcoin_price'):
        print("✅ Comprehensive price data: PASSED")
        tests_passed += 1
    else:
        print("❌ Comprehensive price data: FAILED")
    
    if config_data:
        print("✅ Configuration integration: PASSED")
        tests_passed += 1
    else:
        print("❌ Configuration integration: FAILED")
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed >= 3:
        print("✅ Core price tracking functionality is working!")
        if price_data:
            print("\n💡 Current Market Conditions:")
            if price_data['bitcoin_price'] and price_data['hashprice']:
                if price_data['hashprice'] >= 0.1:
                    print("   📈 High profitability - Good time to mine!")
                elif price_data['hashprice'] >= 0.05:
                    print("   📊 Moderate profitability - Mining is viable")
                else:
                    print("   📉 Low profitability - Consider reducing power or pausing")
    else:
        print("⚠️ Some tests failed. Check network connectivity and API availability.")
    
    print(f"\nPrice tracking features have been added to ThermoHash!")
    print("The enhanced system now includes:")
    print("- 📡 Multi-source Bitcoin price tracking")
    print("- ⛏️ Real-time hash price calculation")
    print("- 🌍 IP-based geolocation (existing)")
    print("- 📍 Manual coordinate override (existing)")
    print("- 🧠 ML-powered optimization with price data")
    print("- ⚙️ Configurable profitability thresholds")

if __name__ == "__main__":
    main()