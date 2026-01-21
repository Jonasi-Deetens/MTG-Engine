from __future__ import annotations

from typing import Any, Callable, Dict

from .effects.effect_router import EffectRouter, create_default_router
from .effects.target_resolver import TargetResolver
from .effects.condition_evaluator import ConditionEvaluator
from .state import GameObject, GameState, ResolveContext


class EffectResolver:
    """Resolves and applies effects.

    This class now uses EffectRouter internally while maintaining
    backward compatibility with existing code.
    """

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self._router = create_default_router(game_state)
        self._target_resolver = TargetResolver(game_state)
        self._condition_evaluator = ConditionEvaluator(game_state)

        # Expose handlers for backward compatibility
        self._handlers = self._router._handlers

    @property
    def router(self) -> EffectRouter:
        """Get the underlying EffectRouter."""
        return self._router

    @property
    def target_resolver(self) -> TargetResolver:
        """Get the TargetResolver."""
        return self._target_resolver

    @property
    def condition_evaluator(self) -> ConditionEvaluator:
        """Get the ConditionEvaluator."""
        return self._condition_evaluator

    def _add_temporary_effect(self, obj: GameObject, effect: Dict[str, Any]) -> None:
        """Add a temporary effect to an object. Delegates to EffectRouter."""
        self._router.add_temporary_effect(obj, effect)

    def apply(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        """Apply an effect. Delegates to EffectRouter."""
        return self._router.apply(effect, context)

