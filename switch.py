""" TODO! """

"""Platform for switch integration."""
import logging

# Import the device class from the component that you want to support
from custom_components import smartsleep
from homeassistant.components.switch import (SwitchEntity)

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Add Somneo switch from config_entry."""
    name = config_entry.data[CONF_NAME]
    data = hass.data[DOMAIN]
    dev_info = data.dev_info

    device_info = {
        "identifiers": {(DOMAIN, dev_info['serial'])},
        "name": 'SmartSleep',
        "friendlyName": dev_info['friendlyName'],
        "manufacturer": dev_info['manufacturer'],
        "model": f"{dev_info['model']} {dev_info['modelNumber']}",
    }

    async_add_entities(
        [
            SomneoRadioSwitch(name, data, device_info, dev_info['serial'])
        ]
    )

class SomneoRadioSwitch(SwitchEntity):
    """Representation of a SmartSleep FM radio switch."""

    def __init__(self, name, data, device_info, serial):
        """Initialize a SwitchEntity."""
        self._name = name + "_radio"
        self._data = data
        self._state = None
        self._device_info = device_info
        self._serial = serial

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def should_poll(self):
        return True

    @property
    def supported_features(self):
        """Flag supported features."""
        return 0

    @property
    def unique_id(self):
        """Return the id of this switch."""
        return self._serial + '_night'

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    def turn_on(self, **kwargs):
        """Instruct the switch to turn on."""
        self._data.somneo.toggle_radio_switch(True)
        self._state['onoff'] = True
        self._state['snddv'] = 'fmr'
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the switch to turn off."""
        self._data.somneo.toggle_radio_switch(False)
        self._state['onoff'] = False
        self._state['snddv'] = 'off'
        self.schedule_update_ha_state()

    async def async_update(self):
        """Fetch new state data for this switch."""
        await self._data.update()
        self._state = self._data.somneo.radio_status()
