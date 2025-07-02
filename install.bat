@echo off
REM ThermoHash Optimized Installation Script for Windows

echo === ThermoHash Optimized Installation ===
echo This script will install ThermoHash with ML optimization support
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is required but not found. Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if grpcurl is installed
grpcurl --version >nul 2>&1
if errorlevel 1 (
    echo grpcurl is required but not found.
    echo Please download grpcurl from: https://github.com/fullstorydev/grpcurl/releases
    echo Extract grpcurl.exe to a folder in your PATH or the same directory as this script
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv thermohash_env
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call thermohash_env\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo === Installation Complete ===
echo.
echo Next steps:
echo 1. Edit config.json with your miner details and location
echo 2. Test the application: thermohash_env\Scripts\python thermohash_optimized.py
echo 3. To run automatically, create a scheduled task or run at startup
echo.
echo Configuration file: config.json
echo Requirements file: requirements.txt
echo Main script: thermohash_optimized.py
echo.
echo To run ThermoHash:
echo thermohash_env\Scripts\python thermohash_optimized.py
echo.
pause