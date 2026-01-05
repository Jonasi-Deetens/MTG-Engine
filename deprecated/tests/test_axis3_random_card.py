import pprint
from sqlalchemy import text

from axis1.schema import Axis1Card

from axis3.compiler.axis3_builder import Axis3CardBuilder
from axis3.engine.casting.context import CastContext
from axis3.state.zones import ZoneType


def load_axis1_card(pg_session, name: str | None = None) -> Axis1Card:
    """
    Loads a specific Axis1 card by name if provided.
    If name is None, loads a random Axis1 card.
    """

    if name is None:
        # Random card
        row = pg_session.execute(
            text("""
                SELECT axis1_json, layout
                FROM axis1_cards
                ORDER BY random()
                LIMIT 1
            """)
        ).fetchone()
    else:
        # Specific card
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

    if row.layout == "art_series":
        raise RuntimeError("Art series cards are not supported yet.")

    return Axis1Card(**row.axis1_json)


def test_axis3_debug(pg_session, game_state, card_name: str | None):
    """
    Debug Axis3 for a specific card OR a random card.
    Run with: pytest -s

    This inspects:
      - Axis1 raw data
      - Axis3Card (static rules view)
      - RuntimeObject (stateful view)
      - Casting permissions from current GameState
    """

    # ============================================================
    # LOAD & BUILD
    # ============================================================

    axis1_card = load_axis1_card(pg_session, card_name)
    axis3_card = Axis3CardBuilder.build(axis1_card, game_state)

    # Put the card into the game as a RuntimeObject in HAND of player 0
    controller = 0
    rt_obj = game_state.create_object(
        axis3_card=axis3_card,
        owner=controller,
        controller=controller,
        zone=ZoneType.HAND,
    )

    # ============================================================
    # BASIC AXIS1 INFO
    # ============================================================

    face = axis1_card.faces[0]

    print("\n=== AXIS 3 DEBUG ===")
    print(f"Name: {face.name}")
    print(f"Types: {face.card_types}")
    print(f"Mana Cost: {face.mana_cost}")
    print(f"Oracle Text:\n{face.oracle_text}")

    # ============================================================
    # AXIS3 CARD VIEW (STATIC RULES)
    # ============================================================

    print("\n[Axis3Card] CHARACTERISTICS:")
    print(f"  colors:          {axis3_card.colors}")
    print(f"  color_identity:  {axis3_card.color_identity}")
    print(f"  types:           {axis3_card.types}")
    print(f"  supertypes:      {axis3_card.supertypes}")
    print(f"  subtypes:        {axis3_card.subtypes}")
    print(f"  power/toughness: {axis3_card.power}/{axis3_card.toughness}")
    print(f"  loyalty:         {axis3_card.loyalty}")
    print(f"  defense:         {axis3_card.defense}")
    print(f"  mana_value:      {axis3_card.mana_value}")
    print(f"  mana_cost:       {axis3_card.mana_cost}")

    print("\nKEYWORDS:")
    if axis3_card.keywords:
        for kw in axis3_card.keywords:
            print(f"  {kw}")
    else:
        print("  None")

    print("\nSTATIC EFFECTS:")
    if axis3_card.static_effects:
        for eff in axis3_card.static_effects:
            print(f"  {eff}  (type={type(eff).__name__})")
    else:
        print("  None")

    print("\nREPLACEMENT EFFECTS:")
    if axis3_card.replacement_effects:
        for eff in axis3_card.replacement_effects:
            print(f"  {eff}  (type={type(eff).__name__})")
    else:
        print("  None")

    print("\nTRIGGERED ABILITIES:")
    if axis3_card.triggered_abilities:
        for trig in axis3_card.triggered_abilities:
            print(f"  event={getattr(trig, 'event', None)!r}  {trig}")
    else:
        print("  None")

    print("\nACTIVATED ABILITIES:")
    if axis3_card.activated_abilities:
        for ability in axis3_card.activated_abilities:
            print(f"  {ability}")
    else:
        print("  None")

    print("\nSPELL EFFECTS:")
    if axis3_card.effects:
        for eff in axis3_card.effects:
            print(f"  {eff} (type={type(eff).__name__})")
    else:
        print("  None")

    print("\nSPECIAL ACTIONS:")
    if axis3_card.special_actions:
        for action in axis3_card.special_actions:
            print(f"  {action}")
    else:
        print("  None")

    print("\nMODAL STRUCTURE:")
    print(f"  mode_choice: {axis3_card.mode_choice}")
    if axis3_card.modes:
        for i, mode in enumerate(axis3_card.modes, start=1):
            print(f"  mode {i}: {mode}")
    else:
        print("  No modes")

    # ============================================================
    # RUNTIME OBJECT VIEW
    # ============================================================

    print("\n[RuntimeObject] STATE:")
    print(f"  id:         {rt_obj.id}")
    print(f"  zone:       {rt_obj.zone}")
    print(f"  owner:      {rt_obj.owner}")
    print(f"  controller: {rt_obj.controller}")
    print(f"  tapped:     {rt_obj.tapped}")
    print(f"  damage:     {rt_obj.damage}")
    print(f"  counters:   {rt_obj.counters}")
    print(f"  is_token:   {rt_obj.is_token}")

    # ============================================================
    # ENGINE VIEW: CASTING / PERMISSIONS
    # ============================================================

    print("\nENGINE CASTING / PERMISSIONS:")
    ctx = CastContext(
        source_id=rt_obj.id,
        controller=controller,
        origin_zone=str(rt_obj.zone),
    )

    can_cast = game_state.casting.permissions.can_cast(ctx, game_state)
    print(f"  can_cast (from {rt_obj.zone}): {can_cast} (ctx.legal={ctx.legal})")
    if not ctx.legal and "illegal_reason" in ctx.metadata:
        print(f"    reason: {ctx.metadata['illegal_reason']}")

    # We can optionally also run cost building without paying:
    game_state.casting.costs.choose_cost(ctx, game_state, cost_choice=None)
    game_state.casting.costs.apply_reductions(ctx, game_state)

    print(f"\n  chosen_cost:       {ctx.chosen_cost}")
    print(f"  used_alt_cost:     {ctx.used_alt_cost}")
    print(f"  reductions_applied:")
    pprint.pprint(ctx.reductions_applied)

    print("\n===========================================")

    assert axis3_card is not None
    assert rt_obj is not None
