"""Data models for the Somneo integration."""
from __future__ import annotations

from datetime import datetime, time
from typing import TypedDict


class SomneoAlarm(TypedDict):
    """Representation of an alarm on the Somneo device."""

    position: int
    name: str
    enabled: bool
    visible: bool
    time: time
    days: list[str]
    days_type: str
    powerwake: bool
    powerwake_delta: int


class SomneoPlayer(TypedDict):
    """Representation of the audio player state."""

    state: bool
    volume: float
    source: str
    possible_sources: list[str]


class SomneoSunset(TypedDict):
    """Representation of the sunset (wind-down) settings."""

    is_on: bool
    duration: int
    curve: str
    level: int
    sound: str
    volume: int


class SomneoData(TypedDict):
    """Data fetched from the Somneo device via the coordinator."""

    temperature: float | None
    humidity: float | None
    luminance: int | None
    noise: float | None
    light_is_on: bool
    light_brightness: int
    nightlight_is_on: bool
    alarms: dict[int, SomneoAlarm]
    sunset: SomneoSunset
    player: SomneoPlayer
    snooze_time: int
    next_alarm: datetime | None
    somneo_status: str
    display_always_on: bool
    display_brightness: int
