"""Switch entities for Somneo."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_CHANNEL,
    ATTR_CURVE,
    ATTR_DURATION,
    ATTR_LEVEL,
    ATTR_SOURCE,
    DOMAIN,
)
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

    alarms = []
    pwrwk = []
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(
            SomneoAlarmToggle(coordinator, unique_id, name, device_info, alarm)
        )
        pwrwk.append(
            SomneoPowerWakeToggle(coordinator, unique_id, name, device_info, alarm)
        )

    sunset = [SomneoSunsetToggle(coordinator, unique_id, name, device_info, "sunset")]

    display = [SomneoDisplayToggle(coordinator, unique_id, name, device_info, 'display_on')]

    async_add_entities(alarms, update_before_add=True)
    async_add_entities(pwrwk, update_before_add=True)
    async_add_entities(sunset, update_before_add=True)
    async_add_entities(display, update_before_add=True)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "set_alarm_light",
        {
            vol.Optional(ATTR_CURVE): cv.string,
            vol.Optional(ATTR_LEVEL): cv.positive_int,
            vol.Optional(ATTR_DURATION): cv.positive_int,
        },
        "set_alarm_light",
    )

    platform.async_register_entity_service(
        "set_alarm_sound",
        {
            vol.Optional(ATTR_SOURCE): cv.string,
            vol.Optional(ATTR_LEVEL): cv.positive_int,
            vol.Optional(ATTR_CHANNEL): cv.string,
        },
        "set_alarm_sound",
    )

    platform.async_register_entity_service("remove_alarm", {}, "remove_alarm")

    platform.async_register_entity_service("add_alarm", {}, "add_alarm")


class SomneoAlarmToggle(SomneoEntity, SwitchEntity):
    """Representation of a alarm switch."""

    _attr_should_poll = True
    _attr_translation_key = "alarm"

    def __init__(self, coordinator, unique_id, name, device_info, alarm):
        """Initialize the switches."""
        super().__init__(
            coordinator, unique_id, name, device_info, "alarm" + str(alarm)
        )

        self._attr_translation_placeholders  = {"number": str(alarm)}
        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["alarms"][self._alarm]["enabled"]

        self._attr_extra_state_attributes = {
            "time": self.coordinator.data["alarms"][self._alarm]["time"],
            "days": self.coordinator.data["alarms"][self._alarm]["days"],
            "powerwake": self.coordinator.data["alarms"][self._alarm]["powerwake"],
            "powerwake_delta": self.coordinator.data["alarms"][self._alarm][
                "powerwake_delta"
            ],
        }
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any):
        """Turn on the switch."""
        await self.coordinator.async_toggle_alarm(self._alarm, True)

    async def async_turn_off(self, **kwargs: Any):
        """Turn off the switch."""
        await self.coordinator.async_toggle_alarm(self._alarm, False)

    # Define service-calls
    async def set_alarm_light(
        self, curve: str = "sunny day", level: int = 20, duration: int = 30
    ):
        """Adjust the light settings of an alarm."""
        await self.coordinator.async_set_alarm_light(
            self._alarm, curve=curve, level=level, duration=duration
        )

    async def set_alarm_sound(
        self, source: str = "wake-up", level: int = 12, channel: str = "forest birds"
    ):
        """Adjust the sound settings of an alarm."""
        await self.coordinator.async_set_alarm_sound(
            self._alarm, source=source, level=level, channel=channel
        )

    async def remove_alarm(self):
        """Remove alarm from list in wake-up app."""
        await self.coordinator.async_remove_alarm(self._alarm)

    async def add_alarm(self):
        """Add alarm to list in wake-up app."""
        await self.coordinator.async_add_alarm(self._alarm)


class SomneoPowerWakeToggle(SomneoEntity, SwitchEntity):
    """Representation of a Powerwake switch."""

    _attr_should_poll = True
    _attr_translation_key = "powerwake"

    def __init__(self, coordinator, unique_id, name, device_info, alarm):
        """Initialize the switches."""
        super().__init__(
            coordinator, unique_id, name, device_info, "alarm" + str(alarm) + "_PW"
        )

        self._attr_translation_placeholders  = {"number": str(alarm)}
        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["alarms"][self._alarm]["powerwake"]
        self._attr_extra_state_attributes = {
            "powerwake_delta": self.coordinator.data["alarms"][self._alarm][
                "powerwake_delta"
            ]
        }
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any):
        """Turn on the switch."""
        await self.coordinator.async_toggle_alarm_powerwake(self._alarm, True)

    async def async_turn_off(self, **kwargs: Any):
        """Turn off the switch."""
        await self.coordinator.async_toggle_alarm_powerwake(self._alarm, False)


class SomneoSunsetToggle(SomneoEntity, SwitchEntity):
    """Representation of a Sunset switch."""

    _attr_should_poll = True
    _attr_translation_key = "sunset"

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["sunset"]["is_on"]
        self._attr_extra_state_attributes = {
            "duration": self.coordinator.data["sunset"]["duration"],
            "curve": self.coordinator.data["sunset"]["curve"],
            "level": self.coordinator.data["sunset"]["level"],
            "sound": self.coordinator.data["sunset"]["sound"],
            "volume": self.coordinator.data["sunset"]["volume"],
        }
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any):
        """Turn on the switch."""
        await self.coordinator.async_toggle_sunset(True)

    async def async_turn_off(self, **kwargs: Any):
        """Turn off the switch."""
        await self.coordinator.async_toggle_sunset(False)

class SomneoDisplayToggle(SomneoEntity, SwitchEntity):
    """Representation of a display always on switch."""

    _attr_should_poll = True
    _attr_translation_key = 'display_on'

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["display_always_on"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any):
        """Turn on the switch."""
        await self.coordinator.async_set_display(state=True)

    async def async_turn_off(self, **kwargs: Any):
        """Turn off the switch."""
        await self.coordinator.async_set_display(state=False)
