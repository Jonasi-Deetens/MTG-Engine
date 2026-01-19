from __future__ import annotations

from typing import Optional

from .continuous_helpers import (
    effect_sort_key,
    pt_baseline_restore,
    pt_baseline_snapshot,
    pt_signature,
    keyword_signature,
    type_signature,
    controller_signature,
    sort_effects_with_dependencies,
)
from .continuous_layers import (
    apply_layer_1_copy,
    apply_layer_2_control,
    apply_layer_3_text,
    apply_layer_4_type,
    apply_layer_5_color,
    apply_layer_6_abilities,
    apply_layer_7a_cda,
    apply_layer_7b_set_pt,
    apply_layer_7c_modify_pt,
    apply_layer_7d_counters,
    copy_signature,
    reset_characteristics,
    reset_layer_2_control,
    reset_layer_3_text,
    reset_layer_4_type,
    reset_layer_6_abilities,
    reset_layer_7_pt,
    update_cda_values,
)
from .continuous_static import gather_static_layer_effects
from .state import GameState
from .zones import ZONE_BATTLEFIELD


def apply_continuous_effects(game_state: GameState) -> None:
    battlefield = [
        obj for obj in game_state.objects.values()
        if obj.zone == ZONE_BATTLEFIELD and not obj.phased_out
    ]
    for obj in battlefield:
        reset_characteristics(obj)

    def apply_layer(
        effect_types: Optional[set[str]],
        apply_fn,
        recompute_until_stable: bool = False,
        signature_fn=None,
        reset_fn=None,
        pre_apply_fn=None,
        include_static: bool = True,
        dependency_sort: bool = False,
        baseline_snapshot_fn=None,
        baseline_restore_fn=None,
    ) -> None:
        previous_signature = None
        max_iterations = 5
        baseline = None
        if baseline_snapshot_fn and baseline_restore_fn:
            baseline = {obj.id: baseline_snapshot_fn(obj) for obj in battlefield}
        for _ in range(max_iterations):
            static_effects = gather_static_layer_effects(game_state, effect_types) if include_static else {}
            for obj in battlefield:
                base_effects = list(obj.temporary_effects)
                if obj.id in static_effects:
                    obj.temporary_effects = base_effects + static_effects[obj.id]
                else:
                    obj.temporary_effects = base_effects
                obj.temporary_effects = sorted(obj.temporary_effects, key=effect_sort_key)
                if dependency_sort:
                    obj.temporary_effects = sort_effects_with_dependencies(obj.temporary_effects)
                if reset_fn:
                    reset_fn(obj)
                if baseline and baseline_restore_fn:
                    baseline_restore_fn(obj, baseline[obj.id])
                if pre_apply_fn:
                    pre_apply_fn(obj)
                apply_fn(obj)
                obj.temporary_effects = base_effects
            if not recompute_until_stable or not signature_fn:
                break
            signature = tuple(signature_fn(obj) for obj in battlefield)
            if signature == previous_signature:
                break
            previous_signature = signature

    apply_layer(
        None,
        lambda obj: apply_layer_1_copy(game_state, obj),
        include_static=False,
        recompute_until_stable=True,
        signature_fn=copy_signature,
        reset_fn=reset_characteristics,
    )
    apply_layer(
        {"change_control"},
        lambda obj: apply_layer_2_control(game_state, obj),
        recompute_until_stable=True,
        signature_fn=controller_signature,
        reset_fn=reset_layer_2_control,
    )
    apply_layer(
        {"set_oracle_text", "append_oracle_text", "remove_oracle_text"},
        apply_layer_3_text,
        recompute_until_stable=True,
        reset_fn=reset_layer_3_text,
    )
    apply_layer(
        {"set_types", "add_type", "remove_type"},
        apply_layer_4_type,
        recompute_until_stable=True,
        signature_fn=type_signature,
        reset_fn=reset_layer_4_type,
    )
    apply_layer({"set_colors", "add_color", "remove_color"}, apply_layer_5_color)
    apply_layer(
        {"gain_keyword"},
        apply_layer_6_abilities,
        recompute_until_stable=True,
        signature_fn=keyword_signature,
        reset_fn=reset_layer_6_abilities,
        dependency_sort=True,
    )
    apply_layer(
        {"cda_power_toughness"},
        apply_layer_7a_cda,
        recompute_until_stable=True,
        signature_fn=pt_signature,
        reset_fn=reset_layer_7_pt,
        pre_apply_fn=lambda obj: update_cda_values(game_state, obj),
    )
    apply_layer(
        {"set_power_toughness"},
        apply_layer_7b_set_pt,
        recompute_until_stable=True,
        signature_fn=pt_signature,
        reset_fn=reset_layer_7_pt,
        dependency_sort=True,
    )
    apply_layer(
        {"change_power_toughness"},
        apply_layer_7c_modify_pt,
        recompute_until_stable=True,
        signature_fn=pt_signature,
        dependency_sort=True,
        baseline_snapshot_fn=pt_baseline_snapshot,
        baseline_restore_fn=pt_baseline_restore,
    )
    apply_layer(set(), apply_layer_7d_counters)

