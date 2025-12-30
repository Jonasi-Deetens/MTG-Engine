from axis1.schema import Axis1Card, Axis1Face, Axis1ActivatedAbility, Axis1TriggeredAbility
from axis2.schema import (
    Axis2Card, Axis2Face, Axis2Characteristics,
    ManaCost, TapCost, SacrificeCost, LoyaltyCost,
    DealDamageEffect, DrawCardsEffect, AddManaEffect, CreateTokenEffect,
    ActivatedAbility, TriggeredAbility, StaticEffect, Mode,
    SymbolicValue, TargetingRules, TargetingRestriction,
    ReplacementEffect, ContinuousEffect, TapCost
)

from axis2.parsing.mana import parse_mana_cost
from axis2.parsing.costs import parse_cost, parse_tap_cost
from axis2.parsing.effects import parse_effect_text
from axis2.parsing.targeting import parse_targeting
from axis2.parsing.static_effects import parse_static_effects
from axis2.parsing.modes import parse_modes
from axis2.parsing.trigger_filters import parse_trigger_filter
from axis2.parsing.replacement_effects import parse_replacement_effects
from axis2.parsing.continuous_effects import parse_continuous_effects
from axis2.parsing.special_actions import parse_ninjutsu
from axis2.parsing.keywords import extract_keywords
from axis2.parsing.sentences import split_into_sentences

class Axis2Builder:

    @staticmethod
    def build(axis1_card: Axis1Card) -> Axis2Card:
        face1: Axis1Face = axis1_card.faces[0]

        # ------------------------------------------------------------
        # 1. Characteristics
        # ------------------------------------------------------------
        characteristics = Axis2Characteristics(
            mana_cost=parse_mana_cost(face1.mana_cost),
            mana_value=face1.mana_value,
            colors=list(face1.colors),
            color_identity=list(axis1_card.characteristics.color_identity),
            color_indicator=list(face1.color_indicator),
            types=list(face1.card_types),
            supertypes=list(face1.supertypes),
            subtypes=list(face1.subtypes),
            power=face1.power,
            toughness=face1.toughness,
            loyalty=face1.loyalty,
            defense=face1.defense,
        )

        # ------------------------------------------------------------
        # 2. Faces
        # ------------------------------------------------------------
        faces = []
        for f in axis1_card.faces:
            special_actions = []
            # Ninjutsu
            ninjutsu = parse_ninjutsu(f.oracle_text or "")
            if ninjutsu:
                special_actions.append(ninjutsu)

            activated = []
            for a in f.activated_abilities:
                costs = [parse_cost(c) for c in a.cost_parts]
                tap_cost = parse_tap_cost(a.cost) 
                if tap_cost: 
                    costs.append(tap_cost)
                effects = parse_effect_text(a.effect)
                targeting = parse_targeting(a.effect)
                activated.append(
                    ActivatedAbility(
                        costs=costs,
                        effects=effects,
                        conditions=a.activation_conditions,
                        targeting=targeting,
                        timing="instant",  # refine later
                    )
                )

            triggered = []
            for t in f.triggered_abilities:
                effects = parse_effect_text(t.effect)
                targeting = parse_targeting(t.effect)
                trigger_filter = parse_trigger_filter(t.condition)

                triggered_ability = TriggeredAbility(
                    event=t.event_hint,
                    condition_text=t.condition,
                    effects=effects,
                    targeting=None,
                    trigger_filter=trigger_filter,
                )
                triggered.append(triggered_ability)


            static_effects = parse_static_effects(f)
            mode_choice, modes = parse_modes(f.oracle_text or "")

            sentences = split_into_sentences(f.oracle_text or "")

            replacement_effects = []
            continuous_effects = []

            for s in sentences:
                replacement_effects.extend(parse_replacement_effects(s))
                continuous_effects.extend(parse_continuous_effects(s))

            faces.append(
                Axis2Face(
                    name=f.name,
                    mana_cost=parse_mana_cost(f.mana_cost),
                    mana_value=f.mana_value,
                    colors=list(f.colors),
                    types=list(f.card_types),
                    supertypes=list(f.supertypes),
                    subtypes=list(f.subtypes),
                    power=f.power,
                    toughness=f.toughness,
                    loyalty=f.loyalty,
                    defense=f.defense,
                    special_actions=special_actions,
                    activated_abilities=activated,
                    triggered_abilities=triggered,
                    static_effects=static_effects,
                    replacement_effects=replacement_effects,
                    continuous_effects=continuous_effects,
                    modes=modes,
                )
            )

        # ------------------------------------------------------------
        # 3. Keywords (simple extraction)
        # ------------------------------------------------------------
        keywords = list(face1.keywords) + extract_keywords(face1.oracle_text or "")

        # ------------------------------------------------------------
        # 4. Build Axis2Card
        # ------------------------------------------------------------
        return Axis2Card(
            card_id=axis1_card.card_id,
            oracle_id=axis1_card.oracle_id,
            set=axis1_card.set,
            collector_number=axis1_card.collector_number,
            faces=faces,
            characteristics=characteristics,
            keywords=keywords,
        )
