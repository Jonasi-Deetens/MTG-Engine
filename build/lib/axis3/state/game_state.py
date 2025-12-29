# src/axis3/state/game_state.py

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from axis3.state.objects import RuntimeObject, RuntimeObjectId
from axis3.rules.events.bus import EventBus
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.engine.stack.stack import Stack
from axis3.rules.layers.layersystem import LayerSystem
from axis3.state.zones import ZoneType
from axis3.engine.turn.phases import Phase
from axis3.engine.turn.steps import Step

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

    mana_pool: Dict[str, int] = field(default_factory=lambda: {
        "W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0
    })
    max_hand_size: int = 7

@dataclass
class TurnState:
    active_player: int = 0
    phase: Phase = Phase.BEGINNING
    step: Step = Step.UNTAP
    turn_number: int = 1

    stack_empty_since_last_priority: bool = True

    lands_played_this_turn: dict[int, int] = field(
        default_factory=lambda: {0: 0, 1: 0}
    )

    def is_main_phase(self) -> bool: 
        return self.phase in (Phase.PRECOMBAT_MAIN, Phase.POSTCOMBAT_MAIN) 
    def is_precombat_main(self) -> bool: 
        return self.phase == Phase.PRECOMBAT_MAIN 
    def is_postcombat_main(self) -> bool: 
        return self.phase == Phase.POSTCOMBAT_MAIN 
    def is_combat_phase(self) -> bool: 
        return self.phase == Phase.COMBAT 
    def is_end_step(self) -> bool: 
        return self.phase == Phase.ENDING and self.step == Step.END


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

    def move_card(self, card_id: str, to_zone: str, controller: int | None = None):
        """
        Move a card between zones in a minimal but correct way.
        This is the central zone-movement API for the engine.
        """

        # 1. Find the runtime object
        obj = self.objects.get(card_id)
        if obj is None:
            raise ValueError(f"Runtime object {card_id} not found")

        # 2. Remove from old zone
        old_zone = obj.zone
        old_controller = obj.controller
        self.add_debug_log(f"move_card: {card_id} from {old_zone} to {to_zone} (controller={controller})")
        self.event_bus.publish(Event( 
            type=EventType.ZONE_CHANGE, 
            payload={ 
                "obj_id": card_id, 
                "from_zone": old_zone, 
                "to_zone": ZoneType[to_zone] if isinstance(to_zone, str) else to_zone, 
                "controller": controller if controller is not None else old_controller, 
                "cause": "engine_move_card", 
            } 
        ))
        
    def max_lands_per_turn(self, player_id: int) -> int:
        base = 1 
        bonus = self.layers.get_land_play_bonus(player_id) 
        return base + bonus

    def add_debug_log(self, msg: str):
        self.debug_log.append(msg)

    def __post_init__(self):
        self.event_bus = EventBus(game_state=self)
        self.layers = LayerSystem(game_state=self)

    def get_object(self, obj_id: str) -> RuntimeObject | None:
        """
        Unified lookup for any runtime object by ID.
        This checks the global objects dictionary, which is the authoritative
        registry for all permanents, tokens, spells, and zone objects.
        """
        return self.objects.get(obj_id)
