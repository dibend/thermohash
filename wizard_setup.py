import os
import json
from pathlib import Path
from typing import Optional

from thermohash_optimized import GeolocationService, WeatherPredictor, FinancialDataService

CONFIG_PATH = Path("config.json")
ENV_PATH = Path(".env")


def save_env_var(key: str, value: str):
    """Persist environment variable to a local .env file and current process."""
    if not value:
        return
    os.environ[key] = value  # Current session
    # Append or replace in .env
    lines = []
    if ENV_PATH.exists():
        with ENV_PATH.open("r") as f:
            lines = f.read().splitlines()
    found = False
    for idx, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[idx] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    with ENV_PATH.open("w") as f:
        f.write("\n".join(lines))


def prompt_api_key(name: str, env_key: str):
    current = os.getenv(env_key)
    if current:
        print(f"✓ {name} API key already set.")
        return current
    entered = input(f"Enter your {name} API key (leave blank to skip): ").strip()
    if entered:
        save_env_var(env_key, entered)
        print(f"Saved {name} API key to .env file.")
    return entered or None


def detect_location() -> Optional[tuple]:
    geo = GeolocationService()
    loc = geo.get_location_from_ip()
    if loc:
        lat, lon = loc
        print(f"Detected coordinates: {lat:.4f}, {lon:.4f}")
    else:
        print("Failed to auto-detect location.")
    return loc


def preview_weather(lat: float, lon: float):
    wp = WeatherPredictor(lat, lon)
    current = wp.get_current_weather()
    if current:
        print(
            f"Current weather: {current['temperature']:.1f}°C, "
            f"humidity {current['humidity']}%, wind {current['wind_speed']} km/h"
        )
    else:
        print("Unable to fetch current weather.")


def preview_financials():
    fin = FinancialDataService()
    btc_price = fin.get_bitcoin_price()
    hp = fin.get_hashprice_index()
    if btc_price:
        print(f"Bitcoin price: ${btc_price:,.2f}")
    if hp:
        print(
            f"Hashprice: ${hp['usd_per_th_day']:.2f}/TH/day "
            f"({hp['btc_per_th_day']:.8f} BTC/TH/day)"
        )


def save_config(lat: float, lon: float):
    config = {
        "latitude": lat,
        "longitude": lon,
    }
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = {}
        existing.update(config)
        config = existing
    with CONFIG_PATH.open("w") as f:
        json.dump(config, f, indent=4)
    print(f"Saved coordinates to {CONFIG_PATH}")


def main():
    print("==============================")
    print(" ThermoHash Setup Wizard")
    print("==============================\n")

    # Step 1: API keys
    print("Step 1/3 – Configure API Keys")
    prompt_api_key("CoinMarketCap", "COINMARKETCAP_API_KEY")
    prompt_api_key("Luxor", "LUXOR_API_KEY")

    # Step 2: Location detection
    print("\nStep 2/3 – Detect Miner Location")
    loc = detect_location()
    if not loc:
        lat = float(input("Enter latitude manually: ").strip())
        lon = float(input("Enter longitude manually: ").strip())
    else:
        lat, lon = loc
    save_config(lat, lon)

    # Step 3: Preview data
    print("\nStep 3/3 – Preview Live Data")
    preview_weather(lat, lon)
    preview_financials()

    print("\nSetup complete! You can now run ThermoHash with live data integrations.")


if __name__ == "__main__":
    main()