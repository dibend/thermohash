import schedule
import time
import os
import json
import requests
import logging
from subprocess import Popen, PIPE

# Setup logging to file for persistent logs
logging.basicConfig(filename='/var/log/thermohash.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.json
logging.debug("Loading configuration from config.json")
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    logging.error("Config file not found. Ensure config.json is in the script's directory.")
    exit(1)
except json.JSONDecodeError:
    logging.error("Config file is not in proper JSON format.")
    exit(1)

# Environment-based configuration for sensitive information
LATITUDE = float(config.get("latitude"))
LONGITUDE = float(config.get("longitude"))
MINER_ADDRESS = config.get("miner_address")
USERNAME = os.getenv("MINER_USERNAME", config.get("username"))
PASSWORD = os.getenv("MINER_PASSWORD", config.get("password"))

# Temperature thresholds and power targets
TEMP_THRESHOLDS = {float(threshold): float(power) for threshold, power in config["temp_thresholds"].items()}
MAX_POWER = max(TEMP_THRESHOLDS.values())
MIN_POWER = min(TEMP_THRESHOLDS.values())

def get_current_temperature(lat, lon):
    """Get the current temperature using Open-Meteo API."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temperature_celsius = data["current_weather"]["temperature"]
        logging.debug(f"Temperature data retrieved: {temperature_celsius}°C")
        return float(temperature_celsius)
    except requests.RequestException as e:
        logging.error(f"Error fetching temperature data: {e}")
        return None

def authenticate():
    """Authenticate and retrieve session token."""
    logging.debug(f"Authenticating with the miner at {MINER_ADDRESS}")
    auth_command = f'grpcurl -plaintext -d \'{{"username":"{USERNAME}","password":"{PASSWORD}"}}\' {MINER_ADDRESS}:50051 braiins.bos.v1.AuthenticationService/Login'

    process = Popen(auth_command, shell=True, stdout=PIPE, stderr=PIPE)
    output, error = process.communicate()

    if process.returncode == 0:
        for line in output.decode().split('\n'):
            if "authorization" in line:
                token = line.split(": ")[1].strip()
                logging.debug(f"Authentication successful. Token: {token}")
                return token
    else:
        logging.error(f"Authentication failed: {error.decode()}")
    return None

def set_power_target(power_target, token):
    """Set the miner's power target using grpcurl."""
    logging.debug(f"Setting power target to {power_target} watts for the miner.")
    set_command = f'grpcurl -plaintext -H "authorization:{token}" -d \'{{"power_target":{{"watt":"{power_target}"}},"save_action":2}}\' {MINER_ADDRESS}:50051 braiins.bos.v1.PerformanceService/SetPowerTarget'

    process = Popen(set_command, shell=True, stdout=PIPE, stderr=PIPE)
    _, error = process.communicate()

    if process.returncode == 0:
        logging.info(f"Power target successfully set to {power_target} watts.")
    else:
        logging.error(f"Failed to set power target. Error: {error.decode()}")

def adjust_power_based_on_weather():
    """Adjust power setting based on the current temperature."""
    logging.debug(f"Adjusting power based on current temperature at ({LATITUDE}, {LONGITUDE})")
    temperature = get_current_temperature(LATITUDE, LONGITUDE)

    if temperature is None:
        logging.error("Could not retrieve temperature data. Skipping power adjustment.")
        return

    power_target = None
    if temperature <= min(TEMP_THRESHOLDS):
        power_target = MIN_POWER
        logging.debug(f"Temperature {temperature}°C is below the lowest threshold. Setting power to minimum: {MIN_POWER} watts.")
    elif temperature >= max(TEMP_THRESHOLDS):
        power_target = MAX_POWER
        logging.debug(f"Temperature {temperature}°C is above the highest threshold. Setting power to maximum: {MAX_POWER} watts.")
    else:
        for threshold, power in sorted(TEMP_THRESHOLDS.items()):
            if temperature <= threshold:
                power_target = power
                logging.debug(f"Temperature {temperature}°C is below or equal to {threshold}°C, setting power to {power_target} watts")
                break

    if power_target is not None:
        token = authenticate()
        if token:
            set_power_target(power_target, token)
        else:
            logging.error("Authentication failed, cannot set power target.")
    else:
        logging.error("No valid power target found for the current temperature.")

# Execute immediately when the script starts
logging.info("Script started, tuning the miner immediately.")
adjust_power_based_on_weather()

# Schedule the task to run every 10 minutes
schedule.every(10).minutes.do(adjust_power_based_on_weather)

# Run the scheduler
logging.info("Scheduler running, will adjust power every 10 minutes.")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Script stopped manually.")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
