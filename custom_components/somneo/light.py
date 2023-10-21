"""Light entities for Somneo."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
)
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
    _attr_supported_color_modes: set[ColorMode| str] = {ColorMode.BRIGHTNESS}
    _attr_translation_key = "normal_light"

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return ColorMode.BRIGHTNESS

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


class SomneoNightLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Night light."""

    _attr_should_poll = True
    _attr_supported_color_modes: set[ColorMode| str] = {ColorMode.ONOFF}
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
        await self.coordinator.async_turn_on_nightlight()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_turn_off_nightlight()
