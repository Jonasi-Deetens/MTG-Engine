from axis1.schema import Axis1Card, Axis1Face, Axis1ActivatedAbility, Axis1TriggeredAbility
from axis2.schema import (
    Axis2Card, Axis2Face, Axis2Characteristics,
    ManaCost, TapCost, SacrificeCost, LoyaltyCost,
    DealDamageEffect, DrawCardsEffect, AddManaEffect, CreateTokenEffect,
    ActivatedAbility, TriggeredAbility, StaticEffect, Mode,
    SymbolicValue, TargetingRules, TargetingRestriction,
    ReplacementEffect, ContinuousEffect, TapCost, DraftFromSpellbookEffect,
    ParseContext
)
from axis2.expanding.keyword_expansion import expand_treasure_keyword
from axis2.parsing.mana import parse_mana_cost
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
from axis2.parsing.triggers import parse_trigger_event
from axis2.parsing.activated import parse_activated_abilities
from axis2.helpers import cleaned_oracle_text

class Axis2Builder:

    @staticmethod
    def build(axis1_card: Axis1Card) -> Axis2Card:
        face1: Axis1Face = axis1_card.faces[0]
        print(f"Building Axis2Card: {axis1_card.names[0]}")
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
            ctx = ParseContext(
                card_name=axis1_card.names[0],
                primary_type=f.card_types[0].lower(),
                face_name=f.name,
                face_types=[t.lower() for t in f.card_types],
            )

            special_actions = []
            # Ninjutsu
            ninjutsu = parse_ninjutsu(f.oracle_text or "")
            if ninjutsu:
                special_actions.append(ninjutsu)

            activated = parse_activated_abilities(f, ctx)
            print(f"Triggered abilities: {f.triggered_abilities}")
            triggered = []
            for t in f.triggered_abilities:
                # 1. Recompute the trigger event (don’t trust Axis1)
                event = parse_trigger_event(t.condition)
                # 2. Parse effects (multi-sentence)
                # If Axis1 failed to extract the effect text, reconstruct it from the oracle text
                if not t.effect:
                    cond = t.condition.lower().rstrip(".").rstrip(",")
                    for sentence in split_into_sentences(f.oracle_text or ""):
                        s = sentence.lower().lstrip().rstrip()
                        s_clean = s.rstrip(".").rstrip(",")
                        if s_clean.startswith(cond):
                            parts = sentence.split(",", 1)
                            if len(parts) == 2:
                                t.effect = parts[1].strip()

                effects = parse_effect_text(t.effect, ctx)
                # 3. Targeting
                targeting = parse_targeting(t.effect)
                # 4. Trigger filter
                trigger_filter = parse_trigger_filter(t.condition)

                triggered_ability = TriggeredAbility(
                    event=event,
                    condition_text=t.condition,
                    effects=effects,
                    targeting=targeting,
                    trigger_filter=trigger_filter,
                )
                triggered.append(triggered_ability)

            static_effects = parse_static_effects(f)
            mode_choice, modes = parse_modes(f.oracle_text or "")

            clean_text = cleaned_oracle_text(f)
            sentences = split_into_sentences(clean_text)

            replacement_effects = []
            continuous_effects = []

            for s in sentences:
                replacement_effects.extend(parse_replacement_effects(s))

                # Use the generic effect parser for everything else
                for eff in parse_effect_text(s, ctx):
                    if isinstance(eff, ContinuousEffect):
                        continuous_effects.append(eff)
                    # you can later route other spell effects somewhere else if you want

            face = Axis2Face(
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
            expand_treasure_keyword(face)
            faces.append(face)

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
