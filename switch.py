"""Platform for switch integration. (on/off alarms & on/off alarms on workdays and/or weekends"""
import logging

from custom_components import somneo
from homeassistant.const import STATE_OFF, STATE_ON
try:
    from homeassistant.components.switch import SwitchEntity
    from homeassistant.components.number import NumberEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

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
    for alarm in list(data.somneo.alarms()):
        alarms.append(SomneoToggle(name, data, device_info, dev_info['serial'], alarm, ALARMS))
        alarms.append(SomneoToggle(name + "_" + WORKDAYS, data, device_info,
                                   dev_info['serial'] + WORKDAYS, alarm, WORKDAYS))
        alarms.append(SomneoToggle(name + "_" + WEEKEND, data, device_info,
                                   dev_info['serial'] + WEEKEND, alarm, WEEKEND))
    async_add_entities(alarms, True)

class SomneoToggle(SwitchEntity):
    def __init__(self, name, data, device_info, serial, alarm, type):
        """Initialize the switches. """
        self._data = data
        self._name = name + "_" + alarm
        self._alarm = alarm
        self._device_info = device_info
        self._serial = serial
        self._state = None
        self._type = type

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def icon(self):
        """Return the icon ref of the switches."""
        if self._type == ALARMS:
            return ALARMS_ICON
        elif self._type == WEEKEND:
            return WEEKEND_ICON
        elif self._type == WORKDAYS:
            return WORKDAYS_ICON

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def state(self):
        """Return the state of the switch."""
        return self._state

    @property
    def unique_id(self):
        """Return the id of this switch."""
        return self._serial + '_' + self._alarm

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    @property
    def should_poll(self):
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}

        attr['time'], attr['days'] = self._data.somneo.alarm_settings(self._alarm)

        return attr

    async def async_update(self):
        """Get the latest data and updates the states of the switches."""
        await self._data.update()
        if self._type == ALARMS:
            if self._data.somneo.alarms()[self._alarm]:
                self._state = STATE_ON
            else:
                self._state = STATE_OFF
        elif self._type == WORKDAYS:
            if self._data.somneo.is_workday(self._alarm):
                self._state = STATE_ON
            else:
                self._state = STATE_OFF
        elif self._type == WEEKEND:
            if self._data.somneo.is_weekend(self._alarm):
                self._state = STATE_ON
            else:
                self._state = STATE_OFF

    def turn_on(self, **kwargs):
        """Called when user Turn On the switch from UI."""
        if self._type == ALARMS:
            self._data.somneo.toggle_alarm(True, self._alarm)
            self._state = STATE_ON
        elif self._type == WORKDAYS:
            self._data.somneo.set_workdays_alarm(True, self._alarm)
        elif self._type == WEEKEND:
            self._data.somneo.set_weekend_alarm(True, self._alarm)

    def turn_off(self, **kwargs):
        """Called when user Turn Off the switch from UI."""
        if self._type == ALARMS:
            self._data.somneo.toggle_alarm(False, self._alarm)
            self._state = STATE_OFF
        elif self._type == WORKDAYS:
            self._data.somneo.set_workdays_alarm(False, self._alarm)
        elif self._type == WEEKEND:
            self._data.somneo.set_weekend_alarm(False, self._alarm)