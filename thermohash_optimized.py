#!/usr/bin/env python3
"""
ThermoHash Optimized - Smart Bitcoin Miner Power Management
Uses OpenMeteo API weather predictions and TensorFlow CPU for optimal power management
Cross-platform compatible (Linux/Windows)
Features automatic IP-based geolocation
"""

import schedule
import time
import os
import json
import requests
import logging
import platform
import sys
import argparse
from datetime import datetime, timedelta
from subprocess import Popen, PIPE, DEVNULL
import socket
import ipaddress
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings

# Suppress TensorFlow warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    import tensorflow as tf
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import joblib
    TF_AVAILABLE = True
except ImportError:
    print("Warning: TensorFlow or scikit-learn not available. ML optimization disabled.")
    TF_AVAILABLE = False


def discover_miners(subnet: str) -> List[Dict]:
    """Scan the given subnet for ASIC miners exposing the gRPC port."""
    miners = []
    network = ipaddress.ip_network(subnet, strict=False)
    for ip in network.hosts():
        addr = str(ip)
        try:
            with socket.create_connection((addr, 50051), timeout=0.5):
                # Try to detect OS via grpcurl service list
                result = Popen(['grpcurl', '-plaintext', f'{addr}:50051', 'list'], stdout=PIPE, stderr=DEVNULL, text=True)
                output, _ = result.communicate(timeout=5)
                os_type = 'braiins' if 'braiins' in output.lower() else 'luxos' if 'lux' in output.lower() else 'unknown'
                miners.append({'address': addr, 'os': os_type})
        except Exception:
            continue
    return miners


def detect_local_subnet() -> str:
    """Guess the local /24 subnet based on the primary network interface."""
    try:
        ip = socket.gethostbyname(socket.gethostname())
        parts = ip.split('.')
        if len(parts) == 4:
            return '.'.join(parts[:3]) + '.0/24'
    except Exception:
        pass
    return '192.168.1.0/24'

