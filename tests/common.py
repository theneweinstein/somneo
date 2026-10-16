"""Shared test data for the Somneo integration tests."""
from __future__ import annotations

from datetime import time

HOST = "192.168.1.123"
SERIAL = "somneo-serial-0001"
NAME = "Somneo"

FAKE_DEVICE_INFO: dict[str, str] = {
    "manufacturer": "Royal Philips Electronics",
    "model": "Wake-up Light",
    "modelnumber": "HF3650/01",
    "serial": SERIAL,
}

FAKE_DATA_HIDDEN: dict = {
    "temperature": 22.5,
    "humidity": 45.0,
    "luminance": 100,
    "noise": 30.0,
    "light_is_on": True,
    "light_brightness": 128,
    "nightlight_is_on": False,
    "alarms": {
        0: {
            "position": 1,
            "name": "alarm0",
            "enabled": True,
            "visible": True,
            "time": time(7, 30),
            "days": ["mon", "tue", "wed", "thu", "fri"],
            "days_type": "workdays",
            "powerwake": True,
            "powerwake_delta": 10,
        },
        1: {
            "position": 2,
            "name": "alarm1",
            "enabled": False,
            "visible": False,
            "time": time(6, 0),
            "days": ["sat", "sun"],
            "days_type": "weekend",
            "powerwake": False,
            "powerwake_delta": 0,
        },
    },
    "sunset": {
        "is_on": False,
        "duration": 30,
        "curve": "sunny day",
        "level": 20,
        "sound": "soft rain",
        "volume": 10,
    },
    "player": {
        "state": False,
        "volume": 0.5,
        "source": "AUX",
        "possible_sources": ["AUX", "FM 1", "FM 2", "FM 3", "FM 4", "FM 5"],
    },
    "snooze_time": 5,
    "next_alarm": None,
    "somneo_status": "off",
    "display_always_on": False,
    "display_brightness": 3,
}

FAKE_DATA: dict = {
    "temperature": 22.5,
    "humidity": 45.0,
    "luminance": 100,
    "noise": 30.0,
    "light_is_on": True,
    "light_brightness": 128,
    "nightlight_is_on": False,
    "alarms": {
        0: {
            "position": 1,
            "name": "alarm0",
            "enabled": True,
            "visible": True,
            "time": time(7, 30),
            "days": ["mon", "tue", "wed", "thu", "fri"],
            "days_type": "workdays",
            "powerwake": True,
            "powerwake_delta": 10,
        },
        1: {
            "position": 2,
            "name": "alarm1",
            "enabled": False,
            "visible": True,
            "time": time(6, 0),
            "days": ["sat", "sun"],
            "days_type": "weekend",
            "powerwake": False,
            "powerwake_delta": 0,
        },
    },
    "sunset": {
        "is_on": False,
        "duration": 30,
        "curve": "sunny day",
        "level": 20,
        "sound": "soft rain",
        "volume": 10,
    },
    "player": {
        "state": False,
        "volume": 0.5,
        "source": "AUX",
        "possible_sources": ["AUX", "FM 1", "FM 2", "FM 3", "FM 4", "FM 5"],
    },
    "snooze_time": 5,
    "next_alarm": None,
    "somneo_status": "off",
    "display_always_on": False,
    "display_brightness": 3,
}
