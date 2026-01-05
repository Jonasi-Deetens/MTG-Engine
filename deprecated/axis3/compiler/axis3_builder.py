# axis3/compiler/axis3_builder.py

from __future__ import annotations
from typing import Any

from axis1.schema import Axis1Card
from axis3.model.axis3_card import Axis3Card

from axis3.rules.costs.mana import parse_mana_cost
from axis3.rules.builder.keywords import derive_keyword_abilities
from axis3.rules.builder.static_effects import derive_static_effects
from axis3.rules.builder.replacement_effects import derive_replacement_effects
from axis3.rules.builder.effects import derive_triggers
from axis3.translate.ability_parsing.activated import derive_activated_abilities
from axis3.rules.builder.modes import parse_modes
from axis3.rules.builder.etb_replacement import derive_etb_replacement_effects

from axis3.translate.compilers import compile_effect


class Axis3CardBuilder:
    def _build_special_actions(axis1_card: Axis1Card, game_state: GameState) -> List[SpecialAction]:
        actions: List[SpecialAction] = []
        text = (axis1_card.faces[0].oracle_text or "").lower()

        # ------------------------------------------------------------
        # Morph
        # ------------------------------------------------------------
        if "morph" in text:
            m = re.search(r"morph\s*\{([^}]+)\}", text)
            cost = m.group(1) if m else None
            actions.append(
                SpecialAction(
                    kind="morph",
                    cost=cost,
                    zones=["Hand"],
                    effect="Cast face down as a 2/2 creature",
                )
            )

        # ------------------------------------------------------------
        # Foretell
        # ------------------------------------------------------------
        if "foretell" in text:
            m = re.search(r"foretell\s*\{([^}]+)\}", text)
            cost = m.group(1) if m else None
            actions.append(
                SpecialAction(
                    kind="foretell",
                    cost=cost,
                    zones=["Hand"],
                    effect="Exile face down; cast later for foretell cost",
                )
            )

        # ------------------------------------------------------------
        # Prototype
        # ------------------------------------------------------------
        if "prototype" in text:
            m = re.search(r"prototype\s*\{([^}]+)\}", text)
            cost = m.group(1) if m else None
            actions.append(
                SpecialAction(
                    kind="prototype",
                    cost=cost,
                    zones=["Hand"],
                    effect="Cast as smaller creature with prototype stats",
                )
            )

        # ------------------------------------------------------------
        # Adventure
        # ------------------------------------------------------------
        if "adventure" in text:
            actions.append(
                SpecialAction(
                    kind="adventure",
                    cost=None,
                    zones=["Hand"],
                    effect="Cast adventure half of the card",
                )
            )

        return actions
    @staticmethod
    def build(axis1_card: Axis1Card, game_state: "GameState") -> Axis3Card:
        """
        Convert Axis1Card → Axis3Card.
        This is the new, Axis3-native card builder.
        """

        face = axis1_card.faces[0]
        oracle = face.oracle_text or ""

        # ------------------------------------------------------------
        # Basic characteristics
        # ------------------------------------------------------------
        mana_cost = parse_mana_cost(face.mana_cost)
        mana_value = getattr(face, "mana_value", None)

        colors = list(face.colors or [])
        color_identity = list(face.color_indicator or [])

        types = list(face.card_types or [])
        supertypes = list(face.supertypes or [])
        subtypes = list(face.subtypes or [])

        power = int(face.power) if face.power is not None else None
        toughness = int(face.toughness) if face.toughness is not None else None
        loyalty = face.loyalty
        defense = face.defense

        # ------------------------------------------------------------
        # Axis3 rules parsing
        # ------------------------------------------------------------

        keywords = derive_keyword_abilities(axis1_card, game_state)
        static_effects = derive_static_effects(axis1_card, game_state)
        replacement_effects = derive_replacement_effects(axis1_card, game_state)
        # triggered_abilities = derive_triggered_abilities(axis1_card)
        activated_abilities = derive_activated_abilities(axis1_card, game_state)
        effects = compile_effects(axis1_card, game_state)
        special_actions = build_special_actions(axis1_card, game_state)
        etb_replacements = derive_etb_replacement_effects(oracle, game_state)

        # Merge ETB replacements into replacement effects
        replacement_effects.extend(etb_replacements)

        mode_choice, modes = parse_modes(oracle, game_state)

        # ------------------------------------------------------------
        # Build Axis3Card
        # ------------------------------------------------------------
        return Axis3Card(
            name=face.name,
            mana_cost=mana_cost,
            mana_value=mana_value,
            colors=colors,
            color_identity=color_identity,
            types=types,
            supertypes=supertypes,
            subtypes=subtypes,
            power=power,
            toughness=toughness,
            loyalty=loyalty,
            defense=defense,
            static_effects=static_effects,
            replacement_effects=replacement_effects,
            triggered_abilities=triggered_abilities,
            activated_abilities=activated_abilities,
            keywords=keywords,
            effects=effects,
            special_actions=special_actions,
            modes=modes,
            mode_choice=mode_choice,
        )
