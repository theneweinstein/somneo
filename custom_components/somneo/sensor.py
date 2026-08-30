"""Sensor entities for Somneo."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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

    sensors = []
    for sensor in list(SENSORS):
        sensors.append(SomneoSensor(coordinator, unique_id, sensor))
    sensors.append(SomneoNextAlarmSensor(coordinator, unique_id, "next"))
    sensors.append(SomneoAlarmStatus(coordinator, unique_id, "alarm_status"))

    async_add_entities(sensors, update_before_add=True)


class SomneoSensor(SomneoEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        unique_id: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, sensor_type)

        self._attr_translation_key = sensor_type
        self._attr_native_unit_of_measurement = SENSORS[sensor_type]
        self._type = sensor_type

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the sensor value."""
        if self._type == "temperature":
            self._attr_native_value = self.coordinator.data["temperature"]
        elif self._type == "humidity":
            self._attr_native_value = self.coordinator.data["humidity"]
        elif self._type == "luminance":
            self._attr_native_value = self.coordinator.data["luminance"]
        elif self._type == "noise":
            self._attr_native_value = self.coordinator.data["noise"]
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the class of this device, from component DEVICE_CLASSES."""
        if self._type == "temperature":
            return SensorDeviceClass.TEMPERATURE
        if self._type == "humidity":
            return SensorDeviceClass.HUMIDITY
        if self._type == "luminance":
            return SensorDeviceClass.ILLUMINANCE
        if self._type == "noise":
            return SensorDeviceClass.SOUND_PRESSURE
        return None


class SomneoNextAlarmSensor(SomneoEntity, SensorEntity):
    """Representation of a Next alarm sensor."""

    _attr_translation_key = "next_alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the next alarm sensor value."""
        self._attr_native_value = self.coordinator.data["next_alarm"]
        self.async_write_ha_state()


class SomneoAlarmStatus(SomneoEntity, SensorEntity):
    """Sensor entity that provides the current status of the alarm."""

    _attr_translation_key = "alarm_status"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the alarm status sensor value."""
        self._attr_native_value = self.coordinator.data["somneo_status"]
        self.async_write_ha_state()
