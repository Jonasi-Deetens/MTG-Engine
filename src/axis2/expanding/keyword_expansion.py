# axis2/expanding/keyword_expansion.py

from axis2.schema import ActivatedAbility, TapCost, SacrificeCost, AddManaEffect, Subject

def expand_treasure_keyword(face):
    """
    Injects the Treasure mana ability:
        "{T}, Sacrifice this artifact: Add one mana of any color."
    This is a keyword-defined ability, not parsed from Oracle text.
    """

    # Must be an Artifact
    if "Artifact" not in face.types:
        return

    # Must have subtype Treasure OR keyword Treasure
    is_treasure = (
        "Treasure" in getattr(face, "subtypes", []) or
        "Treasure" in getattr(face, "keywords", [])
    )

    if not is_treasure:
        return

    # Build the ability
    ability = ActivatedAbility(
        costs=[
            TapCost(subject=Subject(scope="self")),
            SacrificeCost(subject=Subject(scope="self", types=["artifact"]))
        ],
        effects=[
            AddManaEffect(mana=[], choice="any_color")
        ],
        conditions=[],
        targeting=None,
        timing="mana"
    )

    # Attach to the face
    if face.activated_abilities is None:
        face.activated_abilities = []

    face.activated_abilities.append(ability)
