"""Support for Philips Somneo devices."""
from __future__ import annotations

import logging
from datetime import datetime, time, timedelta
from typing import cast

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.service import async_register_platform_entity_service
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as ha_dt
from pysomneo import Somneo

from .const import (
    ATTR_CHANNEL,
    ATTR_CURVE,
    ATTR_DURATION,
    ATTR_LEVEL,
    ATTR_SOURCE,
    DEFAULT_NAME,
    DOMAIN,
)
from .models import SomneoData

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.MEDIA_PLAYER,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.TIME,
]
SCAN_INTERVAL = timedelta(seconds=10)

SERVICE_SET_ALARM_LIGHT = "set_alarm_light"
SERVICE_SET_ALARM_SOUND = "set_alarm_sound"
SERVICE_ADD_ALARM = "add_alarm"
SERVICE_REMOVE_ALARM = "remove_alarm"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Somneo component."""
    _async_register_entity_services(hass)

    return True


@callback
def _async_register_entity_services(hass: HomeAssistant) -> None:
    """Register entity services for the Somneo integration."""
    async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_SET_ALARM_LIGHT,
        entity_domain=Platform.SWITCH,
        schema={
            vol.Optional(ATTR_CURVE): cv.string,
            vol.Optional(ATTR_LEVEL): cv.positive_int,
            vol.Optional(ATTR_DURATION): cv.positive_int,
        },
        func="set_alarm_light",
    )

    async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_SET_ALARM_SOUND,
        entity_domain=Platform.SWITCH,
        schema={
            vol.Optional(ATTR_SOURCE): cv.string,
            vol.Optional(ATTR_LEVEL): cv.positive_int,
            vol.Optional(ATTR_CHANNEL): cv.string,
        },
        func="set_alarm_sound",
    )

    async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_REMOVE_ALARM,
        entity_domain=Platform.SWITCH,
        schema={},
        func="remove_alarm",
    )

    async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_ADD_ALARM,
        entity_domain=Platform.SWITCH,
        schema={},
        func="add_alarm",
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Somneo component."""
    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    unique_id = entry.unique_id
    assert unique_id is not None

    coordinator = SomneoCoordinator(hass, host, name, unique_id)
    await coordinator.async_fetch_device_info()

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        # v1 stored a legacy "options" blob inside the data dict.
        new = {**config_entry.data}
        new.pop("options", None)
        hass.config_entries.async_update_entry(config_entry, data=new, version=3)

    if config_entry.version == 2:
        # v2 stored use_session directly in the data dict.
        new = {**config_entry.data}
        new.pop("use_session", None)
        hass.config_entries.async_update_entry(config_entry, data=new, version=3)

    if config_entry.version == 3:
        # v3 stored dev_info in the entry data; it now lives on the
        # coordinator and is fetched from the device at setup time.
        new = {**config_entry.data}
        new.pop("dev_info", None)
        new.pop("options", None)
        hass.config_entries.async_update_entry(config_entry, data=new, version=4)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


