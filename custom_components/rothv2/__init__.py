"""The Roth Touchline V2 integration."""

from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
