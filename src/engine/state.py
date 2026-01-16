from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
import itertools

from .zones import ZONE_BATTLEFIELD, ZONE_COMMAND, ZONE_EXILE, ZONE_GRAVEYARD, ZONE_HAND, ZONE_LIBRARY
from .events import Event, EventBus
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
    base_controller_id: Optional[int] = None


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
    replacement_effects: List[Dict[str, Any]] = field(default_factory=list)
    replacement_choices: Dict[str, str] = field(default_factory=dict)
    prepared_casts: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    effect_timestamp_counter: int = 0
    replacement_effect_counter: int = 0

    def next_replacement_effect_id(self) -> str:
        self.replacement_effect_counter += 1
        return f"repl_{self.replacement_effect_counter}"

    def log(self, message: str) -> None:
        self.debug_log.append(message)

    def get_player(self, player_id: int) -> PlayerState:
        return next(p for p in self.players if p.id == player_id)

    def add_object(self, obj: GameObject) -> None:
        self.objects[obj.id] = obj
        if obj.zone == ZONE_BATTLEFIELD and obj.entered_turn is None:
            obj.entered_turn = self.turn.turn_number
        if obj.base_controller_id is None:
            obj.base_controller_id = obj.controller_id
        if obj.base_name is None:
            obj.base_name = obj.name
        if obj.base_mana_cost is None:
            obj.base_mana_cost = obj.mana_cost
        if obj.base_mana_value is None:
            obj.base_mana_value = obj.mana_value
        if obj.base_type_line is None:
            obj.base_type_line = obj.type_line
        if obj.base_oracle_text is None:
            obj.base_oracle_text = obj.oracle_text
        if not obj.base_ability_graphs and obj.ability_graphs:
            obj.base_ability_graphs = list(obj.ability_graphs)
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
        previous_zone = obj.zone
        destination = self._apply_zone_replacement(obj, previous_zone, destination)
        if destination != ZONE_HAND:
            self.clear_prepared_casts_for_object(obj_id)
        if destination != ZONE_BATTLEFIELD:
            obj.attached_to = None
        if previous_zone == ZONE_BATTLEFIELD and destination != ZONE_BATTLEFIELD:
            self.event_bus.publish(Event(type="leaves_battlefield", payload={"object_id": obj.id}))
        self._remove_from_zone(obj.zone, obj_id)
        obj.zone = destination
        if obj.is_token and destination != ZONE_BATTLEFIELD:
            del self.objects[obj_id]
            self.log(f"Token removed: {obj_id}")
            return
        if destination == ZONE_BATTLEFIELD:
            obj.entered_turn = self.turn.turn_number
        self._add_to_zone(destination, obj_id)
        if destination == ZONE_BATTLEFIELD and self._enforce_attachment_legality(obj):
            return
        if destination == ZONE_BATTLEFIELD and previous_zone != ZONE_BATTLEFIELD:
            self.event_bus.publish(Event(type="enters_battlefield", payload={"object_id": obj.id}))

    def _apply_zone_replacement(self, obj: GameObject, from_zone: str, to_zone: str) -> str:
        def matches(effect: Dict[str, Any]) -> bool:
            if effect.get("type") != "replace_zone_change":
                return False
            if effect.get("from_zone") and effect.get("from_zone") != from_zone:
                return False
            if effect.get("to_zone") and effect.get("to_zone") != to_zone:
                return False
            if effect.get("object_id") and effect.get("object_id") != obj.id:
                return False
            if effect.get("controller_id") is not None and effect.get("controller_id") != obj.controller_id:
                return False
            if effect.get("owner_id") is not None and effect.get("owner_id") != obj.owner_id:
                return False
            return True

        def consume(effect: Dict[str, Any], container: List[Dict[str, Any]]) -> None:
            remaining = effect.get("uses")
            if remaining is None:
                return
            remaining = int(remaining) - 1
            if remaining <= 0:
                container.remove(effect)
            else:
                effect["uses"] = remaining

        matches_temp = [effect for effect in list(obj.temporary_effects) if matches(effect)]
        matches_global = [effect for effect in list(self.replacement_effects) if matches(effect)]
        matches_all = [(effect, obj.temporary_effects) for effect in matches_temp] + [
            (effect, self.replacement_effects) for effect in matches_global
        ]

        event_key = f"{obj.id}:{from_zone}:{to_zone}"
        if len(matches_all) > 1:
            choice_id = self.replacement_choices.get(event_key)
            if choice_id:
                for effect, container in matches_all:
                    if effect.get("effect_id") == choice_id:
                        replacement = effect.get("replacement_zone")
                        if replacement:
                            consume(effect, container)
                            self.replacement_choices.pop(event_key, None)
                            return replacement
            matches_all.sort(key=lambda item: int(item[0].get("timestamp_order", 0)), reverse=True)
            effect, container = matches_all[0]
            replacement = effect.get("replacement_zone")
            if replacement:
                consume(effect, container)
                self.log(f"Multiple replacements for {obj.id}; defaulted to most recent.")
                return replacement

        for effect, container in matches_all:
            replacement = effect.get("replacement_zone")
            if replacement:
                consume(effect, container)
                return replacement

        return to_zone

    def _is_illegal_attachment(self, attachment: GameObject, attached: GameObject) -> bool:
        if "Hexproof" in attached.keywords and attachment.controller_id != attached.controller_id:
            return True
        if attached.protections and attachment.colors:
            if any(color in attached.protections for color in attachment.colors):
                return True
        return False

    def _enforce_attachment_legality(self, obj: GameObject) -> bool:
        if obj.zone != ZONE_BATTLEFIELD:
            return False
        if "Aura" in obj.types:
            if not obj.attached_to:
                self.move_object(obj.id, ZONE_GRAVEYARD)
                return True
            attached = self.objects.get(obj.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                obj.attached_to = None
                self.move_object(obj.id, ZONE_GRAVEYARD)
                return True
            if attached.phased_out or self._is_illegal_attachment(obj, attached):
                obj.attached_to = None
                self.move_object(obj.id, ZONE_GRAVEYARD)
                return True
            return False
        if "Equipment" in obj.types:
            if not obj.attached_to:
                return False
            attached = self.objects.get(obj.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD or "Creature" not in attached.types or attached.phased_out:
                obj.attached_to = None
            return False
        if obj.attached_to:
            attached = self.objects.get(obj.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                obj.attached_to = None
        return False

    def _apply_enter_copy(self, obj: GameObject, source_id: str) -> None:
        source = self.objects.get(source_id)
        if not source:
            return
        obj.base_name = source.base_name or source.name
        obj.base_mana_cost = source.base_mana_cost or source.mana_cost
        obj.base_mana_value = source.base_mana_value if source.base_mana_value is not None else source.mana_value
        obj.base_type_line = source.base_type_line or source.type_line
        obj.base_oracle_text = source.base_oracle_text or source.oracle_text
        obj.base_types = list(source.base_types) if source.base_types else list(source.types)
        obj.base_colors = list(source.base_colors) if source.base_colors else list(source.colors)
        obj.base_power = source.base_power
        obj.base_toughness = source.base_toughness
        obj.base_keywords = set(source.base_keywords) if source.base_keywords else set(source.keywords)
        obj.base_ability_graphs = list(source.base_ability_graphs) if source.base_ability_graphs else list(source.ability_graphs)
        obj.etb_choices = dict(getattr(source, "etb_choices", {}) or {})

        obj.name = obj.base_name or obj.name
        obj.mana_cost = obj.base_mana_cost
        obj.mana_value = obj.base_mana_value
        obj.type_line = obj.base_type_line
        obj.oracle_text = obj.base_oracle_text
        obj.types = list(obj.base_types)
        obj.colors = list(obj.base_colors)
        obj.power = obj.base_power
        obj.toughness = obj.base_toughness
        obj.keywords = set(obj.base_keywords)
        obj.ability_graphs = list(obj.base_ability_graphs)

    def _apply_enter_choices(self, obj: GameObject, choices: Dict[str, Any]) -> None:
        if not choices:
            return
        obj.etb_choices.update(choices)

    def destroy_object(self, obj_id: str) -> None:
        obj = self.objects.get(obj_id)
        if not obj:
            return
        self.event_bus.publish(Event(type="dies", payload={"object_id": obj_id}))
        if obj.is_token:
            self._remove_from_zone(obj.zone, obj_id)
            del self.objects[obj_id]
            self.log(f"Token destroyed: {obj_id}")
            return
        self.move_object(obj_id, ZONE_GRAVEYARD)
        self.log(f"Object destroyed: {obj_id}")

    def clear_prepared_casts(self) -> None:
        self.prepared_casts.clear()

    def clear_prepared_casts_for_object(self, obj_id: str) -> None:
        to_clear = [player_id for player_id, entry in self.prepared_casts.items()
                    if entry.get("object_id") == obj_id]
        for player_id in to_clear:
            self.prepared_casts.pop(player_id, None)

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
