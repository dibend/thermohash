# ThermoHash Optimized - Smart Bitcoin Miner Power Management

**ThermoHash Optimized** is an enhanced version of the original ThermoHash script with bug fixes, machine learning optimization, and improved weather prediction capabilities using the OpenMeteo API.

## ✨ New Features & Improvements

### 🌍 **NEW: Automatic IP-Based Geolocation**
- **Zero-configuration setup** - automatically detects your location from IP address
- **Multiple geolocation APIs** - ipapi.co, ipinfo.io, ip-api.com for reliability
- **Manual override** - still supports manual latitude/longitude configuration
- **Location caching** - saves detected coordinates to config for faster startup

### 🤖 Machine Learning Optimization
- **TensorFlow CPU integration** for lightweight ML predictions
- **Neural network model** that learns optimal power settings from historical data
- **Automatic model training** with configurable retraining intervals
- **Smart power smoothing** to prevent rapid power changes

### 🌤️ Enhanced Weather Integration
- **OpenMeteo API forecasting** - up to 72 hours of weather predictions
- **Extended weather data** including humidity, wind speed, and weather codes
- **Improved error handling** with robust timeout management
- **Weather-based optimization** using multiple weather parameters

### 🐛 Bug Fixes & Improvements
- **Cross-platform compatibility** - single script works on Linux and Windows
- **Enhanced error handling** with comprehensive logging
- **Token caching** to reduce authentication overhead
- **Configuration validation** to prevent runtime errors
- **Graceful degradation** when ML components are unavailable

### 🔧 Operational Enhancements
- **Automated installation scripts** for both Linux and Windows
- **Systemd service integration** for Linux systems
- **Virtual environment support** for dependency isolation
- **Configurable optimization parameters** for fine-tuning

## 📋 System Requirements

- **Python 3.8+**
- **grpcurl** (automatically installed on Linux)
- **Braiins OS** on your miner with port 50051 accessible
- **4GB+ RAM** recommended for ML features (optional)
- **Internet connection** for weather data and auto-geolocation

## 🚀 Quick Installation

### Linux (Automated)
```bash
# Download the repository
git clone https://github.com/your-username/thermohash.git
cd thermohash

# Run automated installation
chmod +x install.sh
./install.sh
```

### Windows (Automated)
```batch
# Download the repository and navigate to the folder
# Then run:
install.bat
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python thermohash_optimized.py
```

## ⚙️ Configuration

The system uses an enhanced `config.json` file with **automatic geolocation**:

```json
{
    "latitude": null,
    "longitude": null,
    "miner_address": "192.168.1.100",
    "username": "root",
    "password": "your_password",
    "temp_thresholds": {
        "10.0": 1000,
        "15.0": 900,
        "20.0": 800,
        "25.0": 700,
        "30.0": 600,
        "35.0": 500,
        "40.0": 400
    },
    "prediction_settings": {
        "forecast_hours": 24,
        "prediction_model_enabled": true,
        "retrain_interval_hours": 168,
        "min_training_samples": 100
    },
    "optimization_settings": {
        "check_interval_minutes": 10,
        "prediction_weight": 0.7,
        "current_weather_weight": 0.3,
        "power_smoothing_factor": 0.8
    },
    "logging": {
        "level": "INFO",
        "file_path": "/var/log/thermohash.log"
    }
}
```

### 🌍 Geolocation Configuration

**Automatic Mode (Recommended):**
- Set `latitude` and `longitude` to `null` (default)
- System automatically detects your location based on IP address
- Detected coordinates are saved to config for future use

**Manual Mode:**
- Set `latitude` and `longitude` to your specific coordinates
- Example: `"latitude": 40.6982, "longitude": -74.4014`
- Useful for: VPN users, specific location targeting, or privacy concerns

### Configuration Parameters

#### Basic Settings
- `latitude/longitude`: Leave `null` for auto-detection, or set specific coordinates
- `miner_address`: IP or hostname of your Braiins OS miner
- `username/password`: Miner authentication credentials
- `temp_thresholds`: Temperature to power mapping (°C: watts)

#### Prediction Settings
- `forecast_hours`: Hours of weather forecast to fetch (1-72)
- `prediction_model_enabled`: Enable/disable ML optimization
- `retrain_interval_hours`: How often to retrain the model (default: 168 = 1 week)
- `min_training_samples`: Minimum data points needed for training

#### Optimization Settings
- `check_interval_minutes`: How often to check and adjust power
- `prediction_weight`: Weight given to ML predictions (0.0-1.0)
- `current_weather_weight`: Weight given to current weather (0.0-1.0)
- `power_smoothing_factor`: Smoothing factor for power changes (0.0-1.0)

## 🎯 How It Works

### Location Detection Process
1. **Check Config**: If valid coordinates exist in config, use them
2. **Auto-Detect**: Try multiple geolocation APIs (ipapi.co, ipinfo.io, ip-api.com)
3. **Save Results**: Cache detected coordinates to config file
4. **Fallback**: Use New York coordinates if all detection fails

### Traditional Mode (Fallback)
1. Fetches current temperature from OpenMeteo API
2. Maps temperature to power target using configured thresholds
3. Sets miner power target via gRPC

