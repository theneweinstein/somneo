"""Platform for light integration."""
import logging

# Import the device class from the component that you want to support
from homeassistant.components.light import (LightEntity, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS)

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Add Somneo light from config_entry."""
    name = config_entry.data[CONF_NAME]
    data = hass.data[DOMAIN]    
    dev_info = data.dev_info

    device_info = {
        "identifiers": {(DOMAIN, dev_info['serial'])},
        "name": 'Somneo',
        "manufacturer": dev_info['manufacturer'],
        "model": f"{dev_info['model']} {dev_info['modelnumber']}",
    }        

    async_add_entities(
        [
            SomneoLight(name, data, device_info, dev_info['serial']),
            SomneoNightLight(name, data, device_info, dev_info['serial'])
        ]
    )

class SomneoLight(LightEntity):
    """Representation of an Somneo Light."""

    _attr_should_poll = True
    _attr_supported_features = SUPPORT_BRIGHTNESS

    def __init__(self, name, data, device_info, serial):
        """Initialize an SomneoLight."""
        self._attr_name = name
        self._data = data
        self._attr_brightness = None
        self._attr_device_info = device_info
        self._attr_unique_id = serial + '_light'
        self._attr_is_on = None

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
        else:
            brightness = None

        self._data.somneo.toggle_light(True, brightness)
        self._attr_is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._data.somneo.toggle_light(False)
        self._attr_is_on = False
        self.schedule_update_ha_state()

    async def async_update(self):
        """Fetch new state data for this light."""
        await self._data.update()
        self._attr_is_on, self._attr_brightness = self._data.somneo.light_status()

class SomneoNightLight(LightEntity):
    """Representation of an Somneo Light."""

    _attr_should_poll = True
    _attr_supported_features = 0

    def __init__(self, name, data, device_info, serial):
        """Initialize an SomneoLight."""
        self._attr_name = name + "_night"
        self._data = data
        self._attr_is_on = None
        self._attr_brightness = None
        self._attr_device_info = device_info
        self._attr_unique_id = serial + '_night'

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._data.somneo.toggle_night_light(True)
        self._attr_is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._data.somneo.toggle_night_light(False)
        self._attr_is_on = False
        self.schedule_update_ha_state()

    async def async_update(self):
        """Fetch new state data for this light."""
        await self._data.update()
        self._attr_is_on = self._data.somneo.night_light_status()