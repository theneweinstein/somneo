"""Platform for number entity to catch hour/minute of alarms."""
import logging
from datetime import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.time import TimeEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, TIME_ICON
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
    # Add hour & min number_entity for each alarms
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(SmartSleepTime(coordinator, unique_id, name, device_info, alarm))

    async_add_entities(alarms, update_before_add=True)


class SmartSleepTime(SmartSleepEntity, TimeEntity):
    _attr_should_poll = True
    _attr_assumed_state = False
    _attr_available = True
    _attr_has_entity_name = True
    _attr_icon = TIME_ICON
    _attr_native_value = None

    def __init__(self, coordinator, unique_id, name, dev_info, alarm):
        """Initialize number entities."""
        super().__init__(coordinator, unique_id, name, dev_info, alarm + "_time")

        self._attr_translation_key = alarm + "_time"

        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = time(
            self.coordinator.data["alarms_hour"][self._alarm],
            self.coordinator.data["alarms_minute"][self._alarm],
        )

        self.async_write_ha_state()

    async def async_set_value(self, value: time) -> None:
        """Called when user adjust Hours / Minutes in the UI"""
        await self.coordinator.async_set_alarm(
            self._alarm, hours=value.hour, minutes=value.minute
        )
