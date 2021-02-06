""" Philips SmartSleep """
import asyncio
import datetime
import logging
import urllib3
import requests
import json
import xml.etree.ElementTree as ET

from homeassistant.helpers import discovery
from homeassistant.util import Throttle
from homeassistant.config_entries import SOURCE_IMPORT

from pysomneo import Somneo

from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up the SmartSleep component from yaml."""
    if not hass.config_entries.async_entries(DOMAIN) and config.get(DOMAIN, {}):
        # No config entry exists and configuration.yaml config exists, trigger the import flow.
        host = config[DOMAIN][CONF_HOST]
        name = config[DOMAIN][CONF_NAME]
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data={CONF_HOST: host, CONF_NAME: name}
            )
        )

    return True


async def async_setup_entry(hass, config_entry):
    """Setup the SmartSleep component."""
    try:

        hass.data[DOMAIN] = SomneoData(hass, config_entry)
        await hass.data[DOMAIN].get_device_info()
        await hass.data[DOMAIN].update()

        for platform in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(config_entry, platform)
            )


        #### NOTHING BELOW THIS LINE ####
        # If Success:
        _LOGGER.info("SmartSleep has been set up!")
        return True
    except Exception as ex:
        _LOGGER.error('Error while initializing SmartSleep, exception: {}'.format(str(ex)))
        hass.components.persistent_notification.create(
            f'Error: {str(ex)}<br />Fix issue and restart',
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID)
        # If Fail:
        return False

async def async_unload_entry(hass, config_entry):
    """Uload the config entry and platforms."""
    hass.data.pop[DOMAIN]

    tasks = []
    for platform in PLATFORMS:
        tasks.append(hass.config_entries.async_forward_entry_unload(config_entry, platform))

    return all(await asyncio.gather(*tasks))


class SomneoData:
    """Handle for getting latest data from SmartSleep."""

    def __init__(self, hass, config_entry):
        """Initialize."""
        self._hass = hass
        self._config_entry = config_entry
        self.somneo = Somneo(config_entry.data[CONF_HOST])
        self.dev_info = None

    async def get_device_info(self):
        """Get device information."""
        self.dev_info = await self._hass.async_add_executor_job(self.somneo.get_device_info)

    @Throttle(UPDATE_TIME)
    async def update(self):
        """Get the latest update."""
        await self._hass.async_add_executor_job(self.somneo.update)