class SomneoCoordinator(DataUpdateCoordinator[SomneoData]):
    """
    Represent a Somneo Coordinator.

    The coordinator is the single source of truth for all device state. The
    set of alarm slots is fixed per device model; the per-alarm entities
    (switch, number, select, text, time) are created once at setup time based
    on the alarms reported by the first successful refresh. If the device
    reports a different number of alarm slots (e.g. after a firmware change),
    reload the integration to recreate the entities.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        name: str,
        unique_id: str,
    ) -> None:
        """Initialize Somneo client."""
        self.somneo = Somneo(host)
        self._unique_id = unique_id
        self._name = name
        self._dev_info: dict[str, str] = {}

        # Build a stable DeviceInfo for all entities of this device. The
        # identifier uses the config entry unique_id (stable), never the
        # device-reported serial which may fall back to a random UUID.
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="Royal Philips Electronics",
            model="Wake-up Light",
            name=name,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self._async_update,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            ),
        )

    async def async_fetch_device_info(self) -> None:
        """
        Fetch device info from the device to enrich DeviceInfo.

        Best-effort: failures keep the default device info so that setup is
        not blocked on device metadata.
        """
        try:
            self._dev_info = await self.somneo.get_device_info()
        except Exception:  # noqa: BLE001
            _LOGGER.warning(
                "Unable to fetch device info from %s, using defaults", self._name
            )

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer=self._dev_info.get(
                "manufacturer", "Royal Philips Electronics"
            ),
            model=" ".join(
                part
                for part in (
                    self._dev_info.get("model", "Wake-up Light"),
                    self._dev_info.get("modelnumber"),
                )
                if part
            ),
            name=self._name,
        )

    async def _async_update(self) -> SomneoData:
        """Fetch the latest data."""
        try:
            data = cast(SomneoData, await self.somneo.fetch_data(force_slow_refresh=True))

            if data is None:
                _LOGGER.debug("Somneo fetch returned None, using previous data")
                data = self.data or self._default_data()
            else:
                # Convert naive next_alarm datetime to timezone-aware UTC datetime
                # using the Home Assistant configured timezone
                next_alarm = data.get("next_alarm")
                if isinstance(next_alarm, datetime) and next_alarm.tzinfo is None:
                    ha_tz = ha_dt.get_time_zone(self.hass.config.time_zone)
                    if ha_tz:
                        data["next_alarm"] = next_alarm.replace(
                            tzinfo=ha_tz
                        ).astimezone(ha_dt.UTC)
        except Exception:
            _LOGGER.exception("Error fetching data from Somneo")
            # If we have previous data, return it; otherwise return empty dict
            # with defaults
            if self.data is not None:
                return self.data
            return self._default_data()

        return data

    def _default_data(self) -> SomneoData:
        """Return data dict with defaults to prevent KeyError in platforms."""
        return {
            "alarms": {},
            "player": {},
            "sunset": {},
            "next_alarm": None,
            "snooze_time": 5,
            "temperature": None,
            "humidity": None,
            "luminance": None,
            "noise": None,
            "light_is_on": False,
            "light_brightness": 0,
            "nightlight_is_on": False,
            "somneo_status": "unknown",
            "display_always_on": False,
            "display_brightness": 0,
        }

    async def async_toggle_light(
        self, state: bool, brightness: int | None = None
    ) -> None:
        """Toggle the main light."""
        await self.somneo.toggle_light(state, brightness=brightness)
        await self.async_request_refresh()

    async def async_toggle_nightlight(self, state: bool) -> None:
        """Toggle the night light."""
        await self.somneo.toggle_night_light(state)
        await self.async_request_refresh()

    async def async_toggle_alarm(self, alarm: str, state: bool) -> None:
        """Toggle an alarm."""
        await self.somneo.toggle_alarm(alarm, state)
        await self.async_request_refresh()

    async def async_dismiss_alarm(self) -> None:
        """Dismiss alarm."""
        await self.somneo.dismiss_alarm()
        await self.async_request_refresh()

    async def async_set_alarm(
        self, alarm: str, alarm_time: time | None = None, days: str | list | None = None
    ) -> None:
        """Set alarm time."""
        await self.somneo.set_alarm(alarm, v_time=alarm_time, days=days)
        await self.async_request_refresh()

    async def async_toggle_alarm_powerwake(self, alarm: str, state: bool) -> None:
        """Toggle powerwake (default 10 minutes)."""
        await self.somneo.set_alarm_powerwake(alarm, onoff=state, delta=10)
        await self.async_request_refresh()

    async def async_set_alarm_powerwake(self, alarm: str, delta: int = 0) -> None:
        """Set powerwake time."""
        await self.somneo.set_alarm_powerwake(
            alarm, onoff=bool(delta), delta=delta
        )
        await self.async_request_refresh()

    async def async_snooze_alarm(self) -> None:
        """Snooze alarm."""
        await self.somneo.snooze_alarm()
        await self.async_request_refresh()

    async def async_set_snooze_time(self, snooze_time: int | str) -> None:
        """Set snooze time."""
        await self.somneo.set_snooze_time(int(snooze_time))
        await self.async_request_refresh()

    async def async_set_alarm_light(
        self, alarm: str, curve: str = "sunny day", level: int = 20, duration: int = 30
    ) -> None:
        """Adjust the light settings of an alarm."""
        await self.somneo.set_alarm_light(
            alarm, curve=curve, level=level, duration=duration
        )
        await self.async_request_refresh()

    async def async_set_alarm_sound(
        self,
        alarm: str,
        source: str = "wake-up",
        level: int = 12,
        channel: str = "forest birds",
    ) -> None:
        """Adjust the sound settings of an alarm."""
        await self.somneo.set_alarm_sound(
            alarm, source=source, level=level, channel=channel
        )
        await self.async_request_refresh()

    async def async_remove_alarm(self, alarm: str) -> None:
        """Remove alarm from list in Somneo app."""
        await self.somneo.remove_alarm(alarm)

    async def async_add_alarm(self, alarm: str) -> None:
        """Add alarm to list in Somneo app."""
        await self.somneo.add_alarm(alarm)

    async def async_player_toggle(self, state: bool) -> None:
        """Toggle the audio player."""
        await self.somneo.toggle_player(state)
        await self.async_request_refresh()

    async def async_set_player_volume(self, volume: float) -> None:
        """Set the volume of the audio player."""
        await self.somneo.set_player_volume(volume)
        await self.async_request_refresh()

    async def async_set_player_source(self, source: str) -> None:
        """Set the source of the audio player."""
        await self.somneo.set_player_source(source)
        await self.async_request_refresh()

    async def async_toggle_sunset(self, state: bool) -> None:
        """Toggle the main light."""
        await self.somneo.toggle_sunset(state)
        await self.async_request_refresh()

    async def async_set_sunset(
        self,
        curve: str | None = None,
        level: int | None = None,
        duration: int | None = None,
        sound: str | None = None,
        volume: int | None = None,
    ) -> None:
        """Adjust the sunset settings."""
        await self.somneo.set_sunset(
            curve=curve, level=level, duration=duration, sound=sound, volume=volume
        )
        await self.async_request_refresh()

    async def async_set_display(
        self, state: bool | None = None, brightness: int | None = None
    ) -> None:
        """Adjust the display."""
        await self.somneo.set_display(state=state, brightness=brightness)
        await self.async_request_refresh()
