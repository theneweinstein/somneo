"""Platform for sensor integration."""
import logging

from custom_components import smartsleep
from homeassistant.helpers.entity import Entity
from homeassistant.const import DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_ILLUMINANCE, DEVICE_CLASS_TEMPERATURE

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Add Somneo sensors from config_entry."""
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

    sensors = []
    for sensor in list(SENSORS):
        sensors.append(SomneoSensor(name, data, device_info, dev_info['serial'], sensor))
    sensors.append(SomneoNextAlarmSensor(name, data, device_info, dev_info['serial']))

    async_add_entities(sensors, True)


class SomneoSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, name, data, device_info, serial, sensor_type):
        """Initialize the sensor."""
        self._data = data
        self._name = name + "_" + sensor_type
        self._unit_of_measurement = SENSORS[sensor_type]
        self._type = sensor_type
        self._state = None
        self._device_info = device_info
        self._serial = serial

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._state
    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self._serial + '_' + self._type

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        if self._type == "temperature":
            return DEVICE_CLASS_TEMPERATURE
        if self._type == "humidity":
            return DEVICE_CLASS_HUMIDITY
        if self._type == "luminance":
            return DEVICE_CLASS_ILLUMINANCE
        else:
            return None

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()
        if self._type == "temperature":
            self._state = self._data.somneo.temperature()
        if self._type == "humidity":
            self._state = self._data.somneo.humidity()
        if self._type == "luminance":
            self._state = self._data.somneo.luminance()
        if self._type == "noise":
            self._state = self._data.somneo.noise()


class SomneoNextAlarmSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, name, data, device_info, serial):
        """Initialize the sensor."""
        self._data = data
        self._name = name + "_next_alarm"
        self._device_info = device_info
        self._serial = serial
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self._serial + '_next_alarm'

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return self._device_info

    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()
        self._state = self._data.somneo.next_alarm()
