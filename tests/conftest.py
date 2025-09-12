"""Fixtures for testing the Roth Touchline V2 integration."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("homeassistant")
pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

DOMAIN = "rothv2"

# Ensure the custom_components package is importable
sys.path.append(str(Path(__file__).resolve().parents[1]))


class MockPyTouchline:
    """Mock PyTouchline class."""

    def __init__(self, url=None) -> None:
        """Initialize the mock."""
        self.url = url

    def get_number_of_devices(self):
        """Return the number of devices."""
        return "1"


@pytest.fixture(name="skip_notifications_fixture", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


@pytest.fixture(name="mock_pytouchline_extended")
def mock_pytouchline_extended_fixture():
    """Mock pytouchline_extended."""
    mock_module = type("pytouchline_extended", (), {"PyTouchline": MockPyTouchline})
    with patch.dict(sys.modules, {"pytouchline_extended": mock_module}):
        yield


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "1.1.1.1"},
        title="Roth Touchline (1.1.1.1)",
    )
