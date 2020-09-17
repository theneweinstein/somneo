import voluptuous as vol
from datetime import timedelta

from homeassistant.helpers import config_validation as cv
from homeassistant.const import (TEMP_CELSIUS, PERCENTAGE)
DOMAIN = 'somneo'
VERSION = "0.3"

DEFAULT_NAME = "Somneo"

CONF_NAME = 'name'
CONF_HOST = 'host'
CONF_SENS = 'sensors'

ALARMS = 'alarms'

UPDATE_TIME = timedelta(seconds=60)

SENSORS = {'temperature': TEMP_CELSIUS, 'humidity': PERCENTAGE, 'luminance': 'lux', 'noise': 'db'}

PLATFORMS = ['light', 'binary_sensor', 'sensor']

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


NOTIFICATION_ID = "somneosensor_notification"
NOTIFICATION_TITLE = "SomneoSensor Setup"



