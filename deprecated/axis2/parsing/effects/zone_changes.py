# axis2/parsing/effects/zone_changes.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import (
    ChangeZoneEffect, TransformEffect, DestroyEffect, PutOntoBattlefieldEffect,
    Subject, SymbolicValue, ParseContext
)
from axis2.parsing.subject import subject_from_text

# Zone change patterns
RETURN_FROM_GRAVEYARD_TO_HAND_RE = re.compile(
    r"return\s+(?P<subject>.+?)\s+from\s+(?P<from_zone>your graveyard|the graveyard|a graveyard)\s+to\s+(?:its|their|his|her|the)?\s*owner'?s hand",
    re.IGNORECASE
)

RETURN_HAND_RE = re.compile(
    r"return\s+(?P<subject>.+?)\s+(?:from\s+your\s+graveyard\s+)?to\s+your\s+hand",
    re.IGNORECASE
)

RETURN_BATTLEFIELD_RE = re.compile(
    r"return\s+(?P<subject>.+?)\s+to\s+the battlefield",
    re.IGNORECASE
)

# Special pattern for "return the exiled card" (Oblivion Ring, Banishing Light, etc.)
# Matches: "return the exiled card", "return the exiled card to the battlefield", 
# "return the exiled card to the battlefield under its owner's control"
RETURN_EXILED_CARD_RE = re.compile(
    r"return\s+(?:the\s+)?exiled\s+card(?:\s+to\s+the\s+battlefield)?(?:\s+under\s+its\s+owner'?s?\s+control)?\.?",
    re.IGNORECASE
)

ONTO_BATTLEFIELD_RE = re.compile(
    r"put\s+(?P<subject>.+?)\s+onto\s+the battlefield",
    re.IGNORECASE
)

EXILE_RE = re.compile(
    r"exile\s+(?P<subject>.+?)(?:$|\.|,)",
    re.IGNORECASE
)

GRAVEYARD_RE = re.compile(
    r"put\s+(?P<subject>.+?)\s+into\s+(?:its|their|your|his|her)?\s*owner'?s?\s*graveyard",
    re.IGNORECASE
)

LIBRARY_RE = re.compile(
    r"put\s+(?P<subject>.+?)\s+on\s+(?P<position>top|the bottom)\s+of\s+(?:its|their|your)?\s*owner'?s library",
    re.IGNORECASE
)

ZONE_FROM_RE = re.compile( 
    r"from\s+(?:a|any|the|your|their|its)\s+(graveyard|hand|library|battlefield|exile)", 
    re.IGNORECASE 
)

PUT_ONE_BF_TAPPED_RE = re.compile(
    r"put one onto the battlefield tapped",
    re.IGNORECASE
)

PUT_OTHER_HAND_RE = re.compile(
    r"the other into your hand",
    re.IGNORECASE
)

PUT_THAT_CARD_ATTACHED_RE = re.compile(
    r"put\s+that\s+card\s+onto\s+the\s+battlefield\s+attached\s+to\s+(?P<target>[\w\-'']+)",
    re.I
)

TRANSFORM_RE = re.compile(
    r"\btransform\s+(?P<subject>.+?)(?:\.|,|;|$)",
    re.IGNORECASE,
)

DESTROY_RE = re.compile(
    r"\bdestroy\s+(?P<subject>[^.;]+)",
    re.IGNORECASE,
)

PUT_RE = re.compile(
    r"put (?:an|a) ([^ ]+) card .*?from your hand onto the battlefield",
    re.IGNORECASE
)

MV_CONSTRAINT_RE = re.compile(
    r"mana value (?:less than or equal to|<=) (.+?)(?= from| onto| card|$)",
    re.IGNORECASE
)

