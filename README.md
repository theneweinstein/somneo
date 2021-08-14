# SmartSleep custom component for Home Assistant
Home Assistant custom component for the Philips SmartSleep Connected Sleep and Wake-Up Light. This integration lets you control the SmartSleep light, nightlight,  and sunset mode, and surfaces the following sensors: temperature, humidity, luminance, and noise. It also surfaces the wake-up alarms as binary sensors and provides a sensor with the first upcoming alarm.

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

# Compatibility Notes
This custom component has only been tested (so far) with the HF36XX models.
