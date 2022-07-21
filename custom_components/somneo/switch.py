"""Platform for switch integration. (on/off alarms & on/off alarms on workdays and/or weekends"""
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import ATTR_CHANNEL, DOMAIN, ATTR_LEVEL, ATTR_CURVE, ATTR_DURATION, ATTR_SOURCE, ALARMS_ICON
from .entity import SomneoEntity


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data['dev_info']  

    alarms = []
    for alarm in list(coordinator.alarms):
        alarms.append(SomneoToggle(coordinator, unique_id, name, device_info, alarm))

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

class SomneoToggle(SomneoEntity, SwitchEntity):
    _attr_icon = ALARMS_ICON
    _attr_should_poll = True

    def __init__(self, coordinator, unique_id, name, device_info, alarm):
        """Initialize the switches. """
        super().__init__(coordinator, unique_id, name, device_info)

        self._attr_name = alarm.capitalize()
        self._alarm = alarm

    @property
    def is_on(self):
        """Return the state of the device."""
        self.coordinator.alarms[self._alarm]

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self.coordinator.async_get_alarm_attributes(self._alarm)

    def turn_on(self, **kwargs):
        """Called when user Turn On the switch from UI."""
        self.coordinator.async_toggle_alarm(self._alarm, True)

    def turn_off(self, **kwargs):
        """Called when user Turn Off the switch from UI."""
        self.coordinator.async_toggle_alarm(self._alarm, False)

    # Define service-calls
    def set_light_alarm(self, curve = 'sunny day', level = 20, duration = 30):
        """Adjust the light settings of an alarm."""
        self.coordinator.async_set_light_alarm(self._alarm, curve = curve, level = level, duration = duration)

    def set_sound_alarm(self, source = 'wake-up', level = 12, channel = 'forest birds'):
        """Adjust the sound settings of an alarm."""
        self.coordinator.async_set_sound_alarm(self._alarm, source = source, level = level, channel = channel)

    def remove_alarm(self):
        """Function to remove alarm from list in wake-up app"""
        self.coordinator.async_remove_alarm(self._alarm)

    def add_alarm(self):
        """Function to add alarm to list in wake-up app"""
        self.coordinator.async_add_alarm(self._alarm)