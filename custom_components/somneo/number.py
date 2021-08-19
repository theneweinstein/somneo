"""Platform for number entity to catch hour/minute of alarms."""
import logging

from homeassistant.components.number import NumberEntity
from datetime import datetime

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Add Somneo from config_entry."""
    name = config_entry.data[CONF_NAME]
    data = hass.data[DOMAIN]
    dev_info = data.dev_info

    device_info = {
        "identifiers": {(DOMAIN, dev_info['serial'])},
        "name": 'Somneo',
        "manufacturer": dev_info['manufacturer'],
        "model": f"{dev_info['model']} {dev_info['modelnumber']}",
    }

    alarms = []
    # Add hour & min number_entity for each alarms
    for alarm in list(data.somneo.alarms()):
        alarms.append(SomneoTime(name, data, device_info, dev_info['serial'], alarm, HOURS))
        alarms.append(SomneoTime(name, data, device_info, dev_info['serial'], alarm, MINUTES))
    
    snooze = [SomneoSnooze(name, data, device_info, dev_info['serial'])]

    async_add_entities(alarms, True)
    async_add_entities(snooze, True)


class SomneoTime(NumberEntity):
    _attr_should_poll = True
    _attr_assumed_state = False
    _attr_available = True

    def __init__(self, name, data, device_info, serial, alarm, type):
        """Initialize number entities."""
        self._data = data
        self._attr_name = name + "_" + alarm + "_" + type
        self._alarm = alarm
        self._attr_device_info = device_info
        self._attr_unique_id = serial + type + self._alarm
        self._attr_value = 5.0
        self._type = type
        self._alarm_date = None
        if type == HOURS:
            self._attr_min_value = 0
            self._attr_max_value = 23
            self._attr_icon = HOURS_ICON
        elif type == MINUTES:
            self._attr_min_value = 0
            self._attr_max_value = 59
            self._attr_icon = MINUTES_ICON
        self._attr_step = 1

    def set_value(self, value: float):
        """Called when user adjust Hours / Minutes in the UI"""
        if self._alarm_date is not None:
            self._attr_value = value
            if self._type == MINUTES:
                _LOGGER.debug("Set Alarm Date " + str(self._alarm_date.hour) + ":" + str(value))
                self._data.somneo.set_time_alarm(self._alarm, self._alarm_date.hour, value)
            elif self._type == HOURS:
                _LOGGER.debug("Set Alarm Date " + str(value) + ":" + str(self._alarm_date.minute))
                self._data.somneo.set_time_alarm(self._alarm, value, self._alarm_date.minute)


    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()
        attr = {}
        attr['time'], attr['days'] = self._data.somneo.alarm_settings(self._alarm)
        self._alarm_date = datetime.strptime(attr['time'],'%H:%M:%S')
        if self._type == HOURS:
            self._attr_value = self._alarm_date.hour
        elif self._type == MINUTES:
            self._attr_value = self._alarm_date.minute

class SomneoSnooze(NumberEntity):
    _attr_should_poll = True
    _attr_available = True
    _attr_assumed_state = False
    _attr_min_value = 1
    _attr_max_value = 20
    _attr_step = 1
    _attr_icon = 'hass:alarm-snooze'


    def __init__(self, name, data, device_info, serial):
        """Initialize number entities."""
        self._data = data
        self._attr_name = name + '_snooze_time'
        self._attr_unique_id = serial + '_snooze_time'
        self._attr_value = 9.0
        self._attr_device_info = device_info

    def set_value(self, value: float):
        """Called when user adjust snooze time in the UI"""
        self._attr_value = value
        self._data.somneo.set_snooze_time(int(value))

    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()
        self._attr_value = self._data.somneo.snoozetime