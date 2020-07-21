""" Philips Somneo """
import asyncio
import datetime
import logging
import urllib3
import requests
import json
import xml.etree.ElementTree as ET

from homeassistant.helpers import discovery
from homeassistant.util import Throttle

from .const import *

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Setup the Somneo component."""
    try:
        conf = config[DOMAIN]
        host = conf.get(CONF_HOST, DEFAULT_HOST)
        
        #sensors = conf.get(CONF_SENS)        
        hass.data[DOMAIN] = SomneoData(host)
        hass.data[DOMAIN].update(no_throttle=True)

        discovery.load_platform(hass, 'light', DOMAIN, {CONF_NAME: config[DOMAIN].get(CONF_NAME, None)}, config)

        discovery.load_platform(hass, 'sensor', DOMAIN, {CONF_NAME: config[DOMAIN].get(CONF_NAME, None), CONF_SENS: config[DOMAIN][CONF_SENS]}, config)

        discovery.load_platform(hass, 'binary_sensor', DOMAIN, {CONF_NAME: config[DOMAIN].get(CONF_NAME, None)}, config)

        
        #### NOTHING BELOW THIS LINE ####
        # If Success:
        _LOGGER.info("Somneo has been set up!")
        return True
    except Exception as ex:
        _LOGGER.error('Error while initializing Somneo, exception: {}'.format(str(ex)))
        hass.components.persistent_notification.create(
            f'Error: {str(ex)}<br />Fix issue and restart',
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID)
        # If Fail:
        return False

class SomneoData:
    """Get the latest data from Somneo."""

    def __init__(self, host):
        """Initialize."""
        self._get_device_info(host)
        self._base_url = 'https://' + host + '/di/v1/products/1/'
        self._session = requests.Session()
        self.light_data = None
        self.sensor_data = None
        self.alarm_data = dict()
        self.update()

    @Throttle(UPDATE_TIME)
    def update(self):
        """Get the latest update from Somneo."""

        # Get light information
        self.light_data = self._get('wulgt')

        # Get sensor data
        self.sensor_data = self._get('wusrd')
        
        # Get alarm data
        #self.alarm_data['snooze'] = self._get('wualm')['snztm']
        enabled_alarms = self._get('wualm/aenvs')
        time_alarms = self._get('wualm/aalms')
        for alarm, enabled in enumerate(enabled_alarms['prfen']):
            alarm_name = 'alarm' + str(alarm)
            self.alarm_data[alarm_name] = dict()
            self.alarm_data[alarm_name]['enabled'] = bool(enabled)
            self.alarm_data[alarm_name]['time'] = datetime.time(int(time_alarms['almhr'][alarm]), int(time_alarms['almmn'][alarm]))
            self.alarm_data[alarm_name]['days'] = int(time_alarms['daynm'][alarm])

    def _get_device_info(self, host):
        """ Get Device information """
        session = requests.Session()
        response = session.request('GET','https://' + host + '/upnp/description.xml',verify=False)
        root = ET.fromstring(response.content)

        self.manufacturer = root[1][2].text
        self.model = root[1][3].text
        self.modelnumber = root[1][4].text
        self.serial = root[1][6].text


    def toggle_light(self, state, brightness = None):
        """ Toggle the light on or off """
        payload = self.light_data
        payload['onoff'] = state
        payload['ngtlt'] = False
        if brightness:
            payload['ltlvl'] = int(brightness/255 * 25)
        self._put('wulgt', payload = payload)

    def toggle_night_light(self, state):
        """ Toggle the light on or off """
        payload = self.light_data
        payload['onoff'] = False
        payload['ngtlt'] = state
        self._put('wulgt', payload = payload)

    def _internal_call(self, method, url, headers, payload):
        urllib3.disable_warnings()
        args = dict()
        url = self._base_url + url
        if payload:
            args['data'] = json.dumps(payload)

        if headers:
            args['headers'] = headers

        r = self._session.request(method, url, verify=False, **args)

        if r.status_code == 204:
            raise Exception("Empty update.")
        elif r.status_code == 400:
            raise Exception("Invalid update:" + r.json()['error'])
        elif r.status_code == 403:
            raise Exception("Unauthorized access.")
        elif r.status_code == 404:
            raise Exception("Thermostat not found.")
        elif r.status_code == 500:
            raise Exception("Something went wrong with processing the request.")

        if method == 'GET':
            return r.json()
        else:
            return

    def _get(self, url, args=None, payload=None):
        return self._internal_call('GET', url, None, payload)

    def _put(self, url, args=None, payload=None):
        return self._internal_call('PUT', url, {"Content-Type": "application/json"}, payload)

