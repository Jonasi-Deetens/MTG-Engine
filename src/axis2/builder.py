# axis2/builder.py

from __future__ import annotations
from typing import Optional
import re
from axis1.schema import Axis1Card, Axis1Face, Axis1ActivatedAbility, Axis1TriggeredAbility
from axis2.schema import (
    Axis2Card, Axis2Face, Axis2Characteristics,
    ManaCost, TapCost, SacrificeCost, LoyaltyCost,
    DealDamageEffect, DrawCardsEffect, AddManaEffect, CreateTokenEffect,
    ActivatedAbility, TriggeredAbility, StaticEffect, Mode,
    SymbolicValue, TargetingRules, TargetingRestriction,
    ReplacementEffect, ContinuousEffect, TapCost, DraftFromSpellbookEffect,
    ParseContext, Effect, EntersBattlefieldEvent
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
from axis2.parsing.ability_boundaries import detect_ability_boundaries, AbilityChunk
from axis2.parsing.ability_sentences import split_ability_into_sentences
from axis2.parsing.effect_chains import reconstruct_effect_chain


def _extract_characteristics(axis1_card: Axis1Card, face1: Axis1Face) -> Axis2Characteristics:
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
    clean_card_types = [t for t in face.card_types if t not in face.supertypes]
    return ParseContext(
        card_name=axis1_card.names[0],
        primary_type=clean_card_types[0].lower() if clean_card_types else "unknown",
        face_name=face.name,
        face_types=[t.lower() for t in face.card_types],
    )


def _parse_axis1_activated(face: Axis1Face, ctx: ParseContext) -> list[ActivatedAbility]:
    return parse_activated_abilities(face, ctx)


def _detect_equip_abilities_from_text(oracle_text: str, ctx: ParseContext) -> list[ActivatedAbility]:
    import re
    from axis2.parsing.costs import parse_cost_string
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.parsing.targeting import parse_targeting
    from axis2.schema import ActivatedAbility
    
    equip_abilities = []
    
    if not oracle_text:
        return equip_abilities
    
    equip_pattern = re.compile(r"equip\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
    
    for line in oracle_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        m = equip_pattern.match(line)
        if m:
            cost_text = m.group(1).strip()
            effect_text = "Attach this to target creature you control."
            
            costs = parse_cost_string(cost_text)
            effects = parse_effect_text(effect_text, ctx)
            targeting = parse_targeting(effect_text)
            
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


def _normalize_reminder_text(reminder_texts: list[str]) -> str:
    combined = " ".join(reminder_texts)
    if not combined:
        return ""
    combined = combined.strip()
    if combined.startswith("(") and combined.endswith(")"):
        combined = combined[1:-1].strip()
    return combined


def _parse_reminder_text_triggers(reminder_texts: list[str], ctx: ParseContext) -> list[TriggeredAbility]:
    from axis2.parsing.triggers.dispatcher import parse_trigger_event
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.parsing.targeting import parse_targeting
    from axis2.parsing.trigger_filters import parse_trigger_filter
    from axis2.schema import TriggeredAbility
    from axis2.parsing.sentences import split_into_sentences
    
    triggered = []
    combined_reminder = _normalize_reminder_text(reminder_texts)
    if not combined_reminder:
        return triggered
    
    trigger_starters = ("when ", "whenever ", "at the beginning", "at the end")
    
    for sentence in split_into_sentences(combined_reminder):
        sentence_lower = sentence.strip().lower()
        
        if not any(sentence_lower.startswith(starter) for starter in trigger_starters):
            continue
        
        if "," in sentence:
            parts = sentence.split(",", 1)
            condition_text = parts[0].strip()
            effect_text = parts[1].strip()
        else:
            condition_text = sentence.strip()
            effect_text = ""
        
        event = parse_trigger_event(condition_text)
        if event is None or not effect_text:
            continue
        
        # Normalize card names in trigger events to "self" or "this Aura"
        if isinstance(event, EntersBattlefieldEvent):
            if event.subject and event.subject.lower() == ctx.card_name.lower():
                # Card name matches - normalize to "self" or "this Aura" based on type
                if "aura" in ctx.primary_type.lower():
                    event.subject = "this Aura"
                elif "equipment" in ctx.primary_type.lower():
                    event.subject = "this Equipment"
                elif "creature" in ctx.primary_type.lower():
                    event.subject = "this creature"
                elif "enchantment" in ctx.primary_type.lower():
                    event.subject = "this enchantment"
                else:
                    event.subject = "self"
        
        triggered_ctx = ctx.with_flag("is_triggered_ability", True)
        effects = parse_effect_text(effect_text, triggered_ctx)
        
        if not effects:
            continue
        
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


def _parse_reminder_text_etb_effects(reminder_texts: list[str], ctx: ParseContext) -> list[ReplacementEffect]:
    import re
    from axis2.schema import ReplacementEffect, Subject
    
    replacement_effects = []
    combined_reminder = _normalize_reminder_text(reminder_texts)
    if not combined_reminder:
        return replacement_effects
    
    enters_with_counters_re = re.compile(
        r"(?:it\s+)?enters(?:\s+the\s+battlefield)?\s+with\s+(\w+)\s+(\w+)\s+counters?",
        re.IGNORECASE
    )
    
    m = enters_with_counters_re.search(combined_reminder)
    if m:
        amount_str = m.group(1)
        counter_type = m.group(2)
        
        word_to_num = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        if amount_str.lower() in word_to_num:
            amount = word_to_num[amount_str.lower()]
        else:
            try:
                amount = int(amount_str)
            except ValueError:
                amount = None
        
        if amount is not None:
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={
                    "counter_type": counter_type,
                    "amount": amount,
                    "condition": "cast_with_impending_cost"
                },
                zones=["battlefield"],
                text=f"enters with {amount} {counter_type} counters"
            )
            replacement_effects.append(replacement_effect)
    
    return replacement_effects


def _parse_reminder_text_replacement_effects(reminder_texts: list[str], ctx: ParseContext) -> list[ReplacementEffect]:
    from axis2.parsing.replacement_effects import parse_replacement_effects
    from axis2.parsing.sentences import split_into_sentences
    import logging
    
    logger = logging.getLogger(__name__)
    replacement_effects = []
    combined_reminder = _normalize_reminder_text(reminder_texts)
    
    logger.debug(f"[REPLACEMENT] Parsing reminder text replacement effects: {combined_reminder[:200]}")
    
    if not combined_reminder:
        return replacement_effects
    
    for sentence in split_into_sentences(combined_reminder):
        logger.debug(f"[REPLACEMENT] Processing reminder sentence: {sentence[:100]}")
        parsed_effects = parse_replacement_effects(sentence)
        logger.debug(f"[REPLACEMENT] Parsed {len(parsed_effects)} effects from reminder sentence")
        replacement_effects.extend(parsed_effects)
    
    logger.debug(f"[REPLACEMENT] Total reminder replacement effects: {len(replacement_effects)}")
    return replacement_effects


def _detect_triggered_abilities_from_text(oracle_text: str, ctx: ParseContext) -> list[TriggeredAbility]:
    from axis2.parsing.sentences import split_into_sentences
    from axis2.parsing.triggers.dispatcher import parse_trigger_event
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.parsing.targeting import parse_targeting
    from axis2.parsing.trigger_filters import parse_trigger_filter
    from axis2.schema import TriggeredAbility
    
    triggered = []
    
    if not oracle_text:
        return triggered
    
    trigger_starters = ("when ", "whenever ", "at the beginning", "at the end")
    
    for sentence in split_into_sentences(oracle_text):
        sentence_lower = sentence.strip().lower()
        
        if not any(sentence_lower.startswith(starter) for starter in trigger_starters):
            continue
        
        if "," in sentence:
            parts = sentence.split(",", 1)
            condition_text = parts[0].strip()
            effect_text = parts[1].strip()
        else:
            condition_text = sentence.strip()
            effect_text = ""
        
        event = parse_trigger_event(condition_text)
        if event is None or not effect_text:
            continue
        
        # Normalize card names in trigger events to "self" or "this Aura"
        if isinstance(event, EntersBattlefieldEvent):
            if event.subject and event.subject.lower() == ctx.card_name.lower():
                # Card name matches - normalize to "self" or "this Aura" based on type
                if "aura" in ctx.primary_type.lower():
                    event.subject = "this Aura"
                elif "equipment" in ctx.primary_type.lower():
                    event.subject = "this Equipment"
                elif "creature" in ctx.primary_type.lower():
                    event.subject = "this creature"
                elif "enchantment" in ctx.primary_type.lower():
                    event.subject = "this enchantment"
                else:
                    event.subject = "self"
        
        triggered_ctx = ctx.with_flag("is_triggered_ability", True)
        effects = parse_effect_text(effect_text, triggered_ctx)
        
        if not effects:
            continue
        
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


def _extract_effect_text_from_oracle(face: Axis1Face, condition: str, ctx: ParseContext) -> str:
    from axis2.parsing.sentences import split_into_sentences
    import logging
    
    logger = logging.getLogger(__name__)
    cond = condition.lower().rstrip(".").rstrip(",")
    cond_variants = [cond]
    
    if "this " in cond:
        card_name_lower = ctx.card_name.lower()
        cond_variants.append(cond.replace("this ", f"{card_name_lower} "))
        cond_variants.append(f"when {card_name_lower} leaves")
    
    if "enters" in cond and "enters the battlefield" not in cond:
        cond_variants.append(cond.replace("enters", "enters the battlefield"))
    elif "enters the battlefield" in cond:
        cond_variants.append(cond.replace("enters the battlefield", "enters"))
    
    logger.debug(f"[LTB] Trying to extract effect for condition: {condition}")
    logger.debug(f"[LTB] Condition variants: {cond_variants}")
    
    for sentence in split_into_sentences(face.oracle_text or ""):
        s = sentence.lower().lstrip().rstrip()
        s_clean = s.rstrip(".").rstrip(",")
        for variant in cond_variants:
            if s_clean.startswith(variant):
                parts = sentence.split(",", 1)
                if len(parts) == 2:
                    effect_text = parts[1].strip()
                    logger.debug(f"[LTB] Extracted effect from sentence: {sentence} -> {effect_text}")
                    return effect_text
    return ""


def _find_return_effect_in_text(face: Axis1Face, ctx: ParseContext) -> str:
    from axis2.parsing.sentences import split_into_sentences
    
    print(f"[DEBUG LTB] Effect text empty, searching oracle text for return pattern")
    for sentence in split_into_sentences(face.oracle_text or ""):
        print(f"[DEBUG LTB] Checking sentence: '{sentence}'")
        if "return" in sentence.lower() and ("exiled" in sentence.lower() or "that card" in sentence.lower()):
            if "leaves" in sentence.lower() or any(variant in sentence.lower() for variant in ["when " + ctx.card_name.lower(), "when this"]):
                effect_text = sentence
                if "," in sentence and "return" in sentence:
                    parts = sentence.split(",", 1)
                    for part in parts:
                        if "return" in part.lower():
                            effect_text = part.strip()
                            break
                print(f"[DEBUG LTB] Found return pattern in sentence: '{sentence}' -> extracted: '{effect_text}'")
                return effect_text
    return ""


def _split_trigger_condition(condition: str, ctx: ParseContext) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    from axis2.parsing.triggers.dispatcher import parse_trigger_event
    
    if " or " not in condition.lower():
        return None, None, None, None
    
    parts = [p.strip() for p in condition.split(" or ", 1)]
    if len(parts) != 2:
        return None, None, None, None
    
    first_part = parts[0]
    second_part = parts[1]
    
    if not second_part.lower().startswith(("when ", "whenever ")):
        first_words = first_part.split()
        prefix_words = []
        for word in first_words:
            if word.lower() in ("enters", "attacks", "dies", "leaves"):
                break
            prefix_words.append(word)
        if prefix_words:
            prefix = " ".join(prefix_words)
            second_part = f"{prefix} {second_part}"
    
    event1 = parse_trigger_event(first_part)
    event2 = parse_trigger_event(second_part)
    
    if event1 and event2:
        return first_part, second_part, event1, event2
    
    return None, None, None, None


def _parse_axis1_triggered(face: Axis1Face, ctx: ParseContext) -> list[TriggeredAbility]:
    from axis2.parsing.conditional_effects import parse_conditional
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.parsing.targeting import parse_targeting
    from axis2.parsing.trigger_filters import parse_trigger_filter
    from axis2.parsing.triggers.dispatcher import parse_trigger_event
    from axis2.parsing.sentences import split_into_sentences
    
    triggered = []
    for t in face.triggered_abilities:
        effect_text = t.effect or ""
        was_split = False
        
        if not effect_text:
            effect_text = _extract_effect_text_from_oracle(face, t.condition, ctx)
        
        first_part, second_part, event1, event2 = _split_trigger_condition(t.condition, ctx)
        
        if first_part and second_part and event1 and event2:
            triggered_ctx = ctx.with_flag("is_triggered_ability", True)
            conditional_effect = parse_conditional(effect_text, triggered_ctx)
            effects = [conditional_effect] if conditional_effect else parse_effect_text(effect_text, triggered_ctx)
            targeting = parse_targeting(effect_text)
            
            trigger_filter1 = parse_trigger_filter(first_part)
            triggered.append(TriggeredAbility(
                event=event1,
                condition_text=first_part,
                effects=effects,
                targeting=targeting,
                trigger_filter=trigger_filter1,
            ))
            
            trigger_filter2 = parse_trigger_filter(second_part)
            triggered.append(TriggeredAbility(
                event=event2,
                condition_text=second_part,
                effects=effects,
                targeting=targeting,
                trigger_filter=trigger_filter2,
            ))
            
            was_split = True
            continue
        
        if was_split:
            continue
        
        event = parse_trigger_event(t.condition)
        
        # Normalize card names in trigger events to "self" or "this Aura"
        if event and isinstance(event, EntersBattlefieldEvent):
            if event.subject and event.subject.lower() == ctx.card_name.lower():
                # Card name matches - normalize to "self" or "this Aura" based on type
                if "aura" in ctx.primary_type.lower():
                    event.subject = "this Aura"
                elif "equipment" in ctx.primary_type.lower():
                    event.subject = "this Equipment"
                elif "creature" in ctx.primary_type.lower():
                    event.subject = "this creature"
                elif "enchantment" in ctx.primary_type.lower():
                    event.subject = "this enchantment"
                else:
                    event.subject = "self"
        
        if not effect_text:
            effect_text = t.effect or ""
        
        triggered_ctx = ctx.with_flag("is_triggered_ability", True)
        
        if "leaves the battlefield" in t.condition.lower():
            print(f"[DEBUG LTB] Condition: '{t.condition}'")
            print(f"[DEBUG LTB] Initial effect_text from Axis1: '{effect_text}'")
            print(f"[DEBUG LTB] Full oracle text: '{face.oracle_text}'")
        
        if not effect_text and "leaves the battlefield" in t.condition.lower():
            effect_text = _find_return_effect_in_text(face, ctx)
        
        print(f"[DEBUG LTB] Final effect_text being parsed: '{effect_text}'")
        
        conditional_effect = parse_conditional(effect_text, triggered_ctx)
        effects = [conditional_effect] if conditional_effect else parse_effect_text(effect_text, triggered_ctx)
        
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

        if has_until_leaves_clause(t.effect or ""):
            delayed = build_linked_return_trigger(triggered_ability)
            if delayed is not None:
                triggered.append(delayed)
    
    return triggered


def _parse_special_actions(face: Axis1Face, ctx: ParseContext) -> list:
    special_actions = []
    
    ninjutsu = parse_ninjutsu(face.oracle_text or "")
    if ninjutsu:
        special_actions.append(ninjutsu)

    repeatable = parse_repeatable_payment(face.oracle_text or "", ctx)
    if repeatable:
        special_actions.append(repeatable)
    
    return special_actions


def _parse_static_abilities(face: Axis1Face, ctx: ParseContext) -> list[StaticEffect]:
    static_ctx = ctx.with_flag("is_static_ability", True)
    static_effects = parse_static_effects(face, static_ctx)
    return static_effects


def _parse_replacement_effects_from_text(text: str, ctx: ParseContext, skip_duration_effects: bool = False) -> list[ReplacementEffect]:
    import re
    import logging
    logger = logging.getLogger(__name__)
    
    replacement_effects = []
    
    logger.debug(f"[REPLACEMENT] Parsing replacement effects from text (skip_duration={skip_duration_effects}): {text[:200]}")
    
    duration_prefix_pattern = re.compile(
        r"^(until\s+end\s+of\s+turn|this\s+turn|until\s+your\s+next\s+turn)[,\s]+",
        re.IGNORECASE
    )
    
    duration_anywhere_pattern = re.compile(
        r"(until\s+end\s+of\s+turn|this\s+turn|until\s+your\s+next\s+turn)[,\s]+",
        re.IGNORECASE
    )
    
    full_text_has_duration = duration_anywhere_pattern.search(text) is not None
    
    for sentence in split_into_sentences(text):
        sentence_stripped = sentence.strip()
        logger.debug(f"[REPLACEMENT] Processing sentence: {sentence_stripped[:100]}")
        
        if skip_duration_effects:
            if duration_prefix_pattern.match(sentence_stripped):
                logger.debug(f"[REPLACEMENT] Skipping sentence with duration prefix: {sentence_stripped[:50]}")
                continue
            
            if duration_anywhere_pattern.search(sentence_stripped):
                logger.debug(f"[REPLACEMENT] Skipping sentence with duration: {sentence_stripped[:50]}")
                continue
            
            if full_text_has_duration and not duration_anywhere_pattern.search(sentence_stripped):
                if "would" in sentence_stripped.lower() and "instead" in sentence_stripped.lower():
                    logger.debug(f"[REPLACEMENT] Skipping 'would...instead' sentence in duration context: {sentence_stripped[:50]}")
                    continue
        
        parsed_effects = parse_replacement_effects(sentence_stripped)
        logger.debug(f"[REPLACEMENT] Parsed {len(parsed_effects)} effects from sentence: {sentence_stripped[:50]}")
        
        if skip_duration_effects and parsed_effects:
            has_duration_prefix = duration_anywhere_pattern.search(sentence_stripped)
            for effect in parsed_effects:
                if has_duration_prefix and not effect.duration:
                    logger.debug(f"[REPLACEMENT] Skipping effect without duration: {effect.kind}")
                    continue
                if full_text_has_duration and not effect.duration:
                    logger.debug(f"[REPLACEMENT] Skipping effect without duration (full text has duration): {effect.kind}")
                    continue
                replacement_effects.append(effect)
                logger.debug(f"[REPLACEMENT] Added effect: {effect.kind}")
        else:
            replacement_effects.extend(parsed_effects)
            logger.debug(f"[REPLACEMENT] Added {len(parsed_effects)} effects")
    
    logger.debug(f"[REPLACEMENT] Total replacement effects parsed: {len(replacement_effects)}")
    return replacement_effects


def _build_triggered_ability(chunk: AbilityChunk, effects: list[Effect], ctx: ParseContext) -> Optional[TriggeredAbility]:
    """Build TriggeredAbility from chunk and effects."""
    from axis2.parsing.triggers.dispatcher import parse_trigger_event
    from axis2.parsing.targeting import parse_targeting
    from axis2.parsing.trigger_filters import parse_trigger_filter
    
    # Extract condition from start_marker (e.g., "When X enters...")
    # The start_marker should contain the trigger condition
    condition_text = chunk.start_marker
    
    # Try to split on comma to get condition and effect
    if "," in condition_text:
        parts = condition_text.split(",", 1)
        condition_text = parts[0].strip()
        # Effect text is already parsed into effects
    
    event = parse_trigger_event(condition_text)
    if event is None:
        return None
    
    # Normalize card names in trigger events
    if isinstance(event, EntersBattlefieldEvent):
        if event.subject and event.subject.lower() == ctx.card_name.lower():
            if "aura" in ctx.primary_type.lower():
                event.subject = "this Aura"
            elif "equipment" in ctx.primary_type.lower():
                event.subject = "this Equipment"
            elif "creature" in ctx.primary_type.lower():
                event.subject = "this creature"
            elif "enchantment" in ctx.primary_type.lower():
                event.subject = "this enchantment"
            else:
                event.subject = "self"
    
    targeting = parse_targeting(chunk.text)
    trigger_filter = parse_trigger_filter(condition_text)
    
    return TriggeredAbility(
        event=event,
        condition_text=condition_text,
        effects=effects,
        targeting=targeting,
        trigger_filter=trigger_filter,
    )


def _build_activated_ability(chunk: AbilityChunk, effects: list[Effect], ctx: ParseContext) -> Optional[ActivatedAbility]:
    """Build ActivatedAbility from chunk and effects (extract cost from chunk.start_marker)."""
    from axis2.parsing.costs import parse_cost_string
    from axis2.parsing.targeting import parse_targeting
    from axis2.parsing.activated import split_full_ability
    
    # Extract cost from start_marker (e.g., "{T}: Draw a card")
    # The start_marker should be "COST: EFFECT"
    cost_text, effect_text = split_full_ability(chunk.start_marker)
    
    if not cost_text:
        # Try to extract from chunk text
        if ":" in chunk.text:
            parts = chunk.text.split(":", 1)
            cost_text = parts[0].strip()
    
    if not cost_text:
        return None
    
    costs = parse_cost_string(cost_text)
    targeting = parse_targeting(chunk.text)
    
    # Filter out any ContinuousEffects that incorrectly contain the cost in their text field
    # This prevents duplicates where the effect text was parsed from text that included the cost
    # With the fix in split_ability_into_sentences(), this shouldn't happen, but it's a safeguard
    filtered_effects = []
    for effect in effects:
        if isinstance(effect, ContinuousEffect):
            # Check if effect text contains the cost (indicates it was parsed from full ability text)
            effect_text_lower = effect.text.lower().strip()
            cost_text_lower = cost_text.lower().strip()
            
            # If effect text starts with or contains the cost, it was incorrectly parsed
            if effect_text_lower.startswith(cost_text_lower) or \
               (":" in effect_text_lower and effect_text_lower.startswith(("{", "tap", "sacrifice", "discard", "pay"))):
                # This effect contains the cost - skip it to prevent duplicate
                continue
        filtered_effects.append(effect)
    
    # If we filtered out all effects, use the original effects (better to have something than nothing)
    if not filtered_effects and effects:
        filtered_effects = effects
    
    # Determine timing (default to instant, check for sorcery)
    timing = "instant"
    if "sorcery" in chunk.text.lower() or "only as a sorcery" in chunk.text.lower():
        timing = "sorcery"
    
    return ActivatedAbility(
        costs=costs,
        effects=filtered_effects,
        conditions=[],
        targeting=targeting,
        timing=timing,
    )


def _build_static_effects(chunk: AbilityChunk, effects: list[Effect], ctx: ParseContext) -> list[StaticEffect]:
    """Build StaticEffect list from chunk and effects."""
    # Static effects are already parsed as ContinuousEffect or other Effect types
    # We need to convert them to StaticEffect if needed
    static_effects = []
    
    # For now, static effects are handled by parse_static_effects
    # This function is a placeholder for future conversion
    return static_effects


def _merge_activated_abilities(axis1: list[ActivatedAbility], detected: list[ActivatedAbility]) -> list[ActivatedAbility]:
    """Merge Axis1 activated abilities with boundary-detected ones, deduplicating."""
    # Simple merge - in the future, we could deduplicate based on cost/effect similarity
    merged = list(axis1)
    
    # Add detected abilities that don't duplicate axis1
    for detected_ability in detected:
        # Simple deduplication: check if cost/effect combination already exists
        is_duplicate = False
        for existing in merged:
            if (existing.costs == detected_ability.costs and
                existing.effects == detected_ability.effects):
                is_duplicate = True
                break
        
        if not is_duplicate:
            merged.append(detected_ability)
    
    return merged


def _merge_triggered_abilities(axis1: list[TriggeredAbility], detected: list[TriggeredAbility]) -> list[TriggeredAbility]:
    """Merge Axis1 triggered abilities with boundary-detected ones, deduplicating."""
    # Simple merge - in the future, we could deduplicate based on condition/effect similarity
    merged = list(axis1)
    existing_conditions = {t.condition_text.lower() for t in merged}
    
    for detected_ability in detected:
        if detected_ability.condition_text.lower() not in existing_conditions:
            merged.append(detected_ability)
            existing_conditions.add(detected_ability.condition_text.lower())
    
    return merged


def _parse_continuous_effects(text: str, ctx: ParseContext, is_permanent: bool) -> list[ContinuousEffect]:
    import logging
    logger = logging.getLogger(__name__)
    continuous_effects = []
    logger.debug(f"[BUILDER] _parse_continuous_effects: is_permanent={is_permanent}, text length={len(text)}")
    if is_permanent:
        sentences = split_into_sentences(text)
        logger.debug(f"[BUILDER] Split into {len(sentences)} sentences: {sentences}")
        for sentence in sentences:
            logger.debug(f"[BUILDER] Parsing continuous effect sentence: {sentence[:100]}")
            parsed = parse_continuous_effects(sentence, ctx)
            logger.debug(f"[BUILDER] Parsed {len(parsed)} continuous effects from sentence")
            continuous_effects.extend(parsed)
    return continuous_effects


def _parse_spell_effects(text: str, ctx: ParseContext, is_spell: bool) -> tuple[list[Effect], Optional[TargetingRules], list[ContinuousEffect]]:
    spell_effects: list[Effect] = []
    continuous_effects: list[ContinuousEffect] = []
    spell_targeting = None
    
    if is_spell:
        spell_ctx = ctx.with_flag("is_spell_text", True)
        for sentence in split_into_sentences(text):
            for eff in parse_effect_text(sentence, spell_ctx):
                if isinstance(eff, ContinuousEffect):
                    continuous_effects.append(eff)
                else:
                    spell_effects.append(eff)
            
            if spell_targeting is None:
                spell_targeting = parse_targeting(sentence)
    
    return spell_effects, spell_targeting, continuous_effects


def _parse_face(face: Axis1Face, ctx: ParseContext) -> Axis2Face:
    """
    Four-step pipeline:
    1. Extract keywords FIRST (already implemented)
    2. Identify ability boundaries using syntactic markers
    3. Inside each ability, split into sentences
    4. Reconstruct effect chains using semantic heuristics
    5. Emit Axis2 nodes (continuous effects, replacement effects, etc.)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Step 0: Handle keywords FIRST (already implemented)
    # Keywords are detected and removed by keyword registry
    # We start with empty activated/triggered lists since we'll parse from text
    remaining_text, keyword_names, keyword_effects = get_remaining_text_for_parsing(
        face, [], [], ctx
    )
    
    logger.debug(f"[BUILDER] Remaining text after keyword extraction: {remaining_text[:300]}")
    logger.debug(f"[BUILDER] Keyword effects: {len(keyword_effects)}")
    
    # Step 1: Detect ability boundaries
    chunks = detect_ability_boundaries(remaining_text, ctx)
    logger.debug(f"[BUILDER] Detected {len(chunks)} ability chunks")
    
    # Step 2-4: Parse each ability chunk
    detected_activated = []
    detected_triggered = []
    replacement_effects = []
    continuous_effects = []
    static_effects = []
    spell_effects = []
    spell_targeting = None
    
    for chunk in chunks:
        logger.debug(f"[BUILDER] Processing chunk type={chunk.type}, text={chunk.text[:100]}")
        
        # Step 2: Split into sentences within this ability
        sentences = split_ability_into_sentences(chunk)
        logger.debug(f"[BUILDER] Split into {len(sentences)} sentences")
        
        # Step 3: Reconstruct effect chain
        effects = reconstruct_effect_chain(sentences, ctx)
        logger.debug(f"[BUILDER] Reconstructed {len(effects)} effects")
        
        # Step 4: Emit Axis2 nodes based on ability type
        if chunk.type == "triggered":
            triggered_ability = _build_triggered_ability(chunk, effects, ctx)
            if triggered_ability:
                detected_triggered.append(triggered_ability)
        elif chunk.type == "activated":
            activated_ability = _build_activated_ability(chunk, effects, ctx)
            if activated_ability:
                detected_activated.append(activated_ability)
        elif chunk.type == "static":
            # Static effects are parsed as continuous effects
            # First, try parsing the chunk text directly as continuous effects
            # (this handles cases where effect chain reconstruction didn't find them)
            types_lower = [t.lower() for t in face.card_types]
            is_permanent = any(t in types_lower for t in ["enchantment", "artifact", "creature", "planeswalker", "land"])
            if is_permanent:
                # Parse as continuous effects directly
                parsed_continuous = parse_continuous_effects(chunk.text, ctx)
                continuous_effects.extend(parsed_continuous)
            
            # Also check effects from chain reconstruction
            for effect in effects:
                if isinstance(effect, ContinuousEffect):
                    continuous_effects.append(effect)
            
            # Build static effects (placeholder for future conversion)
            static_effects_list = _build_static_effects(chunk, effects, ctx)
            static_effects.extend(static_effects_list)
        elif chunk.type == "replacement":
            for effect in effects:
                if isinstance(effect, ReplacementEffect):
                    replacement_effects.append(effect)
        elif chunk.type == "continuous":
            for effect in effects:
                if isinstance(effect, ContinuousEffect):
                    continuous_effects.append(effect)
        elif chunk.type == "spell":
            for effect in effects:
                if isinstance(effect, ContinuousEffect):
                    continuous_effects.append(effect)
                else:
                    spell_effects.append(effect)
            # Parse targeting from spell text
            if spell_targeting is None:
                spell_targeting = parse_targeting(chunk.text)
        elif chunk.type == "unknown":
            # Skip "Enchant creature" and similar targeting restrictions
            # These are handled separately by parse_enchant_restriction
            chunk_lower = chunk.text.strip().lower()
            if re.match(r"^enchant\s+(creature|artifact|land|planeswalker|enchantment|permanent|player|battle)(?:\s+with\s+.*)?\.?$", chunk_lower):
                logger.debug(f"[BUILDER] Skipping targeting restriction chunk: {chunk.text}")
                continue
            
            # Try to parse as various effect types
            # First try replacement effects
            parsed_replacement = parse_replacement_effects(chunk.text)
            if parsed_replacement:
                replacement_effects.extend(parsed_replacement)
            
            # Always try continuous effects for permanents (even if replacement effects were found)
            types_lower = [t.lower() for t in face.card_types]
            is_permanent = any(t in types_lower for t in ["enchantment", "artifact", "creature", "planeswalker", "land"])
            if is_permanent:
                parsed_continuous = parse_continuous_effects(chunk.text, ctx)
                continuous_effects.extend(parsed_continuous)
            
            # Also check effects from chain reconstruction
            for effect in effects:
                if isinstance(effect, ContinuousEffect):
                    continuous_effects.append(effect)
                elif isinstance(effect, ReplacementEffect):
                    replacement_effects.append(effect)
    
    # Merge with Axis1 structured abilities (hybrid approach)
    axis1_activated = _parse_axis1_activated(face, ctx)
    axis1_triggered = _parse_axis1_triggered(face, ctx)
    
    # Also parse reminder text triggers
    reminder_triggered = _parse_reminder_text_triggers(face.reminder_text or [], ctx)
    axis1_triggered.extend(reminder_triggered)
    
    # Merge and deduplicate
    activated = _merge_activated_abilities(axis1_activated, detected_activated)
    triggered = _merge_triggered_abilities(axis1_triggered, detected_triggered)
    
    # Add equip abilities
    detected_equip = _detect_equip_abilities_from_text(face.oracle_text or "", ctx)
    if detected_equip:
        activated.extend(detected_equip)
    
    mark_mana_abilities(activated)
    
    # Add keyword effects to appropriate lists
    for effect in keyword_effects:
        if isinstance(effect, ReplacementEffect):
            replacement_effects.append(effect)
        elif isinstance(effect, TriggeredAbility):
            triggered.append(effect)
        elif isinstance(effect, ActivatedAbility):
            activated.append(effect)
        elif isinstance(effect, ContinuousEffect):
            continuous_effects.append(effect)
    
    # Parse reminder text effects
    reminder_etb_effects = _parse_reminder_text_etb_effects(face.reminder_text or [], ctx)
    replacement_effects.extend(reminder_etb_effects)
    
    reminder_replacement_effects = _parse_reminder_text_replacement_effects(face.reminder_text or [], ctx)
    replacement_effects.extend(reminder_replacement_effects)
    
    # Parse static effects from remaining text (fallback for patterns not caught by boundary detection)
    static_effects_from_text = _parse_static_abilities(face, ctx)
    static_effects.extend(static_effects_from_text)
    
    # Parse special actions
    special_actions = _parse_special_actions(face, ctx)
    
    # Parse modes
    mode_choice, modes = parse_modes(face.oracle_text or "", ctx)
    
    # Parse enchant restrictions
    from axis2.parsing.enchant_restrictions import parse_enchant_restriction
    if "aura" in [t.lower() for t in face.subtypes]:
        enchant_targeting = parse_enchant_restriction(face.oracle_text or "")
        if enchant_targeting:
            spell_targeting = enchant_targeting
    
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
    for face in faces:
        expand_treasure_keyword(face)


def _add_special_casting_costs(axis1_card: Axis1Card, faces: list[Axis2Face]) -> None:
    keywords = extract_keywords(axis1_card.faces[0].oracle_text or "")
    
    for f, face in zip(axis1_card.faces, faces):
        ctx = _create_context(axis1_card, f)
        oracle_text = f.oracle_text or ""
        
        if "escape" in (kw.lower() for kw in keywords):
            escape_cost = parse_escape_cost(oracle_text)
            if escape_cost:
                face.casting_options.append(escape_cost)
        
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
        
        from axis2.validation import validate_axis2_card
        validation_errors = validate_axis2_card(card)
        if validation_errors:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Validation errors for card {card.card_id}: {validation_errors}")
        
        return card
