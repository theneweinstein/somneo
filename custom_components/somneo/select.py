"""Platform for select entity to catch alarm days."""
import logging

from custom_components import somneo
from homeassistant.components.select import SelectEntity
from datetime import datetime
import asyncio

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
        alarms.append(SomneoDays(name, data, device_info, dev_info['serial'], alarm))

    async_add_entities(alarms, True)

class SomneoDays(SelectEntity):
    _attr_should_poll = True

    def __init__(self, name, data, device_info, serial, alarm):
        """Initialize number entities."""
        self._data = data
        self._attr_name = name + "_" + alarm + "_days"
        self._alarm = alarm
        self._serial = serial
        self._alarm_date = None
        self._device_info = device_info
        self._attr_options = [WORKDAYS, WEEKEND, TOMORROW, EVERYDAY]
        self._attr_option = WORKDAYS

    @property
    def name(self):
        """Return the name of the number entity."""
        return self._attr_name

    @property
    def icon(self):
        """Return the icon ref of the switches."""
        return WORKDAYS_ICON

    @property
    def assumed_state(self):
        """Return the assumed state of the entity."""
        return False

    @property
    def available(self):
        """Return the availability of the entity."""
        return True

    @property
    def should_poll(self):
        return True

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self._serial + '_' + self._alarm + '_days'

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    @property
    def options(self):
        """Return the available options."""
        return self._attr_options

    @property
    def current_option(self):
        """Return the current option."""
        return self._attr_option


    async def select_option(self, option: str):
        """Called when user adjust the option in the UI."""

        self._attr_option = option

        if option == WORKDAYS:
            self._data.somneo.set_workdays_alarm(True, self._alarm)
        elif option == WEEKEND:
            self._data.somneo.set_weekend_alarm(True, self._alarm)
        elif option == TOMORROW:
            self._data.somneo.set_days_alarm(0,self._alarm)
        elif option == EVERYDAY:
            self._data.somneo.set_everyday_alarm(True, self._alarm)

    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()

        if self._data.somneo.is_everyday(self._alarm):
            self._attr_option = EVERYDAY
        elif self._data.somneo.is_workday(self._alarm):
            self._attr_option = WORKDAYS
        elif self._data.somneo.is_weekend(self._alarm):
            self._attr_option = WEEKEND
        elif self._data.somneo.is_tomorrow(self._alarm):
            self._attr_option = TOMORROW
        else:
            self._attr_option = UNKNOWN