# Somneo custom component
Home Assistant custom component for Philips Someo. This integration let's you control the light of the Somneo and reads the following sensors: temperature, humidity, luminance and noise. Furthermore, it provides the alarms set on your Somneo instance as binary sensors and provides a sensor with the first upcoming alarm. 

# Installation
You can install this custom component via HACS as a custom repository (https://hacs.xyz/docs/faq/custom_repositories/). Alternatively you can clone or copy the files into the somneo folder in the custom_components folder of HomeAssistant.

# Configuration
After installation you an either use a config flow to set-up a Somneo device or add:
```
somneo:
  host: IP-ADDRESS (required)
  name: NAME (optional)
```
to your ```configuration.yaml```.

# Alarm Configuration
### With slider-entity-row from HACS`
Add a "manual" card into lovelace UI and copy paste the following code. It will create a card for the first Somneo Alarm (alarm0). 
Other cards can be created for other alarms (alarm1, alarm2, etc.)
```
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: switch.somneo_alarm0
        name: On/Off
      - type: custom:slider-entity-row
        entity: number.somneo_alarm0_hours
        hide_state: false
      - type: custom:slider-entity-row
        entity: number.somneo_alarm0_minutes
        hide_state: false
    title: Alarm Yoga
    show_header_toggle: false
  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: toggle
        hold_action:
          action: none
        show_icon: true
        show_name: true
        icon_height: 40px
        name: workdays
        show_state: true
        entity: switch.somneo_workdays_alarm0
      - type: button
        tap_action:
          action: toggle
        hold_action:
          action: none
        show_icon: true
        show_name: true
        icon_height: 40px
        entity: switch.somneo_weekend_alarm0
        name: Week-ends
        show_state: true
```
<img src="https://github.com/theneweinstein/somneo/blob/master/lovelace1.jpg" alt="Example Lovelace Slider" width="80%"/>

### Without slider-entity-row from HACS

```
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: switch.somneo_alarm0
        name: On/Off
      - entity: number.somneo_alarm0_hours
        hide_state: false
      - entity: number.somneo_alarm0_minutes
        hide_state: false
    title: Alarm Yoga
    show_header_toggle: false
  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: toggle
        hold_action:
          action: none
        show_icon: true
        show_name: true
        icon_height: 40px
        name: workdays
        show_state: true
        entity: switch.somneo_workdays_alarm0
      - type: button
        tap_action:
          action: toggle
        hold_action:
          action: none
        show_icon: true
        show_name: true
        icon_height: 40px
        entity: switch.somneo_weekend_alarm0
        name: Week-ends
        show_state: true
```
<img src="https://github.com/theneweinstein/somneo/blob/master/lovelace2.jpg" alt="Example Lovelace" width="80%"/>
