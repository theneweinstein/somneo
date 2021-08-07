"""Platform for binary sensor integration."""
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
        alarms.append(SomneoToggle(name + "_t", data, device_info, dev_info['serial'] + "_t", alarm))
    async_add_entities(alarms, True)

class SomneoToggle(SwitchEntity):
    def __init__(self, name, data, device_info, serial, alarm):
        """Initialize the sensor. """
        self._data = data
        self._name = name + "_" + alarm
        self._alarm = alarm
        self._device_info = device_info
        self._serial = serial
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return the id of this sensor."""
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
        """Get the latest data and updates the states."""
        await self._data.update()
        if self._data.somneo.alarms()[self._alarm] == True:
            self._state = STATE_ON
        else:
            self._state = STATE_OFF

    def turn_on(self, **kwargs):
        """Turn the entity on."""
        self._data.somneo.toggle_alarm(True, self._alarm)
        self._state = STATE_ON
        #self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self._data.somneo.toggle_alarm(False, self._alarm)
        self._state = STATE_OFF
        #self.schedule_update_ha_state()