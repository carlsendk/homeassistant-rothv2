"""Config flow for Roth Touchline V2 integration."""

from __future__ import annotations

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from pytouchline_extended import PyTouchline

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]

    try:
        py_touchline = PyTouchline(url=host)
        # Test the connection
        number_of_devices = int(py_touchline.get_number_of_devices())
        if number_of_devices <= 0:
            raise Exception("No devices found")
    except Exception as ex:
        _LOGGER.error("Could not connect to Roth Touchline controller: %s", ex)
        raise ValueError("Could not connect to controller") from ex

    # Return info that you want to store in the config entry.
    return {"title": f"Roth Touchline ({host})"}


class RothV2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Roth Touchline V2."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except ValueError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_info):
        """Set up this integration using configuration.yaml."""
        return await self.async_step_user(import_info)
