# src/axis3/state/game_state.py

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from axis3.state.objects import RuntimeObject, RuntimeObjectId
from axis3.rules.events.bus import EventBus
from axis3.engine.stack.stack import Stack
from axis3.rules.layers.layersystem import LayerSystem
from axis3.state.zones import ZoneType


class Phase(Enum):
    BEGINNING = auto()
    PRECOMBAT_MAIN = auto()
    COMBAT = auto()
    POSTCOMBAT_MAIN = auto()
    ENDING = auto()


class Step(Enum):
    UNTAP = auto()
    UPKEEP = auto()
    DRAW = auto()
    BEGIN_COMBAT = auto()
    DECLARE_ATTACKERS = auto()
    DECLARE_BLOCKERS = auto()
    COMBAT_DAMAGE = auto()
    END_COMBAT = auto()
    END_STEP = auto()
    CLEANUP = auto()


@dataclass
class PlayerState:
    id: int
    life: int = 20
    dead: bool = False

    library: List[RuntimeObjectId] = field(default_factory=list)
    hand: List[RuntimeObjectId] = field(default_factory=list)
    battlefield: List[RuntimeObjectId] = field(default_factory=list)
    graveyard: List[RuntimeObjectId] = field(default_factory=list)
    exile: List[RuntimeObjectId] = field(default_factory=list)
    command: List[RuntimeObjectId] = field(default_factory=list)

    mana_pool: Dict[str, int] = field(default_factory=dict)
    max_hand_size: int = 7


@dataclass
class TurnState:
    active_player: int = 0
    priority_player: int = 0
    phase: Phase = Phase.BEGINNING
    step: Step = Step.UNTAP
    turn_number: int = 1

    stack_empty_since_last_priority: bool = True


@dataclass
class GameState:
    players: List[PlayerState]
    objects: Dict[RuntimeObjectId, RuntimeObject]

    turn: TurnState = field(default_factory=TurnState)
    stack: Stack = field(default_factory=Stack)
    event_bus: EventBus = None
    debug_log: List[str] = field(default_factory=list)

    replacement_effects: List[object] = field(default_factory=list)
    continuous_effects: list = field(default_factory=list)
    global_restrictions: list = field(default_factory=list)
    layers: LayerSystem = field(init=False)

    def zone_list(self, controller_id: str, zone: ZoneType):
        player = self.players[int(controller_id)]
        if zone == ZoneType.LIBRARY:
            return player.library
        elif zone == ZoneType.HAND:
            return player.hand
        elif zone == ZoneType.BATTLEFIELD:
            return player.battlefield
        elif zone == ZoneType.GRAVEYARD:
            return player.graveyard
        elif zone == ZoneType.EXILE:
            return player.exile
        elif zone == ZoneType.COMMAND:
            return player.command
        return []

    def add_debug_log(self, msg: str):
        self.debug_log.append(msg)

    def __post_init__(self):
        self.event_bus = EventBus(game_state=self)
        self.layers = LayerSystem(game_state=self)
