from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
import itertools

from .zones import ZONE_BATTLEFIELD, ZONE_COMMAND, ZONE_EXILE, ZONE_GRAVEYARD, ZONE_HAND, ZONE_LIBRARY
from .events import EventBus
from .stack import Stack
from .turn import TurnState


_id_counter = itertools.count(1)


def next_object_id() -> str:
    return f"obj_{next(_id_counter)}"


@dataclass
class GameObject:
    id: str
    name: str
    owner_id: int
    controller_id: int
    types: List[str]
    zone: str
    mana_value: Optional[int] = None
    power: Optional[int] = None
    toughness: Optional[int] = None
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


@dataclass
class PlayerState:
    id: int
    life: int = 40
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

    def log(self, message: str) -> None:
        self.debug_log.append(message)

    def get_player(self, player_id: int) -> PlayerState:
        return next(p for p in self.players if p.id == player_id)

    def add_object(self, obj: GameObject) -> None:
        self.objects[obj.id] = obj
        self._add_to_zone(obj.zone, obj.id)

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
        self.log(f"Token created: {token.name} ({token.id})")
        return token

    def move_object(self, obj_id: str, destination: str) -> None:
        obj = self.objects.get(obj_id)
        if not obj:
            return
        self._remove_from_zone(obj.zone, obj_id)
        obj.zone = destination
        self._add_to_zone(destination, obj_id)

    def destroy_object(self, obj_id: str) -> None:
        obj = self.objects.get(obj_id)
        if not obj:
            return
        if obj.is_token:
            self._remove_from_zone(obj.zone, obj_id)
            del self.objects[obj_id]
            self.log(f"Token destroyed: {obj_id}")
            return
        self.move_object(obj_id, ZONE_GRAVEYARD)
        self.log(f"Object destroyed: {obj_id}")

    def _add_to_zone(self, zone: str, obj_id: str) -> None:
        if zone == ZONE_BATTLEFIELD:
            controller_id = self.objects[obj_id].controller_id
            player = self.get_player(controller_id)
            if obj_id not in player.battlefield:
                player.battlefield.append(obj_id)
            return
        if zone == ZONE_LIBRARY:
            owner = self.objects[obj_id].owner_id
            self.get_player(owner).library.append(obj_id)
            return
        if zone == ZONE_HAND:
            owner = self.objects[obj_id].owner_id
            self.get_player(owner).hand.append(obj_id)
            return
        if zone == ZONE_GRAVEYARD:
            owner = self.objects[obj_id].owner_id
            self.get_player(owner).graveyard.append(obj_id)
            return
        if zone == ZONE_EXILE:
            owner = self.objects[obj_id].owner_id
            self.get_player(owner).exile.append(obj_id)
            return
        if zone == ZONE_COMMAND:
            owner = self.objects[obj_id].owner_id
            self.get_player(owner).command.append(obj_id)
            return
        if zone.startswith("battlefield:"):
            controller_id = int(zone.split(":")[1])
            self.get_player(controller_id).battlefield.append(obj_id)
            return

    def _remove_from_zone(self, zone: str, obj_id: str) -> None:
        if zone == ZONE_LIBRARY:
            owner = self.objects[obj_id].owner_id
            self._safe_remove(self.get_player(owner).library, obj_id)
            return
        if zone == ZONE_HAND:
            owner = self.objects[obj_id].owner_id
            self._safe_remove(self.get_player(owner).hand, obj_id)
            return
        if zone == ZONE_GRAVEYARD:
            owner = self.objects[obj_id].owner_id
            self._safe_remove(self.get_player(owner).graveyard, obj_id)
            return
        if zone == ZONE_EXILE:
            owner = self.objects[obj_id].owner_id
            self._safe_remove(self.get_player(owner).exile, obj_id)
            return
        if zone == ZONE_COMMAND:
            owner = self.objects[obj_id].owner_id
            self._safe_remove(self.get_player(owner).command, obj_id)
            return
        if zone == ZONE_BATTLEFIELD:
            for player in self.players:
                self._safe_remove(player.battlefield, obj_id)
            return
        if zone.startswith("battlefield:"):
            controller_id = int(zone.split(":")[1])
            self._safe_remove(self.get_player(controller_id).battlefield, obj_id)
            return

    @staticmethod
    def _safe_remove(container: List[str], obj_id: str) -> None:
        try:
            container.remove(obj_id)
        except ValueError:
            return
