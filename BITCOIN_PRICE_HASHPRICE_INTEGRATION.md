# Bitcoin Price and Hashprice Integration for ThermoHash

## Overview

The ThermoHash Optimized algorithm now includes live Bitcoin price and hashprice index integration, enabling profitability-based power management in addition to weather-based optimization. This enhancement allows miners to automatically adjust power consumption based on real-time mining profitability while still maintaining optimal thermal management.

## New Features

### 1. Enhanced Financial Data Service

The enhanced `FinancialDataService` class provides:

- **Live Bitcoin Price**: Multi-source fetching with fallbacks:
  - Primary: CoinGecko API
  - Backup: CoinDesk API, Binance API
  - 5-minute caching for efficiency
- **Luxor Hashprice Index**: Direct integration with Luxor's hashprice API
- **Hashprice Calculation**: Real-time calculation fallback based on:
  - Current Bitcoin price
  - Network hashrate and difficulty from multiple sources
  - Block rewards (post-halving: 3.125 BTC)
- **Enhanced Network Data**: Multiple API sources for redundancy:
  - Blockchain.info API
  - Blockchair.com API  
  - Automatic fallback to estimated values
- **Mining Profitability Analysis**: Comprehensive profit/loss calculations

### 2. Profitability-Based Power Optimization

The algorithm now considers:

- **Current Bitcoin price** and market conditions
- **Network hashprice** (USD and BTC per TH/day)
- **Electricity costs** and miner efficiency
- **Profit margins** and operational thresholds

### 3. Enhanced Machine Learning Model

The ML model has been upgraded to include financial features:

- **Input Features**: Weather (6) + Financial (3) = 9 total features
- **Financial Inputs**: Bitcoin price, hashprice (USD/TH/day), network hashrate
- **Improved Architecture**: Deeper network with enhanced capacity

## Configuration

### New Financial Settings

Add the following section to your `config.json`:

```json
"financial_settings": {
    "enable_profitability_optimization": true,
    "miner_efficiency_j_th": 25.0,
    "electricity_cost_kwh": 0.10,
    "min_profit_margin_percent": 10.0,
    "max_unprofitable_hours": 2.0,
    "financial_data_cache_minutes": 5,
    "prefer_luxor_hashprice": true,
    "enable_realtime_price_updates": false,
    "api_timeout_seconds": 15,
    "bitcoin_price_apis": ["coingecko", "coindesk", "binance"],
    "hashprice_apis": ["luxor", "calculated"],
    "network_data_apis": ["blockchain.info", "blockchair.com"]
}
```

### Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `enable_profitability_optimization` | Enable/disable financial optimization | `true` |
| `miner_efficiency_j_th` | Miner efficiency in J/TH (Joules per Terahash) | `25.0` |
| `electricity_cost_kwh` | Electricity cost in USD per kWh | `0.10` |
| `min_profit_margin_percent` | Minimum profit margin to operate at full power | `10.0` |
| `max_unprofitable_hours` | Max hours to operate unprofitably | `2.0` |
| `financial_data_cache_minutes` | Cache duration for financial data | `5` |
| `prefer_luxor_hashprice` | Prioritize Luxor API over calculated hashprice | `true` |
| `enable_realtime_price_updates` | Enable WebSocket real-time price updates | `false` |
| `api_timeout_seconds` | Timeout for API requests in seconds | `15` |
| `bitcoin_price_apis` | Ordered list of Bitcoin price API sources | `["coingecko", "coindesk", "binance"]` |
| `hashprice_apis` | Ordered list of hashprice data sources | `["luxor", "calculated"]` |
| `network_data_apis` | Ordered list of network data API sources | `["blockchain.info", "blockchair.com"]` |

## How It Works

### 1. Data Collection Phase

Every adjustment cycle, the algorithm:

1. **Fetches Weather Data**: Temperature, humidity, wind conditions
2. **Gets Bitcoin Price**: Current USD price from CoinGecko API
3. **Calculates Hashprice**: Real-time hashprice based on network conditions
4. **Retrieves Network Stats**: Current hashrate and difficulty

### 2. Profitability Analysis

For each potential power level:

1. **Calculate Hashrate**: `Hashrate (TH/s) = Power (W) / Efficiency (J/TH)`
2. **Estimate Revenue**: `Daily Revenue = Hashrate × Hashprice`
3. **Calculate Costs**: `Daily Cost = (Power × 24h / 1000) × Electricity Rate`
4. **Determine Profit**: `Daily Profit = Revenue - Costs`
5. **Compute Margin**: `Profit Margin = (Profit / Revenue) × 100%`

### 3. Power Optimization Logic

The algorithm selects power levels based on:

1. **Profitable Operations**: Choose highest profitable power level
2. **Margin Thresholds**: Ensure minimum profit margin requirements
3. **Unprofitable Tolerance**: Allow temporary unprofitable operation
4. **Safety Limits**: Respect temperature-based power constraints

### 4. ML Model Integration

The enhanced neural network considers:

- **Weather Conditions**: Temperature, humidity, wind, time of day
- **Financial Factors**: Bitcoin price, hashprice, network hashrate
- **Historical Performance**: Previous power decisions and outcomes

