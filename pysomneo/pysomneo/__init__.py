import requests
import urllib3
import json
import xml.etree.ElementTree as ET
import logging
import datetime
import asyncio

_LOGGER = logging.getLogger('pysomneo')


class Somneo(object):
    """ 
    Class represents the Somneo wake-up light.
    """

    def __init__(self, host=None):
        """Initialize."""
        urllib3.disable_warnings()
        self.host = host
        self._base_url = 'https://' + host + '/di/v1/products/1/'
        self._session = requests.Session()

        self.light_data = None
        self.sensor_data = None
        self.alarm_data = dict()
        self.alarm_toggle_data = dict()
        self.alarm_time_data = dict()
        self.set_time_task = None

    def get_device_info(self):
        """ Get Device information """
        try:
            response = self._session.request('GET', 'https://' + self.host + '/upnp/description.xml', verify=False,
                                             timeout=20)
        except requests.Timeout:
            _LOGGER.error('Connection to Somneo timed out.')
            raise
        except requests.RequestException:
            _LOGGER.error('Error connecting to Somneo.')
            raise

        root = ET.fromstring(response.content)

        device_info = dict()
        device_info['manufacturer'] = root[1][2].text
        device_info['model'] = root[1][3].text
        device_info['modelnumber'] = root[1][4].text
        device_info['serial'] = root[1][6].text

        return device_info

    def _internal_call(self, method, url, headers, payload):
        """Call to the API."""
        args = dict()
        url = self._base_url + url

        if payload:
            args['data'] = json.dumps(payload)

        if headers:
            args['headers'] = headers

        try:
            r = self._session.request(method, url, verify=False, timeout=20, **args)
        except requests.Timeout:
            _LOGGER.error('Connection to Somneo timed out.')
            raise
        except requests.RequestException:
            _LOGGER.error('Error connecting to Somneo.')
            raise
        else:
            if r.status_code == 422:
                _LOGGER.error('Invalid URL.')
                raise Exception("Invalid URL.")

        if method == 'GET':
            return r.json()
        else:
            return

    def _get(self, url, args=None, payload=None):
        return self._internal_call('GET', url, None, payload)

    def _put(self, url, args=None, payload=None):
        return self._internal_call('PUT', url, {"Content-Type": "application/json"}, payload)

    def toggle_light(self, state, brightness=None):
        """ Toggle the light on or off """
        payload = self.light_data
        payload['onoff'] = state
        payload['ngtlt'] = False
        if brightness:
            payload['ltlvl'] = int(brightness / 255 * 25)
        self._put('wulgt', payload=payload)

    def set_alarm(self, hour, minute, days, alarm):
        _LOGGER.debug("set_time_alarm position " + str(self.alarm_data[alarm]['position'])
                      + str(hour) + ":" + str(minute) + " days " + str(days))
        self.alarm_data[alarm]['time'] = datetime.time(int(hour), int(minute))
        self.alarm_data[alarm]['days'] = days
        payload = dict()
        payload['prfnr'] = self.alarm_data[alarm]['position']  # Alarm position
        payload['prfen'] = self.alarm_data[alarm]['enabled']  # Alarm enabled / disabled
        payload['prfvs'] = True  # Add/Remove alarm from alarm list
        payload['almhr'] = int(hour)  # Alarm hour
        payload['almmn'] = int(minute)  # Alarm Min
        payload['pwrsz'] = 0  # TODO enable / disable PowerWake
        payload['pszhr'] = 0  # TODO set power wake (hour)
        payload['pszmn'] = 0  # TODO set power wake (min)
        payload['ctype'] = 0  # TODO set the default sunrise ("Sunny day" if curve > 0 or "No light" if curve == 0)
        payload['curve'] = 20  # TODO set light level
        payload['durat'] = 30  # TODO set sunrise duration
        payload['daynm'] = days  # set days to repeat the alarm
        # payload['snddv'] = "wus" # TODO set the wake_up sound
        # payload['snztm'] = 0 # TODO set snooze time
        self._put('wualm/prfwu', payload=payload)

    def set_days_alarm(self, days, alarm):
        self.set_alarm(int(self.alarm_data[alarm]['time'].hour),
                       int(self.alarm_data[alarm]['time'].minute), days, alarm)

    def set_workdays_alarm(self, is_on, alarm):
        days = (self.alarm_data[alarm]['days'] & 192)
        if is_on:
            days = days + 62
        _LOGGER.debug("Workday " + str(is_on) + " days =" + str(days))
        self.set_days_alarm(days, alarm)

    def set_weekend_alarm(self, is_on, alarm):
        days = (self.alarm_data[alarm]['days'] & 62)
        if is_on:
            days = days + 192
        _LOGGER.debug("Weekend " + str(is_on) + " days =" + str(days))
        self.set_days_alarm(days, alarm)

    def set_time_alarm(self, hour, minute, alarm):
        self.set_alarm(hour, minute, self.alarm_data[alarm]['days'], alarm)

    def toggle_alarm(self, status, alarm):
        """ Toggle the light on or off """
        self.alarm_data[alarm]['enabled'] = status
        payload = self.alarm_toggle_data
        payload['prfnr'] = self.alarm_data[alarm]['position']
        payload['prfvs'] = True
        payload['prfen'] = status
        self._put('wualm/prfwu', payload=payload)

    def toggle_night_light(self, state):
        """ Toggle the light on or off """
        payload = self.light_data
        payload['onoff'] = False
        payload['ngtlt'] = state
        self._put('wulgt', payload=payload)

    def update(self):
        """Get the latest update from Somneo."""

        # Get light information
        self.light_data = self._get('wulgt')

        # Get sensor data
        self.sensor_data = self._get('wusrd')

        # Get alarm data
        enabled_alarms = self._get('wualm/aenvs')
        time_alarms = self._get('wualm/aalms')

        for alarm, enabled in enumerate(enabled_alarms['prfen']):
            alarm_name = 'alarm' + str(alarm)
            self.alarm_data[alarm_name] = dict()
            self.alarm_data[alarm_name]['position'] = alarm + 1
            self.alarm_data[alarm_name]['enabled'] = bool(enabled)
            self.alarm_data[alarm_name]['time'] = datetime.time(int(time_alarms['almhr'][alarm]),
                                                                int(time_alarms['almmn'][alarm]))
            self.alarm_data[alarm_name]['days'] = int(time_alarms['daynm'][alarm])

    def light_status(self):
        """Return the status of the light."""
        return self.light_data['onoff'], int(int(self.light_data['ltlvl']) / 25 * 255)

    def night_light_status(self):
        """Return the status of the night light."""
        return self.light_data['ngtlt']

    def alarms(self):
        """Return the list of alarms."""
        alarms = dict()
        for alarm in list(self.alarm_data):
            alarms[alarm] = self.alarm_data[alarm]['enabled']

        return alarms

    def day_int(self, mon, tue, wed, thu, fri, sat, sun):
        return mon * 2 + tue * 4 + wed * 8 + thu * 16 + fri * 32 + sat * 64 + sun * 128

    def is_workday(self, alarm):
        days_int = self.alarm_data[alarm]['days']
        return (days_int & 62) == 62

    def is_weekend(self, alarm):
        days_int = self.alarm_data[alarm]['days']
        return (days_int & 192) == 192

    def alarm_settings(self, alarm):
        """Return the time and days alarm is set."""
        alarm_time = self.alarm_data[alarm]['time'].isoformat()

        alarm_days = []
        days_int = self.alarm_data[alarm]['days']
        if days_int & 2:
            alarm_days.append('mon')
        if days_int & 4:
            alarm_days.append('tue')
        if days_int & 8:
            alarm_days.append('wed')
        if days_int & 16:
            alarm_days.append('thu')
        if days_int & 32:
            alarm_days.append('fri')
        if days_int & 64:
            alarm_days.append('sat')
        if days_int & 128:
            alarm_days.append('sun')

        return alarm_time, alarm_days

    def next_alarm(self):
        """Get the next alarm that is set."""
        next_alarm = None
        for alarm in list(self.alarm_data):
            if self.alarm_data[alarm]['enabled'] == True:
                nu_tijd = datetime.datetime.now()
                nu_dag = datetime.date.today()
                alarm_time = self.alarm_data[alarm]['time']
                alarm_days_int = self.alarm_data[alarm]['days']
                alarm_days = []
                if alarm_days_int & 2:
                    alarm_days.append(1)
                if alarm_days_int & 4:
                    alarm_days.append(2)
                if alarm_days_int & 8:
                    alarm_days.append(3)
                if alarm_days_int & 16:
                    alarm_days.append(4)
                if alarm_days_int & 32:
                    alarm_days.append(5)
                if alarm_days_int & 64:
                    alarm_days.append(6)
                if alarm_days_int & 128:
                    alarm_days.append(7)

                day_today = nu_tijd.isoweekday()

                if not alarm_days:
                    alarm_time_full = datetime.datetime.combine(nu_dag, alarm_time)
                    if alarm_time_full > nu_tijd:
                        new_next_alarm = alarm_time_full
                    elif alarm_time_full + datetime.timedelta(days=1) > nu_tijd:
                        new_next_alarm = alarm_time_full
                else:
                    for d in range(0, 7):
                        test_day = day_today + d
                        if test_day > 7:
                            test_day -= 7
                        if test_day in alarm_days:
                            alarm_time_full = datetime.datetime.combine(nu_dag, alarm_time) + datetime.timedelta(days=d)
                            if alarm_time_full > nu_tijd:
                                new_next_alarm = alarm_time_full
                                break

                if next_alarm:
                    if new_next_alarm < next_alarm:
                        next_alarm = new_next_alarm
                else:
                    next_alarm = new_next_alarm

        if next_alarm:
            return next_alarm.isoformat()
        else:
            return None

    def temperature(self):
        """Return the temperature."""
        return self.sensor_data['mstmp']

    def humidity(self):
        """Return the temperature."""
        return self.sensor_data['msrhu']

    def luminance(self):
        """Return the temperature."""
        return self.sensor_data['mslux']

    def noise(self):
        """Return the temperature."""
        return self.sensor_data['mssnd']
