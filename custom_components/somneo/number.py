"""Platform for number entity to catch hour/minute of alarms."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, HOURS, MINUTES, HOURS_ICON, MINUTES_ICON
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data['dev_info']  

    alarms = []
    # Add hour & min number_entity for each alarms
    for alarm in list(coordinator.alarms):
        alarms.append(SomneoTime(coordinator, unique_id, name, device_info, alarm, HOURS))
        alarms.append(SomneoTime(coordinator, unique_id, name, device_info, alarm, MINUTES))
    
    snooze = [SomneoSnooze(coordinator, unique_id, name, device_info, 'snooze')]

    async_add_entities(alarms, True)
    async_add_entities(snooze, True)

class SomneoTime(SomneoEntity, NumberEntity):
    _attr_should_poll = True
    _attr_assumed_state = False
    _attr_available = True
    _attr_native_step = 1

    def __init__(self, coordinator, unique_id, name, dev_info, alarm, type):
        """Initialize number entities."""
        super().__init__(coordinator, unique_id, name, dev_info, alarm + '_' + type)

        self._attr_name = alarm.capitalize() + " " + type
        if type == HOURS:
            self._attr_native_min_value = 0
            self._attr_native_max_value = 23
            self._attr_icon = HOURS_ICON
        elif type == MINUTES:
            self._attr_native_min_value = 0
            self._attr_native_max_value = 59
            self._attr_icon = MINUTES_ICON

        self._alarm = alarm
        self._type = type

    @property
    def native_value(self) -> int:
        if self._type == MINUTES:
            return self.coordinator.alarms_minute[self._alarm]
        elif self._type == HOURS:
            return self.coordinator.alarms_hour[self._alarm]

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust Hours / Minutes in the UI"""
        if self._type == MINUTES:
            await self.coordinator.async_set_alarm(self._alarm, minutes = int(value))
        elif self._type == HOURS:
            await self.coordinator.async_set_alarm(self._alarm, hours = int(value))


class SomneoSnooze(SomneoEntity, NumberEntity):
    _attr_should_poll = True
    _attr_available = True
    _attr_assumed_state = False
    _attr_name = 'Snooze time'
    _attr_native_min_value = 1
    _attr_native_max_value = 20
    _attr_native_step = 1
    _attr_icon = 'hass:alarm-snooze'

    @property
    def native_value(self) -> int:
        return self.coordinator.snooze_time

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust snooze time in the UI"""
        await self.coordinator.async_set_snooze_time(int(value))