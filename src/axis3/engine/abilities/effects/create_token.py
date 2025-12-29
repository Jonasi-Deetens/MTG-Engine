# axis3/effects/create_token.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.engine.abilities.effects.base import Axis3Effect


@dataclass
class CreateTokenEffect(Axis3Effect):
    """
    Axis3 effect: Create one or more tokens with specified characteristics.
    """

    token_name: str
    power: int
    toughness: int
    colors: Optional[List[str]] = None
    types: Optional[List[str]] = None
    subtypes: Optional[List[str]] = None
    count: int = 1

    # Token creation is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        created_ids = []

        for _ in range(self.count):
            token = {
                "name": self.token_name,
                "power": self.power,
                "toughness": self.toughness,
                "colors": self.colors or [],
                "types": self.types or ["Creature"],
                "subtypes": self.subtypes or [],
                "controller": controller,
                "source": source,
                "is_token": True,
            }

            # Assign a runtime ID if your engine uses them
            if hasattr(game_state, "allocate_id"):
                token_id = game_state.allocate_id()
                token["id"] = token_id
                created_ids.append(token_id)

            # Add token to battlefield
            game_state.battlefield.append(token)

        # Optional event emission for UI
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "token_created",
                "source": source,
                "controller": controller,
                "token_name": self.token_name,
                "count": self.count,
                "ids": created_ids,
            })

        return True

@dataclass
class CreateDynamicTokenEffect(Axis3Effect):
    """
    Axis3 effect: Create tokens where the number of tokens is determined
    dynamically at resolution (e.g., 'for each creature you control').
    """

    power: int
    toughness: int
    colors: List[str]
    types: List[str]
    subtypes: List[str]
    count_source: str  # e.g. "creature you control"

    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        # Count objects based on the count_source string
        count = self._evaluate_count(game_state, controller)

        created_ids = []

        for _ in range(count):
            token = {
                "name": f"{self.power}/{self.toughness} token",
                "power": self.power,
                "toughness": self.toughness,
                "colors": self.colors,
                "types": self.types,
                "subtypes": self.subtypes,
                "controller": controller,
                "source": source,
                "is_token": True,
            }

            if hasattr(game_state, "allocate_id"):
                token_id = game_state.allocate_id()
                token["id"] = token_id
                created_ids.append(token_id)

            game_state.battlefield.append(token)

        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "token_created",
                "source": source,
                "controller": controller,
                "token_name": f"{self.power}/{self.toughness} token",
                "count": count,
                "ids": created_ids,
            })

        return True

    def _evaluate_count(self, game_state, controller):
        """
        Evaluate count_source strings like:
        - 'creature you control'
        - 'artifact you control'
        - 'each opponent'
        """
        src = self.count_source

        if src == "creature you control":
            return sum(
                1 for obj in game_state.battlefield
                if obj.get("controller") == controller and "Creature" in obj.get("types", [])
            )

        # Extend this as needed for other patterns
        return 0
