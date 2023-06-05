"""Platform for sensor integration."""
from datetime import datetime
from decimal import Decimal
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorDeviceClass,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
)

from .const import DOMAIN, SENSORS
from .entity import SmartSleepEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add SmartSleep from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    sensors = []
    for sensor in list(SENSORS):
        sensors.append(SmartSleepSensor(coordinator, unique_id, name, device_info, sensor))
    sensors.append(
        SmartSleepNextAlarmSensor(coordinator, unique_id, name, device_info, "next")
    )

    async_add_entities(sensors, update_before_add=True)


class SmartSleepSensor(SmartSleepEntity, SensorEntity):
    _attr_state_class = STATE_CLASS_MEASUREMENT

    """Representation of a Sensor."""

    def __init__(self, coordinator, unique_id, name, dev_info, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, name, dev_info, sensor_type)

        self._attr_translation_key = sensor_type
        self._attr_native_unit_of_measurement = SENSORS[sensor_type]
        self._type = sensor_type

    @callback
    def _handle_coordinator_update(self) -> None:
        if self._type == "temperature":
            self._attr_native_value = self.coordinator.data["temperature"]
        if self._type == "humidity":
            self._attr_native_value = self.coordinator.data["humidity"]
        if self._type == "luminance":
            self._attr_native_value = self.coordinator.data["luminance"]
        if self._type == "noise":
            self._attr_native_value = self.coordinator.data["noise"]
        self.async_write_ha_state()

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


class SmartSleepNextAlarmSensor(SmartSleepEntity, SensorEntity):
    _attr_translation_key = "next_alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["next_alarm"]
        self.async_write_ha_state()
