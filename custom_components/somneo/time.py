"""Time entities for Somneo."""
from __future__ import annotations

import logging
from datetime import time

from homeassistant.components.time import TimeEntity
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
    """Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None

    alarms = []
    # Add hour & min number_entity for each alarms.
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(SomneoTime(coordinator, unique_id, alarm))

    async_add_entities(alarms, update_before_add=True)


class SomneoTime(SomneoEntity, TimeEntity):
    """Representation of a alarm time."""

    _attr_assumed_state = False
    _attr_available = True
    _attr_has_entity_name = True
    _attr_native_value = None
    _attr_translation_key = "time"

    def __init__(
        self,
        coordinator,
        unique_id: str,
        alarm: int | str,
    ) -> None:
        """Initialize time entity."""
        super().__init__(coordinator, unique_id, "alarm" + str(alarm) + "_time")

        self._attr_translation_placeholders = {"number": str(alarm)}

        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the alarm time value."""
        self._attr_native_value = self.coordinator.data["alarms"][self._alarm]["time"]

        self.async_write_ha_state()

    async def async_set_value(self, value: time) -> None:
        """Adjust alarm time."""
        await self.coordinator.async_set_alarm(self._alarm, alarm_time=value)
