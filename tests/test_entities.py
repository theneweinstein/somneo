"""Tests for the Somneo entity platforms."""
from __future__ import annotations

from datetime import time

from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ENTITY_ID,
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.somneo.const import DOMAIN

from .common import FAKE_DATA, SERIAL


def entity_id(hass: HomeAssistant, domain: str, identifier: str) -> str | None:
    """Find the entity id for a platform domain and unique id identifier."""
    registry = er.async_get(hass)
    return registry.async_get_entity_id(domain, DOMAIN, f"{SERIAL}_{identifier}")


async def test_sensor_values(setup_integration, hass: HomeAssistant) -> None:
    """Test the measurement sensors report coordinator data."""
    temperature = hass.states.get(entity_id(hass, Platform.SENSOR, "temperature"))
    assert temperature is not None
    assert temperature.state == "22.5"
    assert temperature.attributes[ATTR_UNIT_OF_MEASUREMENT] == "°C"
    assert (
        temperature.attributes[ATTR_DEVICE_CLASS]
        == SensorDeviceClass.TEMPERATURE
    )

    humidity = hass.states.get(entity_id(hass, Platform.SENSOR, "humidity"))
    assert humidity is not None
    assert humidity.state == "45.0"

    luminance = hass.states.get(entity_id(hass, Platform.SENSOR, "luminance"))
    assert luminance is not None
    assert luminance.state == "100"
    assert (
        luminance.attributes[ATTR_DEVICE_CLASS]
        == SensorDeviceClass.ILLUMINANCE
    )

    noise = hass.states.get(entity_id(hass, Platform.SENSOR, "noise"))
    assert noise is not None
    assert noise.state == "30.0"


async def test_alarm_status_sensor(setup_integration, hass: HomeAssistant) -> None:
    """Test the alarm status sensor."""
    status = hass.states.get(entity_id(hass, Platform.SENSOR, "alarm_status"))
    assert status is not None
    assert status.state == "off"


async def test_next_alarm_sensor_unknown_when_none(
    setup_integration, hass: HomeAssistant
) -> None:
    """Test the next alarm sensor is unknown when no alarm is set."""
    next_alarm = hass.states.get(entity_id(hass, Platform.SENSOR, "next"))
    assert next_alarm is not None
    assert next_alarm.state == STATE_UNKNOWN


async def test_light_state(setup_integration, hass: HomeAssistant) -> None:
    """Test the main light reports state and brightness."""
    light = hass.states.get(entity_id(hass, Platform.LIGHT, "light"))
    assert light is not None
    assert light.state == STATE_ON
    assert light.attributes[ATTR_BRIGHTNESS] == FAKE_DATA["light_brightness"]


async def test_light_turn_on(setup_integration, hass, mock_somneo) -> None:
    """Test turning on the light calls the device with a brightness."""
    light_id = entity_id(hass, Platform.LIGHT, "light")
    await hass.services.async_call(
        Platform.LIGHT,
        "turn_on",
        {ATTR_ENTITY_ID: light_id, ATTR_BRIGHTNESS: 200},
        blocking=True,
    )
    mock_somneo.toggle_light.assert_awaited_once_with(True, brightness=200)


async def test_night_light_state(setup_integration, hass: HomeAssistant) -> None:
    """Test the night light reports state."""
    night = hass.states.get(entity_id(hass, Platform.LIGHT, "nightlight"))
    assert night is not None
    assert night.state == STATE_OFF


async def test_alarm_switch_state(setup_integration, hass: HomeAssistant) -> None:
    """Test the alarm switch reflects the enabled state."""
    alarm = hass.states.get(entity_id(hass, Platform.SWITCH, "alarm0"))
    assert alarm is not None
    assert alarm.state == STATE_ON
    assert alarm.attributes["time"] == time(7, 30)
    assert alarm.attributes["days"] == ["mon", "tue", "wed", "thu", "fri"]
    assert alarm.attributes["powerwake"] is True
    assert alarm.attributes["powerwake_delta"] == 10


async def test_alarm_switch_turn_off(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test turning off an alarm switch calls the device."""
    alarm_id = entity_id(hass, Platform.SWITCH, "alarm0")
    await hass.services.async_call(
        Platform.SWITCH,
        "turn_off",
        {ATTR_ENTITY_ID: alarm_id},
        blocking=True,
    )
    mock_somneo.toggle_alarm.assert_awaited_once_with(0, False)


async def test_sunset_switch(setup_integration, hass: HomeAssistant) -> None:
    """Test the sunset switch exposes its state attributes."""
    sunset = hass.states.get(entity_id(hass, Platform.SWITCH, "sunset"))
    assert sunset is not None
    assert sunset.state == STATE_OFF
    assert sunset.attributes["duration"] == 30
    assert sunset.attributes["curve"] == "sunny day"


async def test_display_switch(setup_integration, hass: HomeAssistant) -> None:
    """Test the display always-on switch."""
    display = hass.states.get(entity_id(hass, Platform.SWITCH, "display_on"))
    assert display is not None
    assert display.state == STATE_OFF


async def test_snooze_number(setup_integration, hass: HomeAssistant) -> None:
    """Test the snooze number entity."""
    snooze = hass.states.get(entity_id(hass, Platform.NUMBER, "snooze"))
    assert snooze is not None
    assert snooze.state == "5"


async def test_snooze_button_press(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test pressing the snooze button calls the device."""
    button_id = entity_id(hass, Platform.BUTTON, "alarm_snooze")
    await hass.services.async_call(
        Platform.BUTTON,
        "press",
        {ATTR_ENTITY_ID: button_id},
        blocking=True,
    )
    mock_somneo.snooze_alarm.assert_awaited_once()


async def test_entity_registry_entries(setup_integration, hass: HomeAssistant) -> None:
    """Test representative entities exist per platform domain."""
    registry = er.async_get(hass)
    assert registry.async_get_entity_id(
        Platform.SENSOR, DOMAIN, f"{SERIAL}_temperature"
    )
    assert registry.async_get_entity_id(Platform.LIGHT, DOMAIN, f"{SERIAL}_light")
    assert registry.async_get_entity_id(Platform.SWITCH, DOMAIN, f"{SERIAL}_alarm0")

