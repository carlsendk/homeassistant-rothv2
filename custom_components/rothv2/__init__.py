"""The Roth Touchline V2 integration."""

from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.typing import ConfigType
from pytouchline_extended import PyTouchline

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CLIMATE]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required(CONF_HOST): cv.string,
        })
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Roth Touchline V2 component."""
    hass.data[DOMAIN] = {}

    if DOMAIN not in config:
        return True

    # Process config from configuration.yaml
    host = config[DOMAIN][CONF_HOST]
    hass.data[DOMAIN]["config"] = config[DOMAIN]

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Roth Touchline V2 from a config entry."""
    host = entry.data[CONF_HOST]

    try:
        py_touchline = PyTouchline(url=host)
        # Test the connection
        number_of_devices = int(py_touchline.get_number_of_devices())
        _LOGGER.info("Found %s Roth Touchline devices", number_of_devices)
    except Exception as ex:
        _LOGGER.error("Unable to connect to Roth Touchline controller: %s", ex)
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "controller": py_touchline,
        "host": host,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_refresh_devices(call: ServiceCall) -> None:
        """Handle the refresh_devices service call."""
        device_id = call.data.get("device_id")

        for entry_id, data in hass.data[DOMAIN].items():
            if isinstance(data, dict) and "controller" in data:
                controller = data["controller"]
                try:
                    # If device_id specified, only refresh that device
                    if device_id:
                        # Convert device ID to controller device number
                        # This is a simplified example and might need adjustment
                        controller_device_id = device_id.split("_")[-1]
                        controller.refresh_device(controller_device_id)
                    else:
                        # Refresh all devices
                        controller.refresh_all()
                    _LOGGER.info("Refreshed Roth Touchline devices")
                except Exception as ex:
                    _LOGGER.error("Error refreshing devices: %s", ex)

    async def handle_set_week_program(call: ServiceCall) -> None:
        """Handle the set_week_program service call."""
        device_id = call.data.get("device_id")
        program = call.data.get("program")

        if not device_id or program is None:
            _LOGGER.error("Missing required fields for set_week_program service")
            return

        # This is a simplified example - you would need to implement the logic
        # to find the correct device object based on the device_id
        for entry_id, data in hass.data[DOMAIN].items():
            if isinstance(data, dict) and "controller" in data:
                # You would need to implement this part based on how your devices are stored
                _LOGGER.info(
                    "Setting week program %s for device %s", program, device_id
                )

    hass.services.async_register(DOMAIN, "refresh_devices", handle_refresh_devices)
    hass.services.async_register(DOMAIN, "set_week_program", handle_set_week_program)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
