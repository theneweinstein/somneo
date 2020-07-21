"""Platform for light integration."""
import logging

# Import the device class from the component that you want to support
from custom_components import somneo
from homeassistant.components.light import (LightEntity, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS)

from .const import *

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Somneo Light platform."""

    name = discovery_info['name']
    somneo_light = SomneoLight(name, hass.data[somneo.DOMAIN])
    somneo_night_light = SomneoNightLight(name, hass.data[somneo.DOMAIN])
    add_entities([somneo_light, somneo_night_light])

class SomneoLight(LightEntity):
    """Representation of an Somneo Light."""

    def __init__(self, name, data):
        """Initialize an SomneoLight."""
        self._name = name
        self._data = data
        self._state = None
        self._brightness = None

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
        return self._data.serial

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": self._data.manufacturer,
            "model": f"{self._data.model} {self._data.modelnumber}",
            "via_device": (DOMAIN, self._data.serial),
        }

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
        else:
            brightness = None

        self._data.toggle_light(True, brightness)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._data.toggle_light(False)
        self._state = False
        self.schedule_update_ha_state()

    def update(self):
        """Fetch new state data for this light."""
        self._data.update()
        self._state = self._data.light_data['onoff']
        self._brightness = int(int(self._data.light_data['ltlvl'])/25*255)

class SomneoNightLight(LightEntity):
    """Representation of an Somneo Light."""

    def __init__(self, name, data):
        """Initialize an SomneoLight."""
        self._name = name + "_night"
        self._state = None
        self._data = data

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
        return self._data.serial + '_night'

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": self._data.manufacturer,
            "model": f"{self._data.model} {self._data.modelnumber}",
            "via_device": (DOMAIN, self._data.serial),
        }

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._data.toggle_night_light(True)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._data.toggle_night_light(False)
        self._state = False
        self.schedule_update_ha_state()

    def update(self):
        """Fetch new state data for this light."""
        self._data.update()
        self._state = self._data.light_data['ngtlt']