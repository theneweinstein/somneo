import voluptuous as vol
from datetime import timedelta

from homeassistant.helpers import config_validation as cv
from homeassistant.const import (TEMP_CELSIUS, UNIT_PERCENTAGE)
DOMAIN = 'somneo'
VERSION = "0.3"

DEFAULT_NAME = "somneo"
DEFAULT_HOST = "192.168.2.131"

CONF_NAME = 'name'
CONF_HOST = 'host'
CONF_SENS = 'sensors'

ALARMS = 'alarms'

UPDATE_TIME = timedelta(seconds=60)

SENSOR_TYPES = {
    "temperature": ["temperature", TEMP_CELSIUS],
    "humidity": ["humidity", UNIT_PERCENTAGE],
    "luminance": ["luminance", "lux"],
    "noise": ["noise", "db"]
}

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_SENS, default=list(SENSOR_TYPES)): [vol.In(SENSOR_TYPES)],
    })
}, extra=vol.ALLOW_EXTRA)


NOTIFICATION_ID = "somneosensor_notification"
NOTIFICATION_TITLE = "SomneoSensor Setup"



