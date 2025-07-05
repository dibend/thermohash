import json
import sys
from datetime import datetime
import pytest

pytestmark = pytest.mark.network

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


def test_weather_api():
    """Test weather API with detected coordinates"""
    lat, lon = test_geolocation()
    if lat is None or lon is None:
        print("\n❌ Skipping weather test - no valid coordinates")
        pytest.skip("No valid coordinates detected")

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


def test_config_saving():
    """Test saving coordinates to config"""
    lat, lon = test_geolocation()
    if lat is None or lon is None:
        print("\n❌ Skipping config test - no valid coordinates")
        pytest.skip("No valid coordinates detected")

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