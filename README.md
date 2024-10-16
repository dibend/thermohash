
# ThermoHash - Miner Power Management Script Using `grpcurl`

**ThermoHash** is a Python script that dynamically adjusts the power target of your Braiins OS miner based on current weather conditions. The script fetches weather data and modifies the miner’s power consumption accordingly using **gRPC** and `grpcurl`.

## Features
- Automatically adjusts the miner's power target based on temperature thresholds.
- Utilizes `grpcurl` to communicate with Braiins OS over gRPC.
- Works with miners running **Braiins OS**.
- Compatible with Windows.

## Prerequisites

1. **Windows Operating System**.
2. **Python 3.x** installed.
3. **`grpcurl`** installed.
4. **Braiins OS** installed on your miner.
5. **Port 50051** open and accessible on your miner for gRPC communication.

---

## Setup Instructions for Windows

### Step 1: Install Python

1. Download and install Python 3.x from [python.org](https://www.python.org/downloads/).
2. During installation, ensure you check the box to **add Python to PATH**.
3. Verify the installation by opening a Command Prompt and running:
   ```bash
   python --version
   ```

### Step 2: Install Required Python Libraries

This script requires `requests` for fetching weather data and `schedule` for scheduling periodic checks.

1. Open a Command Prompt and install them using `pip`:
   ```bash
   pip install requests schedule
   ```
password
### Step 3: Download and Install `grpcurl`

1. Download `grpcurl` from the official [GitHub Releases page](https://github.com/fullstorydev/grpcurl/releases).
2. Extract the ZIP file and move `grpcurl.exe` to a directory included in your system's `PATH` (e.g., `C:\Windows\System32`).
3. Verify the installation by running:
   ```bash
   grpcurl --version
   ```

### Step 4: Open Port 50051 on Your Miner

Ensure that port **50051** is open on your miner. SSH into your miner and open the port using the system's firewall management tool (such as `firewalld`, `ufw`, or `iptables`).

Example using **iptables**:
```bash
iptables -A INPUT -p tcp --dport 50051 -j ACCEPT
/etc/init.d/iptables save
```

### Step 5: Configure the Script

Create a `config.json` file in the same directory as the script to store the miner’s IP/hostname, weather thresholds, and your credentials.

Example `config.json`:
```json
{
    "latitude": 40.6982,
    "longitude": -74.4014,
    "miner_address": "192.168.1.100",
    "username": "root",
    "password": "your_password",
    "temp_thresholds": {
        "10.0": 1000,
        "20.0": 800,
        "30.0": 600,
        "40.0": 400
    }
}
```

- Replace the latitude and longitude with your location.
- Replace `miner_address` with your miner's IP or hostname.
- Set `temp_thresholds` to adjust the power target (in watts) based on temperature (in degrees Celsius).

### Step 6: Run the Script

1. Download the `thermohash.py` Python script and place it in the same directory as `config.json`.
2. Open a Command Prompt and navigate to the script’s directory.
3. Run the script:
   ```bash
   python thermohash.py
   ```

The script will immediately adjust the miner's power target and continue to do so every 10 minutes.

---

## Testing the `grpcurl` Commands

To manually test the `grpcurl` commands:

1. **Authenticate** to get a session token:
   ```bash
   grpcurl -plaintext -d '{"username":"root","password":"your_password"}' 192.168.1.100:50051 braiins.bos.v1.AuthenticationService/Login
   ```

2. **Set the power target** (e.g., 1000 watts) using the token:
   ```bash
   grpcurl -plaintext -H "authorization:your_token" -d '{"save_action": 2, "power_target": {"watt": 1000}}' 192.168.1.100:50051 braiins.bos.v1.PerformanceService/SetPowerTarget
   ```

---

## Troubleshooting

- **Connection Refused**: Ensure that port 50051 is open on your miner and accessible from your network.
- **`grpcurl` Not Found**: Ensure `grpcurl.exe` is in your system’s `PATH`.
- **Incorrect Weather Data**: Verify the latitude and longitude values in `config.json`.

---

## Resources

- **Braiins OS**: [Braiins OS Official Site](https://braiins.com/os)
- **grpcurl**: [grpcurl GitHub](https://github.com/fullstorydev/grpcurl)
- **Python**: [Python Official Site](https://www.python.org/downloads/)
