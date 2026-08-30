"""Button entities for Somneo."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
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
    """Add Somneo from config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None

    buttons = [
        SomneoDismiss(coordinator, unique_id, "alarm_dismiss"),
        SomneoSnooze(coordinator, unique_id, "alarm_snooze"),
    ]

    async_add_entities(buttons, update_before_add=True)


class SomneoDismiss(SomneoEntity, ButtonEntity):
    """Dismiss alarm button."""

    _attr_translation_key = "alarm_dismiss"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_dismiss_alarm()


class SomneoSnooze(SomneoEntity, ButtonEntity):
    """Snooze alarm button."""

    _attr_translation_key = "alarm_snooze"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_snooze_alarm()
