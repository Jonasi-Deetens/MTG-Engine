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


def test_axis2_debug(pg_session, game_state, card_name):
    """
    Debug Axis2 for a specific card OR a random card.
    Run with: pytest -s
    """

    axis1_card = load_axis1_card(pg_session, card_name)
    axis2 = Axis2Builder.build(axis1_card, game_state)

    print("\n=== AXIS 2 DEBUG ===")
    print(f"Name: {axis1_card.faces[0].name}")
    print(f"Types: {axis1_card.characteristics.card_types}")
    print(f"Mana Cost: {axis1_card.characteristics.mana_cost}")
    print(f"Oracle Text:\n{axis1_card.faces[0].oracle_text}")

    print("\nKEYWORDS:")
    for kw in axis2.keywords:
        print(f"  {kw}")

    print("\nENGINE ACTIONS:")
    for name, action in axis2.actions.items():
        print(f"  {name}: {action}")

    print("\nACTIVATED ABILITIES:")
    if axis2.activated_abilities:
        for ability in axis2.activated_abilities:
            print(f"  cost={ability.cost!r}")
            print(f"    effect={ability.effect}")   # effect object
            print(f"    effect type={type(ability.effect).__name__}")
    else:
        print("  None")

    print("\nZONE PERMISSIONS:")
    pprint.pprint(axis2.zone_permissions.permissions)

    print("\nEFFECTS:")
    if axis2.effects:
        for eff in axis2.effects:
            print(" ", eff)
    else:
        print("  No effects found")


    print("\nTRIGGERS:")
    for trig in axis2.triggers:
        print(f"  Trigger:")
        print(f"    condition={trig.condition} ({type(trig.condition).__name__})")
        print(f"    effect={trig.effect} ({type(trig.effect).__name__})")


    print("\nSTATIC EFFECTS:")
    for eff in axis2.static_effects:
        print(f"  {eff}  (type={type(eff).__name__})")

    else:
        print("  No static effects found")

    print("\nCONTINUOUS EFFECTS:")
    for eff in axis2.continuous_effects:
        print(f"  {eff}  (type={type(eff).__name__})")


    print("\nREPLACEMENT EFFECTS:")
    for eff in axis2.replacement_effects:
        print(f"  {eff}  (type={type(eff).__name__})")


    print("\nGLOBAL RESTRICTIONS:")
    for r in axis2.global_restrictions:
        print(f"  {r}")

    print("\nLIMITS:")
    for l in axis2.limits:
        print(f"  {l}")

    print("\nVISIBILITY:")
    print(axis2.visibility_constraints)

    print("\n===========================================")

    assert axis2 is not None