class GeolocationService:
    """Handles automatic geolocation detection based on IP address"""
    
    def __init__(self):
        self.geolocation_apis = [
            {
                'name': 'ipapi.co',
                'url': 'https://ipapi.co/json/',
                'lat_key': 'latitude',
                'lon_key': 'longitude',
                'timeout': 10
            },
            {
                'name': 'ipinfo.io',
                'url': 'https://ipinfo.io/json',
                'lat_key': 'loc',  # Special handling needed - "lat,lon" format
                'lon_key': 'loc',
                'timeout': 10
            },
            {
                'name': 'ip-api.com',
                'url': 'http://ip-api.com/json/',
                'lat_key': 'lat',
                'lon_key': 'lon',
                'timeout': 10
            }
        ]
    
    def get_location_from_ip(self) -> Optional[Tuple[float, float]]:
        """
        Automatically detect location based on IP address
        Returns: (latitude, longitude) tuple or None if failed
        """
        for api in self.geolocation_apis:
            try:
                logging.info(f"Attempting geolocation with {api['name']}")
                response = requests.get(api['url'], timeout=api['timeout'])
                response.raise_for_status()
                data = response.json()
                
                # Handle different API response formats
                if api['name'] == 'ipinfo.io':
                    # ipinfo.io returns loc as "lat,lon" string
                    if 'loc' in data:
                        lat_str, lon_str = data['loc'].split(',')
                        lat, lon = float(lat_str.strip()), float(lon_str.strip())
                    else:
                        continue
                else:
                    # Standard lat/lon keys
                    if api['lat_key'] in data and api['lon_key'] in data:
                        lat = float(data[api['lat_key']])
                        lon = float(data[api['lon_key']])
                    else:
                        continue
                
                # Validate coordinates
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    logging.info(f"Successfully detected location: {lat:.4f}, {lon:.4f} via {api['name']}")
                    
                    # Log additional location info if available
                    location_info = []
                    for key in ['city', 'region', 'country', 'country_name']:
                        if key in data and data[key]:
                            location_info.append(f"{key}: {data[key]}")
                    
                    if location_info:
                        logging.info(f"Location details: {', '.join(location_info)}")
                    
                    return lat, lon
                else:
                    logging.warning(f"Invalid coordinates from {api['name']}: {lat}, {lon}")
                    
            except requests.RequestException as e:
                logging.warning(f"Geolocation API {api['name']} failed: {e}")
            except (ValueError, KeyError, AttributeError) as e:
                logging.warning(f"Error parsing geolocation data from {api['name']}: {e}")
            except Exception as e:
                logging.warning(f"Unexpected error with {api['name']}: {e}")
        
        logging.error("All geolocation services failed")
        return None
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate latitude and longitude values"""
        return -90 <= lat <= 90 and -180 <= lon <= 180

class WeatherPredictor:
    """Handles weather data fetching and prediction using OpenMeteo API"""
    
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    def get_current_weather(self) -> Optional[Dict]:
        """Get current weather data with error handling"""
        try:
            url = f"{self.base_url}?latitude={self.lat}&longitude={self.lon}&current_weather=true&timezone=auto"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data["current_weather"]
            return {
                'temperature': float(current["temperature"]),
                'humidity': current.get("humidity", 50),  # Default fallback
                'wind_speed': float(current["windspeed"]),
                'wind_direction': float(current["winddirection"]),
                'weather_code': int(current["weathercode"]),
                'timestamp': datetime.now()
            }
        except requests.RequestException as e:
            logging.error(f"Error fetching current weather: {e}")
            return None
        except (KeyError, ValueError) as e:
            logging.error(f"Error parsing weather data: {e}")
            return None
    
    def get_weather_forecast(self, hours: int = 24) -> Optional[List[Dict]]:
        """Get weather forecast for specified hours"""
        try:
            url = (f"{self.base_url}?latitude={self.lat}&longitude={self.lon}"
                   f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,"
                   f"wind_direction_10m,weather_code&timezone=auto&forecast_days=3")
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            hourly = data["hourly"]
            forecast = []
            
            for i in range(min(hours, len(hourly["time"]))):
                forecast.append({
                    'temperature': float(hourly["temperature_2m"][i]),
                    'humidity': float(hourly["relative_humidity_2m"][i]),
                    'wind_speed': float(hourly["wind_speed_10m"][i]),
                    'wind_direction': float(hourly["wind_direction_10m"][i]),
                    'weather_code': int(hourly["weather_code"][i]),
                    'timestamp': datetime.fromisoformat(hourly["time"][i].replace('Z', '+00:00'))
                })
            
            return forecast
        except requests.RequestException as e:
            logging.error(f"Error fetching weather forecast: {e}")
            return None
        except (KeyError, ValueError) as e:
            logging.error(f"Error parsing forecast data: {e}")
            return None

class FinancialDataService:
    """Handles Bitcoin price and Luxor hashprice data fetching"""
    
    def __init__(self):
        # Add support for CoinMarketCap & Luxor API keys from environment variables
        self.coinmarketcap_api_key = os.getenv("COINMARKETCAP_API_KEY")
        self.luxor_api_key = os.getenv("LUXOR_API_KEY")
        # Prefer CoinMarketCap if key is present, else fallback to CoinGecko
        self.bitcoin_api_url = (
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            if self.coinmarketcap_api_key
            else "https://api.coingecko.com/api/v3/simple/price"
        )
        # Hashprice endpoints – we will try the official Luxor GraphQL if key provided, then fallback to calculation
        self.luxor_graphql_endpoint = "https://api.hashrateindex.com/graphql"
        self.hashprice_apis = [
            {
                'name': 'LuxorHashpriceGraphQL',
                'url': self.luxor_graphql_endpoint,
                'timeout': 10,
            }
        ]
        # Existing cache attributes
        self.cached_bitcoin_price = None
        self.cached_hashprice = None
        self.bitcoin_cache_time = None
        self.hashprice_cache_time = None
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
    
    def get_bitcoin_price(self) -> Optional[float]:
        """Get current Bitcoin price in USD with caching – tries CoinMarketCap first, then CoinGecko."""
        now = datetime.now()
        if (
            self.cached_bitcoin_price is not None
            and self.bitcoin_cache_time is not None
            and now - self.bitcoin_cache_time < self.cache_duration
        ):
            return self.cached_bitcoin_price

        # 1. Attempt CoinMarketCap if API key present
        if self.coinmarketcap_api_key:
            price = self._get_btc_price_coinmarketcap()
            if price is not None:
                return price  # Successfully fetched & cached inside helper

        # 2. Fallback to CoinGecko (existing logic)
        try:
            params = {
                'ids': 'bitcoin',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
            }
            response = requests.get(self.bitcoin_api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'bitcoin' in data and 'usd' in data['bitcoin']:
                price = float(data['bitcoin']['usd'])
                # Cache
                self.cached_bitcoin_price = price
                self.bitcoin_cache_time = now
                change_24h = data['bitcoin'].get('usd_24h_change')
                market_cap = data['bitcoin'].get('usd_market_cap')
                logging.info(f"Bitcoin price (CoinGecko): ${price:,.2f}")
                if change_24h is not None:
                    logging.info(f"24h change: {change_24h:+.2f}%")
                if market_cap is not None:
                    logging.info(f"Market cap: ${market_cap:,.0f}")
                return price
            else:
                logging.error("Invalid Bitcoin price data format from CoinGecko")
        except requests.RequestException as e:
            logging.error(f"Error fetching Bitcoin price from CoinGecko: {e}")
        except (KeyError, ValueError) as e:
            logging.error(f"Error parsing Bitcoin price data from CoinGecko: {e}")
        return None

    def _get_btc_price_coinmarketcap(self) -> Optional[float]:
        """Internal helper to fetch BTC price from CoinMarketCap."""
        try:
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': self.coinmarketcap_api_key,
            }
            params = {
                'symbol': 'BTC',
                'convert': 'USD',
            }
            response = requests.get(self.bitcoin_api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            price = float(data['data']['BTC']['quote']['USD']['price'])
            now = datetime.now()
            # Cache result
            self.cached_bitcoin_price = price
            self.bitcoin_cache_time = now
            logging.info(f"Bitcoin price (CoinMarketCap): ${price:,.2f}")
            return price
        except (requests.RequestException, KeyError, ValueError) as e:
            logging.warning(f"CoinMarketCap price fetch failed: {e}")
            return None
    
    def get_hashprice_index(self) -> Optional[Dict]:
        """Get current hashprice index – tries Luxor API if key available, else falls back to internal calculation."""
        now = datetime.now()
        if (
            self.cached_hashprice is not None
            and self.hashprice_cache_time is not None
            and now - self.hashprice_cache_time < self.cache_duration
        ):
            return self.cached_hashprice

        # 1. Attempt Luxor Hashprice GraphQL API
        if self.luxor_api_key:
            luxor_data = self._get_hashprice_from_luxor()
            if luxor_data is not None:
                # Cache and return
                self.cached_hashprice = luxor_data
                self.hashprice_cache_time = now
                logging.info(
                    f"Hashprice (Luxor): ${luxor_data['usd_per_th_day']:.2f}/TH/day ({luxor_data['btc_per_th_day']:.8f} BTC/TH/day)"
                )
                return luxor_data

        # 2. Fallback to local calculation
        hashprice_data = self._get_hashprice_from_calculation()
        if hashprice_data:
            self.cached_hashprice = hashprice_data
            self.hashprice_cache_time = now
            logging.info(
                f"Hashprice (calculated): ${hashprice_data['usd_per_th_day']:.2f}/TH/day ({hashprice_data['btc_per_th_day']:.8f} BTC/TH/day)"
            )
            return hashprice_data
        return None

    def _get_hashprice_from_luxor(self) -> Optional[Dict]:
        """Fetch hashprice index directly from Luxor HashrateIndex GraphQL API."""
        try:
            query = (
                "query { getHashprice { btcHashprice usdHashprice networkHashrate difficulty } }"
            )
            headers = {
                'Content-Type': 'application/json',
                'X-API-KEY': self.luxor_api_key,
            }
            resp = requests.post(
                self.luxor_graphql_endpoint,
                json={'query': query},
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            # Attempt to parse accommodating possible field names
            hp = None
            if 'data' in data:
                if 'getHashprice' in data['data']:
                    hp = data['data']['getHashprice']
                elif 'getHashpriceIndex' in data['data']:
                    hp = data['data']['getHashpriceIndex']
            if not hp:
                logging.warning("Unexpected Luxor hashprice response format")
                return None
            usd_hp = float(hp.get('usdHashprice') or hp.get('usd_hashprice') or hp.get('usd_per_th_day') or 0)
            btc_hp = float(hp.get('btcHashprice') or hp.get('btc_hashprice') or hp.get('btc_per_th_day') or 0)
            if usd_hp == 0:
                return None
            # Network stats optional
            net_hashrate_eh = None
            difficulty = None
            if hp.get('networkHashrate'):
                net_hashrate_eh = float(hp['networkHashrate'])
            elif hp.get('network_hashrate'):
                net_hashrate_eh = float(hp['network_hashrate'])
            if hp.get('difficulty'):
                difficulty = float(hp['difficulty'])
            return {
                'usd_per_th_day': usd_hp,
                'btc_per_th_day': btc_hp if btc_hp else None,
                'network_hashrate_eh': net_hashrate_eh,
                'network_difficulty': difficulty,
                'bitcoin_price': self.get_bitcoin_price(),
                'timestamp': datetime.now(),
            }
        except (requests.RequestException, ValueError, KeyError) as e:
            logging.warning(f"Luxor hashprice fetch failed: {e}")
            return None
    
    def _get_hashprice_from_calculation(self) -> Optional[Dict]:
        """Calculate hashprice based on current Bitcoin price and network difficulty"""
        try:
            # Get Bitcoin price
            btc_price = self.get_bitcoin_price()
            if not btc_price:
                return None
            
            # Get Bitcoin network data
            network_data = self._get_bitcoin_network_data()
            if not network_data:
                return None
            
            # Calculate hashprice
            # Daily block reward per TH/s = (block_reward * blocks_per_day) / network_hashrate_th
            block_reward_btc = 3.125  # Post-halving block reward
            blocks_per_day = 144  # Approximately 144 blocks per day
            
            daily_btc_per_th = (block_reward_btc * blocks_per_day) / network_data['hashrate_th']
            daily_usd_per_th = daily_btc_per_th * btc_price
            
            return {
                'usd_per_th_day': daily_usd_per_th,
                'btc_per_th_day': daily_btc_per_th,
                'network_hashrate_eh': network_data['hashrate_eh'],
                'network_difficulty': network_data['difficulty'],
                'bitcoin_price': btc_price,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"Error calculating hashprice: {e}")
            return None
    
    def _get_bitcoin_network_data(self) -> Optional[Dict]:
        """Get Bitcoin network hashrate and difficulty data"""
        try:
            # Try multiple APIs for Bitcoin network data
            apis = [
                {
                    'url': 'https://blockstream.info/api/blocks/tip/height',
                    'stats_url': 'https://api.blockchain.info/stats'
                }
            ]
            
            for api in apis:
                try:
                    # Get network stats
                    response = requests.get(api['stats_url'], timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'hash_rate' in data and 'difficulty' in data:
                        # hash_rate is in GH/s, convert to TH/s and EH/s
                        hashrate_gh = float(data['hash_rate'])
                        hashrate_th = hashrate_gh / 1000  # GH/s to TH/s
                        hashrate_eh = hashrate_th / 1000000  # TH/s to EH/s
                        difficulty = float(data['difficulty'])
                        
                        return {
                            'hashrate_th': hashrate_th,
                            'hashrate_eh': hashrate_eh,
                            'difficulty': difficulty
                        }
                        
                except requests.RequestException:
                    continue
            
            # Fallback: use estimated values based on recent averages
            logging.warning("Using estimated network data as fallback")
            return {
                'hashrate_th': 600000000,  # ~600 EH/s estimated
                'hashrate_eh': 600,
                'difficulty': 83000000000000  # Approximate current difficulty
            }
            
        except Exception as e:
            logging.error(f"Error getting Bitcoin network data: {e}")
            return None
    
    def calculate_mining_profitability(self, power_watts: int, efficiency_j_th: float = 25.0, 
                                     electricity_cost_kwh: float = 0.10) -> Optional[Dict]:
        """Calculate mining profitability for given parameters"""
        try:
            hashprice_data = self.get_hashprice_index()
            if not hashprice_data:
                return None
            
            # Calculate hashrate from power
            # Hashrate (TH/s) = Power (W) / Efficiency (J/TH)
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
                'electricity_cost_kwh': electricity_cost_kwh,
                'efficiency_j_th': efficiency_j_th,
                'power_watts': power_watts,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"Error calculating mining profitability: {e}")
            return None

class PowerOptimizer:
    """TensorFlow-based power optimization using weather predictions"""
    
    def __init__(self, model_path: str = "thermohash_model.pkl"):
        self.model_path = model_path
        self.scaler_path = "thermohash_scaler.pkl"
        self.model = None
        self.scaler = None
        self.training_data = []
        
        if TF_AVAILABLE:
            self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = tf.keras.models.load_model(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logging.info("Loaded existing model and scaler")
            else:
                self._create_model()
                logging.info("Created new model")
        except Exception as e:
            logging.error(f"Error with model: {e}")
            self._create_model()
    
    def _create_model(self):
        """Create a new neural network model with financial features"""
        if not TF_AVAILABLE:
            return
        
        # Enhanced neural network for power prediction with financial features
        # Input features: weather (6) + financial (3) = 9 features
        self.model = tf.keras.Sequential([
            tf.keras.Input(shape=(9,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dropout(0.1),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')
        ])
        
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.scaler = StandardScaler()
    
    def add_training_data(self, weather_data: Dict, power_target: float):
        """Add data point for model training with enhanced features"""
        features = [
            weather_data['temperature'],
            weather_data['humidity'],
            weather_data['wind_speed'],
            weather_data['wind_direction'],
            weather_data['weather_code'],
            weather_data['timestamp'].hour,  # Time of day feature
            weather_data.get('bitcoin_price', 50000.0),  # Default fallback
            weather_data.get('hashprice_usd', 50.0),     # Default fallback
            weather_data.get('network_hashrate', 600.0)   # Default fallback (EH/s)
        ]
        
        self.training_data.append({
            'features': features,
            'target': power_target,
            'timestamp': weather_data['timestamp']
        })
        
        # Keep only recent data (last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        self.training_data = [
            d for d in self.training_data 
            if d['timestamp'] > cutoff
        ]
    
    def train_model(self, min_samples: int = 100) -> bool:
        """Train the model if enough data is available"""
        if not TF_AVAILABLE or len(self.training_data) < min_samples:
            return False
        
        try:
            # Prepare training data
            X = np.array([d['features'] for d in self.training_data])
            y = np.array([d['target'] for d in self.training_data])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model.fit(
                X_train, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_test, y_test),
                verbose=0
            )
            
            # Save model and scaler
            self.model.save(self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            logging.info(f"Model trained successfully with {len(self.training_data)} samples")
            return True
            
        except Exception as e:
            logging.error(f"Error training model: {e}")
            return False
    
    def predict_optimal_power(self, weather_data: Dict) -> Optional[float]:
        """Predict optimal power based on weather and financial data"""
        if not TF_AVAILABLE or self.model is None or self.scaler is None:
            return None
        
        try:
            features = np.array([[
                weather_data['temperature'],
                weather_data['humidity'],
                weather_data['wind_speed'],
                weather_data['wind_direction'],
                weather_data['weather_code'],
                weather_data['timestamp'].hour,
                weather_data.get('bitcoin_price', 50000.0),  # Default fallback
                weather_data.get('hashprice_usd', 50.0),     # Default fallback
                weather_data.get('network_hashrate', 600.0)   # Default fallback (EH/s)
            ]])
            
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled, verbose=0)[0][0]
            
            return float(prediction)
            
        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            return None

class MinerController:
    """Handles miner communication and power management for a single miner."""

    def __init__(self, miner_address: str, username: str, password: str, os_type: str = "braiins"):
        self.miner_address = miner_address
        self.username = username
        self.password = password
        self.os_type = os_type.lower()
        self.current_token = None
        self.token_expiry = None
        
    def authenticate(self) -> Optional[str]:
        """Authenticate and get session token with platform-specific handling"""
        if self.current_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.current_token
        
        try:
            auth_data = json.dumps({"username": self.username, "password": self.password})
            service = 'braiins.bos.v1.AuthenticationService/Login'
            if self.os_type == 'luxos':
                service = 'luxor.firmware.v1.AuthenticationService/Login'
            auth_command = [
                'grpcurl', '-plaintext', '-d', auth_data,
                f'{self.miner_address}:50051',
                service
            ]
            
            process = Popen(auth_command, stdout=PIPE, stderr=PIPE, text=True)
            output, error = process.communicate(timeout=30)
            
            if process.returncode == 0:
                # Try JSON body first (newer Braiins OS versions return token in response body)
                try:
                    body_json = json.loads(output.strip() or '{}')
                    if isinstance(body_json, dict) and body_json.get("token"):
                        token = str(body_json["token"])
                        self.current_token = token
                        self.token_expiry = datetime.now() + timedelta(hours=1)
                        logging.debug("Authentication successful (token extracted from JSON body)")
                        return token
                except json.JSONDecodeError:
                    # Not a JSON body, fall back to legacy header parsing below
                    pass

                for line in output.split('\n'):
                    if "authorization" in line:
                        token = line.split(": ")[1].strip().strip('"')
                        self.current_token = token
                        self.token_expiry = datetime.now() + timedelta(hours=1)
                        logging.debug("Authentication successful")
                        return token
            else:
                logging.error(f"Authentication failed: {error}")
                
        except Exception as e:
            logging.error(f"Authentication error: {e}")
        
        return None
    
    def set_power_target(self, power_target: int) -> bool:
        """Set miner power target with enhanced error handling"""
        token = self.authenticate()
        if not token:
            logging.error("Cannot set power target: authentication failed")
            return False
        
        try:
            power_data = json.dumps({
                "power_target": {"watt": power_target},
                "save_action": 2
            })
            
            service = 'braiins.bos.v1.PerformanceService/SetPowerTarget'
            if self.os_type == 'luxos':
                service = 'luxor.firmware.v1.PerformanceService/SetPowerTarget'

            set_command = [
                'grpcurl', '-plaintext',
                '-H', f'authorization:{token}',
                '-d', power_data,
                f'{self.miner_address}:50051',
                service
            ]
            
            process = Popen(set_command, stdout=PIPE, stderr=PIPE, text=True)
            output, error = process.communicate(timeout=30)
            
            if process.returncode == 0:
                logging.info(f"Power target successfully set to {power_target} watts")
                return True
            else:
                logging.error(f"Failed to set power target: {error}")
                return False
                
        except Exception as e:
            logging.error(f"Error setting power target: {e}")
            return False


class MultiMinerController:
    """Manage a fleet of MinerController instances."""

    def __init__(self, miners: List[Dict]):
        self.controllers = []
        for m in miners:
            self.controllers.append(
                MinerController(
                    m.get("address"),
                    m.get("username", "root"),
                    m.get("password", ""),
                    m.get("os", "braiins"),
                )
            )

    def set_power_target(self, power_target: int) -> bool:
        """Set power target on all miners; returns True if all succeed."""
        results = []
        for c in self.controllers:
            results.append(c.set_power_target(power_target))
        return all(results)

class ThermoHashOptimized:
    """Main ThermoHash application with ML optimization and auto-geolocation"""
    
    def __init__(self, config_path: str = "config.json", simulate: bool = False):
        self.config = self._load_config(config_path)

        # Simulation flag (stub API responses & disable miner calls)
        self.simulate = simulate

        # If running in simulation, ensure we write logs to a local file to avoid permission issues
        if self.simulate:
            self.config.setdefault("logging", {})
            self.config["logging"]["file_path"] = "thermohash_sim.log"

        # Setup logging AFTER potential simulation adjustments
        self._setup_logging()

        # Get coordinates (auto-detect or use configured) – skip external lookup in simulation
        if self.simulate:
            config_lat = self.config.get("latitude", 40.7128)
            config_lon = self.config.get("longitude", -74.0060)

            if config_lat is None:
                config_lat = 40.7128
            if config_lon is None:
                config_lon = -74.0060

            self.lat, self.lon = float(config_lat), float(config_lon)
        else:
            self.lat, self.lon = self._get_coordinates()
        
        # Initialize components
        self.weather_predictor = WeatherPredictor(self.lat, self.lon)
        self.financial_service = FinancialDataService()
        
        self.power_optimizer = PowerOptimizer() if TF_AVAILABLE else None

        # Initialize miner controller(s)
        if "miners" in self.config:
            self.miner_controller = MultiMinerController(self.config["miners"])
        else:
            # Auto-discover miners on local network when list not provided
            subnet = self.config.get("subnet", detect_local_subnet())
            discovered = discover_miners(subnet)
            if discovered:
                self.config["miners"] = discovered
                self.miner_controller = MultiMinerController(discovered)
            else:
                self.miner_controller = MinerController(
                    self.config["miner_address"],
                    os.getenv("MINER_USERNAME", self.config["username"]),
                    os.getenv("MINER_PASSWORD", self.config["password"])
                )
        
        self.temp_thresholds = {
            float(k): float(v) for k, v in self.config["temp_thresholds"].items()
        }
        
        self.last_training = None
        self.last_power_target = None
        self.last_profitability = None
        
        # Enable simulation stubs if requested
        if self.simulate:
            self._enable_simulation_mode()
        
    def _get_coordinates(self) -> Tuple[float, float]:
        """Get coordinates from config or auto-detect via IP geolocation"""
        
        # Check if coordinates are provided in config
        config_lat = self.config.get("latitude")
        config_lon = self.config.get("longitude")
        
        geolocation_service = GeolocationService()
        
        # If coordinates are provided and valid, use them
        if (config_lat is not None and config_lon is not None and 
            geolocation_service.validate_coordinates(float(config_lat), float(config_lon))):
            lat, lon = float(config_lat), float(config_lon)
            logging.info(f"Using configured coordinates: {lat:.4f}, {lon:.4f}")
            return lat, lon
        
        # Auto-detect via IP geolocation
        logging.info("No valid coordinates in config, attempting auto-detection...")
        auto_location = geolocation_service.get_location_from_ip()
        
        if auto_location:
            lat, lon = auto_location
            
            # Save detected coordinates to config for future use
            self._save_detected_coordinates(lat, lon)
            
            return lat, lon
        else:
            # Fallback to default coordinates if all else fails
            logging.warning("Auto-geolocation failed, using default coordinates (New York)")
            lat, lon = 40.7128, -74.0060  # New York City as fallback
            
            # Save fallback coordinates to config
            self._save_detected_coordinates(lat, lon)
            
            return lat, lon
    
    def _save_detected_coordinates(self, lat: float, lon: float):
        """Save detected coordinates to config file for future use"""
        try:
            self.config["latitude"] = lat
            self.config["longitude"] = lon
            self.config["coordinates_auto_detected"] = True
            self.config["coordinates_detection_time"] = datetime.now().isoformat()
            
            with open("config.json", "w") as config_file:
                json.dump(self.config, config_file, indent=4)
            
            logging.info(f"Saved detected coordinates to config: {lat:.4f}, {lon:.4f}")
            
        except Exception as e:
            logging.warning(f"Could not save coordinates to config: {e}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration with error handling and coordinate validation"""
        try:
            with open(config_path, "r") as config_file:
                config = json.load(config_file)
                
            # Validate required keys (latitude/longitude now optional for auto-detection)
            required_keys = ["temp_thresholds"]
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Missing required config key: {key}")

            # Backwards compatibility: single miner fields or new miners list
            if "miners" not in config:
                for key in ["miner_address", "username", "password"]:
                    if key not in config:
                        raise ValueError(f"Missing required config key: {key}")
            else:
                if not isinstance(config["miners"], list) or not config["miners"]:
                    raise ValueError("miners must be a non-empty list")
            
            # Validate temp_thresholds
            if not isinstance(config["temp_thresholds"], dict) or not config["temp_thresholds"]:
                raise ValueError("temp_thresholds must be a non-empty dictionary")
                    
            return config
            
        except FileNotFoundError:
            logging.error(f"Config file {config_path} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config file: {e}")
            sys.exit(1)
        except ValueError as e:
            logging.error(f"Config validation error: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup logging with cross-platform compatibility"""
        log_config = self.config.get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO"))
        
        # Use appropriate log path for platform
        if platform.system() == "Windows":
            log_path = log_config.get("file_path", "thermohash.log")
        else:
            log_path = log_config.get("file_path", "/var/log/thermohash.log")
            
        # Ensure log directory exists
        log_dir = os.path.dirname(log_path)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except PermissionError:
                log_path = "thermohash.log"  # Fallback to current directory
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def calculate_power_from_temperature(self, temperature: float) -> int:
        """Calculate power target based on temperature thresholds"""
        if temperature <= min(self.temp_thresholds.keys()):
            return int(max(self.temp_thresholds.values()))
        elif temperature >= max(self.temp_thresholds.keys()):
            return int(min(self.temp_thresholds.values()))
        else:
            # Linear interpolation between thresholds
            sorted_thresholds = sorted(self.temp_thresholds.items())
            for i, (temp_threshold, power) in enumerate(sorted_thresholds):
                if temperature <= temp_threshold:
                    if i == 0:
                        return int(power)
                    else:
                        # Interpolate between previous and current threshold
                        prev_temp, prev_power = sorted_thresholds[i-1]
                        ratio = (temperature - prev_temp) / (temp_threshold - prev_temp)
                        interpolated_power = prev_power + ratio * (power - prev_power)
                        return int(interpolated_power)
            
            return int(min(self.temp_thresholds.values()))
    
    def get_optimized_power_target(self, current_weather: Dict, forecast: List[Dict] = None) -> int:
        """Get optimized power target using current weather, ML predictions, and financial data"""
        # Calculate base power from current temperature
        base_power = self.calculate_power_from_temperature(current_weather['temperature'])
        
        # Get financial data and profitability constraints
        financial_config = self.config.get("financial_settings", {})
        profitability_optimization = financial_config.get("enable_profitability_optimization", True)
        
        if profitability_optimization:
            optimized_power = self._get_profitability_optimized_power(base_power, current_weather)
        else:
            optimized_power = base_power
        
        # Apply ML optimization if available
        if TF_AVAILABLE and self.power_optimizer:
            ml_prediction = self.power_optimizer.predict_optimal_power(current_weather)
            
            if ml_prediction is not None:
                # Combine predictions using configured weights
                optimization_config = self.config.get("optimization_settings", {})
                prediction_weight = optimization_config.get("prediction_weight", 0.7)
                current_weight = optimization_config.get("current_weather_weight", 0.3)
                smoothing_factor = optimization_config.get("power_smoothing_factor", 0.8)
                
                # Weighted combination
                combined_power = (prediction_weight * ml_prediction + current_weight * optimized_power)
                
                # Apply smoothing if we have a previous target
                if self.last_power_target is not None:
                    combined_power = (smoothing_factor * self.last_power_target + 
                                    (1 - smoothing_factor) * combined_power)
                
                optimized_power = combined_power
        
        # Ensure within valid range
        min_power = min(self.temp_thresholds.values())
        max_power = max(self.temp_thresholds.values())
        final_power = max(min_power, min(max_power, optimized_power))
        
        return int(final_power)
    
    def _get_profitability_optimized_power(self, base_power: float, current_weather: Dict) -> float:
        """Optimize power based on current Bitcoin price and hashprice profitability"""
        try:
            financial_config = self.config.get("financial_settings", {})
            
            # Get miner specifications from config
            miner_efficiency = financial_config.get("miner_efficiency_j_th", 25.0)
            electricity_cost = financial_config.get("electricity_cost_kwh", 0.10)
            min_profit_margin = financial_config.get("min_profit_margin_percent", 10.0)
            max_unprofitable_hours = financial_config.get("max_unprofitable_hours", 2.0)
            
            # Test profitability at different power levels
            power_levels = []
            min_power = min(self.temp_thresholds.values())
            max_power = max(self.temp_thresholds.values())
            
            # Test power levels from min to max in increments
            for power in range(int(min_power), int(max_power) + 1, 50):
                profitability = self.financial_service.calculate_mining_profitability(
                    power, miner_efficiency, electricity_cost
                )
                
                if profitability:
                    power_levels.append({
                        'power': power,
                        'profit_margin': profitability['profit_margin_percent'],
                        'daily_profit': profitability['daily_profit_usd'],
                        'profitability_data': profitability
                    })
            
            if not power_levels:
                logging.warning("Could not calculate profitability, using base power")
                return base_power
            
            # Filter profitable levels
            profitable_levels = [
                p for p in power_levels 
                if p['profit_margin'] >= min_profit_margin
            ]
            
            if not profitable_levels:
                # Check if we should operate at a loss temporarily
                best_level = max(power_levels, key=lambda x: x['profit_margin'])
                
                if self.last_profitability:
                    # Calculate hours since last profitable operation
                    hours_unprofitable = (datetime.now() - self.last_profitability['timestamp']).total_seconds() / 3600
                    
                    if hours_unprofitable < max_unprofitable_hours:
                        logging.warning(f"Operating at {best_level['profit_margin']:.1f}% margin (unprofitable but within tolerance)")
                        return float(best_level['power'])
                    else:
                        logging.warning("Reducing power due to extended unprofitability")
                        return float(min_power)
                else:
                    # First run, be conservative
                    logging.warning("First profitability check - using minimum power")
                    return float(min_power)
            
            else:
                # Find optimal profitable power level
                # Prefer higher power if still profitable (more absolute profit)
                optimal_level = max(profitable_levels, key=lambda x: x['daily_profit'])
                
                # Update last profitability timestamp
                self.last_profitability = {
                    'timestamp': datetime.now(),
                    'profit_margin': optimal_level['profit_margin'],
                    'power': optimal_level['power']
                }
                
                logging.info(f"Optimal profitable power: {optimal_level['power']}W "
                           f"(margin: {optimal_level['profit_margin']:.1f}%, "
                           f"profit: ${optimal_level['daily_profit']:.2f}/day)")
                
                return float(optimal_level['power'])
        
        except Exception as e:
            logging.error(f"Error in profitability optimization: {e}")
            return base_power
    
    def adjust_power_based_on_weather(self):
        """Main power adjustment function with ML optimization and financial data"""
        try:
            logging.info("Starting power adjustment cycle")
            
            # Get current weather
            current_weather = self.weather_predictor.get_current_weather()
            if not current_weather:
                logging.error("Could not retrieve current weather data")
                return
            
            logging.info(f"Current weather at ({self.lat:.4f}, {self.lon:.4f}): "
                        f"{current_weather['temperature']:.1f}°C, "
                        f"Humidity: {current_weather['humidity']:.1f}%, "
                        f"Wind: {current_weather['wind_speed']:.1f} km/h")
            
            # Get financial data
            bitcoin_price = self.financial_service.get_bitcoin_price()
            hashprice_data = self.financial_service.get_hashprice_index()
            
            if bitcoin_price:
                logging.info(f"Current Bitcoin price: ${bitcoin_price:,.2f}")
            
            if hashprice_data:
                logging.info(f"Current hashprice: ${hashprice_data['usd_per_th_day']:.2f}/TH/day "
                           f"({hashprice_data['btc_per_th_day']:.8f} BTC/TH/day)")
                logging.info(f"Network hashrate: {hashprice_data['network_hashrate_eh']:.1f} EH/s")
            
            # Get forecast for optimization
            prediction_config = self.config.get("prediction_settings", {})
            forecast_hours = prediction_config.get("forecast_hours", 24)
            forecast = self.weather_predictor.get_weather_forecast(forecast_hours)
            
            # Calculate optimized power target
            power_target = self.get_optimized_power_target(current_weather, forecast)
            
            # Calculate and log profitability at chosen power level
            financial_config = self.config.get("financial_settings", {})
            if financial_config.get("enable_profitability_optimization", True):
                miner_efficiency = financial_config.get("miner_efficiency_j_th", 25.0)
                electricity_cost = financial_config.get("electricity_cost_kwh", 0.10)
                
                profitability = self.financial_service.calculate_mining_profitability(
                    power_target, miner_efficiency, electricity_cost
                )
                
                if profitability:
                    logging.info(f"Mining profitability at {power_target}W: "
                               f"${profitability['daily_profit_usd']:.2f}/day profit "
                               f"({profitability['profit_margin_percent']:.1f}% margin)")
                    logging.info(f"Hashrate: {profitability['hashrate_th']:.1f} TH/s, "
                               f"Revenue: ${profitability['daily_revenue_usd']:.2f}/day, "
                               f"Power cost: ${profitability['daily_electricity_cost']:.2f}/day")
            
            logging.info(f"Calculated power target: {power_target} watts")
            
            # Set power target on miner
            if self.miner_controller.set_power_target(power_target):
                # Add training data for ML model (now including financial data)
                if TF_AVAILABLE and self.power_optimizer:
                    enhanced_weather = current_weather.copy()
                    if bitcoin_price:
                        enhanced_weather['bitcoin_price'] = bitcoin_price
                    if hashprice_data:
                        enhanced_weather['hashprice_usd'] = hashprice_data['usd_per_th_day']
                        enhanced_weather['network_hashrate'] = hashprice_data['network_hashrate_eh']
                    
                    self.power_optimizer.add_training_data(enhanced_weather, power_target)
                
                self.last_power_target = power_target
                logging.info(f"Successfully set power target to {power_target} watts")
            else:
                logging.error("Failed to set power target on miner")
            
            # Periodic model training
            self._check_and_train_model()
            
        except Exception as e:
            logging.error(f"Error in power adjustment cycle: {e}")
    
    def _check_and_train_model(self):
        """Check if model needs retraining and do it if necessary"""
        if not TF_AVAILABLE or not self.power_optimizer:
            return
        
        prediction_config = self.config.get("prediction_settings", {})
        retrain_interval = prediction_config.get("retrain_interval_hours", 168)  # 1 week
        min_samples = prediction_config.get("min_training_samples", 100)
        
        now = datetime.now()
        if (self.last_training is None or 
            (now - self.last_training).total_seconds() > retrain_interval * 3600):
            
            if len(self.power_optimizer.training_data) >= min_samples:
                logging.info("Starting model retraining")
                if self.power_optimizer.train_model(min_samples):
                    self.last_training = now
                    logging.info("Model retraining completed successfully")
                else:
                    logging.warning("Model retraining failed")
    
    def _enable_simulation_mode(self):
        """Patch external API calls with static data for offline testing"""
        logging.warning("Running in SIMULATION mode – external API calls are stubbed.")

        def fake_current_weather():
            return {
                'temperature': 20.0,
                'humidity': 50,
                'wind_speed': 5,
                'wind_direction': 180,
                'weather_code': 0,
                'timestamp': datetime.now()
            }

        def fake_forecast(hours: int = 24):
            base = datetime.now()
            return [
                {
                    'temperature': 20.0 + (i % 5),
                    'humidity': 50,
                    'wind_speed': 5,
                    'wind_direction': 180,
                    'weather_code': 0,
                    'timestamp': base + timedelta(hours=i)
                } for i in range(hours)
            ]

        # Stub weather services
        self.weather_predictor.get_current_weather = fake_current_weather  # type: ignore
        self.weather_predictor.get_weather_forecast = fake_forecast  # type: ignore

        # Stub financial services
        self.financial_service.get_bitcoin_price = lambda: 60000.0  # type: ignore
        self.financial_service.get_hashprice_index = lambda: {
            'usd_per_th_day': 0.06,
            'btc_per_th_day': 0.000001,
            'network_hashrate_eh': 600,
            'network_difficulty': 83000000000000,
            'bitcoin_price': 60000.0,
            'timestamp': datetime.now()
        }  # type: ignore

        # Stub miner controller so no real calls are made
        self.miner_controller.set_power_target = lambda power: True  # type: ignore
    
    def run(self):
        """Main application loop"""
        logging.info("ThermoHash Optimized with Auto-Geolocation starting up")
        logging.info(f"TensorFlow available: {TF_AVAILABLE}")
        logging.info(f"Platform: {platform.system()}")
        logging.info(f"Using coordinates: {self.lat:.4f}, {self.lon:.4f}")
        
        # Run initial adjustment
        self.adjust_power_based_on_weather()
        
        # Schedule periodic adjustments
        optimization_config = self.config.get("optimization_settings", {})
        interval_minutes = optimization_config.get("check_interval_minutes", 10)
        
        schedule.every(interval_minutes).minutes.do(self.adjust_power_based_on_weather)
        
        logging.info(f"Scheduler running, will adjust power every {interval_minutes} minutes")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("ThermoHash stopped by user")
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            raise

def main():
    """Entry point"""
    parser = argparse.ArgumentParser(description="ThermoHash Optimized")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration JSON file")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode with stubbed APIs")
    args = parser.parse_args()

    try:
        app = ThermoHashOptimized(config_path=args.config, simulate=args.simulate)
        app.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()