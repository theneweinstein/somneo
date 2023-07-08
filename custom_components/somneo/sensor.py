"""Sensor entities for Somneo."""
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
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    sensors = []
    for sensor in list(SENSORS):
        sensors.append(SomneoSensor(coordinator, unique_id, name, device_info, sensor))
    sensors.append(
        SomneoNextAlarmSensor(coordinator, unique_id, name, device_info, "next")
    )
    sensors.append(
        SomneoAlarmStatus(coordinator, unique_id, name, device_info, "alarm_status")
    )

    async_add_entities(sensors, update_before_add=True)


class SomneoSensor(SomneoEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_state_class = STATE_CLASS_MEASUREMENT

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


class SomneoNextAlarmSensor(SomneoEntity, SensorEntity):
    """Representation of a Next alarm sensor."""

    _attr_translation_key = "next_alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["next_alarm"]
        self.async_write_ha_state()


class SomneoAlarmStatus(SomneoEntity, SensorEntity):
    """Sensor entity that provides the current status of the alarm."""

    _attr_translation_key = "alarm_status"

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["alarm_status"]
        self.async_write_ha_state()

    @property
    def icon(self):
        if self._attr_native_value == "off":
            return "mdi:alarm-off"
        if self._attr_native_value == "on":
            return "mdi:alarm"
        if self._attr_native_value == "snooze":
            return "mdi:alarm-snooze"
        if self._attr_native_value == "wake-up":
            return "mdi:weather-sunset-up"
