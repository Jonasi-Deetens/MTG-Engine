from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
import itertools

from .zones import ZONE_BATTLEFIELD, ZONE_COMMAND, ZONE_EXILE, ZONE_GRAVEYARD, ZONE_HAND, ZONE_LIBRARY
from .choices_runtime import queue_choice
from .events import Event, EventBus
from .stack import Stack
from .turn import TurnState

# Import managers
from .managers.zone_manager import ZoneManager
from .managers.object_manager import ObjectManager, next_object_id
from .managers.attachment_manager import AttachmentManager
from .managers.replacement_manager import ReplacementManager

# Re-export for backward compatibility
__all__ = [
    "GameObject",
    "PlayerState",
    "ResolveContext",
    "GameState",
    "next_object_id",
]


@dataclass
class GameObject:
    id: str
    name: str
    owner_id: int
    controller_id: int
    types: List[str]
    zone: str
    mana_cost: Optional[str] = None
    base_name: Optional[str] = None
    base_mana_cost: Optional[str] = None
    base_mana_value: Optional[int] = None
    base_types: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    base_colors: List[str] = field(default_factory=list)
    type_line: Optional[str] = None
    base_type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    base_oracle_text: Optional[str] = None
    mana_value: Optional[int] = None
    power: Optional[int] = None
    toughness: Optional[int] = None
    base_power: Optional[int] = None
    base_toughness: Optional[int] = None
    cda_power: Optional[int] = None
    cda_toughness: Optional[int] = None
    base_keywords: Set[str] = field(default_factory=set)
    entered_turn: Optional[int] = None
    tapped: bool = False
    damage: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    keywords: Set[str] = field(default_factory=set)
    protections: Set[str] = field(default_factory=set)
    attached_to: Optional[str] = None
    is_token: bool = False
    was_cast: bool = False
    is_attacking: bool = False
    is_blocking: bool = False
    phased_out: bool = False
    transformed: bool = False
    regenerate_shield: bool = False
    temporary_effects: List[Dict[str, Any]] = field(default_factory=list)
    ability_graphs: List[Dict[str, Any]] = field(default_factory=list)
    base_ability_graphs: List[Dict[str, Any]] = field(default_factory=list)
    activation_limits: Dict[str, int] = field(default_factory=dict)
    etb_choices: Dict[str, Any] = field(default_factory=dict)
    base_etb_choices: Dict[str, Any] = field(default_factory=dict)
    base_controller_id: Optional[int] = None


@dataclass
class PlayerState:
    id: int
    life: int = 40
    max_hand_size: int = 7
    has_lost: bool = False
    removed_from_game: bool = False
    poison_counters: int = 0
    mana_pool: Dict[str, int] = field(default_factory=dict)
    library: List[str] = field(default_factory=list)
    hand: List[str] = field(default_factory=list)
    graveyard: List[str] = field(default_factory=list)
    exile: List[str] = field(default_factory=list)
    command: List[str] = field(default_factory=list)
    battlefield: List[str] = field(default_factory=list)
    commander_id: Optional[str] = None
    commander_tax: int = 0
    commander_damage_taken: Dict[str, int] = field(default_factory=dict)

    def total_mana(self) -> int:
        return sum(self.mana_pool.values())


