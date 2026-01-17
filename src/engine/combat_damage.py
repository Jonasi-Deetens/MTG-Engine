from __future__ import annotations

from typing import Any, Dict, List, Optional

from .damage import apply_damage_to_object, apply_damage_to_player
from .sba import apply_state_based_actions
from .state import GameObject, GameState


def resolve_combat_damage(
    game_state: GameState,
    turn_manager,
    player_id: int,
    damage_assignments: Optional[Dict[str, Dict[str, int]]] = None,
    combat_damage_pass: Optional[str] = None,
) -> None:
    combat_state = game_state.turn.combat_state
    if not combat_state:
        raise ValueError("No combat state is active.")

    def _redirect_effects(source_id: str) -> List[Dict[str, Any]]:
        return [
            effect
            for effect in list(game_state.replacement_effects)
            if effect.get("type") == "redirect_damage" and effect.get("source") == source_id
        ]

    def _prevent_effects_for_object(obj: GameObject) -> List[Dict[str, Any]]:
        return [effect for effect in obj.temporary_effects if effect.get("prevent_damage") is not None]

    def _prevent_effects_for_player(target_player_id: int) -> List[Dict[str, Any]]:
        return [
            effect
            for effect in list(game_state.replacement_effects)
            if effect.get("type") == "prevent_damage" and effect.get("player_id") == target_player_id
        ]

    def _requires_choice(source_id: str, target_key: str) -> bool:
        return target_key not in game_state.replacement_choices

    def _register_event_choice(
        source_id: str,
        target_key: str,
        target_obj: Optional[GameObject],
        player_target_id: Optional[int],
    ) -> bool:
        redirect_effects = _redirect_effects(source_id)
        if target_obj:
            prevent_effects = _prevent_effects_for_object(target_obj)
        else:
            prevent_effects = _prevent_effects_for_player(player_target_id) if player_target_id is not None else []
        if len(redirect_effects) + len(prevent_effects) > 1:
            return _requires_choice(source_id, target_key)
        return False

    def get_power(obj) -> int:
        return int(obj.power or 0)

    def has_keyword(obj, keyword: str) -> bool:
        return keyword in obj.keywords

    def is_alive(obj) -> bool:
        return obj.zone == "battlefield"

    def lethal_damage_required(defender, deathtouch: bool) -> int:
        if defender.toughness is None:
            return 0
        if deathtouch:
            return 1
        return max(0, int(defender.toughness) - int(defender.damage or 0))

    has_first_strike_combat = False
    for attacker_id in combat_state.attackers:
        attacker = game_state.objects.get(attacker_id)
        if attacker and (has_keyword(attacker, "First strike") or has_keyword(attacker, "Double strike")):
            has_first_strike_combat = True
            break
        for blocker_id in combat_state.blockers.get(attacker_id, []):
            blocker = game_state.objects.get(blocker_id)
            if blocker and (has_keyword(blocker, "First strike") or has_keyword(blocker, "Double strike")):
                has_first_strike_combat = True
                break
        if has_first_strike_combat:
            break

    if combat_damage_pass not in (None, "first_strike", "regular"):
        raise ValueError("Invalid combat damage pass.")
    if has_first_strike_combat:
        if combat_damage_pass == "first_strike" and combat_state.first_strike_resolved:
            raise ValueError("First strike combat damage already assigned.")
        if combat_damage_pass == "regular" and not combat_state.first_strike_resolved:
            raise ValueError("First strike combat damage must resolve first.")
        if combat_damage_pass is None and damage_assignments:
            raise ValueError("Combat damage pass is required with first/double strike.")
        if combat_damage_pass is None and combat_state.first_strike_resolved:
            raise ValueError("Combat damage pass is required with first/double strike.")
    else:
        if combat_damage_pass == "first_strike":
            raise ValueError("First strike combat damage does not apply.")

    def is_eligible_for_pass(obj) -> bool:
        if combat_damage_pass == "first_strike":
            return has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")
        if combat_damage_pass == "regular":
            return not has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")
        return True

    def _validate_manual_assignments(assignments: Dict[str, Dict[str, int]]) -> None:
        if not combat_state:
            raise ValueError("No combat state is active.")
        if not assignments:
            raise ValueError("No damage assignments provided.")
        valid_attackers = set(combat_state.attackers)
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            if get_power(attacker) <= 0:
                continue
            if not is_eligible_for_pass(attacker):
                continue
            if attacker_id not in assignments:
                raise ValueError("Missing combat damage assignment.")
        for source_id, targets in assignments.items():
            if source_id not in valid_attackers:
                raise ValueError("Invalid combat damage source.")
            source = game_state.objects.get(source_id)
            if not source or source.zone != "battlefield":
                raise ValueError("Invalid combat damage source.")
            if not is_eligible_for_pass(source):
                raise ValueError("Combat damage source is not eligible this pass.")
            if not targets:
                raise ValueError("Damage assignments missing targets.")
            blocker_ids = combat_state.blockers.get(source_id, [])
            has_player_assignment = False
            total = 0
            for target_id, amount in targets.items():
                try:
                    amt = int(amount)
                except (TypeError, ValueError):
                    raise ValueError("Invalid damage amount.")
                if amt < 0:
                    raise ValueError("Damage amount must be non-negative.")
                if target_id == "player":
                    if combat_state.defending_player_id is None:
                        raise ValueError("No defending player for combat damage.")
                    if combat_state.defending_object_id is not None:
                        raise ValueError("Combat damage must be assigned to the defending planeswalker.")
                    has_player_assignment = True
                elif target_id == "defender":
                    if combat_state.defending_object_id is None:
                        raise ValueError("No defending planeswalker for combat damage.")
                    has_player_assignment = True
                elif target_id.startswith("player:"):
                    player_target_id = int(target_id.split(":", 1)[1])
                    if player_target_id != combat_state.defending_player_id:
                        raise ValueError("Combat damage can only be assigned to the defending player.")
                    if combat_state.defending_object_id is not None:
                        raise ValueError("Combat damage must be assigned to the defending planeswalker.")
                    has_player_assignment = True
                elif target_id.startswith("planeswalker:"):
                    planeswalker_id = target_id.split(":", 1)[1]
                    if combat_state.defending_object_id != planeswalker_id:
                        raise ValueError("Combat damage can only be assigned to the defending planeswalker.")
                    has_player_assignment = True
                else:
                    if target_id not in combat_state.blockers.get(source_id, []):
                        raise ValueError("Combat damage assigned to an invalid blocker.")
                total += amt
            source_power = int(source.power or 0)
            if total > source_power:
                raise ValueError("Assigned damage exceeds power.")
            if total < source_power and "Trample" not in source.keywords:
                raise ValueError("Assigned damage must equal power without trample.")
            if blocker_ids and has_player_assignment and "Trample" not in source.keywords:
                raise ValueError("Combat damage to player requires trample.")
            if combat_state.blockers.get(source_id):
                order = combat_state.blockers.get(source_id, [])
                deathtouch = "Deathtouch" in source.keywords
                remaining = source_power
                for blocker_id in order:
                    if remaining <= 0:
                        break
                    blocker = game_state.objects.get(blocker_id)
                    if not blocker:
                        continue
                    assign = int(targets.get(blocker_id, 0))
                    lethal = lethal_damage_required(blocker, deathtouch)
                    if assign < min(remaining, lethal):
                        raise ValueError("Damage must be assigned to blockers in lethal order.")
                    remaining -= assign
                if remaining > 0 and "Trample" not in source.keywords:
                    raise ValueError("Unassigned combat damage without trample.")

    if damage_assignments:
        _validate_manual_assignments(damage_assignments)
        missing_choices: List[str] = []
        used_event_keys: set[str] = set()
        for source_id, assignments in damage_assignments.items():
            source = game_state.objects.get(source_id)
            if not source:
                continue
            for target_id, amount in assignments.items():
                if int(amount) <= 0:
                    continue
                if target_id.startswith("player:"):
                    player_target_id = int(target_id.split(":", 1)[1])
                    event_key = f"damage:event:{source_id}:player:{player_target_id}"
                    if _register_event_choice(source_id, event_key, None, player_target_id):
                        missing_choices.append(event_key)
                    used_event_keys.add(event_key)
                elif target_id == "player":
                    event_key = f"damage:event:{source_id}:player:{combat_state.defending_player_id}"
                    if _register_event_choice(source_id, event_key, None, combat_state.defending_player_id):
                        missing_choices.append(event_key)
                    used_event_keys.add(event_key)
                elif target_id == "defender":
                    planeswalker_id = combat_state.defending_object_id
                    if planeswalker_id:
                        target = game_state.objects.get(planeswalker_id)
                        event_key = f"damage:event:{source_id}:object:{planeswalker_id}"
                        if target and _register_event_choice(source_id, event_key, target, None):
                            missing_choices.append(event_key)
                        used_event_keys.add(event_key)
                elif target_id.startswith("planeswalker:"):
                    planeswalker_id = target_id.split(":", 1)[1]
                    target = game_state.objects.get(planeswalker_id)
                    event_key = f"damage:event:{source_id}:object:{planeswalker_id}"
                    if target and _register_event_choice(source_id, event_key, target, None):
                        missing_choices.append(event_key)
                    used_event_keys.add(event_key)
                else:
                    target = game_state.objects.get(target_id)
                    if target:
                        event_key = f"damage:event:{source_id}:object:{target_id}"
                        if _register_event_choice(source_id, event_key, target, None):
                            missing_choices.append(event_key)
                        used_event_keys.add(event_key)
        if missing_choices:
            raise ValueError("Damage replacement choice required.")
        for source_id, assignments in damage_assignments.items():
            source = game_state.objects.get(source_id)
            if not source:
                continue
            for target_id, amount in assignments.items():
                if int(amount) <= 0:
                    continue
                if target_id.startswith("player:"):
                    player_target_id = int(target_id.split(":", 1)[1])
                    apply_damage_to_player(game_state, source, player_target_id, int(amount))
                elif target_id == "player":
                    apply_damage_to_player(game_state, source, combat_state.defending_player_id, int(amount))
                elif target_id == "defender":
                    planeswalker_id = combat_state.defending_object_id
                    target = game_state.objects.get(planeswalker_id) if planeswalker_id else None
                    if target:
                        apply_damage_to_object(game_state, source, target, int(amount))
                elif target_id.startswith("planeswalker:"):
                    planeswalker_id = target_id.split(":", 1)[1]
                    target = game_state.objects.get(planeswalker_id)
                    if target:
                        apply_damage_to_object(game_state, source, target, int(amount))
                else:
                    target = game_state.objects.get(target_id)
                    if target:
                        apply_damage_to_object(game_state, source, target, int(amount))
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            blockers = [
                game_state.objects.get(blocker_id)
                for blocker_id in combat_state.blockers.get(attacker_id, [])
            ]
            blockers = [b for b in blockers if b and is_alive(b) and b.is_blocking and is_eligible_for_pass(b)]
            for blocker in blockers:
                if get_power(blocker) <= 0:
                    continue
                used_event_keys.add(f"damage:event:{blocker.id}:object:{attacker_id}")
                apply_damage_to_object(game_state, blocker, attacker, get_power(blocker))
        apply_state_based_actions(game_state)
        for key in used_event_keys:
            game_state.replacement_choices.pop(key, None)
        if has_first_strike_combat:
            if combat_damage_pass == "first_strike":
                combat_state.first_strike_resolved = True
            elif combat_damage_pass == "regular":
                combat_state.combat_damage_resolved = True
        else:
            combat_state.combat_damage_resolved = True
        return

    def can_deal_in_first_strike(obj) -> bool:
        return has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")

    def can_deal_in_second_strike(obj) -> bool:
        return not has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")

    def register_combat_event_choice(
        source_obj: GameObject,
        target_obj: Optional[GameObject],
        player_target_id: Optional[int],
        event_key: str,
    ) -> bool:
        return _register_event_choice(source_obj.id, event_key, target_obj, player_target_id)

    def apply_damage_to_defender(attacker: GameObject, amount: int, used_event_keys: Optional[set[str]] = None) -> None:
        if combat_state.defending_object_id:
            defender = game_state.objects.get(combat_state.defending_object_id)
            if defender:
                if used_event_keys is not None:
                    used_event_keys.add(f"damage:event:{attacker.id}:object:{defender.id}")
                apply_damage_to_object(game_state, attacker, defender, amount)
            return
        if used_event_keys is not None:
            used_event_keys.add(f"damage:event:{attacker.id}:player:{combat_state.defending_player_id}")
        apply_damage_to_player(game_state, attacker, combat_state.defending_player_id, amount)

    def deal_to_blockers(attacker, blockers, used_event_keys: Optional[set[str]] = None):
        remaining = get_power(attacker)
        if remaining <= 0:
            return
        deathtouch = has_keyword(attacker, "Deathtouch")
        for blocker in blockers:
            if remaining <= 0:
                break
            lethal = lethal_damage_required(blocker, deathtouch)
            assign = remaining if lethal == 0 else min(remaining, lethal)
            if assign > 0:
                if used_event_keys is not None:
                    used_event_keys.add(f"damage:event:{attacker.id}:object:{blocker.id}")
                apply_damage_to_object(game_state, attacker, blocker, assign)
            remaining -= assign
        if remaining > 0 and has_keyword(attacker, "Trample"):
            apply_damage_to_defender(attacker, remaining, used_event_keys)

    def deal_blocker_damage(attacker, blockers, used_event_keys: Optional[set[str]] = None):
        for blocker in blockers:
            if get_power(blocker) <= 0:
                continue
            if used_event_keys is not None:
                used_event_keys.add(f"damage:event:{blocker.id}:object:{attacker.id}")
            apply_damage_to_object(game_state, blocker, attacker, get_power(blocker))

    def resolve_combat_pass(first_strike_pass: bool, used_event_keys: Optional[set[str]] = None):
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            blockers = [
                game_state.objects.get(blocker_id)
                for blocker_id in combat_state.blockers.get(attacker_id, [])
            ]
            blockers = [b for b in blockers if b and is_alive(b) and b.is_blocking]

            attacker_can_deal = can_deal_in_first_strike(attacker) if first_strike_pass else can_deal_in_second_strike(attacker)
            eligible_blockers = [
                b for b in blockers
                if (can_deal_in_first_strike(b) if first_strike_pass else can_deal_in_second_strike(b))
            ]

            if not blockers:
                if attacker_can_deal:
                    apply_damage_to_defender(attacker, get_power(attacker), used_event_keys)
                continue

            if attacker_can_deal:
                deal_to_blockers(attacker, blockers, used_event_keys)
            if eligible_blockers and is_alive(attacker):
                deal_blocker_damage(attacker, eligible_blockers, used_event_keys)

        apply_state_based_actions(game_state)

    def _collect_missing_combat_choices() -> List[str]:
        missing: List[str] = []
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            if not is_eligible_for_pass(attacker):
                continue
            blockers = [
                game_state.objects.get(blocker_id)
                for blocker_id in combat_state.blockers.get(attacker_id, [])
            ]
            blockers = [b for b in blockers if b and is_alive(b) and b.is_blocking and is_eligible_for_pass(b)]
            if not blockers:
                if combat_state.defending_object_id:
                    defender = game_state.objects.get(combat_state.defending_object_id)
                    if defender:
                        event_key = f"damage:event:{attacker.id}:object:{defender.id}"
                        if register_combat_event_choice(attacker, defender, None, event_key):
                            missing.append(event_key)
                else:
                    event_key = f"damage:event:{attacker.id}:player:{combat_state.defending_player_id}"
                    if register_combat_event_choice(attacker, None, combat_state.defending_player_id, event_key):
                        missing.append(event_key)
                continue
            remaining = get_power(attacker)
            if remaining > 0:
                deathtouch = has_keyword(attacker, "Deathtouch")
                for blocker in blockers:
                    if remaining <= 0:
                        break
                    lethal = lethal_damage_required(blocker, deathtouch)
                    assign = remaining if lethal == 0 else min(remaining, lethal)
                    if assign > 0:
                        event_key = f"damage:event:{attacker.id}:object:{blocker.id}"
                        if register_combat_event_choice(attacker, blocker, None, event_key):
                            missing.append(event_key)
                    remaining -= assign
                if remaining > 0 and has_keyword(attacker, "Trample"):
                    if combat_state.defending_object_id:
                        defender = game_state.objects.get(combat_state.defending_object_id)
                        if defender:
                            event_key = f"damage:event:{attacker.id}:object:{defender.id}"
                            if register_combat_event_choice(attacker, defender, None, event_key):
                                missing.append(event_key)
                    else:
                        event_key = f"damage:event:{attacker.id}:player:{combat_state.defending_player_id}"
                        if register_combat_event_choice(attacker, None, combat_state.defending_player_id, event_key):
                            missing.append(event_key)
            for blocker in blockers:
                if get_power(blocker) <= 0:
                    continue
                event_key = f"damage:event:{blocker.id}:object:{attacker.id}"
                if register_combat_event_choice(blocker, attacker, None, event_key):
                    missing.append(event_key)
        return missing

    if _collect_missing_combat_choices():
        raise ValueError("Damage replacement choice required.")
    used_event_keys: set[str] = set()
    if combat_damage_pass == "first_strike":
        resolve_combat_pass(first_strike_pass=True, used_event_keys=used_event_keys)
        combat_state.first_strike_resolved = True
    elif combat_damage_pass == "regular":
        resolve_combat_pass(first_strike_pass=False, used_event_keys=used_event_keys)
        combat_state.combat_damage_resolved = True
    else:
        if has_first_strike_combat:
            resolve_combat_pass(first_strike_pass=True, used_event_keys=used_event_keys)
            resolve_combat_pass(first_strike_pass=False, used_event_keys=used_event_keys)
            combat_state.first_strike_resolved = True
            combat_state.combat_damage_resolved = True
        else:
            resolve_combat_pass(first_strike_pass=False, used_event_keys=used_event_keys)
            combat_state.combat_damage_resolved = True
    for key in used_event_keys:
        game_state.replacement_choices.pop(key, None)
    turn_manager.after_player_action(player_id)

