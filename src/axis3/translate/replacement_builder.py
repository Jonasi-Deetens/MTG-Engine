# src/axis3/translate/replacement_builder.py

from axis3.rules.replacement.types import ReplacementEffect
from axis3.state.zones import ZoneType as Zone


def build_replacement_effects_for_object(game_state, rt_obj):
    axis2 = rt_obj.axis2_card

    for repl in axis2.replacement_effects:
        kind = repl.kind

        if kind == "enters_tapped":
            game_state.replacement_effects.append(
                ReplacementEffect(
                    source_id=rt_obj.id,
                    applies_to="zone_change",
                    condition=lambda e, obj_id=rt_obj.id: (
                        e["obj_id"] == obj_id and e["to_zone"] == Zone.BATTLEFIELD
                    ),
                    apply=lambda e: {**e, "enters_tapped": True},
                )
            )

        elif kind == "enters_with_counters":
            count = repl.count
            counter_type = repl.counter_type

            game_state.replacement_effects.append(
                ReplacementEffect(
                    source_id=rt_obj.id,
                    applies_to="zone_change",
                    condition=lambda e, obj_id=rt_obj.id: (
                        e["obj_id"] == obj_id and e["to_zone"] == Zone.BATTLEFIELD
                    ),
                    apply=lambda e, c=count, ct=counter_type: {
                        **e,
                        "add_counters": (ct, c),
                    },
                )
            )

        elif kind == "dies_exile_instead":
            game_state.replacement_effects.append(
                ReplacementEffect(
                    source_id=rt_obj.id,
                    applies_to="zone_change",
                    condition=lambda e, obj_id=rt_obj.id: (
                        e["obj_id"] == obj_id and e["to_zone"] == Zone.GRAVEYARD
                    ),
                    apply=lambda e: {**e, "to_zone": Zone.EXILE},
                )
            )
