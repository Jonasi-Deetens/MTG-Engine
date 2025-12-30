# axis3/engine/casting/cast_spell.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from axis3.engine.casting.context import CastContext
from axis3.engine.casting.permission_engine import PermissionEngine
from axis3.engine.casting.cost_engine import CostEngine
from axis3.engine.casting.replacement_engine import ReplacementEngine

from axis3.engine.stack.stack import StackItem
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType


@dataclass
class CastSpellEngine:
    """
    Full casting pipeline for Axis3.

    - cast_spell:   puts a spell on the stack (no resolution)
    - resolve_spell: resolves a spell on the stack
    """

    permissions: PermissionEngine
    costs: CostEngine
    replacements: ReplacementEngine

    # ============================================================
    # PUBLIC API
    # ============================================================

    def cast_spell(
        self,
        game_state: Any,
        source_id: str,
        controller: int,
        cost_choice: Optional[str] = None,
    ) -> CastContext:
        """
        Cast a spell from any zone and put it onto the stack.

        Resolution happens later when both players pass and the
        TurnManager instructs the stack to resolve the top item.
        """
        obj = game_state.get_object(source_id)
        if obj is None:
            raise ValueError(f"Object {source_id} not found")

        ctx = CastContext(
            source_id=source_id,
            controller=controller,
            origin_zone=obj.zone,
        )

        # 1. Permission check (zone, timing, global restrictions)
        if not self.permissions.can_cast(ctx, game_state):
            return ctx  # ctx.legal = False

        # 2. Choose cost (base or alternative)
        self.costs.choose_cost(ctx, game_state, cost_choice)
        if not ctx.legal:
            return ctx

        # 3. Apply cost reductions
        self.costs.apply_reductions(ctx, game_state)
        if not ctx.legal:
            return ctx

        # 4. Pay costs
        if not self.costs.pay_cost(ctx, game_state):
            return ctx

        # 5. Put spell on the stack
        stack_item = StackItem(
            kind="spell",
            source_id=source_id,
            controller=controller,
            cast_context=ctx,
        )
        game_state.stack.push(stack_item)
        ctx.placed_on_stack = True

        # 6. Publish SPELL_CAST event
        game_state.event_bus.publish(
            Event(
                type=EventType.SPELL_CAST,
                payload={"obj_id": source_id, "controller": controller, "ctx": ctx},
            )
        )

        return ctx

    # ============================================================
    # RESOLUTION
    # ============================================================

def resolve_spell(self, game_state: Any, ctx: CastContext):
    if ctx.countered:
        return

    obj = game_state.get_object(ctx.source_id)
    if obj is None:
        game_state.add_debug_log(
            f"resolve_spell: object {ctx.source_id} not found"
        )
        return

    card = getattr(obj, "axis3_card", None)

    # 1. Publish resolution event (subject to resolution replacements)
    event = Event(
        type=EventType.SPELL_RESOLVE,
        payload={"obj_id": ctx.source_id, "ctx": ctx},
    )
    event = self.replacements.apply_resolution_replacements(event, ctx, game_state)

    # 2. Apply card effects if still resolving normally
    if not ctx.countered and card and getattr(card, "effects", None):
        for effect in card.effects:
            effect.apply(game_state, obj.id, ctx.controller)

    ctx.resolved = True

    # 3. Remove the spell from the stack
    game_state.stack.remove_item_for_source(ctx.source_id)

    # 4. If something already moved/exiled it, don't touch it
    if ctx.get_metadata("moved_on_resolution", False):
        return

    # 5. Default destination: permanent → battlefield, non-permanent → graveyard
    if card and self._is_permanent_spell(card):
        game_state.move_card(obj.id, "BATTLEFIELD", controller=ctx.controller, ctx=ctx)
    else:
        game_state.move_card(obj.id, "GRAVEYARD", controller=ctx.controller, ctx=ctx)

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _is_permanent_spell(self, card: Any) -> bool:
        """
        Decide whether a spell is a permanent spell based on its card types.
        """
        types = {t.lower() for t in card.types}
        return any(
            t in types
            for t in (
                "creature",
                "artifact",
                "enchantment",
                "planeswalker",
                "battle",
                "land",
            )
        )
