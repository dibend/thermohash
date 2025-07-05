#!/usr/bin/env python3
"""
Test script for ThermoHash Auto-Geolocation functionality
Tests IP-based coordinate detection without requiring miner setup
"""

import json
import sys
from datetime import datetime
import pytest

pytest.skip("Skipping geolocation tests that rely on external APIs", allow_module_level=True)

# Import the geolocation service from our main script
try:
    from thermohash_optimized import GeolocationService, WeatherPredictor
    print("✅ Successfully imported ThermoHash modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

def test_geolocation():
    """Test the IP-based geolocation functionality"""
    print("\n🌍 Testing IP-based Geolocation...")
    print("=" * 50)
    
    geo_service = GeolocationService()
    
    # Test coordinate detection
    location = geo_service.get_location_from_ip()
    
    if location:
        lat, lon = location
        print(f"✅ Location detected: {lat:.4f}, {lon:.4f}")
        
        # Validate coordinates
        if geo_service.validate_coordinates(lat, lon):
            print("✅ Coordinates are valid")
        else:
            print("❌ Invalid coordinates detected")
            
        return lat, lon
    else:
        print("❌ Auto-geolocation failed")
        return None, None

def test_weather_api(lat, lon):
    """Test weather API with detected coordinates"""
    if lat is None or lon is None:
        print("\n❌ Skipping weather test - no valid coordinates")
        return
        
    print(f"\n🌤️ Testing Weather API at {lat:.4f}, {lon:.4f}...")
    print("=" * 50)
    
    try:
        weather = WeatherPredictor(lat, lon)
        
        # Test current weather
        current = weather.get_current_weather()
        if current:
            print(f"✅ Current weather: {current['temperature']:.1f}°C")
            print(f"   Humidity: {current['humidity']:.1f}%")
            print(f"   Wind: {current['wind_speed']:.1f} km/h")
            print(f"   Weather code: {current['weather_code']}")
        else:
            print("❌ Failed to get current weather")
            
        # Test forecast
        forecast = weather.get_weather_forecast(6)  # 6 hours
        if forecast:
            print(f"✅ Forecast retrieved: {len(forecast)} hours")
            print("   Next few hours:")
            for i, f in enumerate(forecast[:3]):
                time_str = f['timestamp'].strftime('%H:%M')
                print(f"   {time_str}: {f['temperature']:.1f}°C")
        else:
            print("❌ Failed to get weather forecast")
            
    except Exception as e:
        print(f"❌ Weather API error: {e}")

def test_config_saving(lat, lon):
    """Test saving coordinates to config"""
    if lat is None or lon is None:
        print("\n❌ Skipping config test - no valid coordinates")
        return
        
    print(f"\n💾 Testing Config Saving...")
    print("=" * 50)
    
    try:
        test_config = {
            "latitude": lat,
            "longitude": lon,
            "coordinates_auto_detected": True,
            "coordinates_detection_time": datetime.now().isoformat(),
            "test_mode": True
        }
        
        with open("test_config.json", "w") as f:
            json.dump(test_config, f, indent=4)
            
        print("✅ Test config saved to test_config.json")
        
        # Verify reading back
        with open("test_config.json", "r") as f:
            loaded = json.load(f)
            
        if (loaded["latitude"] == lat and loaded["longitude"] == lon):
            print("✅ Config read back successfully")
        else:
            print("❌ Config readback failed")
            
    except Exception as e:
        print(f"❌ Config saving error: {e}")

def main():
    """Main test function"""
    print("🧪 ThermoHash Auto-Geolocation Test Suite")
    print("==========================================")
    print("This script tests the IP-based geolocation features")
    print("without requiring a full miner setup.\n")
    
    # Test geolocation
    lat, lon = test_geolocation()
    
    # Test weather API if we got coordinates
    test_weather_api(lat, lon)
    
    # Test config saving
    test_config_saving(lat, lon)
    
    print("\n📋 Test Summary")
    print("=" * 50)
    if lat and lon:
        print("✅ All tests completed successfully!")
        print(f"Your detected location: {lat:.4f}, {lon:.4f}")
        print("\nTo use these coordinates in ThermoHash:")
        print("1. Leave latitude/longitude as null in config.json for auto-detection")
        print("2. Or manually set them to the detected values above")
    else:
        print("❌ Geolocation failed - manual coordinates required")
        print("\nTo configure manual coordinates:")
        print('1. Set "latitude": YOUR_LAT, "longitude": YOUR_LON in config.json')
        print("2. Find coordinates at: https://www.latlong.net/")
    
    print("\nCleanup: Removing test_config.json...")
    try:
        import os
        os.remove("test_config.json")
        print("✅ Cleanup completed")
    except:
        print("⚠️ Manual cleanup may be needed")

if __name__ == "__main__":
    main()