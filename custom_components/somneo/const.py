import voluptuous as vol
from datetime import timedelta

from homeassistant.helpers import config_validation as cv
from homeassistant.const import (TEMP_CELSIUS, PERCENTAGE)
DOMAIN = 'smartsleep'
VERSION = "0.4"

DEFAULT_NAME = "SmartSleep"

CONF_NAME = 'name'
CONF_HOST = 'host'
CONF_SENS = 'sensors'

ALARMS = 'alarms'
HOURS = 'hours'
MINUTES = 'minutes'
WORKDAYS = 'workdays'
WEEKEND = 'weekend'
TOMORROW = 'tomorrow'
EVERYDAY = 'everyday'
UNKNOWN = 'unknown'

ALARMS_ICON = 'hass:alarm'
HOURS_ICON = 'hass:counter'
MINUTES_ICON = 'hass:counter'
WORKDAYS_ICON = 'hass:calendar-range'
WEEKEND_ICON = 'hass:calendar-range'

ATTR_ALARM = 'alarm'
ATTR_CURVE = 'curve'
ATTR_LEVEL = 'level'
ATTR_DURATION = 'duration'
ATTR_SOURCE = 'source'
ATTR_CHANNEL = 'channel'

UPDATE_TIME = timedelta(seconds=60)

SENSORS = {'temperature': TEMP_CELSIUS, 'humidity': PERCENTAGE, 'luminance': 'lux', 'noise': 'db'}

PLATFORMS = ['light', 'sensor', 'switch', 'number', 'select']

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


NOTIFICATION_ID = "somneosensor_notification"
NOTIFICATION_TITLE = "SomneoSensor Setup"
