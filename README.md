# Somneo custom component
Home Assistant custom component for Philips Someo. This integration let's you control the light of the Somneo and reads the following sensors: temperature, humidity, luminance and noise. Furthermore, it provides the alarms set on your Somneo instance as binary sensors and provides a sensor with the first upcoming alarm. 

# Installation
You can install this custom component via HACS as a custom repository (https://hacs.xyz/docs/faq/custom_repositories/). Alternatively you can clone or copy the files into the somneo folder in the custom_components folder of HomeAssistant.

# Configuration
Go to: https://my.home-assistant.io/redirect/config_flow_start/?domain=somneo

# Alarm Configuration
### With slider-entity-row from HACS`
Add a "manual" card into lovelace UI and copy paste the following code. It will create a card for the first Somneo Alarm (alarm0). 
Other cards can be created for other alarms (alarm1, alarm2, etc.)
```
type: entities
entities:
  - entity: switch.somneo_alarm0
    name: On/Off
  - type: custom:slider-entity-row
    entity: number.somneo_alarm0_hours
    hide_state: false
    name: Hours
  - type: custom:slider-entity-row
    entity: number.somneo_alarm0_minutes
    hide_state: false
    name: Minutes
  - entity: select.somneo_alarm0_days
    name: Days
title: Alarm work
show_header_toggle: false
```
<img src="https://github.com/theneweinstein/somneo/blob/master/lovelace1.jpg" alt="Example Lovelace Slider" width="80%"/>

### Without slider-entity-row from HACS

```
type: entities
entities:
  - entity: switch.somneo_alarm0
    name: On/Off
  - entity: number.somneo_alarm0_hours
    name: Hours
  - entity: number.somneo_alarm0_minutes
    name: Minutes
  - entity: select.somneo_alarm0_days
    name: Days
title: Alarm work
show_header_toggle: false
```
<img src="https://github.com/theneweinstein/somneo/blob/master/lovelace2.jpg" alt="Example Lovelace" width="80%"/>

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
  level: 12
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
