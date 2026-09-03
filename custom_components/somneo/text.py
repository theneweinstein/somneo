"""Text entities for Somneo."""
from __future__ import annotations

import logging

from homeassistant.components.text import TextEntity
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

    alarms = [
        SomneoAlarmDays(coordinator, unique_id, alarm)
        for alarm in list(coordinator.data["alarms"])
    ]

    async_add_entities(alarms, update_before_add=True)


class SomneoAlarmDays(SomneoEntity, TextEntity):
    """Representation of a alarm switch."""

    _attr_assumed_state = False
    _attr_available = True
    _attr_native_value = None
    _attr_pattern = "^((tomorrow|daily|mon|tue|wed|thu|fri|sat|sun)(,)?)+$"
    _attr_translation_key = "days_str"

    def __init__(
        self,
        coordinator,
        unique_id: str,
        alarm: int | str,
    ) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, unique_id, "alarm" + str(alarm))

        self._attr_translation_placeholders = {"number": str(alarm)}
        self._alarm = alarm
        self._attr_entity_registry_enabled_default = coordinator.data["alarms"].get(
            alarm, {}
        ).get("visible", False)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the alarm days text value."""
        days_list = self.coordinator.data["alarms"][self._alarm]["days"]
        self._attr_native_value = ",".join([str(item) for item in days_list if item])

        self.async_write_ha_state()

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        await self.coordinator.async_set_alarm(self._alarm, days=value.split(","))
