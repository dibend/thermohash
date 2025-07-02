# ThermoHash Price Tracking Enhancement

## Overview

This enhancement adds comprehensive Bitcoin price and hash price tracking capabilities to the ThermoHash system, enabling intelligent mining power management based on real-time market conditions and profitability metrics.

## New Features Added

### 🚀 Core Enhancements

1. **Multi-Source Bitcoin Price Tracking**
   - CoinGecko API integration
   - CoinDesk API fallback
   - Binance API secondary fallback
   - Automatic failover between sources
   - Price validation and caching

2. **Real-Time Hash Price Calculation**
   - Dynamic hash price computation based on:
     - Current Bitcoin price
     - Network hashrate
     - Block reward (6.25 BTC)
     - Daily block production (144 blocks)
   - Formula: `Hash Price = (BTC Price × Block Reward × 144) / Network Hashrate`

3. **Network Statistics Monitoring**
   - Bitcoin network hashrate tracking
   - Mining difficulty monitoring
   - Real-time network health metrics

4. **Enhanced ML Optimization**
   - Expanded neural network to include price features
   - 8-input feature model (weather + price data)
   - Improved power prediction accuracy

5. **Profitability-Based Power Management**
   - Configurable hash price thresholds
   - Dynamic power scaling based on profitability
   - Automatic power reduction during low-profit periods

### 🌍 Existing Features Enhanced

The system maintains all existing capabilities while adding price intelligence:

- ✅ **IP-based Geolocation** - Automatic location detection
- ✅ **Manual Coordinate Override** - Precise location input for better accuracy
- ✅ **Weather Integration** - Temperature-based power optimization
- ✅ **Machine Learning** - Enhanced with price data features

## Configuration

### New Price Settings

Added to `config.json`:

```json
{
  "price_settings": {
    "enable_price_optimization": true,
    "min_profitable_hashprice": 0.05,
    "optimal_hashprice": 0.15,
    "max_power_price_factor": 1.2,
    "min_power_price_factor": 0.7,
    "price_check_interval_minutes": 30,
    "bitcoin_price_sources": ["coingecko", "coindesk", "binance"],
    "enable_profitability_shutdown": false,
    "shutdown_hashprice_threshold": 0.02
  }
}
```

### Configuration Explanation

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| `enable_price_optimization` | Enable/disable price-based power adjustments | `true` | boolean |
| `min_profitable_hashprice` | Minimum profitable hash price (USD/TH/day) | `0.05` | 0.01-1.0 |
| `optimal_hashprice` | Hash price for maximum power operation | `0.15` | 0.05-1.0 |
| `max_power_price_factor` | Maximum power increase when profitable | `1.2` | 1.0-2.0 |
| `min_power_price_factor` | Power reduction when unprofitable | `0.7` | 0.3-1.0 |
| `enable_profitability_shutdown` | Auto-shutdown when unprofitable | `false` | boolean |
| `shutdown_hashprice_threshold` | Hash price threshold for shutdown | `0.02` | 0.01-0.1 |

## How It Works

### 1. Data Collection
```python
# Price tracking cycle
price_data = price_tracker.get_price_data()
# Returns:
{
    'bitcoin_price': 109041.0,
    'hashprice': 0.114049,
    'network_hashrate_th': 863.45,
    'difficulty': 116958512019762,
    'timestamp': datetime.now()
}
```

### 2. Power Optimization Logic
```python
# Base power from temperature
base_power = calculate_power_from_temperature(weather['temperature'])

# Apply price-based adjustments
if hashprice <= min_profitable_hashprice:
    power_factor = min_power_price_factor  # Reduce power
elif hashprice >= optimal_hashprice:
    power_factor = max_power_price_factor  # Increase power
else:
    # Linear interpolation between thresholds
    power_factor = interpolate(hashprice, min_profitable, optimal)

optimized_power = base_power * power_factor
```

### 3. Machine Learning Integration
The enhanced ML model now includes:
- Weather features: temperature, humidity, wind speed, wind direction, weather code, time of day
- **NEW**: Bitcoin price (normalized)
- **NEW**: Hash price (normalized)

This provides more accurate power predictions by considering market conditions.

## API Sources and Redundancy

### Bitcoin Price APIs
1. **Primary**: CoinGecko (`api.coingecko.com`)
   - Reliable, high uptime
   - Multiple cryptocurrency support
   - Rate limit friendly

2. **Secondary**: CoinDesk (`api.coindesk.com`)
   - Financial industry standard
   - USD-focused pricing
   - Historical data available

3. **Tertiary**: Binance (`api.binance.com`)
   - High-frequency updates
   - Trading platform data
   - Global liquidity

### Network Statistics API
- **Blockchain.info** (`api.blockchain.info`)
  - Official Bitcoin network statistics
  - Real-time hashrate and difficulty
  - Comprehensive network metrics

## Profitability Scenarios

### High Profitability (Hash Price ≥ $0.15/TH/day)
- **Action**: Increase power by up to 20%
- **Logic**: Maximize earnings during profitable periods
- **Example**: $0.20/TH/day → Power increased to 120% of base

