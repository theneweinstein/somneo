""" Philips Somneo """
from datetime import timedelta
import logging
import requests
from typing import Final
import datetime

from pysomneo import Somneo

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, NOTIFICATION_ID, NOTIFICATION_TITLE, UNKNOWN, WEEKEND, WORKDAYS, TOMORROW, EVERYDAY, HOURS, MINUTES

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final[list[Platform]] = [Platform.LIGHT, Platform.NUMBER, Platform.SELECT, Platform.SENSOR, Platform.SWITCH]
SCAN_INTERVAL: Final = timedelta(seconds=60)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Setup the Somneo component."""
    try:
        host = config_entry.data[CONF_HOST]
        
        coordinator = SomneoCoordinator(hass, host)
        config_entry.async_on_unload(config_entry.add_update_listener(update_listener))
        
        await coordinator.async_config_entry_first_refresh()

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][config_entry.entry_id] = coordinator

        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

        #### NOTHING BELOW THIS LINE ####
        # If Success:
        _LOGGER.info("Somneo has been set up!")
        return True
    except requests.RequestException as ex:
        _LOGGER.error('Error while initializing Somneo, exception: {}'.format(str(ex)))
        raise PlatformNotReady
    except Exception as ex:
        _LOGGER.error('Error while initializing Somneo, exception: {}'.format(str(ex)))
        hass.components.persistent_notification.create(
            f'Error: {str(ex)}<br />Fix issue and restart',
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID)
        # If Fail:
        return False

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class SomneoCoordinator(DataUpdateCoordinator[None]):
    """Representation of a Somneo Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
    ) -> None:
        """Initialize Somneo client."""
        self.somneo = Somneo(host)
        self.light_is_on: bool = False
        self.brightness: float | None = None
        self.nightlight_is_on: bool = False
        self.alarms: list | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            ),
        )
    
    def update_somneo(self) -> None:
        """Update Somneo info."""
        self.somneo.update()

        self.light_is_on, self.brightness = self.somneo.light_status()
        self.nightlight_is_on = self.somneo.night_light_status()
        self.alarms = self.somneo.alarms()

    async def _async_update_data(self) -> None:
        """Fetch the latest data."""
        if self.state_lock.locked():
            return

        await self.hass.async_add_executor_job(self.update_somneo)

    async def async_turn_on_light(self, brightness) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_light, True, brightness)
            await self.async_request_refresh()

    async def async_turn_off_light(self) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_light, False)
            await self.async_request_refresh()

    async def async_turn_on_nightlight(self, brightness) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_night_light, True)
            await self.async_request_refresh()

    async def async_turn_off_nightlight(self) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_night_light, False)
            await self.async_request_refresh()

    async def async_toggle_alarm(self, alarm, state: bool) -> None:
        """Toggle alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_alarm, alarm, state)
            await self.async_request_refresh()
        
    async def async_set_alarm(self, alarm, hours: int | None = None, minutes: int | None = None):
        async with self.state_lock:
            if minutes != None:
                await self.hass.async_add_executor_job(self.somneo.set_alarm, alarm, minute=int(minutes))
            elif hours != None:
                await self.hass.async_add_executor_job(self.somneo.set_alarm, alarm, minute=int(hours))
            await self.async_request_refresh()

    async def async_get_alarm(self, alarm, type):
        async with self.state_lock:
            attr = await self.async_get_alarm_attributes(alarm)
            alarm_datetime = datetime.strptime(attr['time'],'%H:%M:%S')
            if type == HOURS:
                return alarm_datetime.hour
            elif type == MINUTES:
                return alarm_datetime.minute

    async def async_get_alarm_attributes(self, alarm):
        async with self.state_lock:
            attr = {}
            attr['time'], attr['days'] = await self.hass.async_add_executor_job(self.somneo.alarm_settings, alarm)
            return attr

    async def async_set_snooze_time(self, time):
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.set_snooze_time, int(time))
            await self.async_request_refresh()

    async def async_get_snooze_time(self):
        async with self.state_lock:
            return await self.hass.async_add_executor_job(self.somneo.snoozetime)

    async def async_get_alarm_day(self, alarm):
        async with self.state_lock:
            if await self.hass.async_add_executor_job(self.somneo.is_everyday, alarm):
                return EVERYDAY
            elif await self.hass.async_add_executor_job(self.somneo.is_workday, alarm):
                return WORKDAYS
            elif await self.hass.async_add_executor_job(self.somneo.is_weekend, alarm):
                return WEEKEND
            elif await self.hass.async_add_executor_job(self.somneo.is_tomorrow, alarm):
                return TOMORROW
            else:
                return UNKNOWN

    async def async_set_alarm_day(self, alarm, day):
        async with self.state_lock:
            if day == WORKDAYS:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_workdays, alarm)
                _LOGGER.debug('Optie is werkday')
            elif day == WEEKEND:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_weekend, alarm)
                _LOGGER.debug('Optie is weekend')
            elif day == TOMORROW:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_tomorrow, alarm)
                _LOGGER.debug('Optie is morgen')
            elif day == EVERYDAY:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_everyday, alarm)
                _LOGGER.debug('Optie is elke dag')

            await self.async_request_refresh()

    async def async_get_next_alarm(self):
        async with self.state_lock:
            next_alarm = await self.hass.async_add_executor_job(self.somneo.next_alarm)
            return await datetime.fromisoformat(next_alarm).astimezone() if next_alarm else None

    async def async_set_light_alarm(self, curve = 'sunny day', level = 20, duration = 30):
        """Adjust the light settings of an alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.somneo.set_light_alarm,
                self._alarm,
                curve = curve, 
                level = level, 
                duration = duration
                )

    async def async_set_sound_alarm(self, source = 'wake-up', level = 12, channel = 'forest birds'):
        """Adjust the sound settings of an alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.somneo.set_sound_alarm,
                self._alarm, 
                source = source, 
                level = level, 
                channel = channel
                )

    async def async_remove_alarm(self):
        """Function to remove alarm from list in wake-up app"""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.someo.remove_alarm,self._alarm)

    async def async_add_alarm(self):
        """Function to add alarm to list in wake-up app"""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.someo.add_alarm,self._alarm)

    async def async_get_sensor(self, sensor):
        async with self.state_lock:
            if sensor == "temperature":
                return await self.hass.async_add_executor_job(self.somneo.temperature)
            if sensor == "humidity":
                return await self.hass.async_add_executor_job(self.somneo.humidity)
            if sensor == "luminance":
                return await self.hass.async_add_executor_job(self.somneo.luminance)
            if sensor == "noise":
                return await self.hass.async_add_executor_job(self.somneo.noise)
