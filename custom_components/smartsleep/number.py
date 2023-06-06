"""Platform for number entity to catch hour/minute of alarms."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PW_ICON, SNOOZE_ICON
from .entity import SmartSleepEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add SmartSleep from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    alarms = []
    # Add all PowerWake deltas
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(SmartSleepPowerWake(coordinator, unique_id, name, device_info, alarm))

    snooze = [SmartSleepSnooze(coordinator, unique_id, name, device_info, "snooze")]

    async_add_entities(alarms, update_before_add=True)
    async_add_entities(snooze, update_before_add=True)


class SmartSleepPowerWake(SmartSleepEntity, NumberEntity):
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
            coordinator, unique_id, name, dev_info, alarm + "_powerwake_delta"
        )

        self._attr_translation_key = alarm + "_powerwake_delta"

        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle update"""
        self._attr_native_value = self.coordinator.data["powerwake_delta"][self._alarm]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust Hours / Minutes in the UI"""
        await self.coordinator.async_set_powerwake(self._alarm, delta=int(value))


class SmartSleepSnooze(SmartSleepEntity, NumberEntity):
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
