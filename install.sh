#!/bin/bash
# ThermoHash Optimized Installation Script for Linux

set -e

echo "=== ThermoHash Optimized Installation ==="
echo "This script will install ThermoHash with ML optimization support"
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Check if grpcurl is installed
if ! command -v grpcurl &> /dev/null; then
    echo "Installing grpcurl..."
    
    # Download and install grpcurl
    GRPCURL_VERSION="1.8.9"
    wget -q "https://github.com/fullstorydev/grpcurl/releases/download/v${GRPCURL_VERSION}/grpcurl_${GRPCURL_VERSION}_linux_x86_64.tar.gz"
    tar -xzf "grpcurl_${GRPCURL_VERSION}_linux_x86_64.tar.gz"
    sudo mv grpcurl /usr/local/bin/
    rm "grpcurl_${GRPCURL_VERSION}_linux_x86_64.tar.gz"
    
    echo "grpcurl installed successfully"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv thermohash_env
source thermohash_env/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make the script executable
chmod +x thermohash_optimized.py

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/thermohash.service > /dev/null <<EOF
[Unit]
Description=ThermoHash Optimized - Smart Bitcoin Miner Power Management
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/thermohash_env/bin
ExecStart=$(pwd)/thermohash_env/bin/python $(pwd)/thermohash_optimized.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log
sudo chmod 755 /var/log

echo
echo "=== Installation Complete ==="
echo
echo "Next steps:"
echo "1. Edit config.json with your miner details and location"
echo "2. Test the application: ./thermohash_env/bin/python thermohash_optimized.py"
echo "3. Enable automatic startup: sudo systemctl enable thermohash"
echo "4. Start the service: sudo systemctl start thermohash"
echo "5. Check logs: sudo journalctl -u thermohash -f"
echo
echo "Configuration file: config.json"
echo "Requirements file: requirements.txt"
echo "Main script: thermohash_optimized.py"
echo
echo "For Windows installation, run install.bat instead"