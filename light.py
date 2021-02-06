"""Platform for light integration."""
import logging

# Import the device class from the component that you want to support
from custom_components import smartsleep
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
        "name": 'SmartSleep',
        "friendlyName": dev_info['friendlyName'],
        "manufacturer": dev_info['manufacturer'],
        "model": f"{dev_info['model']} {dev_info['modelNumber']}",
    }

    async_add_entities(
        [
            SomneoLight(name, data, device_info, dev_info['serial']),
            SomneoNightLight(name, data, device_info, dev_info['serial']),
            SomneoSunset(name, data, device_info, dev_info['serial'])
        ]
    )

class SomneoLight(LightEntity):
    """Representation of an SmartSleep Light."""

    def __init__(self, name, data, device_info, serial):
        """Initialize an SomneoLight."""
        self._name = name
        self._data = data
        self._state = None
        self._brightness = None
        self._device_info = device_info
        self._serial = serial

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def should_poll(self):
        return True

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def unique_id(self):
        """Return the id of this light."""
        return self._serial + "_light"

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
        else:
            brightness = None

        self._data.somneo.toggle_light(True, brightness)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._data.somneo.toggle_light(False)
        self._state = False
        self.schedule_update_ha_state()

    async def async_update(self):
        """Fetch new state data for this light."""
        await self._data.update()
        self._state, self._brightness = self._data.somneo.light_status()

class SomneoNightLight(LightEntity):
    """Representation of a SmartSleep Light."""

    def __init__(self, name, data, device_info, serial):
        """Initialize an SomneoLight."""
        self._name = name + "_night"
        self._data = data
        self._state = None
        self._brightness = None
        self._device_info = device_info
        self._serial = serial

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
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
        """Return the id of this light."""
        return self._serial + '_night'

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._data.somneo.toggle_night_light(True)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._data.somneo.toggle_night_light(False)
        self._state = False
        self.schedule_update_ha_state()

    async def async_update(self):
        """Fetch new state data for this light."""
        await self._data.update()
        self._state = self._data.somneo.night_light_status()

class SomneoSunset(LightEntity):
    """Representation of the SmartSleep's sunset (dusk) mode."""

    def __init__(self, name, data, device_info, serial):
        """Initialize a Sunset mode entity."""
        self._name = "Sunset"
        self._data = data
        self._state = None
        self._timer = None
        self._brightness = None
        self._device_info = device_info
        self._serial = serial

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light setting in sunset mode, between 0..255."""
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def should_poll(self):
        return True

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def unique_id(self):
        """Return the id of this light."""
        return self._serial

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    def turn_on(self, **kwargs):
        """Instruct the sunset mode to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
        else:
            brightness = None
        self._data.somneo.toggle_sunset(True, brightness)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the sunset mode to turn off."""
        self._data.somneo.toggle_sunset(False)
        self._state = False
        self.schedule_update_ha_state()

    async def async_update(self):
        """Fetch new state data for sunset mode."""
        await self._data.update()
        self._state = self._data.somneo.sunset_status()
