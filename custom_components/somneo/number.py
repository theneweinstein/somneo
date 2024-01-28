"""Number entities for Somneo."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PW_ICON, SNOOZE_ICON, SUNSET_ICON
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
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    alarms = []
    # Add all PowerWake deltas
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(SomneoPowerWake(coordinator, unique_id, name, device_info, alarm))

    snooze = [SomneoSnooze(coordinator, unique_id, name, device_info, "snooze")]

    sunset = [SomneoSunsetDuration(coordinator, unique_id, name, device_info, "sunset_duration"),
              SomneoSunsetLevel(coordinator, unique_id, name, device_info, "sunset_level"),
              SomneoSunsetVolume(coordinator, unique_id, name, device_info, "sunset_volume")
    ]

    async_add_entities(alarms, update_before_add=True)
    async_add_entities(snooze, update_before_add=True)
    async_add_entities(sunset, update_before_add=True)


class SomneoPowerWake(SomneoEntity, NumberEntity):
    """Representation of a Powerwake number."""

    _attr_should_poll = True
    _attr_assumed_state = False
    _attr_available = True
    _attr_native_step = 1
    _attr_has_entity_name = True
    _attr_native_min_value = 0
    _attr_native_max_value = 59
    _attr_icon = PW_ICON

    def __init__(self, coordinator, unique_id, name, dev_info, alarm):
        """Initialize number entities."""
        super().__init__(
            coordinator, unique_id, name, dev_info, "alarm" + str(alarm) + "_powerwake_delta"
        )

        self._attr_translation_key = "alarm" + str(alarm) + "_powerwake_delta"

        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle update"""
        self._attr_native_value = self.coordinator.data["alarms"][self._alarm]["powerwake_delta"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust Hours / Minutes in the UI"""
        await self.coordinator.async_set_alarm_powerwake(self._alarm, delta=int(value))


class SomneoSnooze(SomneoEntity, NumberEntity):
    """Representation of a snooze time."""

    _attr_should_poll = True
    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "snooze_time"
    _attr_native_min_value = 1
    _attr_native_max_value = 20
    _attr_native_step = 1
    _attr_icon = SNOOZE_ICON
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["snooze_time"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust snooze time in the UI"""
        await self.coordinator.async_set_snooze_time(int(value))

class SomneoSunsetDuration(SomneoEntity, NumberEntity):
    """Represenation of the Sunset duration."""

    _attr_should_poll = True
    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "sunset_duration"
    _attr_native_min_value = 5
    _attr_native_max_value = 60
    _attr_native_step = 5
    _attr_icon = SUNSET_ICON
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["sunset"]["duration"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust snooze time in the UI"""
        await self.coordinator.async_set_sunset(duration = int(value))

class SomneoSunsetLevel(SomneoEntity, NumberEntity):
    """Represenation of the Sunset level."""

    _attr_should_poll = True
    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "sunset_level"
    _attr_native_min_value = 0
    _attr_native_max_value = 25
    _attr_native_step = 1
    _attr_icon = SUNSET_ICON
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["sunset"]["level"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust snooze time in the UI"""
        await self.coordinator.async_set_sunset(level = int(value))

class SomneoSunsetVolume(SomneoEntity, NumberEntity):
    """Represenation of the Sunset volume."""

    _attr_should_poll = True
    _attr_available = True
    _attr_assumed_state = False
    _attr_translation_key = "sunset_volume"
    _attr_native_min_value = 1
    _attr_native_max_value = 25
    _attr_native_step = 1
    _attr_icon = SUNSET_ICON
    _attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["sunset"]["volume"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust snooze time in the UI"""
        await self.coordinator.async_set_sunset(volume = int(value))