def _extract_restrictions(subject_text: str):
    """
    Extracts clauses like:
      - "that isn't a God"
      - "that is not legendary"
      - "that is a creature"
    Returns (clean_subject, filters_dict)
    """
    filters = {}

    # match "that isn't a God"
    m = re.search(r"that\s+(?:is|isn't|is not)\s+([a-z ]+)", subject_text, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()

        # remove leading articles
        raw = re.sub(r"^(a|an|the)\s+", "", raw)

        # detect negation
        if "isn't" in subject_text or "is not" in subject_text:
            filters["not_subtype"] = raw
        else:
            filters["subtype"] = raw

        # remove the clause from subject text
        subject_text = re.sub(r"that\s+(?:is|isn't|is not)\s+[a-z ]+", "", subject_text, flags=re.IGNORECASE).strip()

    m = ZONE_FROM_RE.search(subject_text)
    if m:
        zone = m.group(1).lower()
        filters["zone"] = zone

        # Remove the zone clause from the subject text
        subject_text = ZONE_FROM_RE.sub("", subject_text).strip()

    return subject_text, filters

class ZoneChangeParser(EffectParser):
    """Parses zone change effects: return, exile, put onto battlefield, etc."""
    priority = 40  # Generic effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return any(keyword in lower for keyword in [
            "return", "exile", "put", "destroy", "transform", "attach"
        ])
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        # Do not parse "put it onto the battlefield" generically
        # when the sentence contains a search effect.
        if "put it onto the battlefield" in text.lower():
            return ParseResult(matched=False)

        # Prevent mis-parsing conditional clauses like "exiled this way"
        lower = text.lower()
        if "exiled this way" in lower:
            return ParseResult(matched=False)

        t = text.strip()

        # 0. Attach this to target/that creature (Equip ability or triggered ability)
        # Pattern: "Attach this to target creature you control." or "attach this Aura to that creature"
        ATTACH_TO_TARGET_RE = re.compile(
            r"attach\s+(?:this|this\s+\w+)\s+to\s+(?:target|that)\s+[^\.]+",
            re.IGNORECASE
        )
        m = ATTACH_TO_TARGET_RE.search(t)
        if m:
            # For Equip, attach_to is "target" (the targeting is handled by ActivatedAbility.targeting)
            # For triggered abilities, attach_to is "that_creature" (referring to the triggering creature)
            if "that" in t.lower():
                attach_to = "that_creature"
            else:
                attach_to = "target"
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=Subject(scope="self"),
                    to_zone="battlefield",  # Equipment/Aura stays on battlefield, just attaches
                    attach_to=attach_to  # String identifier - targeting rules are in ActivatedAbility or trigger
                ),
                consumed_text=text
            )

        # 1. Return from graveyard → hand
        m = RETURN_FROM_GRAVEYARD_TO_HAND_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject_text, filters = _extract_restrictions(subject_text)

            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    from_zone="graveyard",
                    to_zone="hand"
                ),
                consumed_text=text
            )

        # 2a. Return [card name] to its owner's hand (specific card name pattern - check BEFORE generic)
        # Pattern: "return [Card Name] to its owner's hand"
        RETURN_CARD_NAME_TO_HAND_RE = re.compile(
            r"return\s+(.+?)\s+to\s+its\s+owner'?s?\s+hand",
            re.IGNORECASE
        )
        m = RETURN_CARD_NAME_TO_HAND_RE.search(t)
        if m:
            subject_text = m.group(1).strip()
            # Check if it's the card's own name (self-reference)
            if subject_text.lower() == ctx.card_name.lower():
                return ParseResult(
                    matched=True,
                    effect=ChangeZoneEffect(
                        subject=Subject(scope="self"),
                        to_zone="hand",
                        owner="owner"
                    ),
                    consumed_text=text
                )
            # Otherwise, try to parse as a general subject
            subject_text, filters = _extract_restrictions(subject_text)
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    to_zone="hand",
                    owner="owner"
                ),
                consumed_text=text
            )
        
        # 2b. Return → hand (no from-zone clause, generic)
        m = RETURN_HAND_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject_text, filters = _extract_restrictions(subject_text)
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    to_zone="hand"
                ),
                consumed_text=text
            )

        # 3a. Return the exiled card → battlefield (special case for Oblivion Ring, etc.)
        # Check this BEFORE the generic return pattern to ensure it matches first
        # Match variations: "return the exiled card", "return the exiled card to the battlefield", etc.
        if "exiled card" in t.lower() and "return" in t.lower():
            print(f"[DEBUG ZoneChange] Checking 'return exiled card' pattern for text: '{t}'")
            # Try the specific pattern first
            m = RETURN_EXILED_CARD_RE.search(t)
            print(f"[DEBUG ZoneChange] Pattern search result: {m}")
            if m:
                print(f"[DEBUG ZoneChange] Pattern matched! Creating linked_exiled_card effect")
                return ParseResult(
                    matched=True,
                    effect=ChangeZoneEffect(
                        subject=Subject(
                            scope="linked_exiled_card",
                            filters={"source": "self"},
                        ),
                        to_zone="battlefield"
                    ),
                    consumed_text=text
                )
            else:
                print(f"[DEBUG ZoneChange] Pattern did NOT match text: '{t}'")
                print(f"[DEBUG ZoneChange] Pattern regex: {RETURN_EXILED_CARD_RE.pattern}")

        # 3b. Return → battlefield (generic)
        m = RETURN_BATTLEFIELD_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject_text, filters = _extract_restrictions(subject_text)
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    to_zone="battlefield"
                ),
                consumed_text=text
            )

        # 4. Put onto battlefield
        m = ONTO_BATTLEFIELD_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject_text, filters = _extract_restrictions(subject_text)
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    to_zone="battlefield"
                ),
                consumed_text=text
            )

        # 5. Exile
        m = EXILE_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject_text, filters = _extract_restrictions(subject_text)

            if subject_text.lower().startswith("target"):
                # Extract the type after "target"
                words = subject_text.split()
                if len(words) >= 2:
                    type_word = words[1]  # "creature"
                    # Build filters from the rest of the phrase
                    extra_filters = filters.copy()
                    if "opponent controls" in subject_text.lower():
                        extra_filters["opponent_controls"] = True

                    return ParseResult(
                        matched=True,
                        effect=ChangeZoneEffect(
                            subject=Subject(
                                scope="target",
                                types=[type_word],
                                filters=extra_filters
                            ),
                            to_zone="exile"
                        ),
                        consumed_text=text
                    )

            # FALLBACK: normal subject parsing
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    to_zone="exile"
                ),
                consumed_text=text
            )

        # 6. Put into graveyard
        m = GRAVEYARD_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject_text, filters = _extract_restrictions(subject_text)
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    to_zone="graveyard"
                ),
                consumed_text=text
            )

        # 7. Put on top/bottom of library
        m = LIBRARY_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject_text, filters = _extract_restrictions(subject_text)
            position = m.group("position").strip()
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=subject_from_text(subject_text, ctx, extra_filters=filters),
                    to_zone="library",
                    position=position
                ),
                consumed_text=text
            )

        # 8. Transform
        m = TRANSFORM_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject = subject_from_text(subject_text, ctx)
            return ParseResult(
                matched=True,
                effect=TransformEffect(subject=subject),
                consumed_text=text
            )

        # 9. Destroy
        m = DESTROY_RE.search(t)
        if m:
            subject_text = m.group("subject").strip()
            subject = subject_from_text(subject_text, ctx)
            return ParseResult(
                matched=True,
                effect=DestroyEffect(subject=subject),
                consumed_text=text
            )

        # 10. Put onto battlefield from hand (specific pattern)
        m = PUT_RE.search(t)
        if m:
            card_type = m.group(1).capitalize()
            optional = "you may" in lower
            constraint = None
            mv = MV_CONSTRAINT_RE.search(text)
            if mv:
                raw = mv.group(1).strip()
                constraint = {
                    "mana_value_lte": SymbolicValue(
                        kind="variable",
                        expression=raw
                    )
                }

            return ParseResult(
                matched=True,
                effect=PutOntoBattlefieldEffect(
                    zone_from="hand",
                    card_filter={"types": [card_type]},
                    tapped=False,
                    attacking=False,
                    constraint=constraint,
                    optional=optional,
                ),
                consumed_text=text
            )

        # 11. Put one onto battlefield tapped (search result)
        if PUT_ONE_BF_TAPPED_RE.search(t):
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=Subject(scope="searched_card", index=0),
                    to_zone="battlefield",
                    tapped=True
                ),
                consumed_text=text
            )

        # 12. Put other into hand (search result)
        if PUT_OTHER_HAND_RE.search(t):
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=Subject(scope="searched_card", index=1),
                    to_zone="hand"
                ),
                consumed_text=text
            )

        # 13. Put that card attached (Lightpaws)
        m = PUT_THAT_CARD_ATTACHED_RE.search(t)
        if m:
            # Light-Paws always attaches to itself
            attach_to = "self"
            return ParseResult(
                matched=True,
                effect=ChangeZoneEffect(
                    subject=Subject(scope="searched_card"),
                    to_zone="battlefield",
                    attach_to=attach_to
                ),
                consumed_text=text
            )

        return ParseResult(matched=False)

