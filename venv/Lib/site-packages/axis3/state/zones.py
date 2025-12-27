# src/axis3/state/zones.py

from __future__ import annotations
from enum import Enum, auto


class ZoneType(Enum):
    LIBRARY = auto()
    HAND = auto()
    BATTLEFIELD = auto()
    GRAVEYARD = auto()
    EXILE = auto()
    STACK = auto()
    COMMAND = auto()


# Zones visible to both players
PUBLIC_ZONES = {
    ZoneType.BATTLEFIELD,
    ZoneType.GRAVEYARD,
    ZoneType.EXILE,
    ZoneType.STACK,
    ZoneType.COMMAND,
}

# Zones where order matters (top/bottom)
ORDERED_ZONES = {
    ZoneType.LIBRARY,
    ZoneType.STACK,
}


def is_public_zone(zone: ZoneType) -> bool:
    return zone in PUBLIC_ZONES


def is_ordered_zone(zone: ZoneType) -> bool:
    return zone in ORDERED_ZONES
