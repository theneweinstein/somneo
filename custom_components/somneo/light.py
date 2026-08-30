"""Light entities for Somneo."""
from __future__ import annotations

import logging
from typing import Any, ClassVar

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
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

    async_add_entities(
        [
            SomneoLight(coordinator, unique_id, "light"),
            SomneoNightLight(coordinator, unique_id, "nightlight"),
        ],
        update_before_add=True,
    )


class SomneoLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Light."""

    _attr_supported_color_modes: ClassVar[set[ColorMode | str]] = {
        ColorMode.BRIGHTNESS
    }
    _attr_translation_key = "normal_light"

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return ColorMode.BRIGHTNESS

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the state from coordinator data."""
        if not self.coordinator.data:
            _LOGGER.debug("No data received from coordinator, skipping update.")
            return

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

    _attr_supported_color_modes: ClassVar[set[ColorMode | str]] = {
        ColorMode.ONOFF
    }
    _attr_translation_key = "night_light"

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return ColorMode.ONOFF

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the state from coordinator data."""
        if not self.coordinator.data:
            _LOGGER.debug("No data received from coordinator, skipping update.")
            return

        self._attr_is_on = self.coordinator.data.get("nightlight_is_on", False)
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        await self.coordinator.async_toggle_nightlight(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_toggle_nightlight(False)