### Optimized Mode (With ML)
1. Fetches current weather and 24-hour forecast
2. Uses neural network to predict optimal power based on:
   - Temperature
   - Humidity  
   - Wind speed and direction
   - Weather conditions
   - Time of day
3. Combines ML prediction with traditional temperature mapping
4. Applies power smoothing to prevent rapid changes
5. Continuously learns from decisions to improve predictions

### Machine Learning Model
- **Input features**: 6 weather/time parameters
- **Architecture**: 32→16→8→1 dense layers with dropout
- **Training**: Automatic retraining on historical data
- **Persistence**: Models saved to disk for continuity

## 🔄 Usage

### First-Time Setup
```bash
# 1. Install ThermoHash
./install.sh  # or install.bat on Windows

# 2. Configure your miner (coordinates auto-detected)
nano config.json  # Only need to set miner_address, username, password

# 3. Run and watch auto-geolocation
python thermohash_optimized.py
```

### Running the Application
```bash
# Using virtual environment (recommended)
./thermohash_env/bin/python thermohash_optimized.py

# Or directly (if dependencies installed globally)
python thermohash_optimized.py
```

### As a Service (Linux)
```bash
# Enable automatic startup
sudo systemctl enable thermohash

# Start the service
sudo systemctl start thermohash

# Check status
sudo systemctl status thermohash

# View logs
sudo journalctl -u thermohash -f
```

### Monitoring
```bash
# View real-time logs
tail -f /var/log/thermohash.log

# Or on Windows
type thermohash.log
```

## 📊 Performance & Benefits

### Resource Usage
- **CPU**: Minimal impact (~1-2% during adjustments)
- **Memory**: ~100MB base + ~200MB with ML features
- **Network**: <2KB per weather/location check (every 10 minutes)
- **Disk**: ~50MB for TensorFlow CPU, models <10MB

### Optimization Benefits
- **Zero-config setup**: No need to lookup coordinates manually
- **Improved accuracy**: Location-specific weather data
- **Automatic adaptation**: ML learns optimal settings over time
- **Smoother operation**: Reduced power fluctuations
- **Predictive adjustments**: Anticipates weather changes
- **Self-improving**: Performance improves with more data

## 🛠️ Troubleshooting

### Geolocation Issues

**Auto-detection failed:**
```bash
# Check logs for specific error
tail -f /var/log/thermohash.log

# Manual override - set coordinates in config:
{
    "latitude": 40.6982,
    "longitude": -74.4014
}
```

**Wrong location detected:**
- VPN users: Set manual coordinates or disable VPN temporarily
- Corporate networks: May show company location instead of physical location
- Use manual coordinates for precision applications

**Geolocation APIs blocked:**
- Check firewall/proxy settings
- Try different network connection
- Set manual coordinates as fallback

### Common Issues

**TensorFlow/ML features not working:**
```bash
# Install with ML support
pip install tensorflow-cpu scikit-learn

# Or disable ML in config
"prediction_model_enabled": false
```

**grpcurl not found (Windows):**
- Download from [grpcurl releases](https://github.com/fullstorydev/grpcurl/releases)
- Extract `grpcurl.exe` to your PATH or script directory

**Connection refused to miner:**
- Ensure port 50051 is open on your miner
- Check miner IP address in config
- Verify Braiins OS is running

**Permission denied on log file (Linux):**
```bash
sudo chmod 666 /var/log/thermohash.log
# Or change log path in config to writable location
```

### Debug Mode
Enable detailed logging by setting log level to "DEBUG" in config:
```json
"logging": {
    "level": "DEBUG",
    "file_path": "/var/log/thermohash.log"
}
```

## 🔒 Security & Privacy Considerations

### Geolocation Privacy
- **IP-based detection**: Only approximate location (city/region level)
- **No GPS data**: System doesn't access device location services
- **Manual override**: Can always set specific coordinates
- **Data storage**: Coordinates saved locally in config file only

### Network Security
- **HTTPS APIs**: All geolocation APIs use secure connections
- **No tracking**: Location requests are anonymous
- **Local processing**: Weather data processed locally

### Miner Security
- **Credentials**: Use environment variables for sensitive data:
  ```bash
  export MINER_USERNAME="your_username"
  export MINER_PASSWORD="your_password"
  ```
- **Network**: Ensure miner is on a secure network
- **Firewall**: Restrict access to port 50051 on your miner

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional geolocation services
- More sophisticated ML models
- Multi-miner support
- Web dashboard interface
- Mobile notifications

## 📄 License

This project is licensed under the same terms as the original ThermoHash project.

## 🙏 Acknowledgments

- Original ThermoHash project contributors
- OpenMeteo API for free weather data
- Geolocation API providers (ipapi.co, ipinfo.io, ip-api.com)
- TensorFlow team for excellent ML frameworks
- Braiins team for comprehensive gRPC API

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review logs for specific error messages
3. Create an issue with detailed information about your setup

---

**ThermoHash Optimized** - Smart mining with auto-geolocation and machine learning! 🌍🚀⚡