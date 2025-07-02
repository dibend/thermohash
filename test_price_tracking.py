#!/usr/bin/env python3
"""
Test script for ThermoHash Price Tracking functionality
Tests Bitcoin price and hash price tracking without requiring miner setup
"""

import json
import sys
from datetime import datetime

# Import the price tracking service from our main script
try:
    from thermohash_optimized import PriceTracker
    print("✅ Successfully imported ThermoHash PriceTracker")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

def test_bitcoin_price():
    """Test Bitcoin price fetching from multiple sources"""
    print("\n💰 Testing Bitcoin Price Tracking...")
    print("=" * 50)
    
    price_tracker = PriceTracker()
    
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
    
    price_tracker = PriceTracker()
    
    try:
        # Test hashrate
        hashrate = price_tracker.get_network_hashrate()
        if hashrate:
            print(f"✅ Network hashrate: {hashrate:,.2f} TH/s")
        else:
            print("❌ Failed to get network hashrate")
        
        # Test difficulty
        difficulty = price_tracker.get_mining_difficulty()
        if difficulty:
            print(f"✅ Mining difficulty: {difficulty:,.0f}")
        else:
            print("❌ Failed to get mining difficulty")
            
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
        price_tracker = PriceTracker()
        
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
        price_tracker = PriceTracker()
        
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
    print("🧪 ThermoHash Price Tracking Test Suite")
    print("==========================================")
    print("This script tests the Bitcoin price and hash price tracking features")
    print("without requiring a full miner setup.\n")
    
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
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Price tracking is working correctly.")
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
    
    print(f"\nPrice tracking features are now integrated with ThermoHash!")
    print("The system will automatically:")
    print("- Track Bitcoin price from multiple sources")
    print("- Calculate real-time hash price")
    print("- Adjust mining power based on profitability")
    print("- Include price data in ML optimization")

if __name__ == "__main__":
    main()