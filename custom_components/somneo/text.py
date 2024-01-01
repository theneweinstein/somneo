"""Text entities for Somneo."""
import logging
from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.text import TextEntity
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import (
    DOMAIN,
    WORKDAYS_ICON
)
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
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(
            SomneoAlarmDays(coordinator, unique_id, name, device_info, alarm)
        )

    async_add_entities(alarms, update_before_add=True)


class SomneoAlarmDays(SomneoEntity, TextEntity):
    """Representation of a alarm switch."""

    _attr_should_poll = True
    _attr_assumed_state = False
    _attr_available = True
    _attr_icon = WORKDAYS_ICON
    _attr_native_value = None
    _attr_pattern = "^((tomorrow|mon|tue|wed|thu|fri|sat|sun)(,)?)+$"

    def __init__(self, coordinator, unique_id, name, device_info, alarm):
        """Initialize the switches."""
        super().__init__(coordinator, unique_id, name, device_info, "alarm" + str(alarm))

        self._attr_translation_key = "alarm" + str(alarm) + '_days_str'
        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        days_list = self.coordinator.data["alarms"][self._alarm]['days']
        self._attr_native_value = ",".join([str(item) for item in days_list if item])

        self.async_write_ha_state()

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        await self.coordinator.async_set_alarm(self._alarm, days = value.split(','))