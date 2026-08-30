"""Tests for the Somneo entity services."""
from __future__ import annotations

from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant

from custom_components.somneo.const import DOMAIN

from .test_entities import entity_id


async def test_services_registered(setup_integration, hass: HomeAssistant) -> None:
    """Test the entity services are registered under the somneo domain."""
    for service in (
        "set_alarm_light",
        "set_alarm_sound",
        "remove_alarm",
        "add_alarm",
    ):
        assert hass.services.has_service(DOMAIN, service)


async def test_set_alarm_light_service(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test the set_alarm_light service dispatches to the target entity."""
    alarm_id = entity_id(hass, Platform.SWITCH, "alarm0")
    await hass.services.async_call(
        DOMAIN,
        "set_alarm_light",
        {
            ATTR_ENTITY_ID: alarm_id,
            "curve": "island red",
            "level": 15,
            "duration": 30,
        },
        blocking=True,
    )
    mock_somneo.set_alarm_light.assert_awaited_once_with(
        0, curve="island red", level=15, duration=30
    )


async def test_set_alarm_sound_service(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test the set_alarm_sound service dispatches to the target entity."""
    alarm_id = entity_id(hass, Platform.SWITCH, "alarm0")
    await hass.services.async_call(
        DOMAIN,
        "set_alarm_sound",
        {
            ATTR_ENTITY_ID: alarm_id,
            "source": "wake-up",
            "level": 12,
            "channel": "forest birds",
        },
        blocking=True,
    )
    mock_somneo.set_alarm_sound.assert_awaited_once_with(
        0, source="wake-up", level=12, channel="forest birds"
    )


async def test_add_alarm_service(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test the add_alarm service dispatches to the target entity."""
    alarm_id = entity_id(hass, Platform.SWITCH, "alarm1")
    await hass.services.async_call(
        DOMAIN,
        "add_alarm",
        {ATTR_ENTITY_ID: alarm_id},
        blocking=True,
    )
    mock_somneo.add_alarm.assert_awaited_once_with(1)


async def test_remove_alarm_service(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test the remove_alarm service dispatches to the target entity."""
    alarm_id = entity_id(hass, Platform.SWITCH, "alarm1")
    await hass.services.async_call(
        DOMAIN,
        "remove_alarm",
        {ATTR_ENTITY_ID: alarm_id},
        blocking=True,
    )
    mock_somneo.remove_alarm.assert_awaited_once_with(1)
