# axis3/engine/abilities/effects/create_token.py

from dataclasses import dataclass, field
from typing import List, Optional

from axis3.engine.abilities.effects.base import Axis3Effect
from axis3.model.axis3_card import Axis3Card
from axis3.state.zones import ZoneType


@dataclass
class CreateTokenEffect(Axis3Effect):
    token_name: str = ""
    power: int = 0
    toughness: int = 0
    colors: Optional[List[str]] = None
    types: Optional[List[str]] = None
    subtypes: Optional[List[str]] = None
    count: int = 1

    layering: str = "resolution"

    def apply(self, game_state, source_id, controller):
        created_ids = []

        for _ in range(self.count):
            # 1. Build an Axis3Card for the token
            token_card = Axis3Card(
                name=self.token_name,
                mana_cost=None,
                mana_value=None,
                colors=self.colors or [],
                color_identity=self.colors or [],
                types=self.types or ["Creature"],
                supertypes=[],
                subtypes=self.subtypes or [],
                power=self.power,
                toughness=self.toughness,
                loyalty=None,
                defense=None,
                static_effects=[],
                replacement_effects=[],
                activated_abilities=[],
                keywords=[],
                effects=[],
                special_actions=[],
                modes=[],
                mode_choice=None,
            )

            # 2. Create a RuntimeObject on the battlefield
            rt_obj = game_state.create_object(
                axis3_card=token_card,
                owner=controller,
                controller=controller,
                zone=ZoneType.BATTLEFIELD,
            )

            created_ids.append(rt_obj.id)

        # 3. Publish event
        game_state.event_bus.publish({
            "type": "TOKEN_CREATED",
            "source": source_id,
            "controller": controller,
            "token_name": self.token_name,
            "count": self.count,
            "ids": created_ids,
        })

        return True


@dataclass
class CreateDynamicTokenEffect(Axis3Effect):
    power: int = 0
    toughness: int = 0
    colors: List[str] = field(default_factory=list)
    types: List[str] = field(default_factory=list)
    subtypes: List[str] = field(default_factory=list)
    count_source: str = ""

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
