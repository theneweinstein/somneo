"""Light entities for Somneo."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo light from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    async_add_entities(
        [
            SomneoLight(coordinator, unique_id, name, device_info, "light"),
            SomneoNightLight(coordinator, unique_id, name, device_info, "nightlight"),
        ],
        update_before_add=True,
    )


class SomneoLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Light."""

    _attr_should_poll = True
    _attr_supported_color_modes: set[ColorMode | str] = {ColorMode.BRIGHTNESS}
    _attr_translation_key = "normal_light"

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return ColorMode.BRIGHTNESS

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.data:
            _LOGGER.debug("No data received from Somneo coordinator")
            return

        # Use .get() to avoiod TypeError when a key is missing.
        self._attr_is_on = self.coordinator.data.get("light_is_on", False)
        self._attr_brightness = self.coordinator.data.get("light_brightness", 0)

        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        await self.coordinator.async_toggle_light(
            True, brightness=kwargs.get(ATTR_BRIGHTNESS)
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_toggle_light(False)


class SomneoNightLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Night light."""

    _attr_should_poll = True
    _attr_supported_color_modes: set[ColorMode | str] = {ColorMode.ONOFF}
    _attr_translation_key = "night_light"

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return ColorMode.ONOFF

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["nightlight_is_on"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        await self.coordinator.async_toggle_nightlight(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_toggle_nightlight(False)
