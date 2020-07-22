"""Platform for binary sensor integration."""
import logging

from custom_components import somneo
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import *

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Somneo binary sensor platform."""
    name = discovery_info['name']

    dev = []
    for alarm in list(hass.data[DOMAIN].alarm_data):
        dev.append(SomneoAlarm(name, hass.data[DOMAIN], alarm))
    add_entities(dev, True)

class SomneoAlarm(BinarySensorEntity):
    """Representation of a binary  for alarms."""
    def __init__(self, name, data, alarm):
        """Initialize the sensor."""
        self._data = data
        self._name = name + "_" + alarm
        self._alarm = alarm
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
        return self._data.serial + '_' + self._alarm

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

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}

        attr['time'] = self._data.alarm_data[self._alarm]['time'].isoformat()

        days = []
        day_int = self._data.alarm_data[self._alarm]['days']
        if day_int & 2:
            days.append('mon')
        if day_int & 4:
            days.append('tue')
        if day_int & 8:
            days.append('wed')
        if day_int & 16:
            days.append('thu')
        if day_int & 32:
            days.append('fri')
        if day_int & 64:
            days.append('sat')
        if day_int & 128:
            days.append('sun')

        attr['days'] = days

        return attr
    
    def update(self):
        """Get the latest data and updates the states."""
        if self._data.alarm_data[self._alarm]['enabled'] == True:
            self._state = STATE_ON
        else:
            self._state = STATE_OFF




