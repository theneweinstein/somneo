# Somneo custom component
Home Assistant custom component for Philips Someo. This integration let's you control the light of the Somneo and reads the following sensors: temperature, humidity, luminance and noise. Furthermore, it provides the alarms set on your Somneo instance as binary sensors and provides a sensor with the first upcoming alarm. 

# Installation
On your Home Assistant instance, go to /custom_components. Now clone this respository: ```git clone https://github.com/theneweinstein/somneo.git somneo```. Alternatively you can manually copy the files into the somneo folder.

# Configuration
After installation you an either use a config flow to set-up a Somneo device or add:
```
somneo:
  host: IP-ADDRESS (required)
  name: NAME (optional)
```
to your ```configuration.yaml```.
