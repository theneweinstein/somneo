"""Platform for light integration."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.light import (
    LightEntity,
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SmartSleepEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add SmartSleep light from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    async_add_entities(
        [
            SmartSleepLight(coordinator, unique_id, name, device_info, "light"),
            SmartSleepNightLight(coordinator, unique_id, name, device_info, "nightlight"),
            SmartSleepSunset(coordinator, unique_id, name, device_info, "sunset")
        ],
        update_before_add=True,
    )


class SmartSleepLight(SmartSleepEntity, LightEntity):
    """Representation of an SmartSleep Light."""

    _attr_should_poll = True
    _attr_supported_features = SUPPORT_BRIGHTNESS
    _attr_translation_key = "normal_light"

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["light_is_on"]
        self._attr_brightness = self.coordinator.data["light_brightness"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        await self.coordinator.async_turn_on_light(kwargs.get(ATTR_BRIGHTNESS))

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_turn_off_light()


class SmartSleepNightLight(SmartSleepEntity, LightEntity):
    """Representation of an SmartSleep Night light."""

    _attr_should_poll = True
    _attr_supported_features = 0
    _attr_translation_key = "night_light"

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["nightlight_is_on"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        await self.coordinator.async_turn_on_nightlight()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_turn_off_nightlight()

class SmartSleepSunset(SmartSleepEntity, LightEntity):
    """Representation of the SmartSleep's sunset (dusk) mode."""
    
    _attr_should_poll = True
    _attr_supported_features = SUPPORT_BRIGHTNESS
    _attr_translation_key = "sunset"

    def __init__(self, name, data, device_info, serial):
        """Initialize a Sunset mode entity."""
        self._name = name + "_sunset"
        self._data = data
        self._state = None
        self._timer = None
        self._brightness = None
        self._device_info = device_info
        self._serial = serial

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["light_is_on"]
        self._attr_brightness = self.coordinator.data["light_brightness"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the sunset mode to turn on."""
        await self.coordinator.async_turn_on_sunset(kwargs.get(ATTR_BRIGHTNESS))

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the sunset mode to turn off."""
        await self.coordinator.async_turn_off_sunset()
