"""Tests for the per-alarm entities (select, number, time, text)."""
from __future__ import annotations

from datetime import time

from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant

from .test_entities import entity_id


async def test_select_days_state(setup_integration, hass: HomeAssistant) -> None:
    """Test the alarm days select shows the current day type."""
    select_id = entity_id(hass, Platform.SELECT, "alarm0")
    select = hass.states.get(select_id)
    assert select is not None
    assert select.state == "workdays"


async def test_select_days_options(setup_integration, hass: HomeAssistant) -> None:
    """Test the alarm days select exposes the expected options."""
    select_id = entity_id(hass, Platform.SELECT, "alarm0")
    select = hass.states.get(select_id)
    assert select is not None
    assert select.attributes["options"] == [
        "workdays",
        "weekend",
        "tomorrow",
        "daily",
        "custom",
    ]


async def test_select_days_change(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test selecting a new day type calls the device."""
    select_id = entity_id(hass, Platform.SELECT, "alarm0")
    await hass.services.async_call(
        Platform.SELECT,
        "select_option",
        {ATTR_ENTITY_ID: select_id, "option": "weekend"},
        blocking=True,
    )
    mock_somneo.set_alarm.assert_awaited_once_with(0, v_time=None, days="weekend")


async def test_number_powerwake_delta(setup_integration, hass: HomeAssistant) -> None:
    """Test the powerwake delta number shows the device value."""
    number_id = entity_id(hass, Platform.NUMBER, "alarm0_powerwake_delta")
    number = hass.states.get(number_id)
    assert number is not None
    assert number.state == "10"


async def test_number_powerwake_delta_set(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test setting the powerwake delta calls the device."""
    number_id = entity_id(hass, Platform.NUMBER, "alarm0_powerwake_delta")
    await hass.services.async_call(
        Platform.NUMBER,
        "set_value",
        {ATTR_ENTITY_ID: number_id, "value": 20},
        blocking=True,
    )
    mock_somneo.set_alarm_powerwake.assert_awaited_once_with(
        0, onoff=True, delta=20
    )


async def test_time_alarm(setup_integration, hass: HomeAssistant) -> None:
    """Test the alarm time entity shows the device time."""
    time_id = entity_id(hass, Platform.TIME, "alarm0_time")
    alarm_time = hass.states.get(time_id)
    assert alarm_time is not None
    assert alarm_time.state == "07:30:00"


async def test_time_alarm_set(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test setting the alarm time calls the device."""
    time_id = entity_id(hass, Platform.TIME, "alarm0_time")
    await hass.services.async_call(
        Platform.TIME,
        "set_value",
        {ATTR_ENTITY_ID: time_id, "time": "06:45:00"},
        blocking=True,
    )
    mock_somneo.set_alarm.assert_awaited_once_with(
        0, v_time=time(6, 45), days=None
    )


async def test_text_alarm_days(setup_integration, hass: HomeAssistant) -> None:
    """Test the alarm days text shows the comma separated days."""
    text_id = entity_id(hass, Platform.TEXT, "alarm0")
    text = hass.states.get(text_id)
    assert text is not None
    assert text.state == "mon,tue,wed,thu,fri"


async def test_text_alarm_days_set(
    setup_integration, hass: HomeAssistant, mock_somneo
) -> None:
    """Test setting the alarm days text calls the device."""
    text_id = entity_id(hass, Platform.TEXT, "alarm0")
    await hass.services.async_call(
        Platform.TEXT,
        "set_value",
        {ATTR_ENTITY_ID: text_id, "value": "mon,tue"},
        blocking=True,
    )
    mock_somneo.set_alarm.assert_awaited_once_with(
        0, v_time=None, days=["mon", "tue"]
    )