## API Data Sources

### Bitcoin Price Data

- **Primary Source**: CoinGecko API (free tier)
  - **Endpoint**: `https://api.coingecko.com/api/v3/simple/price`
  - **Includes**: Price, 24h change, market cap
- **Backup Sources**:
  - CoinDesk API: `https://api.coindesk.com/v1/bpi/currentprice.json`
  - Binance API: `https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT`
- **Update Frequency**: Every 5 minutes (cached)
- **Failover**: Automatic fallback to backup sources if primary fails

### Luxor Hashprice Index

- **Primary Source**: Luxor Technologies API
  - **Endpoint**: `https://api.luxor.tech/v1/mining/hashprice`
  - **Data**: Real-time hashprice in USD/TH/day and BTC/TH/day
  - **Update Frequency**: Real-time with 5-minute caching
- **Fallback**: Calculated hashprice when Luxor API unavailable

### Network Hashrate Data

- **Primary Sources**:
  - Blockchain.info API: `https://api.blockchain.info/stats`
  - Blockchair.com API: `https://api.blockchair.com/bitcoin/stats`
- **Fallback**: Estimated values based on recent network averages
- **Data Points**: Network hashrate, difficulty, block times

### Hashprice Calculation (Fallback)

When direct hashprice APIs are unavailable, the system calculates using:

```
Daily Hashprice (USD/TH) = (Block Reward × Blocks/Day × BTC Price) / Network Hashrate (TH)
```

Where:
- Block Reward = 3.125 BTC (post-halving)
- Blocks/Day ≈ 144 blocks
- Network Hashrate = Current network hashrate in TH/s from multiple APIs

## Logging and Monitoring

### Enhanced Logging

The algorithm now logs:

```
[INFO] Bitcoin price: $67,234.56
[INFO] Bitcoin price from CoinDesk backup: $67,156.23
[INFO] Hashprice (USD): $52.34/TH/day
[INFO] Hashprice (BTC): 0.00077865 BTC/TH/day
[INFO] Data source: Luxor API
[INFO] Network data from blockchain.info: 583.2 EH/s
[INFO] Mining profitability at 800W: $24.67/day profit (18.2% margin)
[INFO] Hashrate: 32.0 TH/s, Revenue: $135.45/day, Power cost: $110.78/day
[INFO] Optimal profitable power: 850W (margin: 15.3%, profit: $20.89/day)
```

### Profitability Monitoring

Track key metrics:
- Daily profit/loss projections
- Profit margin trends
- Revenue vs. electricity costs
- Network difficulty changes

## Usage Examples

### Basic Setup

1. **Update Configuration**: Add financial settings to `config.json`
2. **Set Miner Specs**: Configure your miner's efficiency (J/TH)
3. **Set Electricity Rate**: Enter your local electricity cost per kWh
4. **Run Algorithm**: The system will automatically optimize based on profitability

### Conservative Mining

For conservative operation with higher profit margins:

```json
"financial_settings": {
    "min_profit_margin_percent": 20.0,
    "max_unprofitable_hours": 1.0
}
```

### Aggressive Mining

For maximum revenue extraction:

```json
"financial_settings": {
    "min_profit_margin_percent": 5.0,
    "max_unprofitable_hours": 6.0
}
```

## Benefits

### 1. **Automated Profitability Management**
- Automatic power reduction during unprofitable periods
- Maximized profits during favorable conditions
- Reduced manual intervention required

### 2. **Market-Responsive Operation**
- Real-time adaptation to Bitcoin price changes
- Network difficulty adjustments consideration
- Hashprice volatility management

### 3. **Enhanced ML Performance**
- Improved predictions with financial data
- Better long-term optimization strategies
- More sophisticated power management decisions

### 4. **Comprehensive Monitoring**
- Detailed profitability reporting
- Financial performance tracking
- Operational efficiency metrics

## Troubleshooting

### Common Issues

1. **API Connection Failures**
   - Check internet connectivity
   - Verify API endpoints are accessible
   - Review firewall settings

2. **Inaccurate Profitability Calculations**
   - Verify miner efficiency settings
   - Check electricity cost configuration
   - Ensure network data is updating

3. **Frequent Power Adjustments**
   - Increase `financial_data_cache_minutes`
   - Adjust `power_smoothing_factor`
   - Review profit margin thresholds

### Performance Optimization

1. **Reduce API Calls**: Increase cache duration for stable operations
2. **Tune Thresholds**: Adjust profit margins based on your risk tolerance
3. **Monitor Logs**: Regular review of profitability calculations

## Future Enhancements

Planned improvements include:

1. **Additional Data Sources**: Integration with more hashprice providers
2. **Advanced Algorithms**: Time-series forecasting for price predictions
3. **Risk Management**: Volatility-based power adjustment strategies
4. **Pool Integration**: Direct integration with mining pool APIs

## Support

For questions or issues with the Bitcoin price and hashprice integration:

1. Check the logs for detailed error messages
2. Verify your configuration settings
3. Ensure all required APIs are accessible
4. Review the network connectivity

The enhanced ThermoHash algorithm provides intelligent, market-aware mining optimization that maximizes both thermal efficiency and financial performance.