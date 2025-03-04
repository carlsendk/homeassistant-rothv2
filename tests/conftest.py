"""Fixtures for testing the Roth Touchline V2 integration."""

import sys
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.rothv2.const import DOMAIN


# This fixture enables loading custom integrations in all tests.
# Remove this fixture if you don't need it.
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


# Mock PyTouchline class
class MockPyTouchline:
    """Mock PyTouchline class."""

    def __init__(self, url=None):
        """Initialize the mock."""
        self.url = url

    def get_number_of_devices(self):
        """Return the number of devices."""
        return "1"


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications_fixture", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


# This fixture patches the PyTouchline class
@pytest.fixture(name="mock_pytouchline_extended")
def mock_pytouchline_extended_fixture():
    """Mock pytouchline_extended."""
    with patch.dict(sys.modules, {"pytouchline_extended": MockPyTouchline}):
        yield


# This fixture creates a mock entry for testing
@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "1.1.1.1"},
        title="Roth Touchline (1.1.1.1)",
    )
