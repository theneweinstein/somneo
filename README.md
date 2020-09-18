# SmartSleep custom component for Home Assistant
Home Assistant custom component for Philips SmartSleep (Somneo). This integration lets you control the SmartSleep light and reads the following sensors: temperature, humidity, luminance and noise. It also provides the alarms set on your SmartSleep instance as binary sensors and provides a sensor with the first upcoming alarm.

# Installation
On your Home Assistant instance, go to /custom_components and clone this repository. Alternatively you can manually copy the files into the smartsleep folder.

# Configuration
After installation you an either use a config flow to set-up a SmartSleep device or add:
```
smartsleep:
  host: IP-ADDRESS (required)
  name: NAME (optional)
```
to your ```configuration.yaml```.
