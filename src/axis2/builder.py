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
    ParseContext, Effect
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


def _detect_equip_abilities_from_text(oracle_text: str, ctx: ParseContext) -> list[ActivatedAbility]:
    """
    Fallback: Detect Equip abilities directly from oracle text.
    Used when Axis1 doesn't extract them.
    """
    import re
    from axis2.parsing.costs import parse_cost_string
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.parsing.targeting import parse_targeting
    from axis2.schema import ActivatedAbility
    
    equip_abilities = []
    
    if not oracle_text:
        return equip_abilities
    
    # Pattern: "Equip {2}" or "Equip {1}{R}"
    equip_pattern = re.compile(r"equip\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
    
    for line in oracle_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        m = equip_pattern.match(line)
        if m:
            cost_text = m.group(1).strip()
            effect_text = "Attach this to target creature you control."
            
            # Parse cost
            costs = parse_cost_string(cost_text)
            
            # Parse effect
            effects = parse_effect_text(effect_text, ctx)
            targeting = parse_targeting(effect_text)
            
            # Equip is always sorcery timing
            equip_abilities.append(
                ActivatedAbility(
                    costs=costs,
                    effects=effects,
                    conditions=[{"type": "timing", "value": "sorcery_only"}],
                    targeting=targeting,
                    timing="sorcery",
                )
            )
    
    return equip_abilities


def _detect_triggered_abilities_from_text(oracle_text: str, ctx: ParseContext) -> list[TriggeredAbility]:
    """
    Fallback: Detect triggered abilities directly from oracle text.
    Used when Axis1 doesn't extract them (e.g., "enters" vs "enters the battlefield").
    """
    from axis2.parsing.sentences import split_into_sentences
    from axis2.parsing.triggers.dispatcher import parse_trigger_event
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.parsing.targeting import parse_targeting
    from axis2.parsing.trigger_filters import parse_trigger_filter
    from axis2.schema import TriggeredAbility
    
    triggered = []
    
    if not oracle_text:
        return triggered
    
    # Check each sentence for trigger patterns
    for sentence in split_into_sentences(oracle_text):
        sentence_lower = sentence.strip().lower()
        
        # Check if this sentence starts with a trigger word
        trigger_starters = ("when ", "whenever ", "at the beginning", "at the end")
        if not any(sentence_lower.startswith(starter) for starter in trigger_starters):
            continue
        
        # Try to split into condition and effect
        if "," in sentence:
            parts = sentence.split(",", 1)
            condition_text = parts[0].strip()
            effect_text = parts[1].strip()
        else:
            # No comma - might be a simple trigger without effect, or effect is in next sentence
            condition_text = sentence.strip()
            effect_text = ""
        
        # Parse the trigger event
        event = parse_trigger_event(condition_text)
        if event is None:
            # Not a recognized trigger pattern, skip
            continue
        
        # If no effect text, try to find it in the next sentence or look for common patterns
        if not effect_text:
            # For now, skip triggers without clear effect text
            # In the future, we could look ahead to the next sentence
            continue
        
        # Parse the effect
        triggered_ctx = ctx.with_flag("is_triggered_ability", True)
        effects = parse_effect_text(effect_text, triggered_ctx)
        
        if not effects:
            # Couldn't parse effects, skip this trigger
            continue
        
        # Parse targeting and trigger filter
        targeting = parse_targeting(effect_text)
        trigger_filter = parse_trigger_filter(condition_text)
        
        triggered_ability = TriggeredAbility(
            event=event,
            condition_text=condition_text,
            effects=effects,
            targeting=targeting,
            trigger_filter=trigger_filter,
        )
        triggered.append(triggered_ability)
    
    return triggered


def _parse_axis1_triggered(face: Axis1Face, ctx: ParseContext) -> list[TriggeredAbility]:
    """Parse triggered abilities from Axis1 structured data."""
    triggered = []
    for t in face.triggered_abilities:
        event = parse_trigger_event(t.condition)

        # Fallback: extract effect from oracle text if Axis1 didn't provide it
        if not t.effect:
            cond = t.condition.lower().rstrip(".").rstrip(",")
            # Also try matching without "this" prefix for old templating (e.g., "When Oblivion Ring leaves...")
            cond_variants = [cond]
            if "this " in cond:
                # Replace "this X" with card name for old templating
                card_name_lower = ctx.card_name.lower()
                cond_variants.append(cond.replace("this ", f"{card_name_lower} "))
                # Also try just the card name
                cond_variants.append(f"when {card_name_lower} leaves")
            # Also handle "enters" vs "enters the battlefield" variations
            if "enters" in cond and "enters the battlefield" not in cond:
                # Add variant with "enters the battlefield"
                cond_variants.append(cond.replace("enters", "enters the battlefield"))
            elif "enters the battlefield" in cond:
                # Add variant with just "enters"
                cond_variants.append(cond.replace("enters the battlefield", "enters"))
            
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"[LTB] Trying to extract effect for condition: {t.condition}")
            logger.debug(f"[LTB] Condition variants: {cond_variants}")
            
            for sentence in split_into_sentences(face.oracle_text or ""):
                s = sentence.lower().lstrip().rstrip()
                s_clean = s.rstrip(".").rstrip(",")
                # Try all variants
                for variant in cond_variants:
                    if s_clean.startswith(variant):
                        parts = sentence.split(",", 1)
                        if len(parts) == 2:
                            t.effect = parts[1].strip()
                            logger.debug(f"[LTB] Extracted effect from sentence: {sentence} -> {t.effect}")
                            break
                if t.effect:
                    break

        # Create context for triggered ability parsing
        triggered_ctx = ctx.with_flag("is_triggered_ability", True)
        # Ensure we have effect text - if still empty, try to extract from full oracle text
        effect_text = t.effect or ""
        
        # DEBUG: Print what we have
        if "leaves the battlefield" in t.condition.lower():
            print(f"[DEBUG LTB] Condition: '{t.condition}'")
            print(f"[DEBUG LTB] Initial effect_text from Axis1: '{effect_text}'")
            print(f"[DEBUG LTB] Full oracle text: '{face.oracle_text}'")
        
        if not effect_text and "leaves the battlefield" in t.condition.lower():
            # For LTB triggers, try to find the return effect in the oracle text
            # Look for patterns like "return the exiled card" or "return that card"
            print(f"[DEBUG LTB] Effect text empty, searching oracle text for return pattern")
            for sentence in split_into_sentences(face.oracle_text or ""):
                print(f"[DEBUG LTB] Checking sentence: '{sentence}'")
                if "return" in sentence.lower() and ("exiled" in sentence.lower() or "that card" in sentence.lower()):
                    # Check if this sentence is related to the LTB trigger
                    if "leaves" in sentence.lower() or any(variant in sentence.lower() for variant in ["when " + ctx.card_name.lower(), "when this"]):
                        effect_text = sentence
                        # Extract just the return part if it's a compound sentence
                        if "," in sentence and "return" in sentence:
                            parts = sentence.split(",", 1)
                            for part in parts:
                                if "return" in part.lower():
                                    effect_text = part.strip()
                                    break
                        print(f"[DEBUG LTB] Found return pattern in sentence: '{sentence}' -> extracted: '{effect_text}'")
                        break
        
        print(f"[DEBUG LTB] Final effect_text being parsed: '{effect_text}'")
        
        # Check for conditional clauses in the effect text
        from axis2.parsing.conditional_effects import parse_conditional
        conditional_effect = parse_conditional(effect_text, triggered_ctx)
        if conditional_effect:
            # Effect has a conditional clause, use it
            effects = [conditional_effect]
        else:
            # No conditional clause, parse as normal effects
            effects = parse_effect_text(effect_text, triggered_ctx)
        
        print(f"[DEBUG LTB] Parsed {len(effects)} effects: {effects}")
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
    static_ctx = ctx.with_flag("is_static_ability", True)
    static_effects = parse_static_effects(face, static_ctx)
    return static_effects


