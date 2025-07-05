"""Pytest configuration to control optional network/API-key tests.

Usage:
    pytest             # run standard, non-network tests (network & apikey tests are skipped)
    pytest --run-network      # include tests that need internet but no API key
    pytest --run-network --run-apikey   # include all tests (network + API key)
    pytest --run-apikey       # include only API-key tests (also implies network)
"""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:  # type: ignore[type-arg]
    group = parser.getgroup("thermohash optional tests")
    group.addoption(
        "--run-network",
        action="store_true",
        default=False,
        help="Run tests that require an internet connection (no API key)",
    )
    group.addoption(
        "--run-apikey",
        action="store_true",
        default=False,
        help="Run tests that require valid API keys (implies --run-network)",
    )


def pytest_configure(config: pytest.Config) -> None:  # type: ignore[type-arg]
    # Register custom markers so 'pytest --markers' lists them and to avoid warnings
    config.addinivalue_line("markers", "network: test requires an internet connection")
    config.addinivalue_line("markers", "apikey: test requires a valid API key and internet connection")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:  # type: ignore[type-arg]
    run_network = config.getoption("--run-network") or config.getoption("--run-apikey")
    run_apikey = config.getoption("--run-apikey")

    skip_network = pytest.mark.skip(reason="need --run-network option to run")
    skip_apikey = pytest.mark.skip(reason="need --run-apikey option to run (requires API key)")

    for item in items:
        if "apikey" in item.keywords and not run_apikey:
            item.add_marker(skip_apikey)
        elif "network" in item.keywords and not run_network:
            item.add_marker(skip_network)