#!/usr/bin/env python3
"""
Mock test for Bitcoin price and hashprice integration
Tests the structure and logic without external API calls
"""

import json
from datetime import datetime, timedelta

def mock_bitcoin_price():
    """Mock Bitcoin price"""
    return 67234.56

def mock_network_data():
    """Mock Bitcoin network data"""
    return {
        'hashrate_th': 600000000,  # 600 EH/s in TH/s
        'hashrate_eh': 600,
        'difficulty': 83000000000000
    }

def calculate_hashprice(btc_price, network_data):
    """Calculate hashprice - same logic as in FinancialDataService"""
    block_reward_btc = 3.125  # Post-halving block reward
    blocks_per_day = 144  # Approximately 144 blocks per day
    
    daily_btc_per_th = (block_reward_btc * blocks_per_day) / network_data['hashrate_th']
    daily_usd_per_th = daily_btc_per_th * btc_price
    
    return {
        'usd_per_th_day': daily_usd_per_th,
        'btc_per_th_day': daily_btc_per_th,
        'network_hashrate_eh': network_data['hashrate_eh'],
        'bitcoin_price': btc_price
    }

def calculate_mining_profitability(power_watts, efficiency_j_th, electricity_cost_kwh, hashprice_data):
    """Calculate mining profitability - same logic as in FinancialDataService"""
    # Calculate hashrate from power
    hashrate_th = power_watts / efficiency_j_th
    
    # Daily revenue
    daily_revenue_btc = hashrate_th * hashprice_data['btc_per_th_day']
    daily_revenue_usd = hashrate_th * hashprice_data['usd_per_th_day']
    
    # Daily electricity cost
    daily_power_kwh = (power_watts * 24) / 1000  # Convert W*h to kWh
    daily_electricity_cost = daily_power_kwh * electricity_cost_kwh
    
    # Profit calculations
    daily_profit_usd = daily_revenue_usd - daily_electricity_cost
    profit_margin = (daily_profit_usd / daily_revenue_usd * 100) if daily_revenue_usd > 0 else 0
    
    return {
        'hashrate_th': hashrate_th,
        'daily_revenue_btc': daily_revenue_btc,
        'daily_revenue_usd': daily_revenue_usd,
        'daily_electricity_cost': daily_electricity_cost,
        'daily_profit_usd': daily_profit_usd,
        'profit_margin_percent': profit_margin,
        'power_watts': power_watts
    }

def test_config_structure():
    """Test that config.json has the new financial settings"""
    print("Testing Configuration Structure...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check for financial settings
        if 'financial_settings' in config:
            print("✓ Financial settings section found")
            fs = config['financial_settings']
            
            required_fields = [
                'enable_profitability_optimization',
                'miner_efficiency_j_th',
                'electricity_cost_kwh',
                'min_profit_margin_percent',
                'max_unprofitable_hours'
            ]
            
            for field in required_fields:
                if field in fs:
                    print(f"✓ {field}: {fs[field]}")
                else:
                    print(f"✗ Missing field: {field}")
        else:
            print("✗ Financial settings section missing")
            
    except Exception as e:
        print(f"✗ Config test error: {e}")

def test_financial_calculations():
    """Test the financial calculation logic"""
    print("\nTesting Financial Calculations...")
    
    # Mock data
    btc_price = mock_bitcoin_price()
    network_data = mock_network_data()
    
    print(f"Mock Bitcoin price: ${btc_price:,.2f}")
    print(f"Mock network hashrate: {network_data['hashrate_eh']} EH/s")
    
    # Test hashprice calculation
    hashprice = calculate_hashprice(btc_price, network_data)
    print(f"✓ Calculated hashprice: ${hashprice['usd_per_th_day']:.2f}/TH/day")
    print(f"✓ Calculated hashprice: {hashprice['btc_per_th_day']:.8f} BTC/TH/day")
    
    # Test profitability at different power levels
    print("\nProfitability Analysis:")
    print("Power (W) | Hashrate (TH/s) | Daily Profit ($) | Margin (%)")
    print("-" * 60)
    
    power_levels = [400, 600, 800, 1000]
    efficiency = 25.0  # J/TH
    electricity_cost = 0.10  # $/kWh
    
    for power in power_levels:
        prof = calculate_mining_profitability(power, efficiency, electricity_cost, hashprice)
        print(f"{power:8d} | {prof['hashrate_th']:11.1f} | {prof['daily_profit_usd']:12.2f} | {prof['profit_margin_percent']:8.1f}")

def test_optimization_logic():
    """Test the power optimization logic"""
    print("\nTesting Optimization Logic...")
    
    # Simulate profitability-based power selection
    btc_price = mock_bitcoin_price()
    network_data = mock_network_data()
    hashprice = calculate_hashprice(btc_price, network_data)
    
    min_power, max_power = 400, 1000
    min_profit_margin = 10.0
    
    print(f"Finding optimal power between {min_power}W and {max_power}W")
    print(f"Minimum required profit margin: {min_profit_margin}%")
    
    profitable_levels = []
    
    for power in range(min_power, max_power + 1, 50):
        prof = calculate_mining_profitability(power, 25.0, 0.10, hashprice)
        if prof['profit_margin_percent'] >= min_profit_margin:
            profitable_levels.append({
                'power': power,
                'profit_margin': prof['profit_margin_percent'],
                'daily_profit': prof['daily_profit_usd']
            })
    
    if profitable_levels:
        # Find optimal (highest profit)
        optimal = max(profitable_levels, key=lambda x: x['daily_profit'])
        print(f"✓ Optimal power: {optimal['power']}W")
        print(f"✓ Profit margin: {optimal['profit_margin']:.1f}%")
        print(f"✓ Daily profit: ${optimal['daily_profit']:.2f}")
    else:
        print("✗ No profitable power levels found")

def main():
    """Run all tests"""
    print("Bitcoin Price and Hashprice Integration Test")
    print("=" * 50)
    
    test_config_structure()
    test_financial_calculations()
    test_optimization_logic()
    
    print("\n" + "=" * 50)
    print("✓ Integration structure test completed!")
    print("\nNote: This test uses mock data. For live testing,")
    print("ensure internet connectivity and run the actual algorithm.")

if __name__ == "__main__":
    main()