def _parse_replacement_effects_from_text(text: str, ctx: ParseContext, skip_duration_effects: bool = False) -> list[ReplacementEffect]:
    """
    Parse replacement effects from text.
    
    Args:
        text: Text to parse replacement effects from
        ctx: Parse context
        skip_duration_effects: If True, skip replacement effects with duration prefixes
            (e.g., "Until end of turn"). Use True when parsing from static text,
            False when parsing from activated/triggered ability text.
    """
    import re
    replacement_effects = []
    
    # Pattern to detect duration prefixes
    duration_prefix_pattern = re.compile(
        r"^(until\s+end\s+of\s+turn|this\s+turn|until\s+your\s+next\s+turn)[,\s]+",
        re.IGNORECASE
    )
    
    # Pattern to detect if text contains duration prefix anywhere
    duration_anywhere_pattern = re.compile(
        r"(until\s+end\s+of\s+turn|this\s+turn|until\s+your\s+next\s+turn)[,\s]+",
        re.IGNORECASE
    )
    
    # Check if the full text contains a duration prefix (for context tracking)
    full_text_has_duration = duration_anywhere_pattern.search(text) is not None
    
    for sentence in split_into_sentences(text):
        sentence_stripped = sentence.strip()
        
        # Skip replacement effects with duration prefixes when parsing from static text
        # These are temporary effects that should only come from activated/triggered abilities
        if skip_duration_effects:
            # Check if sentence starts with duration prefix
            if duration_prefix_pattern.match(sentence_stripped):
                continue
            
            # Also check if the sentence contains a duration prefix anywhere (defensive check)
            # This catches cases where sentence splitting might have separated the prefix
            if duration_anywhere_pattern.search(sentence_stripped):
                continue
            
            # CRITICAL: If the full text had a duration prefix but this sentence doesn't,
            # and this sentence looks like it could be part of a replacement effect with duration,
            # skip it. This handles cases where sentence splitting separated the duration from the effect.
            if full_text_has_duration and not duration_anywhere_pattern.search(sentence_stripped):
                # Check if this sentence looks like a replacement effect that would have duration
                # (contains "would" and "instead" - key markers of replacement effects)
                if "would" in sentence_stripped.lower() and "instead" in sentence_stripped.lower():
                    # This is likely part of a duration-prefixed replacement effect that was split
                    continue
        
        # Parse replacement effects from this sentence
        parsed_effects = parse_replacement_effects(sentence_stripped)
        
        # Additional safety check: if we're skipping duration effects and a parsed effect
        # has no duration but the original text had a duration prefix, skip it
        if skip_duration_effects and parsed_effects:
            # Check if original sentence had duration prefix
            has_duration_prefix = duration_anywhere_pattern.search(sentence_stripped)
            for effect in parsed_effects:
                # If effect has no duration but text had duration prefix, skip it
                if has_duration_prefix and not effect.duration:
                    continue
                # Also skip if full text had duration but effect doesn't (defensive)
                if full_text_has_duration and not effect.duration:
                    continue
                replacement_effects.append(effect)
        else:
            replacement_effects.extend(parsed_effects)
    
    return replacement_effects


