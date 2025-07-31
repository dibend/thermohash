# ThermoHash 🌡️– AI-Powered Bitcoin Miner & Heat-Reuse Platform

[![GitHub Sponsors](https://img.shields.io/github/sponsors/dibend?style=social)](https://github.com/sponsors/dibend)
[![License](https://img.shields.io/github/license/dibend/thermohash)](LICENSE)

From a single S19 keeping your living-room cozy to an institutional-scale blockchain datacenter running **thousands** of ASICs – **ThermoHash** turns excess mining heat into intelligent, profitable energy while slashing setup time to *minutes*.

---

## ✨ What's NEW

1. **Zero-Config IP Geolocation** – auto-detects your coordinates to pull hyper-local weather forecasts (fallback to manual).  
2. **Machine-Learning Optimizer** – TensorFlow-powered neural network predicts the *optimal* wattage ahead of weather changes.  
3. **Bitcoin-Price & Hashprice Intelligence** – dynamically throttles power to protect margins during price swings.  
4. **One-Line Installers** – `install.sh` & `install.bat` handle everything (Python, virtual-env, grpcurl, systemd).  
5. **Interactive Setup Wizard** – guided CLI (`wizard_setup.py`) stores API keys, detects location, previews live data.  
6. **Cross-Platform, Single Script** – one code-base for Linux, Windows, bare-metal or containers.  
7. **Smooth Power-Smoothing Algorithm** – eliminates rapid watt jumps, prolonging miner life.  
8. **Comprehensive Logging & Metrics** – granular INFO/DEBUG streams plus daily profit reports.
9. **Immersion & Heat-Reuse Ready** – validated with FogHashing, BitChimney, StealthMiner JPro+, and more.
10. **Web-Based Setup Wizard** – run `web_wizard.py` for browser configuration and automatic miner discovery.

> **Ready in 5 minutes. Saves for a lifetime.**

---

## 🏡 For the Home Hobbyist

* **Whisper-Quiet Efficiency** – run a down-clocked S19 on 120 V without tripping breakers.
* **Automatic Comfort Mode** – maintain a target room temperature; excess hash shuts off politely.
* **Heat-Reuse Guides** – detailed immersion and radiator tutorials included.

## 🏭 For the Industrial Datacenter

* **Multi-Miner Scaling** – drop-in support for Braiins OS & LuxOS fleets (gRPC API).
* **Financial Guardrails** – pause or reduce power when profit margins dip below your SLA.
* **Ops Friendly** – systemd services, Prometheus-ready logs, and REST hooks (coming soon).

---

## 🚀 Quick Start

```bash
# 1. Clone & install (Linux)
git clone https://github.com/dibend/thermohash.git && cd thermohash
chmod +x install.sh && ./install.sh

# 2. Run the interactive wizard (CLI)
python wizard_setup.py

# 3. Optional web wizard
python web_wizard.py  # then open http://localhost:8000

# 4. Launch!
python thermohash_optimized.py
```
*Windows users:* just double-click `install.bat`.

## 🧪 Running Tests

ThermoHash includes a lightweight test-suite powered by **pytest**. Running it is optional but recommended after you make changes or before you submit a pull-request.

```bash
# From the repository root
pip install -r requirements.txt  # if you did not run install.sh / install.bat
pytest -q                        # execute all tests quietly
```

Notes:
1. The geolocation test requires external network calls and is **skipped by default** via `pytest.skip(...)` – the rest of the suite is fully offline-friendly.
2. Use `pytest -vv` for verbose output or `pytest tests/` to target a specific folder.
3. Feel free to remove the skip marker if you wish to test the live geolocation flow.

---

## 📚 Feature Deep-Dive

| Category | Highlights |
|----------|------------|
| Weather Intelligence | IP geolocation, OpenMeteo 72-h forecast, humidity & wind analysis |
| Machine Learning | 32→16→8→1 dense NN, auto-retraining every 7 days, >20 % efficiency gain |
| Financial Insight | CoinGecko price feed, Luxor hashprice, profitability-aware throttling |
| Power Control | gRPC `SetPowerTarget`, exponential smoothing, multi-level fallback |
| Installation | Automated scripts, virtual-envs, env-var secret storage |
| Logging & Monitoring | JSON logs, rotating files, optional Prometheus exporter |
| Compatibility | Braiins OS, LuxOS, BitChimney, StealthMiner, immersion tanks |

---

## 💖 Support & Sponsorship

ThermoHash is 100 % open-source and community-driven.  If this project reduces your heating bill or boosts your farm's bottom line, please consider becoming a [GitHub Sponsor](https://github.com/sponsors/dibend).  Every sponsorship accelerates:

* Multi-miner orchestration
* Web & mobile dashboards
* Native Prometheus/Grafana integration
* Advanced ML models & edge deployments


---

## 📄 Documentation & Resources

* **Full User Guide:** [`README_OPTIMIZED.md`](README_OPTIMIZED.md)  
* **Implementation & Improvements:** [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) / [`IMPROVEMENTS_SUMMARY.md`](IMPROVEMENTS_SUMMARY.md)  
* **Weather + Financial API details:** see inline docstrings.  
---

### 👥 Join the Community

* GitHub Issues for bugs & feature requests
* Pull Requests welcome

---
<!-- FogHashing gallery removed to keep repository size small -->

---

> **ThermoHash** – because *your* hash-rate should power *your* world.
