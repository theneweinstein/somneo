"""Number entities for Somneo."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.number import NumberEntity
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
    # Add all PowerWake deltas
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(SomneoPowerWake(coordinator, unique_id, alarm))

    snooze = [SomneoSnooze(coordinator, unique_id, "snooze")]

    sunset = [
        SomneoSunsetDuration(coordinator, unique_id, "sunset_duration"),
        SomneoSunsetLevel(coordinator, unique_id, "sunset_level"),
        SomneoSunsetVolume(coordinator, unique_id, "sunset_volume"),
    ]

    display = [
        SomneoDisplayBrightness(coordinator, unique_id, "display_brightness")
    ]

    async_add_entities(alarms, update_before_add=True)
    async_add_entities(snooze, update_before_add=True)
    async_add_entities(sunset, update_before_add=True)
    async_add_entities(display, update_before_add=True)


class SomneoPowerWake(SomneoEntity, NumberEntity):
    """Representation of a Powerwake number."""

    _attr_has_entity_name = True
    _attr_native_min_value = 0
    _attr_native_max_value = 59
    _attr_native_step = 1
    _attr_translation_key = "powerwake_delta"

    def __init__(
        self,
        coordinator,
        unique_id: str,
        alarm: int | str,
    ) -> None:
        """Initialize number entities."""
        super().__init__(
            coordinator, unique_id, "alarm" + str(alarm) + "_powerwake_delta"
        )

        self._attr_translation_placeholders = {"number": str(alarm)}

        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the PowerWake delta value."""
        self._attr_native_value = self.coordinator.data["alarms"][self._alarm]["powerwake_delta"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjusts PowerWake delta in the UI."""
        await self.coordinator.async_set_alarm_powerwake(self._alarm, delta=int(value))


class SomneoSnooze(SomneoEntity, NumberEntity):
    """Representation of a snooze time."""

    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "snooze_time"
    _attr_native_min_value = 1
    _attr_native_max_value = 20
    _attr_native_step = 1
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the snooze time value."""
        self._attr_native_value = self.coordinator.data["snooze_time"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjusts snooze time in the UI."""
        await self.coordinator.async_set_snooze_time(int(value))

class SomneoSunsetDuration(SomneoEntity, NumberEntity):
    """Represenation of the Sunset duration."""

    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "sunset_duration"
    _attr_native_min_value = 5
    _attr_native_max_value = 60
    _attr_native_step = 5
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the sunset duration value."""
        self._attr_native_value = self.coordinator.data["sunset"]["duration"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjusts sunset duration in the UI."""
        await self.coordinator.async_set_sunset(duration=int(value))

class SomneoSunsetLevel(SomneoEntity, NumberEntity):
    """Represenation of the Sunset level."""

    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "sunset_level"
    _attr_native_min_value = 0
    _attr_native_max_value = 25
    _attr_native_step = 1
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the sunset level value."""
        self._attr_native_value = self.coordinator.data["sunset"]["level"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjusts sunset level in the UI."""
        await self.coordinator.async_set_sunset(level=int(value))

class SomneoSunsetVolume(SomneoEntity, NumberEntity):
    """Represenation of the Sunset volume."""

    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "sunset_volume"
    _attr_native_min_value = 1
    _attr_native_max_value = 25
    _attr_native_step = 1
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the sunset volume value."""
        self._attr_native_value = self.coordinator.data["sunset"]["volume"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjusts sunset volume in the UI."""
        await self.coordinator.async_set_sunset(volume=int(value))


class SomneoDisplayBrightness(SomneoEntity, NumberEntity):
    """Representation of the display brightness."""

    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "display_brightness"
    _attr_native_min_value = 1
    _attr_native_max_value = 6
    _attr_native_step = 1
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the display brightness value."""
        self._attr_native_value = self.coordinator.data["display_brightness"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjusts display brightness in the UI."""
        await self.coordinator.async_set_display(brightness=int(value))