@dataclass
class ResolveContext:
    source_id: Optional[str] = None
    controller_id: Optional[int] = None
    triggering_source_id: Optional[str] = None
    triggering_aura_id: Optional[str] = None
    triggering_spell_id: Optional[str] = None
    targets: Dict[str, Any] = field(default_factory=dict)
    targets_by_effect: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required_targets_by_effect: Dict[str, List[str]] = field(default_factory=dict)
    distinct_targets_by_effect: Dict[str, List[str]] = field(default_factory=dict)
    min_targets_by_effect: Dict[str, Dict[str, int]] = field(default_factory=dict)
    choices: Dict[str, Any] = field(default_factory=dict)
    previous_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GameState:
    players: List[PlayerState]
    objects: Dict[str, GameObject] = field(default_factory=dict)
    stack: Stack = field(default_factory=Stack)
    event_bus: EventBus = field(default_factory=EventBus)
    turn: TurnState = field(default_factory=TurnState)
    debug_log: List[str] = field(default_factory=list)
    replacement_effects: List[Dict[str, Any]] = field(default_factory=list)
    replacement_choices: Dict[str, str] = field(default_factory=dict)
    choices: Dict[str, Any] = field(default_factory=dict)
    pending_triggers: List[Dict[str, Any]] = field(default_factory=list)
    prepared_casts: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    effect_timestamp_counter: int = 0
    replacement_effect_counter: int = 0

    # Managers (initialized in __post_init__)
    _zone_manager: Optional[ZoneManager] = field(default=None, repr=False)
    _object_manager: Optional[ObjectManager] = field(default=None, repr=False)
    _attachment_manager: Optional[AttachmentManager] = field(default=None, repr=False)
    _replacement_manager: Optional[ReplacementManager] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize managers after dataclass initialization."""
        self._zone_manager = ZoneManager(
            objects=self.objects,
            players=self.players,
            get_player=self.get_player,
        )
        self._object_manager = ObjectManager(
            objects=self.objects,
            get_turn_number=lambda: self.turn.turn_number,
        )
        self._attachment_manager = AttachmentManager(
            objects=self.objects,
            move_object=self.move_object,
        )
        self._replacement_manager = ReplacementManager(
            replacement_effects=self.replacement_effects,
            replacement_choices=self.replacement_choices,
            queue_choice_fn=lambda choice: queue_choice(self, choice),
            log_fn=self.log,
        )

    @property
    def zone_manager(self) -> ZoneManager:
        """Get the zone manager."""
        if self._zone_manager is None:
            self.__post_init__()
        return self._zone_manager  # type: ignore

    @property
    def object_manager(self) -> ObjectManager:
        """Get the object manager."""
        if self._object_manager is None:
            self.__post_init__()
        return self._object_manager  # type: ignore

    @property
    def attachment_manager(self) -> AttachmentManager:
        """Get the attachment manager."""
        if self._attachment_manager is None:
            self.__post_init__()
        return self._attachment_manager  # type: ignore

    @property
    def replacement_manager(self) -> ReplacementManager:
        """Get the replacement manager."""
        if self._replacement_manager is None:
            self.__post_init__()
        return self._replacement_manager  # type: ignore

    def next_replacement_effect_id(self) -> str:
        self.replacement_effect_counter += 1
        return f"repl_{self.replacement_effect_counter}"

    def log(self, message: str) -> None:
        self.debug_log.append(message)

    def get_player(self, player_id: int) -> PlayerState:
        return next(p for p in self.players if p.id == player_id)

    def add_object(self, obj: GameObject) -> None:
        """Add an object to the game."""
        self.object_manager.add(obj)
        self.zone_manager.add_to_zone(obj.zone, obj.id)

    def create_token(
        self,
        name: str,
        controller_id: int,
        power: Optional[int] = None,
        toughness: Optional[int] = None,
        types: Optional[List[str]] = None,
    ) -> GameObject:
        token = GameObject(
            id=next_object_id(),
            name=name,
            owner_id=controller_id,
            controller_id=controller_id,
            types=types or ["Token"],
            zone=ZONE_BATTLEFIELD,
            power=power,
            toughness=toughness,
            is_token=True,
        )
        self.add_object(token)
        self.event_bus.publish(Event(
            type="enters_battlefield",
            payload={
                "object_id": token.id,
                "cardTypes": list(token.types or []),
                "controller_id": token.controller_id,
                "owner_id": token.owner_id,
            },
        ))
        self.event_bus.publish(Event(
            type="card_enters",
            payload={
                "object_id": token.id,
                "entersWhere": ZONE_BATTLEFIELD,
                "entersFrom": None,
                "cardTypes": list(token.types or []),
                "controller_id": token.controller_id,
                "owner_id": token.owner_id,
            },
        ))
        self.log(f"Token created: {token.name} ({token.id})")
        return token

    def move_object(self, obj_id: str, destination: str) -> None:
        obj = self.objects.get(obj_id)
        if not obj:
            return
        player = self.get_player(obj.owner_id)
        if (
            obj.id == player.commander_id
            and destination in (ZONE_GRAVEYARD, ZONE_EXILE, ZONE_HAND, ZONE_LIBRARY)
        ):
            destination = ZONE_COMMAND
        previous_zone = obj.zone
        destination = self.replacement_manager.apply_zone_replacement(obj, previous_zone, destination)
        if destination != ZONE_HAND:
            self.clear_prepared_casts_for_object(obj_id)
        if destination != ZONE_BATTLEFIELD:
            obj.attached_to = None
        if previous_zone == ZONE_BATTLEFIELD and destination != ZONE_BATTLEFIELD:
            self.object_manager.clear_battlefield_state(obj)
            for attached in list(self.objects.values()):
                if attached.zone != ZONE_BATTLEFIELD:
                    continue
                if attached.attached_to != obj_id:
                    continue
                attached.attached_to = None
                if "Aura" in attached.types:
                    self.move_object(attached.id, ZONE_GRAVEYARD)
            self.event_bus.publish(Event(type="leaves_battlefield", payload={"object_id": obj.id}))
        self.zone_manager.remove_from_zone(obj.zone, obj_id)
        obj.zone = destination
        if obj.is_token and destination != ZONE_BATTLEFIELD:
            del self.objects[obj_id]
            self.log(f"Token removed: {obj_id}")
            return
        if destination == ZONE_BATTLEFIELD:
            obj.entered_turn = self.turn.turn_number
        self.zone_manager.add_to_zone(destination, obj_id)
        if destination == ZONE_BATTLEFIELD and self.attachment_manager.enforce_legality(obj):
            return
        if destination == ZONE_BATTLEFIELD and previous_zone != ZONE_BATTLEFIELD:
            self.event_bus.publish(Event(
                type="enters_battlefield",
                payload={
                    "object_id": obj.id,
                    "cardTypes": list(obj.types or []),
                    "controller_id": obj.controller_id,
                    "owner_id": obj.owner_id,
                },
            ))
        if previous_zone != destination:
            self.event_bus.publish(Event(
                type="card_enters",
                payload={
                    "object_id": obj.id,
                    "entersWhere": destination,
                    "entersFrom": previous_zone,
                    "cardTypes": list(obj.types or []),
                    "controller_id": obj.controller_id,
                    "owner_id": obj.owner_id,
                },
            ))
    def remove_player_from_game(self, player_id: int) -> None:
        player = self.get_player(player_id)
        if getattr(player, "removed_from_game", False):
            return
        player.removed_from_game = True

        self.prepared_casts.pop(player_id, None)
        self.replacement_choices = {
            key: value for key, value in self.replacement_choices.items() if str(player_id) not in key
        }
        self.replacement_effects = [
            effect
            for effect in self.replacement_effects
            if effect.get("player_id") != player_id
            and effect.get("controller_id") != player_id
            and effect.get("owner_id") != player_id
        ]

        self.stack.items = [
            item for item in self.stack.items if not self._stack_item_for_player(item, player_id)
        ]

        owned_objects = [obj for obj in list(self.objects.values()) if obj.owner_id == player_id]
        for obj in owned_objects:
            self._remove_owned_object_from_game(obj)

        for obj in list(self.objects.values()):
            if obj.controller_id != player_id or obj.owner_id == player_id:
                continue
            if obj.zone == ZONE_BATTLEFIELD:
                prev_controller = obj.controller_id
                obj.controller_id = obj.owner_id
                if obj.base_controller_id is not None:
                    obj.base_controller_id = obj.owner_id
                prev_player = self.get_player(prev_controller)
                if obj.id in prev_player.battlefield:
                    prev_player.battlefield.remove(obj.id)
                self.zone_manager.add_to_zone(ZONE_BATTLEFIELD, obj.id)
                self.attachment_manager.enforce_legality(obj)

        player.library = []
        player.hand = []
        player.graveyard = []
        player.command = []
        player.battlefield = []

    def _stack_item_for_player(self, item, player_id: int) -> bool:
        if item.controller_id == player_id:
            return True
        payload = item.payload or {}
        for key in ("object_id", "source_object_id", "copy_of"):
            obj_id = payload.get(key)
            if obj_id and obj_id in self.objects and self.objects[obj_id].owner_id == player_id:
                return True
        return False

    def _remove_owned_object_from_game(self, obj: GameObject) -> None:
        previous_zone = obj.zone
        if previous_zone == ZONE_BATTLEFIELD:
            for attached in list(self.objects.values()):
                if attached.zone != ZONE_BATTLEFIELD:
                    continue
                if attached.attached_to != obj.id:
                    continue
                attached.attached_to = None
                if "Aura" in attached.types:
                    self.move_object(attached.id, ZONE_GRAVEYARD)
        self.zone_manager.remove_from_zone(previous_zone, obj.id)
        obj.attached_to = None
        obj.zone = ZONE_EXILE
        if obj.is_token:
            self.objects.pop(obj.id, None)
            return
        owner = self.get_player(obj.owner_id)
        if obj.id not in owner.exile:
            owner.exile.append(obj.id)

    def destroy_object(self, obj_id: str, allow_regen: bool = True) -> None:
        obj = self.objects.get(obj_id)
        if not obj:
            return
        if allow_regen and "Indestructible" in obj.keywords:
            self.log(f"Destroy prevented (indestructible): {obj_id}")
            return
        if allow_regen and obj.regenerate_shield:
            obj.regenerate_shield = False
            obj.tapped = True
            obj.damage = 0
            obj.is_attacking = False
            obj.is_blocking = False
            self.log(f"Regenerated: {obj_id}")
            return
        replacement = self.replacement_manager.apply_object_replacement(obj, "replace_destroy", ZONE_GRAVEYARD)
        if replacement == "skip":
            self.log(f"Destroy skipped: {obj_id}")
            return
        if replacement != ZONE_GRAVEYARD:
            self.move_object(obj_id, replacement)
            self.log(f"Object destroyed (replaced): {obj_id}")
            return
        self.event_bus.publish(Event(
            type="dies",
            payload={
                "object_id": obj_id,
                "controller_id": obj.controller_id,
                "owner_id": obj.owner_id,
                "cardTypes": list(obj.types or []),
            },
        ))
        if obj.is_token:
            self.zone_manager.remove_from_zone(obj.zone, obj_id)
            del self.objects[obj_id]
            self.log(f"Token destroyed: {obj_id}")
            return
        self.move_object(obj_id, ZONE_GRAVEYARD)
        self.log(f"Object destroyed: {obj_id}")

    def sacrifice_object(self, obj_id: str) -> None:
        obj = self.objects.get(obj_id)
        if not obj:
            return
        replacement = self.replacement_manager.apply_object_replacement(obj, "replace_sacrifice", ZONE_GRAVEYARD)
        if replacement == "skip":
            self.log(f"Sacrifice skipped: {obj_id}")
            return
        if replacement != ZONE_GRAVEYARD:
            self.move_object(obj_id, replacement)
            self.log(f"Object sacrificed (replaced): {obj_id}")
            return
        self.event_bus.publish(Event(
            type="dies",
            payload={
                "object_id": obj_id,
                "controller_id": obj.controller_id,
                "owner_id": obj.owner_id,
                "cardTypes": list(obj.types or []),
            },
        ))
        if obj.is_token:
            self.zone_manager.remove_from_zone(obj.zone, obj_id)
            del self.objects[obj_id]
            self.log(f"Token sacrificed: {obj_id}")
            return
        self.move_object(obj_id, ZONE_GRAVEYARD)
        self.log(f"Object sacrificed: {obj_id}")

    def state_based_put_into_graveyard(self, obj_id: str) -> None:
        obj = self.objects.get(obj_id)
        if not obj:
            return
        self.event_bus.publish(Event(
            type="dies",
            payload={
                "object_id": obj_id,
                "controller_id": obj.controller_id,
                "owner_id": obj.owner_id,
                "cardTypes": list(obj.types or []),
            },
        ))
        if obj.is_token:
            self.zone_manager.remove_from_zone(obj.zone, obj_id)
            del self.objects[obj_id]
            self.log(f"Token removed by SBA: {obj_id}")
            return
        self.move_object(obj_id, ZONE_GRAVEYARD)
        self.log(f"Object moved to graveyard by SBA: {obj_id}")

    def clear_prepared_casts(self) -> None:
        self.prepared_casts.clear()

    def clear_prepared_casts_for_object(self, obj_id: str) -> None:
        to_clear = [player_id for player_id, entry in self.prepared_casts.items()
                    if entry.get("object_id") == obj_id]
        for player_id in to_clear:
            self.prepared_casts.pop(player_id, None)
