# API Key Storage Best Practices

## Overview
Proper API key management is crucial for security. Never commit API keys, passwords, or sensitive tokens to version control.

## Recommended Approaches (in order of preference)

### 1. Environment Variables (.env file) ⭐ **RECOMMENDED**

Create a `.env` file in your project root:

```bash
# .env file
WEATHER_API_KEY=your_weather_api_key
BITCOIN_API_KEY=your_bitcoin_api_key
MINER_USERNAME=root
MINER_PASSWORD=your_secure_password
OPENWEATHER_API_KEY=your_openweather_key
GEOLOCATION_API_KEY=your_geolocation_key
```

**Important**: Add `.env` to your `.gitignore` file:
```
# Add to .gitignore
.env
*.env
config/secrets.json
```

**Usage in Python**:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv('WEATHER_API_KEY')
miner_password = os.getenv('MINER_PASSWORD')
```

**Install python-dotenv**:
```bash
pip install python-dotenv
```

### 2. System Environment Variables

Set environment variables at the system level:

```bash
# Linux/macOS
export WEATHER_API_KEY="your_api_key_here"
export MINER_PASSWORD="your_password"

# Windows
set WEATHER_API_KEY=your_api_key_here
set MINER_PASSWORD=your_password
```

**Usage**:
```python
import os
api_key = os.getenv('WEATHER_API_KEY')
```

### 3. Separate Configuration Files (Not in Git)

Create a `secrets.json` or `private_config.json` file:

```json
{
    "weather_api_key": "your_weather_api_key",
    "bitcoin_api_key": "your_bitcoin_api_key",
    "miner_credentials": {
        "username": "root",
        "password": "your_secure_password"
    }
}
```

**Usage**:
```python
import json

with open('secrets.json', 'r') as f:
    secrets = json.load(f)
    
weather_api_key = secrets['weather_api_key']
```

### 4. Cloud Secret Management (Production)

For production deployments:
- **AWS**: AWS Secrets Manager or Parameter Store
- **Azure**: Azure Key Vault
- **Google Cloud**: Secret Manager
- **Docker**: Docker Secrets

## Current Project Recommendations

### For Your ThermoHash Project:

1. **Move sensitive data from `config.json`**:
   - The current `config.json` contains `username` and `password`
   - These should be moved to environment variables

2. **Create a `.env` file**:
```bash
# .env
MINER_USERNAME=root
MINER_PASSWORD=your_actual_password
WEATHER_API_KEY=your_weather_api_key
BITCOIN_API_KEY=your_bitcoin_api_key
```

3. **Update your Python code**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Replace hardcoded credentials
USERNAME = os.getenv('MINER_USERNAME', 'root')  # fallback to 'root'
PASSWORD = os.getenv('MINER_PASSWORD')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
```

4. **Update `config.json`**:
```json
{
    "latitude": null,
    "longitude": null,
    "miner_address": "192.168.1.100",
    // Remove username and password - use environment variables instead
    "temp_thresholds": {
        // ... rest of your config
    }
}
```

## Security Checklist

- [ ] API keys not in source code
- [ ] `.env` file added to `.gitignore`
- [ ] Different keys for different environments (dev/staging/prod)
- [ ] Regular key rotation
- [ ] Least privilege access
- [ ] Monitor for exposed keys (GitHub secret scanning)

## Common Mistakes to Avoid

❌ **Don't do this**:
```python
API_KEY = "abc123secret"  # Hardcoded in source
```

❌ **Don't commit**:
- `.env` files
- `secrets.json` files
- Any file with actual API keys

✅ **Do this**:
```python
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")
```

## Example Implementation

For your specific project, here's how to implement secure credential management:

1. Install dependencies:
```bash
pip install python-dotenv
```

2. Create `.env` file with your actual values
3. Add to `.gitignore`:
```
.env
```

4. Update your authentication code:
```python
import os
from dotenv import load_dotenv

load_dotenv()

MINER_ADDRESS = "192.168.1.100"  # This can stay in config
USERNAME = os.getenv('MINER_USERNAME')
PASSWORD = os.getenv('MINER_PASSWORD')

def authenticate():
    if not USERNAME or not PASSWORD:
        raise ValueError("Miner credentials not found in environment variables")
    # ... rest of authentication logic
```

This approach keeps your code secure while maintaining functionality.