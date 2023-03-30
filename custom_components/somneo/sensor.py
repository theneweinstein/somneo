"""Platform for sensor integration."""
from datetime import datetime
from decimal import Decimal
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorDeviceClass, STATE_CLASS_MEASUREMENT, SensorEntity

from .const import DOMAIN, SENSORS
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data['dev_info']  

    sensors = []
    for sensor in list(SENSORS):
        sensors.append(SomneoSensor(coordinator, unique_id, name, device_info, sensor))
    sensors.append(SomneoNextAlarmSensor(coordinator, unique_id, name, device_info, 'next'))

    async_add_entities(sensors, True)
    

class SomneoSensor(SomneoEntity, SensorEntity):
    
    _attr_state_class = STATE_CLASS_MEASUREMENT

    """Representation of a Sensor."""
    def __init__(self, coordinator, unique_id, name, dev_info, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, name, dev_info, sensor_type)

        self._attr_name = sensor_type.capitalize()
        self._attr_native_unit_of_measurement = SENSORS[sensor_type]
        self._type = sensor_type

    @property
    def native_value(self) -> Decimal:
        """Returns the native value of this device."""
        if self._type == "temperature":
            return self.coordinator.data['temperature']
        if self._type == "humidity":
            return self.coordinator.data['humidity']
        if self._type == "luminance":
            return self.coordinator.data['luminance']
        if self._type == "noise":
            return self.coordinator.data['noise']

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the class of this device, from component DEVICE_CLASSES."""
        if self._type == "temperature":
            return SensorDeviceClass.TEMPERATURE
        if self._type == "humidity":
            return SensorDeviceClass.HUMIDITY
        if self._type == "luminance":
            return SensorDeviceClass.ILLUMINANCE
        if self._type == "noise":
            return SensorDeviceClass.SOUND_PRESSURE
        else:
            return None


class SomneoNextAlarmSensor(SomneoEntity, SensorEntity):

    _attr_name = "Next_alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime:
        """Returns the native value of this device."""
        return self.coordinator.data['next_alarm']
