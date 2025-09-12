"""Platform for Roth Touchline floor heating controller."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, ClassVar, NamedTuple

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, CONF_HOST, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from pytouchline_extended import PyTouchline

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, ICON_THERMOSTAT, UNIQUE_ID_BASE

_LOGGER = logging.getLogger(__name__)


class PresetMode(NamedTuple):
    """Settings for preset mode."""

    mode: int
    program: int


PRESET_MODES = {
    "Normal": PresetMode(mode=0, program=0),
    "Night": PresetMode(mode=1, program=0),
    "Holiday": PresetMode(mode=2, program=0),
    "Pro 1": PresetMode(mode=0, program=1),
    "Pro 2": PresetMode(mode=0, program=2),
    "Pro 3": PresetMode(mode=0, program=3),
}

TOUCHLINE_HA_PRESETS = {
    (settings.mode, settings.program): preset
    for preset, settings in PRESET_MODES.items()
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Roth Touchline climate platform from config entry."""
    host = entry.data[CONF_HOST]
    controller = hass.data[DOMAIN][entry.entry_id]["controller"]

    coordinator = TouchlineDataUpdateCoordinator(
        hass, controller, DEFAULT_SCAN_INTERVAL
    )

    number_of_devices = int(controller.get_number_of_devices())
    entities: list[TouchlineClimate] = []

    for device_id in range(number_of_devices):
        touchline_device = PyTouchline(id=device_id, url=host)
        coordinator.register_device(touchline_device)
        entities.append(
            TouchlineClimate(
                coordinator, touchline_device, host, entry.entry_id, device_id
            )
        )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(entities)


class TouchlineDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage data updates from the Touchline controller."""

    def __init__(
        self, hass: HomeAssistant, controller: PyTouchline, update_interval: int
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.controller = controller
        self.devices: list[PyTouchline] = []

    def register_device(self, device: PyTouchline) -> None:
        """Register a device for coordinated updates."""
        self.devices.append(device)

    async def _async_update_data(self):
        """Fetch data from Touchline devices."""
        for idx, device in enumerate(self.devices):
            try:
                await self.hass.async_add_executor_job(device.update)
            except Exception as err:
                _LOGGER.error("Error updating Touchline device %s: %s", idx, err)
        return None


class TouchlineClimate(CoordinatorEntity[TouchlineDataUpdateCoordinator], ClimateEntity):
    """Representation of a Touchline climate device."""

    _attr_hvac_mode = HVACMode.HEAT
    _attr_hvac_modes: ClassVar[list[HVACMode]] = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True
    _attr_name = None
    _attr_icon = ICON_THERMOSTAT

    def __init__(
        self,
        coordinator: TouchlineDataUpdateCoordinator,
        touchline_thermostat: PyTouchline,
        host: str,
        entry_id: str | None,
        device_id: int,
    ) -> None:
        """Initialize the Touchline device."""
        super().__init__(coordinator)
        self.unit = touchline_thermostat
        self._device_id = device_id
        self._host = host
        self._entry_id = entry_id
        self._attr_unique_id = UNIQUE_ID_BASE.format(f"{host}_{device_id}")

        self._current_temperature: float | None = None
        self._target_temperature: float | None = None
        self._hvac_mode = HVACMode.HEAT
        self._hvac_action: HVACAction | None = None
        self._preset_mode: str | None = None
        self._available = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=self.name,
            manufacturer="Roth",
            model="Touchline Controller",
            via_device=(DOMAIN, f"controller_{self._host}"),
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            self._available = True
            self._attr_name = self.unit.get_name()
            self._current_temperature = self.unit.get_current_temperature()
            self._target_temperature = self.unit.get_target_temperature()

            if self.unit.is_heating():
                self._hvac_action = HVACAction.HEATING
            else:
                self._hvac_action = HVACAction.IDLE

            self._preset_mode = TOUCHLINE_HA_PRESETS.get(
                (self.unit.get_operation_mode(), self.unit.get_week_program())
            )
        except Exception as ex:
            _LOGGER.error("Error updating Touchline device %s: %s", self._device_id, ex)
            self._available = False
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._available

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation mode."""
        return self._hvac_mode

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation."""
        return self._hvac_action

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        return self._preset_mode

    @property
    def preset_modes(self):
        """Return available preset modes."""
        return list(PRESET_MODES)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new target preset mode."""
        preset_mode_settings = PRESET_MODES[preset_mode]
        await self.hass.async_add_executor_job(
            self.unit.set_operation_mode, preset_mode_settings.mode
        )
        await self.hass.async_add_executor_job(
            self.unit.set_week_program, preset_mode_settings.program
        )
        self._preset_mode = preset_mode
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.HEAT:
            await self.hass.async_add_executor_job(self.unit.enable_heating)
            self._hvac_mode = HVACMode.HEAT
        elif hvac_mode == HVACMode.OFF:
            await self.hass.async_add_executor_job(self.unit.disable_heating)
            self._hvac_mode = HVACMode.OFF
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
            await self.hass.async_add_executor_job(
                self.unit.set_target_temperature, self._target_temperature
            )
            await self.coordinator.async_request_refresh()
