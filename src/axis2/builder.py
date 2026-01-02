# axis2/builder.py

from __future__ import annotations
from typing import Optional
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
from axis2.parsing.delayed_triggers import (
    has_until_leaves_clause,
    build_linked_return_trigger,
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
from axis2.parsing.special_actions import parse_ninjutsu, parse_repeatable_payment
from axis2.parsing.costs import parse_escape_cost
from axis2.parsing.casting_costs import parse_all_casting_costs
from axis2.parsing.keywords import extract_keywords
from axis2.parsing.sentences import split_into_sentences
from axis2.parsing.triggers import parse_trigger_event
from axis2.parsing.activated import parse_activated_abilities
from axis2.helpers import cleaned_oracle_text
from axis2.parsing.text_extraction import get_remaining_text_for_parsing
from axis2.parsing.mana_abilities import mark_mana_abilities


def _extract_characteristics(axis1_card: Axis1Card, face1: Axis1Face) -> Axis2Characteristics:
    """Phase 1: Extract characteristics from Axis1."""
    return Axis2Characteristics(
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


def _create_context(axis1_card: Axis1Card, face: Axis1Face) -> ParseContext:
    """Create ParseContext for a face."""
    clean_card_types = [t for t in face.card_types if t not in face.supertypes]
    return ParseContext(
        card_name=axis1_card.names[0],
        primary_type=clean_card_types[0].lower() if clean_card_types else "unknown",
        face_name=face.name,
        face_types=[t.lower() for t in face.card_types],
    )


def _parse_axis1_activated(face: Axis1Face, ctx: ParseContext) -> list[ActivatedAbility]:
    """Parse activated abilities from Axis1 structured data."""
    return parse_activated_abilities(face, ctx)


def _parse_axis1_triggered(face: Axis1Face, ctx: ParseContext) -> list[TriggeredAbility]:
    """Parse triggered abilities from Axis1 structured data."""
    triggered = []
    for t in face.triggered_abilities:
        event = parse_trigger_event(t.condition)

        # Fallback: extract effect from oracle text if Axis1 didn't provide it
        if not t.effect:
            cond = t.condition.lower().rstrip(".").rstrip(",")
            for sentence in split_into_sentences(face.oracle_text or ""):
                s = sentence.lower().lstrip().rstrip()
                s_clean = s.rstrip(".").rstrip(",")
                if s_clean.startswith(cond):
                    parts = sentence.split(",", 1)
                    if len(parts) == 2:
                        t.effect = parts[1].strip()

        # Create context for triggered ability parsing
        triggered_ctx = ParseContext(
            card_name=ctx.card_name,
            primary_type=ctx.primary_type,
            face_name=ctx.face_name,
            face_types=ctx.face_types,
            is_triggered_ability=True,
        )
        effects = parse_effect_text(t.effect, triggered_ctx)
        targeting = parse_targeting(t.effect)
        trigger_filter = parse_trigger_filter(t.condition)

        triggered_ability = TriggeredAbility(
            event=event,
            condition_text=t.condition,
            effects=effects,
            targeting=targeting,
            trigger_filter=trigger_filter,
        )
        triggered.append(triggered_ability)

        # Synthesize delayed triggers like "until this creature leaves the battlefield"
        if has_until_leaves_clause(t.effect or ""):
            delayed = build_linked_return_trigger(triggered_ability)
            if delayed is not None:
                triggered.append(delayed)
    
    return triggered


def _parse_special_actions(face: Axis1Face, ctx: ParseContext) -> list:
    """Parse special actions (Ninjutsu, repeatable payment, etc.)."""
    special_actions = []
    
    # Ninjutsu
    ninjutsu = parse_ninjutsu(face.oracle_text or "")
    if ninjutsu:
        special_actions.append(ninjutsu)

    # Repeatable payment (Adversary cycle)
    repeatable = parse_repeatable_payment(face.oracle_text or "", ctx)
    if repeatable:
        special_actions.append(repeatable)
    
    return special_actions


def _parse_static_abilities(face: Axis1Face, ctx: ParseContext) -> list[StaticEffect]:
    """Parse static abilities (they create continuous effects)."""
    # Create context for static ability parsing
    static_ctx = ParseContext(
        card_name=ctx.card_name,
        primary_type=ctx.primary_type,
        face_name=ctx.face_name,
        face_types=ctx.face_types,
        is_static_ability=True,
    )
    static_effects = parse_static_effects(face, static_ctx)
    return static_effects


def _parse_replacement_effects_from_text(text: str, ctx: ParseContext) -> list[ReplacementEffect]:
    """Parse replacement effects from remaining text."""
    replacement_effects = []
    for sentence in split_into_sentences(text):
        replacement_effects.extend(parse_replacement_effects(sentence))
    return replacement_effects


def _parse_continuous_effects(text: str, ctx: ParseContext, is_permanent: bool) -> list[ContinuousEffect]:
    """Parse continuous effects from remaining text."""
    continuous_effects = []
    if is_permanent:
        for sentence in split_into_sentences(text):
            continuous_effects.extend(parse_continuous_effects(sentence, ctx))
    return continuous_effects


def _parse_spell_effects(text: str, ctx: ParseContext, is_spell: bool) -> tuple[list, Optional[TargetingRules]]:
    """Parse spell effects for instants/sorceries."""
    spell_effects = []
    spell_targeting = None
    
    if is_spell:
        # Create context for spell text parsing
        spell_ctx = ParseContext(
            card_name=ctx.card_name,
            primary_type=ctx.primary_type,
            face_name=ctx.face_name,
            face_types=ctx.face_types,
            is_spell_text=True,
        )
        for sentence in split_into_sentences(text):
            for eff in parse_effect_text(sentence, spell_ctx):
                if isinstance(eff, ContinuousEffect):
                    # Spell-based continuous effects (e.g., "gets +3/+3 until end of turn")
                    # These will be added to continuous_effects separately
                    pass
                else:
                    # One-shot spell effects
                    spell_effects.append(eff)
            
            # Parse targeting for spells (only need to do this once)
            if spell_targeting is None:
                spell_targeting = parse_targeting(sentence)
    
    return spell_effects, spell_targeting


def _parse_face(face: Axis1Face, ctx: ParseContext) -> Axis2Face:
    """
    Parse face in correct dependency order:
    1. Structured data from Axis1 (activated, triggered abilities)
    2. Special actions (Ninjutsu, etc.)
    3. Static abilities (they create continuous effects)
    4. Get remaining text (after removing parsed abilities)
    5. Replacement effects (must be parsed before continuous effects)
    6. Continuous effects (from static abilities and spells)
    7. Spell effects (for instants/sorceries)
    8. Modes (modal spells)
    """
    activated = _parse_axis1_activated(face, ctx)
    triggered = _parse_axis1_triggered(face, ctx)
    
    mark_mana_abilities(activated)
    
    special_actions = _parse_special_actions(face, ctx)
    
    static_effects = _parse_static_abilities(face, ctx)
    
    remaining_text = get_remaining_text_for_parsing(face, activated, triggered)
    
    replacement_effects = _parse_replacement_effects_from_text(remaining_text, ctx)
    
    types_lower = [t.lower() for t in face.card_types]
    is_spell = "instant" in types_lower or "sorcery" in types_lower
    is_permanent = any(t in types_lower for t in ["enchantment", "artifact", "creature", "planeswalker", "land"])
    
    continuous_effects = _parse_continuous_effects(remaining_text, ctx, is_permanent)
    
    spell_effects, spell_targeting = _parse_spell_effects(remaining_text, ctx, is_spell)
    
    if is_spell:
        spell_ctx = ParseContext(
            card_name=ctx.card_name,
            primary_type=ctx.primary_type,
            face_name=ctx.face_name,
            face_types=ctx.face_types,
            is_spell_text=True,
        )
        for sentence in split_into_sentences(remaining_text):
            for eff in parse_effect_text(sentence, spell_ctx):
                if isinstance(eff, ContinuousEffect):
                    continuous_effects.append(eff)
    
    mode_choice, modes = parse_modes(face.oracle_text or "", ctx)
    
    return Axis2Face(
        name=face.name,
        mana_cost=parse_mana_cost(face.mana_cost),
        mana_value=face.mana_value,
        colors=list(face.colors),
        types=list(face.card_types),
        supertypes=list(face.supertypes),
        subtypes=list(face.subtypes),
        power=face.power,
        toughness=face.toughness,
        loyalty=face.loyalty,
        defense=face.defense,
        special_actions=special_actions,
        activated_abilities=activated,
        triggered_abilities=triggered,
        static_effects=static_effects,
        replacement_effects=replacement_effects,
        continuous_effects=continuous_effects,
        modes=modes,
        spell_effects=spell_effects,
        spell_targeting=spell_targeting,
    )


def _expand_keywords(faces: list[Axis2Face]) -> None:
    """Phase 3a: Expand keywords (e.g., Treasure)."""
    for face in faces:
        expand_treasure_keyword(face)


def _add_special_casting_costs(axis1_card: Axis1Card, faces: list[Axis2Face]) -> None:
    """Phase 3b: Add special casting costs (Escape, Flashback, Overload, etc.)."""
    keywords = extract_keywords(axis1_card.faces[0].oracle_text or "")
    
    for f, face in zip(axis1_card.faces, faces):
        ctx = _create_context(axis1_card, f)
        oracle_text = f.oracle_text or ""
        
        # Parse Escape (legacy, keyword-based)
        if "escape" in (kw.lower() for kw in keywords):
            escape_cost = parse_escape_cost(oracle_text)
            if escape_cost:
                face.casting_options.append(escape_cost)
        
        # Parse all other special casting costs
        special_costs = parse_all_casting_costs(oracle_text, ctx)
        face.casting_options.extend(special_costs)


class Axis2Builder:

    @staticmethod
    def build(axis1_card: Axis1Card) -> Axis2Card:
        face1: Axis1Face = axis1_card.faces[0]
        print(f"Building Axis2Card: {axis1_card.names[0]}")
        
        characteristics = _extract_characteristics(axis1_card, face1)

        faces = []
        for f in axis1_card.faces:
            ctx = _create_context(axis1_card, f)
            face = _parse_face(f, ctx)
            faces.append(face)

        _expand_keywords(faces)
        _add_special_casting_costs(axis1_card, faces)

        keywords = list(face1.keywords) + extract_keywords(face1.oracle_text or "")

        return Axis2Card(
            card_id=axis1_card.card_id,
            oracle_id=axis1_card.oracle_id,
            set=axis1_card.set,
            collector_number=axis1_card.collector_number,
            faces=faces,
            characteristics=characteristics,
            keywords=keywords,
        )
