"""Platform for sensor integration."""
import logging

from datetime import datetime

from homeassistant.const import DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_ILLUMINANCE, DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_PRESSURE, DEVICE_CLASS_TIMESTAMP
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT, SensorEntity

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

    sensors = []
    for sensor in list(SENSORS):
        sensors.append(SomneoSensor(name, data, device_info, dev_info['serial'], sensor))
    sensors.append(SomneoNextAlarmSensor(name, data, device_info, dev_info['serial']))

    async_add_entities(sensors, True)
    

class SomneoSensor(SensorEntity):
    
    _attr_state_class = STATE_CLASS_MEASUREMENT

    """Representation of a Sensor."""
    def __init__(self, name, data, device_info, serial, sensor_type):
        """Initialize the sensor."""
        self._data = data
        self._attr_name = name + "_" + sensor_type
        self._attr_native_unit_of_measurement = SENSORS[sensor_type]
        self._type = sensor_type
        self._attr_native_value = None
        self._attr_device_info = device_info
        self._attr_unique_id = serial + '_' + sensor_type

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        if self._type == "temperature":
            return DEVICE_CLASS_TEMPERATURE
        if self._type == "humidity":
            return DEVICE_CLASS_HUMIDITY
        if self._type == "luminance":
            return DEVICE_CLASS_ILLUMINANCE
        if self._type == "pressure":
            return DEVICE_CLASS_PRESSURE
        else:
            return None
    
    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()
        if self._type == "temperature":
            self._attr_native_value = self._data.somneo.temperature()
        if self._type == "humidity":
            self._attr_native_value = self._data.somneo.humidity()
        if self._type == "luminance":
            self._attr_native_value = self._data.somneo.luminance()
        if self._type == "noise":
            self._attr_native_value = self._data.somneo.noise()


class SomneoNextAlarmSensor(SensorEntity):
    """Representation of a Sensor."""
    def __init__(self, name, data, device_info, serial):
        """Initialize the sensor."""
        self._data = data
        self._attr_name = name + "_next_alarm"
        self._attr_device_info = device_info
        self._attr_unique_id = serial + '_next_alarm'
        self._attr_native_value = None
        self._attr_device_class = DEVICE_CLASS_TIMESTAMP
    
    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()
        self._attr_native_value = datetime.fromisoformat(self._data.somneo.next_alarm()).astimezone() if self._data.somneo.next_alarm() else None
