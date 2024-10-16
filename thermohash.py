import schedule
import time
import os
import json
import requests
import logging

# Setup logging for very verbose output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.json
logging.debug("Loading configuration from config.json")
with open("config.json", "r") as config_file:
    config = json.load(config_file)

LATITUDE = float(config["latitude"])
LONGITUDE = float(config["longitude"])
MINER_ADDRESS = config["miner_address"]  # This can be either a hostname or an IP address
USERNAME = config["username"]
PASSWORD = config["password"]

# Temperature thresholds and power targets (ensure they are handled as floats)
TEMP_THRESHOLDS = {float(threshold): float(power) for threshold, power in config["temp_thresholds"].items()}

# Function to get the current temperature using Open-Meteo API
def get_current_temperature(lat, lon):
    logging.debug(f"Fetching current temperature for coordinates: {lat}, {lon}")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    data = response.json()
    temperature_celsius = data["current_weather"]["temperature"]  # Temperature in Celsius
    logging.debug(f"Temperature data retrieved: {temperature_celsius}°C")
    return float(temperature_celsius)

# Function to authenticate and get the session token
def authenticate():
    logging.debug(f"Authenticating with the miner at {MINER_ADDRESS}")
    # Properly format the grpcurl command with correct JSON formatting for username and password
    auth_command = f'grpcurl -plaintext -d \'{{"username":"{USERNAME}","password":"{PASSWORD}"}}\' {MINER_ADDRESS}:50051 braiins.bos.v1.AuthenticationService/Login'
    logging.debug(f"Running command: {auth_command}")
    
    stream = os.popen(auth_command)
    output = stream.read()

    logging.debug(f"Authentication output: {output}")
    token_line = [line for line in output.split('\n') if "authorization" in line]
    
    if token_line:
        token = token_line[0].split(": ")[1].strip()
        logging.debug(f"Authentication successful. Token: {token}")
        return token
    else:
        logging.error("Failed to authenticate. No token received.")
        return None

# Function to set the miner's power target using grpcurl
def set_power_target(power_target, token):
    logging.debug(f"Setting power target to {power_target} watts for the miner.")
    # Properly format the grpcurl command with the authorization token and power target
    set_command = f'grpcurl -plaintext -H "authorization:{token}" -d \'{{"power_target":{{"watt":"{power_target}"}},"save_action":2}}\' {MINER_ADDRESS}:50051 braiins.bos.v1.PerformanceService/SetPowerTarget'
    logging.debug(f"Running command: {set_command}")
    
    result = os.system(set_command)
    if result == 0:
        logging.info(f"Power target successfully set to {power_target} watts.")
    else:
        logging.error(f"Failed to set power target. Command exited with code {result}.")

# Function to adjust power based on temperature
def adjust_power_based_on_weather():
    logging.debug(f"Adjusting power based on current temperature at ({LATITUDE}, {LONGITUDE})")
    temperature = get_current_temperature(LATITUDE, LONGITUDE)
    logging.info(f"Current temperature at ({LATITUDE}, {LONGITUDE}): {temperature}°C")

    # Determine the appropriate power target based on the temperature thresholds
    power_target = None
    for threshold, power in sorted(TEMP_THRESHOLDS.items()):
        logging.debug(f"Checking if temperature {temperature}°C <= threshold {threshold}°C")
        if temperature <= threshold:
            power_target = power
            logging.debug(f"Temperature {temperature}°C is below or equal to {threshold}°C, setting power to {power_target} watts")
            break

    if power_target is not None:
        # Authenticate to get the token
        token = authenticate()
        if token:
            set_power_target(power_target, token)
        else:
            logging.error("No token available, cannot set power target.")
    else:
        logging.error("No valid power target found for the current temperature.")

# Execute the function immediately when the script starts
logging.info("Script started, tuning the miner immediately.")
adjust_power_based_on_weather()

# Schedule the task to run every 10 minutes
schedule.every(10).minutes.do(adjust_power_based_on_weather)

# Run the scheduler
logging.info("Scheduler running, will adjust power every 10 minutes.")
while True:
    schedule.run_pending()
    time.sleep(1)
