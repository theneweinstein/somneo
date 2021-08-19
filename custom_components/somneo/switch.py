"""Platform for switch integration. (on/off alarms & on/off alarms on workdays and/or weekends"""
import logging

from homeassistant.const import STATE_OFF, STATE_ON
try:
    from homeassistant.components.switch import SwitchEntity
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
        alarms.append(SomneoToggle(name, data, device_info, dev_info['serial'], alarm))

    async_add_entities(alarms, True)

class SomneoToggle(SwitchEntity):
    _attr_icon: ALARMS_ICON
    _attr_should_poll = True

    def __init__(self, name, data, device_info, serial, alarm):
        """Initialize the switches. """
        self._data = data
        self._attr_name = name + "_" + alarm
        self._alarm = alarm
        self._attr_device_info = device_info
        self._attr_unique_id = serial + '_' + alarm
        self._attr_state = None
        self._attr_is_on = self._attr_state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}
        attr['time'], attr['days'] = self._data.somneo.alarm_settings(self._alarm)
        return attr

    async def async_update(self):
        """Get the latest data and updates the states of the switches."""
        await self._data.update()
        if self._data.somneo.alarms()[self._alarm]:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    def turn_on(self, **kwargs):
        """Called when user Turn On the switch from UI."""
        self._data.somneo.toggle_alarm(self._alarm, True)
        self._attr_state = STATE_ON

    def turn_off(self, **kwargs):
        """Called when user Turn Off the switch from UI."""
        self._data.somneo.toggle_alarm(self._alarm, False)
        self._attr_state = STATE_OFF