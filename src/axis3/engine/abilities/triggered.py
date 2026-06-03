# axis3/engine/abilities/triggered.py

from axis3.rules.events.event import Event


class RuntimeTriggeredAbility:
    """Runtime representation of a triggered ability."""

    def __init__(self, source_id: str, controller: int, axis2_trigger):
        self.source_id = source_id
        self.controller = controller
        self.axis2_trigger = axis2_trigger

    def resolve(self, game_state):
        effects = getattr(self.axis2_trigger, "effects", []) or []
        game_state.effect_executor.execute_all(
            effects,
            self.source_id,
            self.controller,
        )
