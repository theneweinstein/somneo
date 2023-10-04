# Somneo custom integration
Home Assistant custom integration to control a Philips Somneo device. This integration let's you control:
  - The light and nightlight of the Somneo
  - All the 16 available alarms (toggle, time, days, powerwake)
  - Media player of the Somneo (FM radio or aux. input)
  - Snooze or ignore alarm (buttons)

Furthermore, it provides the following sensors:
  - Ambient sensors (temperature, humidity, luminance and noise)
  - Alarm status (on, off, snooze, wake-up)
  - Next alarm

# Installation
You can install this custom component via HACS as a custom repository (https://hacs.xyz/docs/faq/custom_repositories/). Alternatively you can clone or copy the files into the somneo folder in the custom_components folder of HomeAssistant.

# Configuration
The Somneo should be automatically detected via SSDP. If not, you can also manually configure the Somneo:
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=somneo)

# Alarm UI configuration
Add a "manual" card into lovelace UI and copy paste the following code. It will create a card for the first Somneo Alarm (alarm0).
Other cards can be created for other alarms (alarm1, alarm2, etc.)
```
type: entities
entities:
  - entity: switch.somneo_alarm0
    name: On/Off
  - entity: time.somneo_alarm0_time
    name: Time
  - entity: select.somneo_alarm0_days
    name: Days
  - entity: switch.somneo_alarm0_powerwake
    name: PowerWake
  - entity: number.somneo_alarm0_powerwake_delay
    name: PowerWake delay
title: Alarm work
```
<img src="https://github.com/theneweinstein/somneo/blob/master/lovelace1.jpg" alt="Example Lovelace" width="80%"/>

# Custom alarm days

The select entity for the days only supports a limited set of days, namely weekdays, weekends, everyday and tomorrow. In case you want to select a different day for the alarm, you can use the text entity. The text contains a comma-seperated list (without white-spaces) of abbreviations of the day of the week (i.e. `mon,tue,wed,thu,fri,sat,sun`) or `tomorrow`.
```
type: entities
entities:
  - entity: switch.somneo_alarm0
    name: On/Off
  - entity: time.somneo_alarm0_time
    name: Time
  - entity: text.somneo_alarm0_days
    name: Days
  - entity: switch.somneo_alarm0_powerwake
    name: PowerWake
  - entity: number.somneo_alarm0_powerwake_delay
    name: PowerWake delay
title: Alarm work
```
<img src="https://github.com/theneweinstein/somneo/blob/master/lovelace2.jpg" alt="Example Lovelace with custom days" width="80%"/>


# Services
This component includes two services to adjust the wake-up light and sound settings. To adjust the light settings of an alarm you can call the following function:
```
service: somneo.set_light_alarm
target:
  entity_id: switch.somneo_alarm0
data:
  curve: sunny day
  level: 20
  duration: 30
```
The curve is either `sunny day`, `island red` or `nordic white`. Level should be between 0 and 25 and duration betweeen 4 and 40 minutes.

To adjust the sound settings of an alarm you can call the following function:
```
service: somneo.set_sound_alarm
target:
  entity_id: switch.somneo_alarm0
data:
  source: wake-up
  channel: forest birds
  level: 10

```
The source is `wake-up` for the wake-up sounds, `radio` for the FM radio of `off` for no sound. If the wake-up sound is selected, channel is one of the following sounds: `forest birds`, `summer birds`, `morning alps`, `yoga harmony`, `nepal bowls`, `summer lake` or `ocean waves`. If the radio is selected, channel has a value 1 till 5 (formatted as a string). The level should be between 1 and 25.

Furthermore, alarms can be added to or removed from the list in the Somneo app with:
```
service: somneo.add_alarm
target:
  entity_id: switch.somneo_alarm0
```
```
service: somneo.remove_alarm
target:
  entity_id: switch.somneo_alarm0
```
