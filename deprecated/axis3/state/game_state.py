# axis3/state/game_state.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from axis3.state.objects import RuntimeObject, RuntimeObjectId
from axis3.state.registries import EffectRegistries
from axis3.state.commander import CommanderEngine

from axis3.engine.casting.permission_engine import PermissionEngine
from axis3.engine.casting.cost_engine import CostEngine
from axis3.engine.casting.replacement_engine import ReplacementEngine
from axis3.engine.casting.cast_spell import CastSpellEngine
from axis3.engine.movement.zone_movement import ZoneMovementEngine

from axis3.engine.stack.stack import Stack
from axis3.rules.events.bus import EventBus
from axis3.rules.layers.layersystem import LayerSystem
from axis3.state.zones import ZoneType


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
class GameState:
    """
    The modern Axis3 GameState.

    This class is intentionally thin. It delegates:
      - Casting to CastSpellEngine
      - Zone movement to ZoneMovementEngine
      - Commander logic to CommanderEngine
      - Effect storage to EffectRegistries
      - Layer application to LayerSystem
      - Event dispatch to EventBus

    GameState no longer contains mechanic-specific logic.
    """

    players: List[PlayerState]
    objects: Dict[RuntimeObjectId, RuntimeObject]

    # Core systems
    stack: Stack = field(default_factory=Stack)
    event_bus: EventBus = field(init=False)
    layers: LayerSystem = field(init=False)

    # Effect registries (permissions, alt costs, reductions, replacements…)
    registries: EffectRegistries = field(default_factory=EffectRegistries)

    # Sub-engines
    commander: CommanderEngine = field(init=False)
    movement: ZoneMovementEngine = field(init=False)
    casting: CastSpellEngine = field(init=False)

    debug_log: List[str] = field(default_factory=list)

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __post_init__(self):
        # Event bus
        self.event_bus = EventBus(game_state=self)

        # Layer system
        self.layers = LayerSystem(game_state=self)

        # Commander engine
        self.commander = CommanderEngine(self)

        # Replacement engine
        replacement_engine = ReplacementEngine(
            replacements=self.registries.replacement_effects
        )

        # Movement engine
        self.movement = ZoneMovementEngine(
            replacements=replacement_engine
        )

        # Casting engine
        self.casting = CastSpellEngine(
            permissions=PermissionEngine(self.registries.permissions),
            costs=CostEngine(
                alt_costs=self.registries.alternative_costs,
                reductions=self.registries.cost_reductions,
            ),
            replacements=replacement_engine,
        )

    # ============================================================
    # ZONE ACCESS
    # ============================================================

    def zone_list(self, controller_id: int, zone: str) -> List[str]:
        """
        Return the list corresponding to a player's zone.
        """

        player = self.players[controller_id]
        zone = zone.upper()

        if zone == "LIBRARY":
            return player.library
        if zone == "HAND":
            return player.hand
        if zone == "BATTLEFIELD":
            return player.battlefield
        if zone == "GRAVEYARD":
            return player.graveyard
        if zone == "EXILE":
            return player.exile
        if zone == "COMMAND":
            return player.command

        raise ValueError(f"Unknown zone: {zone}")

    # ============================================================
    # OBJECT ACCESS
    # ============================================================

    def get_object(self, obj_id: str) -> Optional[RuntimeObject]:
        return self.objects.get(obj_id)

    # ============================================================
    # ZONE MOVEMENT (delegated)
    # ============================================================

    def move_card(self, obj_id: str, to_zone: str,
                  controller: Optional[int] = None,
                  ctx: Optional[Any] = None):
        """
        Delegate to ZoneMovementEngine.
        """
        self.movement.move_card(
            game_state=self,
            obj_id=obj_id,
            to_zone=to_zone,
            controller=controller,
            ctx=ctx,
        )

    # ============================================================
    # CASTING (delegated)
    # ============================================================

    def cast_spell(self, source_id: str, controller: int,
                   cost_choice: Optional[str] = None):
        """
        Delegate to CastSpellEngine.
        """
        return self.casting.cast_spell(
            game_state=self,
            source_id=source_id,
            controller=controller,
            cost_choice=cost_choice,
        )

    # ============================================================
    # DEBUGGING
    # ============================================================

    def add_debug_log(self, msg: str):
        self.debug_log.append(msg)

    # ============================================================
    # OBJECT CREATION
    # ============================================================

    def allocate_id(self) -> str:
        return f"obj_{len(self.objects) + 1}"

    def create_object(self, axis3_card, owner: int, controller: int, zone: ZoneType):
        obj_id = self.allocate_id()

        obj = RuntimeObject(
            id=obj_id,
            owner=owner,
            controller=controller,
            zone=zone,
            axis3_card=axis3_card,
            name=axis3_card.name,
        )

        self.objects[obj_id] = obj
        self.zone_list(controller, zone.name).append(obj_id)

        return obj

    def create_token(self, axis3_card, controller: int):
        obj_id = self.allocate_id()

        token = RuntimeObject(
            id=obj_id,
            owner=controller,
            controller=controller,
            zone=ZoneType.BATTLEFIELD,
            axis3_card=axis3_card,
            name=axis3_card.name,
            is_token=True,
        )

        self.objects[obj_id] = token
        self.players[controller].battlefield.append(obj_id)

        return token
