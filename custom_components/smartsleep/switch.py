"""Platform for switch integration. (on/off alarms & on/off alarms on workdays and/or weekends"""
import logging

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity
from homeassistant.helpers import config_validation as cv, entity_platform, service

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Add SmartSleep from config_entry."""
    name = config_entry.data[CONF_NAME]
    data = hass.data[DOMAIN]
    dev_info = data.dev_info

    device_info = {
        "identifiers": {(DOMAIN, dev_info['serial'])},
        "name": 'SmartSleep',
        "manufacturer": dev_info['manufacturer'],
        "model": f"{dev_info['model']} {dev_info['modelnumber']}",
    }

    alarms = []
    for alarm in list(data.somneo.alarms()):
        alarms.append(SomneoToggle(
            name, data, device_info, dev_info['serial'], alarm))

    async_add_entities(alarms, True)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        'set_light_alarm',
        {
            vol.Optional(ATTR_CURVE): cv.string,
            vol.Optional(ATTR_LEVEL): cv.positive_int,
            vol.Optional(ATTR_DURATION): cv.positive_int,
        },
        'set_light_alarm'
    )

    platform.async_register_entity_service(
        'set_sound_alarm',
        {
            vol.Optional(ATTR_SOURCE): cv.string,
            vol.Optional(ATTR_LEVEL): cv.positive_int,
            vol.Optional(ATTR_CHANNEL): cv.string,
        },
        'set_sound_alarm'
    )

    platform.async_register_entity_service(
        'remove_alarm',
        {},
        'remove_alarm'
    )

    platform.async_register_entity_service(
        'add_alarm',
        {},
        'add_alarm'
    )

class SomneoToggle(SwitchEntity):
    _attr_icon = ALARMS_ICON
    _attr_should_poll = True

    def __init__(self, name, data, device_info, serial, alarm):
        """Initialize the switches. """
        self._data = data
        self._attr_name = name + "_" + alarm
        self._alarm = alarm
        self._attr_device_info = device_info
        self._attr_unique_id = serial + '_' + alarm

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}
        attr['time'], attr['days'] = self._data.somneo.alarm_settings(
            self._alarm)
        return attr

    async def async_update(self):
        """Get the latest data and updates the states of the switches."""
        await self._data.update()
        self._attr_is_on = self._data.somneo.alarms()[self._alarm]

    def turn_on(self, **kwargs):
        """Called when user Turn On the switch from UI."""
        self._data.somneo.toggle_alarm(self._alarm, True)
        self._attr_is_on = True

    def turn_off(self, **kwargs):
        """Called when user Turn Off the switch from UI."""
        self._data.somneo.toggle_alarm(self._alarm, False)
        self._attr_is_on = False

    # Define service-calls
    def set_light_alarm(self, curve='sunny day', level=20, duration=30):
        """Adjust the light settings of an alarm."""
        self._data.somneo.set_light_alarm(
            self._alarm, curve=curve, level=level, duration=duration)

    def set_sound_alarm(self, source='wake-up', level=12, channel='forest birds'):
        """Adjust the sound settings of an alarm."""
        self._data.somneo.set_sound_alarm(
            self._alarm, source=source, level=level, channel=channel)

    def remove_alarm(self):
        """Function to remove alarm from list in wake-up app"""
        self._data.someo.remove_alarm(self._alarm)

    def add_alarm(self):
        """Function to add alarm to list in wake-up app"""
        self._data.someo.add_alarm(self._alarm)
