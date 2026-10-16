"""Sensor entities for Somneo."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfSoundPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    "temperature": SensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    "humidity": SensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    "luminance": SensorEntityDescription(
        key="luminance",
        translation_key="luminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    "noise": SensorEntityDescription(
        key="noise",
        translation_key="noise",
        device_class=SensorDeviceClass.SOUND_PRESSURE,
        native_unit_of_measurement=UnitOfSoundPressure.DECIBEL,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None

    sensors = [
        SomneoSensor(coordinator, unique_id, sensor)
        for sensor in list(SENSOR_DESCRIPTIONS)
    ]
    sensors.append(SomneoNextAlarmSensor(coordinator, unique_id, "next"))
    sensors.append(SomneoAlarmStatus(coordinator, unique_id, "alarm_status"))

    async_add_entities(sensors, update_before_add=True)


class SomneoSensor(SomneoEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self,
        coordinator,
        unique_id: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, sensor_type)

        self.entity_description = SENSOR_DESCRIPTIONS[sensor_type]
        self._type = sensor_type

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the sensor value."""
        self._attr_native_value = self.coordinator.data[self._type]
        self.async_write_ha_state()


class SomneoNextAlarmSensor(SomneoEntity, SensorEntity):
    """Representation of a Next alarm sensor."""

    _attr_translation_key = "next_alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the next alarm sensor value."""
        next_alarm = self.coordinator.data["next_alarm"]
        # The coordinator guarantees a timezone-aware datetime; a naive value
        # would be invalid for a TIMESTAMP sensor, so drop it defensively.
        if next_alarm is not None and next_alarm.tzinfo is None:
            _LOGGER.warning(
                "next_alarm is not timezone-aware (%s), ignoring", next_alarm
            )
            next_alarm = None
        self._attr_native_value = next_alarm
        self.async_write_ha_state()


class SomneoAlarmStatus(SomneoEntity, SensorEntity):
    """Sensor entity that provides the current status of the alarm."""

    _attr_translation_key = "alarm_status"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the alarm status sensor value."""
        self._attr_native_value = self.coordinator.data["somneo_status"]
        self.async_write_ha_state()

