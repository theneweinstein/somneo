"""Platform for binary sensor integration."""
import logging

from custom_components import somneo
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.components.number import NumberEntity
from datetime import datetime
import asyncio

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Add Somneo sensors from config_entry."""
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
    for alarm in list(data.somneo.alarms()):
        alarms.append(SomneoTime(name, data, device_info, dev_info['serial'] + "_hour", alarm, HOURS))
        alarms.append(SomneoTime(name, data, device_info, dev_info['serial'] + "_min", alarm, MINUTES))

    async_add_entities(alarms, True)


class SomneoTime(NumberEntity):
    """Representation of a binary  for alarms."""
    _attr_should_poll = True

    def __init__(self, name, data, device_info, serial, alarm, type):
        """Initialize the sensor."""
        self._data = data
        self._attr_name = name + "_" + alarm + "_" + type
        self._alarm = alarm
        self._attr_unique_id = serial
        self._attr_value = 5.0
        self._type = type
        self._alarm_date = None
        if type == HOURS:
            self._attr_min_value = 0
            self._attr_max_value = 23
        elif type == MINUTES:
            self._attr_min_value = 0
            self._attr_max_value = 59
        self._attr_step = 1

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def assumed_state(self):
        """Return the state of the sensor."""
        return False

    @property
    def available(self):
        """Return the state of the sensor."""
        return True

    @property
    def should_poll(self):
        return True

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self._attr_unique_id + '_' + self._alarm

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self.entity_id

    def set_value(self, value: float):
        _LOGGER.error("Set Value " + str(self._attr_value))
        if self._alarm_date is not None:
            self._attr_value = value
            if self._type == MINUTES:
                _LOGGER.error("Set Alarm Date " + str(self._alarm_date.hour) + ":" + str(self._attr_value))
                self._data.somneo.set_time_alarm(self._alarm_date.hour, self._attr_value, self._alarm)
            elif self._type == HOURS:
                _LOGGER.error("Set Alarm Date " + str(self._attr_value) + ":" + str(self._alarm_date.minute))
                self._data.somneo.set_time_alarm(self._attr_value, self._alarm_date.minute, self._alarm)

    @property
    def value(self) -> float :
        """Return the entity value to represent the entity state."""
        return self._attr_value

    @property
    def min_value(self) -> float:
        """Return the entity value to represent the entity state."""
        return self._attr_min_value

    @property
    def max_value(self) -> float:
        """Return the entity value to represent the entity state."""
        return self._attr_max_value

    @property
    def step(self) -> float:
        """Return the entity value to represent the entity state."""
        return self._attr_step

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