# SmartSleep custom component for Home Assistant

Home Assistant custom component for the Philips SmartSleep Connected Sleep and Wake-Up Light. This integration lets you control the SmartSleep light, nightlight, and sunset mode, and surfaces the following sensors: temperature, humidity, luminance, and noise. It also surfaces the wake-up alarms as binary sensors and provides a sensor with the first upcoming alarm.

## Original Component

This is a custom fork of the original Somneo component from @theneweinstein, which utilizes a custom fork of the pysomneo library (also from @theneweinstein). This features rebranding of Somneo to SmartSleep and some additional (minor) features.

## Installation

You can install this custom component via HACS as a custom repository (https://hacs.xyz/docs/faq/custom_repositories/). Alternatively you can clone or copy the files into the smartsleep folder in the custom_components folder of HomeAssistant.

### Compatibility Notes

This custom component has only been tested (so far) with the HF36XX models.

## Configuration

After installation you can either use a config flow to set-up a SmartSleep device or add:

```yaml
smartsleep:
  host: IP-ADDRESS (required)
  name: NAME (optional)
```

to your `configuration.yaml`.

### Alarm Configuration

#### With slider-entity-row from HACS

Add a "manual" card into lovelace UI and copy paste the following code. It will create a card for the first SmartSleep Alarm (alarm0).

Other cards can be created for other alarms (alarm1, alarm2, etc.)

```yaml
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

#### Without slider-entity-row from HACS

```yaml
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

## Services

This component includes two services to adjust the wake-up light and sound settings. To adjust the light settings of an alarm you can call the following function:

```yaml
service: somneo.set_light_alarm
target:
  entity_id: switch.somneo_alarm0
data:
  curve: sunny day
  level: 20
  duration: 30
```

The curve is either `sunny day`, `island red` or `nordic white`. Level should be between 0 and 25 and duration between 4 and 40 minutes.

To adjust the sound settings of an alarm you can call the following function:

```yaml
service: somneo.set_sound_alarm
target:
  entity_id: switch.somneo_alarm0
data:
  source: wake-up
  channel: forest birds
  level: 10

```

The source is `wake-up` for the wake-up sounds, `radio` for the FM radio of `off` for no sound. If the wake-up sound is selected, channel is one of the following sounds: `forest birds`, `summer birds`, `morning alps`, `yoga harmony`, `nepal bowls`, `summer lake` or `ocean waves`. If the radio is selected, channel has a value 1 till 5 (formatted as a string). The level should be between 1 and 25.

Alarms can be added to or removed from the list in the SmartSleep app with:

```yaml
service: somneo.add_alarm
target:
  entity_id: switch.somneo_alarm0
```

```yaml
service: somneo.remove_alarm
target:
  entity_id: switch.somneo_alarm0
```
