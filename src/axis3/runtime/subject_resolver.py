from __future__ import annotations

from typing import Any, List, Optional, Union

from axis2.schema import Subject
from axis3.state.zones import ZoneType


class SubjectResolver:
    """Resolve Axis2 Subject descriptors to runtime objects or players."""

    def __init__(self, game_state: Any):
        self.game_state = game_state

    def resolve(
        self,
        subject: Union[Subject, str, None],
        source_id: str,
        controller: int,
    ) -> List[Any]:
        if subject is None:
            return []
        if isinstance(subject, str):
            return self._resolve_string(subject, source_id, controller)
        return self._resolve_subject(subject, source_id, controller)

    def resolve_object_ids(
        self,
        subject: Union[Subject, str, None],
        source_id: str,
        controller: int,
        *,
        zone: Optional[str] = "BATTLEFIELD",
    ) -> List[str]:
        ids: List[str] = []
        for item in self.resolve(subject, source_id, controller):
            if isinstance(item, str):
                ids.append(item)
            elif hasattr(item, "id"):
                if zone is None or getattr(item, "zone", None) == zone or (
                    hasattr(item.zone, "name") and item.zone.name == zone
                ):
                    ids.append(item.id)
        return ids

    def resolve_player_ids(
        self,
        subject: Union[Subject, str, None],
        source_id: str,
        controller: int,
    ) -> List[int]:
        players: List[int] = []
        for item in self.resolve(subject, source_id, controller):
            if isinstance(item, int):
                players.append(item)
            elif hasattr(item, "id") and isinstance(item.id, int):
                players.append(item.id)
        return players

    def _opponent(self, controller: int) -> int:
        return 1 - controller if len(self.game_state.players) == 2 else 0

    def _resolve_string(self, text: str, source_id: str, controller: int) -> List[Any]:
        t = text.strip().lower()
        gs = self.game_state

        if t in ("you", "controller"):
            return [gs.players[controller]]
        if t in ("opponent", "target_opponent", "each_opponent"):
            opp = self._opponent(controller)
            return [gs.players[opp]]
        if t in ("each_player", "all_players"):
            return list(gs.players)
        if t in ("this", "self", "source", "it"):
            obj = gs.get_object(source_id)
            return [obj] if obj else []
        if t in ("that", "that_permanent", "that_card"):
            obj = gs.get_object(source_id)
            return [obj] if obj else []
        if "player" in t:
            if "opponent" in t:
                return [gs.players[self._opponent(controller)]]
            return [gs.players[controller]]

        return self._objects_from_zone("BATTLEFIELD", controller, t)

    def _resolve_subject(self, subject: Subject, source_id: str, controller: int) -> List[Any]:
        gs = self.game_state
        results: List[Any] = []

        ctrl = subject.controller
        if ctrl == "you":
            player_ids = [controller]
        elif ctrl in ("opponent", "opponents"):
            player_ids = [self._opponent(controller)]
        elif ctrl == "any":
            player_ids = list(range(len(gs.players)))
        else:
            player_ids = [controller]

        types = subject.types or []
        scope = (subject.scope or "each").lower()

        # Player-only subjects
        if types == ["player"] or (types and "player" in types and len(types) == 1):
            for pid in player_ids:
                results.append(gs.players[pid])
            if scope == "target" and results:
                return [results[0]]
            return results

        zone_name = "BATTLEFIELD"
        if subject.filters and subject.filters.get("zone"):
            zone_name = str(subject.filters["zone"]).upper()

        candidates = []
        for pid in player_ids:
            for oid in gs.zone_list(pid, zone_name):
                obj = gs.get_object(oid)
                if obj and self._matches_types(obj, types):
                    if self._matches_filters(obj, subject.filters):
                        candidates.append(obj)

        if scope in ("target", "up_to_n") and candidates:
            max_n = subject.max_targets or 1
            return candidates[:max_n]

        return candidates

    def _objects_from_zone(self, zone: str, controller: int, hint: str) -> List[Any]:
        gs = self.game_state
        results = []
        player_ids = [controller]
        if "opponent" in hint:
            player_ids = [self._opponent(controller)]

        type_hints = []
        for token in ("creature", "artifact", "enchantment", "planeswalker", "land", "battle"):
            if token in hint:
                type_hints.append(token.capitalize())

        for pid in player_ids:
            for oid in gs.zone_list(pid, zone):
                obj = gs.get_object(oid)
                if not obj:
                    continue
                if type_hints and not any(self._obj_has_type(obj, t) for t in type_hints):
                    continue
                results.append(obj)

        if "target" in hint and results:
            return [results[0]]
        return results

    def _obj_has_type(self, obj: Any, card_type: str) -> bool:
        if hasattr(obj, "axis2_card") and obj.axis2_card:
            types = getattr(obj.axis2_card.characteristics, "types", []) or []
            if card_type in types:
                return True
        if hasattr(obj, "axis3_card") and obj.axis3_card:
            if card_type in (obj.axis3_card.types or []):
                return True
        if hasattr(obj, "has_type"):
            return obj.has_type(card_type)
        return False

    def _matches_types(self, obj: Any, types: List[str]) -> bool:
        if not types:
            return True
        normalized = [t.lower() for t in types]
        if "player" in normalized:
            return False
        for t in types:
            if self._obj_has_type(obj, t):
                return True
            if self._obj_has_type(obj, t.capitalize()):
                return True
            if self._obj_has_type(obj, t.title()):
                return True
        return False

    def _matches_filters(self, obj: Any, filters: Optional[dict]) -> bool:
        if not filters:
            return True
        if "keyword" in filters:
            kw = filters["keyword"].lower()
            keywords = []
            if hasattr(obj, "axis2_card") and obj.axis2_card:
                keywords = [k.lower() for k in (obj.axis2_card.keywords or [])]
            if kw not in keywords:
                return False
        return True
