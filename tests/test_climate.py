import sys
import types
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.const import ATTR_TEMPERATURE

pytestmark = pytest.mark.asyncio


def load_climate():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "rothv2"
        / "climate.py"
    )
    package_name = "custom_components.rothv2"

    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(module_path.parent)]
        sys.modules[package_name] = package

    dummy_lib = types.SimpleNamespace(PyTouchline=MagicMock())
    with patch.dict(sys.modules, {"pytouchline_extended": dummy_lib}):
        spec = spec_from_file_location(f"{package_name}.climate", module_path)
        climate_module = module_from_spec(spec)
        sys.modules[f"{package_name}.climate"] = climate_module
        spec.loader.exec_module(climate_module)
    return climate_module


def create_device(
    *,
    name="Living Room",
    current_temperature=21.5,
    target_temperature=23.0,
    is_heating=True,
    operation_mode=0,
    week_program=0,
):
    device = MagicMock()
    device.update = MagicMock()
    device.get_name.return_value = name
    device.get_current_temperature.return_value = current_temperature
    device.get_target_temperature.return_value = target_temperature
    device.is_heating.return_value = is_heating
    device.get_operation_mode.return_value = operation_mode
    device.get_week_program.return_value = week_program
    device.set_target_temperature = MagicMock()
    device.set_operation_mode = MagicMock()
    device.set_week_program = MagicMock()
    device.enable_heating = MagicMock()
    device.disable_heating = MagicMock()
    return device


async def setup_entity(hass, device):
    climate = load_climate()
    coordinator = climate.TouchlineDataUpdateCoordinator(hass, MagicMock(), 30)
    coordinator.update_interval = None
    coordinator.async_request_refresh = coordinator.async_refresh
    coordinator.register_device(device)
    entity = climate.TouchlineClimate(coordinator, device, "1.1.1.1", "entry", 0)
    entity.hass = hass
    entity.entity_id = "climate.test"
    entity.platform = MagicMock()
    await entity.async_added_to_hass()
    await coordinator.async_refresh()
    return climate, entity, coordinator


async def test_initial_state(hass):
    climate, entity, _ = await setup_entity(hass, create_device())
    assert entity.current_temperature == 21.5
    assert entity.target_temperature == 23.0
    assert entity.hvac_mode == HVACMode.HEAT
    assert entity.hvac_action == HVACAction.HEATING
    assert entity.preset_mode == "Normal"
    assert entity.preset_modes == list(climate.PRESET_MODES)


async def test_set_temperature_updates_device_and_state(hass):
    device = create_device(target_temperature=22.0)
    _, entity, coordinator = await setup_entity(hass, device)
    await entity.async_set_temperature(**{ATTR_TEMPERATURE: 25})
    assert device.set_target_temperature.call_args[0][0] == 25
    device.get_target_temperature.return_value = 25
    await coordinator.async_request_refresh()
    assert entity.target_temperature == 25


async def test_set_preset_mode_sends_expected_settings(hass):
    climate, entity, coordinator = await setup_entity(hass, create_device())
    device = entity.unit
    for preset, settings in climate.PRESET_MODES.items():
        device.set_operation_mode.reset_mock()
        device.set_week_program.reset_mock()
        device.get_operation_mode.return_value = settings.mode
        device.get_week_program.return_value = settings.program
        await entity.async_set_preset_mode(preset)
        device.set_operation_mode.assert_called_once_with(settings.mode)
        device.set_week_program.assert_called_once_with(settings.program)
        await coordinator.async_request_refresh()
        assert entity.preset_mode == preset


async def test_set_hvac_mode_off_disables_heating(hass):
    device = create_device(is_heating=True)
    _, entity, coordinator = await setup_entity(hass, device)
    device.is_heating.return_value = False
    await entity.async_set_hvac_mode(HVACMode.OFF)
    device.disable_heating.assert_called_once()
    await coordinator.async_request_refresh()
    assert entity.hvac_mode == HVACMode.OFF
    assert entity.hvac_action == HVACAction.IDLE


async def test_set_hvac_mode_heat_enables_heating(hass):
    device = create_device(is_heating=False)
    _, entity, coordinator = await setup_entity(hass, device)
    device.is_heating.return_value = True
    await entity.async_set_hvac_mode(HVACMode.HEAT)
    device.enable_heating.assert_called_once()
    await coordinator.async_request_refresh()
    assert entity.hvac_mode == HVACMode.HEAT
    assert entity.hvac_action == HVACAction.HEATING


async def test_coordinator_marks_entity_unavailable_on_failure(hass):
    device = create_device()
    _, entity, coordinator = await setup_entity(hass, device)
    device.get_name.side_effect = RuntimeError("boom")
    await coordinator.async_refresh()
    assert entity.available is False


async def test_preset_roundtrip_from_device_state(hass):
    climate, entity, coordinator = await setup_entity(hass, create_device())
    device = entity.unit
    for preset, settings in climate.PRESET_MODES.items():
        device.get_operation_mode.return_value = settings.mode
        device.get_week_program.return_value = settings.program
        await coordinator.async_refresh()
        assert entity.preset_mode == preset


async def test_hvac_action_reflects_device_heating_state(hass):
    device = create_device(is_heating=True)
    _, entity, coordinator = await setup_entity(hass, device)
    device.is_heating.return_value = False
    await coordinator.async_refresh()
    assert entity.hvac_action == HVACAction.IDLE
    device.is_heating.return_value = True
    await coordinator.async_refresh()
    assert entity.hvac_action == HVACAction.HEATING