def _parse_continuous_effects(text: str, ctx: ParseContext, is_permanent: bool) -> list[ContinuousEffect]:
    """Parse continuous effects from remaining text."""
    continuous_effects = []
    if is_permanent:
        for sentence in split_into_sentences(text):
            continuous_effects.extend(parse_continuous_effects(sentence, ctx))
    return continuous_effects


def _parse_spell_effects(text: str, ctx: ParseContext, is_spell: bool) -> tuple[list[Effect], Optional[TargetingRules], list[ContinuousEffect]]:
    """
    Parse spell effects for instants/sorceries.
    
    Returns:
        Tuple of (spell_effects, spell_targeting, continuous_effects)
        where continuous_effects are spell-based continuous effects
    """
    spell_effects: list[Effect] = []
    continuous_effects: list[ContinuousEffect] = []
    spell_targeting = None
    
    if is_spell:
        # Create context for spell text parsing
        spell_ctx = ctx.with_flag("is_spell_text", True)
        for sentence in split_into_sentences(text):
            for eff in parse_effect_text(sentence, spell_ctx):
                if isinstance(eff, ContinuousEffect):
                    # Spell-based continuous effects (e.g., "gets +3/+3 until end of turn")
                    continuous_effects.append(eff)
                else:
                    # One-shot spell effects
                    spell_effects.append(eff)
            
            # Parse targeting for spells (only need to do this once)
            if spell_targeting is None:
                spell_targeting = parse_targeting(sentence)
    
    return spell_effects, spell_targeting, continuous_effects


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
    
    # Fallback: detect triggered abilities from oracle text if Axis1 didn't extract them
    # This handles cases where Axis1 misses triggers (e.g., "enters" vs "enters the battlefield")
    # We check the full oracle text to catch any missed triggers
    detected_triggered = _detect_triggered_abilities_from_text(face.oracle_text or "", ctx)
    # Only add triggers that weren't already parsed by Axis1
    # Simple check: if condition_text doesn't match any existing trigger
    existing_conditions = {t.condition_text.lower() for t in triggered}
    for new_trigger in detected_triggered:
        if new_trigger.condition_text.lower() not in existing_conditions:
            triggered.append(new_trigger)
    
    # Fallback: detect Equip abilities from oracle text if Axis1 didn't extract them
    detected_equip = _detect_equip_abilities_from_text(face.oracle_text or "", ctx)
    # Add detected Equip abilities (they won't duplicate since Axis1 would have extracted them if present)
    if detected_equip:
        activated.extend(detected_equip)
    
    mark_mana_abilities(activated)
    
    special_actions = _parse_special_actions(face, ctx)
    
    static_effects = _parse_static_abilities(face, ctx)
    
    remaining_text = get_remaining_text_for_parsing(face, activated, triggered)
    
    # Parse replacement effects from static text (skip those with duration prefixes)
    # NOTE: Replacement effects from activated abilities are now attached directly to those abilities
    # in parse_activated_abilities, so we don't parse them here anymore
    replacement_effects = _parse_replacement_effects_from_text(remaining_text, ctx, skip_duration_effects=True)
    
    types_lower = [t.lower() for t in face.card_types]
    is_spell = "instant" in types_lower or "sorcery" in types_lower
    is_permanent = any(t in types_lower for t in ["enchantment", "artifact", "creature", "planeswalker", "land"])
    
    continuous_effects = _parse_continuous_effects(remaining_text, ctx, is_permanent)
    
    spell_effects, spell_targeting, spell_continuous_effects = _parse_spell_effects(remaining_text, ctx, is_spell)
    
    # Add spell-based continuous effects to continuous_effects
    continuous_effects.extend(spell_continuous_effects)
    
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

        card = Axis2Card(
            card_id=axis1_card.card_id,
            oracle_id=axis1_card.oracle_id,
            set=axis1_card.set,
            collector_number=axis1_card.collector_number,
            faces=faces,
            characteristics=characteristics,
            keywords=keywords,
        )
        
        # Validate the card before returning
        from axis2.validation import validate_axis2_card
        validation_errors = validate_axis2_card(card)
        if validation_errors:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Validation errors for card {card.card_id}: {validation_errors}")
            # Continue anyway - validation errors are warnings, not fatal
        
        return card
