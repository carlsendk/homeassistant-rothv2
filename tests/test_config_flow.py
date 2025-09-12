"""Test the Roth Touchline V2 config flow."""

import sys
import types
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResultType

DOMAIN = "rothv2"

pytestmark = pytest.mark.asyncio


def load_config_flow():
    """Load the config_flow module directly."""
    module_path = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "rothv2"
        / "config_flow.py"
    )
    package_name = "custom_components.rothv2"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(module_path.parent)]
        sys.modules[package_name] = package
    spec = spec_from_file_location(f"{package_name}.config_flow", module_path)
    config_flow = module_from_spec(spec)
    spec.loader.exec_module(config_flow)
    return config_flow


async def test_form(hass, mock_pytouchline_extended):
    """Test we get the form."""
    config_flow = load_config_flow()
    flow = config_flow.RothV2ConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.rothv2.config_flow.PyTouchline.get_number_of_devices",
        return_value="1",
    ):
        result2 = await flow.async_step_user({CONF_HOST: "1.1.1.1"})

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Roth Touchline (1.1.1.1)"
    assert result2["data"] == {CONF_HOST: "1.1.1.1"}


async def test_form_cannot_connect(hass, mock_pytouchline_extended):
    """Test we handle cannot connect error."""
    config_flow = load_config_flow()
    flow = config_flow.RothV2ConfigFlow()
    flow.hass = hass

    with patch(
        "custom_components.rothv2.config_flow.PyTouchline.get_number_of_devices",
        side_effect=ConnectionError,
    ):
        result = await flow.async_step_user({CONF_HOST: "1.1.1.1"})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
