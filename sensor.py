"""Platform for sensor integration."""
import logging
import datetime

from custom_components import somneo
from homeassistant.helpers.entity import Entity
from homeassistant.const import DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_ILLUMINANCE, DEVICE_CLASS_TEMPERATURE


from .const import *

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Somneo sensor platform."""
    name = discovery_info['name']

    dev = []
    for sensor in discovery_info[CONF_SENS]:
        dev.append(SomneoSensor(name, hass.data[DOMAIN], sensor))
    dev.append(SomneoNextAlarmSensor(name, hass.data[DOMAIN]))
    add_entities(dev, True)

    

class SomneoSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, name, data, sensor_types):
        """Initialize the sensor."""
        self._data = data
        self._name = (name + "_" + SENSOR_TYPES[sensor_types][0])
        self._unit_of_measurement = SENSOR_TYPES[sensor_types][1]
        self._type = sensor_types
        self._state = None
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    
    @property
    def state(self):
        """Return the state of the sensor."""
    
        return self._state
    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self._data.serial + '_' + self._type

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        if self._type == "temperature":
            return DEVICE_CLASS_TEMPERATURE
        if self._type == "humidity":
            return DEVICE_CLASS_HUMIDITY
        if self._type == "luminance":
            return DEVICE_CLASS_ILLUMINANCE
        else:
            return None

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": self._data.manufacturer,
            "model": f"{self._data.model} {self._data.modelnumber}",
            "via_device": (DOMAIN, self._data.serial),
        }
    
    def update(self):
        """Get the latest data and updates the states."""
        if self._type == "temperature":
            self._state = self._data.sensor_data['mstmp']
        if self._type == "humidity":
            self._state = self._data.sensor_data['msrhu']
        if self._type == "luminance":
            self._state = self._data.sensor_data['mslux']
        if self._type == "noise":
            self._state = self._data.sensor_data['mssnd']


class SomneoNextAlarmSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, name, data):
        """Initialize the sensor."""
        self._data = data
        self._name = (name + "_next_alarm")
        self._state = None
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self._data.serial + '_next_alarm'

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": self._data.manufacturer,
            "model": f"{self._data.model} {self._data.modelnumber}",
            "via_device": (DOMAIN, self._data.serial),
        }
    
    def update(self):
        """Get the latest data and updates the states."""
        next_alarm = None
        for alarm in list(self._data.alarm_data):
            if self._data.alarm_data[alarm]['enabled'] == True:
                nu_tijd = datetime.datetime.now()
                nu_dag = datetime.date.today()
                alarm_time = self._data.alarm_data[alarm]['time']
                alarm_days_int = self._data.alarm_data[alarm]['days']
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
                    for d in range(0,7):
                        if day_today + d in alarm_days:
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
            self._state = next_alarm.isoformat()
        else:
            self._state = None