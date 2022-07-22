"""Platform for light integration."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.light import (LightEntity, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ Add Somneo light from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data['dev_info']  

    async_add_entities(
        [
            SomneoLight(coordinator, unique_id, name, device_info, 'light'),
            SomneoNightLight(coordinator, unique_id, name, device_info, 'nightlight'),
        ]
    )

class SomneoLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Light."""

    _attr_name = "Light"
    _attr_should_poll = True
    _attr_supported_features = SUPPORT_BRIGHTNESS

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self.coordinator.brightness

    @property
    def is_on(self) -> bool | None:
        """Return True if light is on."""
        return self.coordinator.light_is_on

    async def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        await self.coordinator.async_turn_on_light(kwargs.get(ATTR_BRIGHTNESS))

    async def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_turn_off_light()

class SomneoNightLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Night light."""

    _attr_name = "Night light"
    _attr_should_poll = True
    _attr_supported_features = 0

    @property
    def is_on(self) -> bool | None:
        """Return True if light is on."""
        return self.coordinator.nightlight_is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        await self.coordinator.async_turn_on_nightlight()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_turn_off_nightlight()