### Moderate Profitability ($0.05 - $0.15/TH/day)
- **Action**: Linear power adjustment
- **Logic**: Scale power proportionally with profitability
- **Example**: $0.10/TH/day → Power at ~95% of base

### Low Profitability (Hash Price ≤ $0.05/TH/day)
- **Action**: Reduce power by up to 30%
- **Logic**: Minimize losses during unprofitable periods
- **Example**: $0.03/TH/day → Power reduced to 70% of base

### Critical Unprofitability (Hash Price ≤ $0.02/TH/day)
- **Action**: Optional automatic shutdown
- **Logic**: Prevent operational losses
- **Note**: Requires `enable_profitability_shutdown: true`

## Testing and Validation

### Test Suite
Run the comprehensive test suite:
```bash
# Full test (requires all dependencies)
python3 test_price_tracking.py

# Simplified test (minimal dependencies)
python3 test_price_simple.py
```

### Test Coverage
- ✅ Bitcoin price fetching from multiple sources
- ✅ Network statistics retrieval
- ✅ Hash price calculation accuracy
- ✅ Configuration integration
- ✅ Error handling and fallbacks
- ✅ Price validation and bounds checking

## Integration with Existing System

### Geolocation Integration
The price tracking system works seamlessly with existing geolocation features:

```python
# Combined initialization
coordinates = get_coordinates()  # IP-based or manual
weather_predictor = WeatherPredictor(lat, lon)
price_tracker = PriceTracker()

# Unified optimization
weather_data = weather_predictor.get_current_weather()
price_data = price_tracker.get_price_data()
optimized_power = get_optimized_power_target(weather_data, price_data)
```

### Weather + Price Optimization
The system now considers both environmental and economic factors:
1. **Weather-based optimization** - Adjust for temperature efficiency
2. **Price-based optimization** - Scale for profitability
3. **ML prediction** - Combine all factors for optimal power setting

## Monitoring and Logging

### Enhanced Logging
New log entries include:
```
2025-07-02 23:27:05 - INFO - Bitcoin price: $109,041.00 (from CoinGecko)
2025-07-02 23:27:05 - INFO - Hash price: $0.114049 per TH/s per day
2025-07-02 23:27:05 - INFO - High hash price detected, increasing power by 20%
2025-07-02 23:27:05 - INFO - Network difficulty: 116,958,512,019,762
```

### Market Condition Alerts
- 📈 **High Profitability**: "Good time to mine!"
- 📊 **Moderate Profitability**: "Mining is viable"
- 📉 **Low Profitability**: "Consider reducing power or pausing"

## Performance Impact

### Minimal Overhead
- API calls cached for 30 minutes (configurable)
- Lightweight JSON parsing
- Efficient price calculations
- Fail-fast error handling

### Network Requirements
- ~10KB data per price check cycle
- 3-5 API requests per update (with fallbacks)
- Automatic retry with exponential backoff

## Security Considerations

### API Safety
- No API keys required for price data
- Read-only data access
- Rate limiting respected
- Timeout protection (10s max per request)

### Data Validation
- Price bounds checking ($1,000 - $500,000)
- Hash price sanity validation (0.001 - 1.0)
- Network metric verification
- Error handling for malformed responses

## Upgrade Path

### From Previous Version
1. Update `config.json` with new price settings
2. Install any missing dependencies
3. Run test suite to verify functionality
4. Monitor initial operations

### Backward Compatibility
- All existing features remain unchanged
- Graceful degradation if price APIs fail
- Optional price optimization (can be disabled)

## Future Enhancements

### Planned Features
- [ ] Multiple cryptocurrency support (ETH, LTC)
- [ ] Electricity cost integration
- [ ] Historical profitability analysis
- [ ] Predictive market modeling
- [ ] Mobile notifications for market changes
- [ ] Custom price alert thresholds

### API Expansions
- [ ] Additional price source integrations
- [ ] Real-time WebSocket price feeds
- [ ] Mining pool difficulty predictions
- [ ] Renewable energy price correlation

## Support and Troubleshooting

### Common Issues
1. **Price API failures**: System automatically falls back to cached values
2. **Network connectivity**: Continues with weather-only optimization
3. **Invalid hash prices**: Uses conservative default values
4. **Configuration errors**: Detailed error messages and validation

### Debug Mode
Enable detailed logging by setting log level to DEBUG in config.json:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## Conclusion

The price tracking enhancement transforms ThermoHash from a temperature-reactive system into a comprehensive, market-aware mining optimization platform. By combining:

- 🌍 **Intelligent Geolocation** (IP-based + manual override)
- 🌡️ **Weather Optimization** 
- 💰 **Real-time Price Intelligence**
- 🧠 **Machine Learning Prediction**

The system now provides optimal mining power management that maximizes profitability while maintaining operational efficiency.

---

*For technical support or feature requests, please refer to the project documentation or submit an issue.*