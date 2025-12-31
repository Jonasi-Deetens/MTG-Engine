import pprint
from sqlalchemy import text

from axis1.schema import Axis1Card
from axis2.builder import Axis2Builder


def load_axis1_card(pg_session, name: str | None = None) -> Axis1Card:
    """
    Loads a specific Axis1 card by name if provided.
    If name is None, loads a random Axis1 card.
    """

    if name is None:
        row = pg_session.execute(
            text("""
                SELECT axis1_json, layout
                FROM axis1_cards
                ORDER BY random()
                LIMIT 1
            """)
        ).fetchone()
    else:
        row = pg_session.execute(
            text("""
                SELECT axis1_json, layout
                FROM axis1_cards
                WHERE axis1_json->'faces'->0->>'name' = :name
                LIMIT 1
            """),
            {"name": name}
        ).fetchone()

    if not row:
        raise RuntimeError(f"No Axis1 card found for name={name!r}")

    # If we got an art series card, try again with a fallback query
    if row.layout == "art_series":
        row = pg_session.execute(
            text("""
                SELECT axis1_json, layout
                FROM axis1_cards
                WHERE axis1_json->'faces'->0->>'name' = :name
                AND layout != 'art_series'
                LIMIT 1
            """),
            {"name": name}
        ).fetchone()

        if not row:
            raise RuntimeError(f"No non-art-series card found for name={name!r}")


    return Axis1Card(**row.axis1_json)


def test_axis2_debug(pg_session, card_name):
    """
    Debug Axis2 for a specific card OR a random card.
    Run with: pytest -s

    This inspects:
      - Axis1 raw data
      - Axis2Card (semantic rules view)
    """

    # ============================================================
    # LOAD & BUILD
    # ============================================================

    axis1_card = load_axis1_card(pg_session, card_name)
    axis2_card = Axis2Builder.build(axis1_card)

    face = axis1_card.faces[0]

    print("\n=== AXIS 2 DEBUG ===")
    print(f"Name: {face.name}")
    print(f"Types: {face.card_types}")
    print(f"Mana Cost: {face.mana_cost}")
    print(f"Oracle Text:\n{face.oracle_text}")

    # ============================================================
    # AXIS2 CHARACTERISTICS
    # ============================================================

    print("\n[Axis2Card] CHARACTERISTICS:")
    ch = axis2_card.characteristics
    print(f"  colors:          {ch.colors}")
    print(f"  color_identity:  {ch.color_identity}")
    print(f"  types:           {ch.types}")
    print(f"  supertypes:      {ch.supertypes}")
    print(f"  subtypes:        {ch.subtypes}")
    print(f"  power/toughness: {ch.power}/{ch.toughness}")
    print(f"  loyalty:         {ch.loyalty}")
    print(f"  defense:         {ch.defense}")
    print(f"  mana_value:      {ch.mana_value}")
    print(f"  mana_cost:       {ch.mana_cost}")

    # ============================================================
    # AXIS2 FACES
    # ============================================================

    print("\nFACES:")
    for i, f in enumerate(axis2_card.faces, start=1):
        print(f"\n  Face {i}: {f.name}")
        print(f"    types:      {f.types}")
        print(f"    supertypes: {f.supertypes}")
        print(f"    subtypes:   {f.subtypes}")
        print(f"    mana_cost:  {f.mana_cost}")
        print(f"    mana_value: {f.mana_value}")
        print(f"    power/toughness: {f.power}/{f.toughness}")
        print(f"    loyalty:    {f.loyalty}")
        print(f"    defense:    {f.defense}")

        # Activated abilities
        print("\n    ACTIVATED ABILITIES:")
        if f.activated_abilities:
            for ab in f.activated_abilities:
                print(f"      {ab}")
        else:
            print("      None")

        # Triggered abilities
        print("\n    TRIGGERED ABILITIES:")
        if f.triggered_abilities:
            for trig in f.triggered_abilities:
                print(f"      {trig}")
                print("\n        EFFECT:")
                for eff in trig.effects:
                    print(f"        {eff}")
        else:
            print("      None")

        # Static effects
        print("\n    STATIC EFFECTS:")
        if f.static_effects:
            for eff in f.static_effects:
                print(f"      {eff}")
        else:
            print("      None")

        # Special actions
        print("\n    SPECIAL ACTIONS:")
        if f.special_actions:
            for sa in f.special_actions:
                print(f"      {sa}")
        else:
            print("      None")

        # Replacement effects
        print("\n    REPLACEMENT EFFECTS:")
        if f.replacement_effects:
            for eff in f.replacement_effects:
                print(f"      {eff}")
        else:
            print("      None")

        # Continuous effects
        print("\n    CONTINUOUS EFFECTS:")
        if f.continuous_effects:
            for eff in f.continuous_effects:
                print(f"      {eff}")
        else:
            print("      None")

        # Modes
        print("\n    MODES:")
        if f.modes:
            for m in f.modes:
                print(f"      {m}")
        else:
            print("      None")

    # ============================================================
    # KEYWORDS
    # ============================================================

    print("\nKEYWORDS:")
    if axis2_card.keywords:
        for kw in axis2_card.keywords:
            print(f"  {kw}")
    else:
        print("  None")

    print("\n===========================================")

    assert axis2_card is not None
