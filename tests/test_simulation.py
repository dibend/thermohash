import pytest

from thermohash_optimized import ThermoHashOptimized


def test_simulation_mode_runs():
    """Ensure the application runs one adjustment cycle in simulation mode without errors."""
    app = ThermoHashOptimized(simulate=True)
    # Run a single adjustment; should not raise and should set a power target
    app.adjust_power_based_on_weather()
    assert app.last_power_target is not None