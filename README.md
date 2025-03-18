# Smart Bitcoin Heater App

## New: ThermoHash Version S9
Learn more about ThermoHash version S9 [here](https://github.com/dibend/Thermohash_Version_S9).
<hr>

<img src="https://njweb.solutions/img/ThermoHashLogo.gif" width="90%"><b
r>
# ThermoHash - Miner Power Management Script Using `grpcurl`
**ThermoHash** is a Python script that dynamically adjusts the power target of your Braiins OS miner based on current weather conditions. It fetches weather data and modifies the miner's power consumption accordingly using **gRPC** and `grpcurl`.

## Features
- Automatically adjusts the miner's power target based on temperature thresholds.
- Utilizes `grpcurl` to communicate with Braiins OS over gRPC.
- Works with miners running **Braiins OS**.
- Compatible with **Windows** and **Linux**.

---

## Prerequisites

1. **Python 3.x** installed.
2. **`grpcurl`** installed.
3. **Braiins OS** installed on your miner.
4. **Port 50051** open and accessible on your miner for gRPC communication.

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

Create a `config.json` file in the same directory as the script to store the miner's IP/hostname, weather thresholds, and your credentials.

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
2. Open a Command Prompt and navigate to the scriptâ€™s directory.
3. Run the script:
   ```bash
   python thermohash.py
   ```

The script will immediately adjust the miner's power target and continue to do so every 10 minutes.

---

## Setup Instructions for Linux

### Step 1: Install Python and Required Libraries

1. Ensure Python 3.x is installed. Install it with:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. Install required Python libraries:
   ```bash
   pip3 install requests schedule
   ```

### Step 2: Install `grpcurl`

1. Download `grpcurl` from the [GitHub Releases page](https://github.com/fullstorydev/grpcurl/releases).
2. Extract the downloaded file and move `grpcurl` to `/usr/local/bin`:
   ```bash
   sudo mv grpcurl /usr/local/bin
   ```
3. Verify the installation by running:
   ```bash
   grpcurl --version
   ```

### Step 3: Open Port 50051 on Your Miner

Ensure that port **50051** is open on your miner. SSH into your miner and open the port using the system's firewall management tool (such as `firewalld`, `ufw`, or `iptables`).

Example using **iptables**:
```bash
sudo iptables -A INPUT -p tcp --dport 50051 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

### Step 4: Configure the Script

Follow the same instructions as for Windows to create the `config.json` file.

### Step 5: Run the Script

1. Open a terminal and navigate to the scriptâ€™s directory.
2. Run the script:
   ```bash
   python3 thermohash.py
   ```

### Optional: Set Up as a Systemd Service

To run the script automatically on startup and keep it running, you can set it up as a systemd service.

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/thermohash.service
   ```
2. Add the following configuration:
   ```ini
   [Unit]
   Description=ThermoHash Miner Power Management
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/thermohash.py
   Restart=always
   User=yourusername

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl enable thermohash.service
   sudo systemctl start thermohash.service
   ```

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
- **`grpcurl` Not Found**: Ensure `grpcurl` is in your system's `PATH`.
- **Incorrect Weather Data**: Verify the latitude and longitude values in `config.json`.

---

## Resources

- **Braiins OS**: [Braiins OS Official Site](https://braiins.com/os)
- **grpcurl**: [grpcurl GitHub](https://github.com/fullstorydev/grpcurl)
- **Python**: [Python Official Site](https://www.python.org/downloads/)

## Compatibility with AltairTech's BitChimney
ThermoHash is now compatible with AltairTech's BitChimney. BitChimney enhances ThermoHash's capabilities by providing more efficient power management and additional configuration options. For more details, visit [AltairTech's BitChimney](https://altairtech.io/product/bitchimney/?srsltid=AfmBOoqnhF02WvDTAmUuJz-_YXwjuwLPuZlx2TcJ8JoVt1ODGnEYLrGB).
<img src="https://altairtech.io/wp-content/uploads/2023/09/Bitchimneyv2_1.png" width="90%">

Also compatible with
## StealthMiner JPro+

[![StealthMiner JPro+](https://structur3.io/cdn/shop/files/stealthminer-v1.1-black-01.jpg?v=1737642194)](https://structur3.io/products/stealthminer)

The StealthMiner JPro+ is a SHA256 miner available on [Structur3.io](https://structur3.io/products/stealthminer). This efficient miner operates at 20-32TH with an average performance of 24-26 J/T in the 500-800W range. Designed for longevity and quiet operation on standard North American 120V circuits, it utilizes recycled JPro+ Hashboards and APW3++ PSUs, down clocked for efficiency. Its cooling system ensures tighter operating temperature gradients under 60dB. Powered by an AMLogic A113D Control Board running LuxOS firmware, it includes standard mining I/O and comes with a 14-day warranty. Please review the specifications for power, hardware, and environmental requirements.

