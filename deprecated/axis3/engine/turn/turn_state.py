from dataclasses import dataclass, field
from axis3.engine.turn.phases import Phase
from axis3.engine.turn.steps import Step

@dataclass
class TurnState:
    active_player: int = 0
    phase: Phase = Phase.BEGINNING
    step: Step = Step.UNTAP
    turn_number: int = 1

    stack_empty_since_last_priority: bool = True

    lands_played_this_turn: dict[int, int] = field(
        default_factory=lambda: {0: 0, 1: 0}
    )

    def is_main_phase(self) -> bool: 
        return self.phase in (Phase.PRECOMBAT_MAIN, Phase.POSTCOMBAT_MAIN) 
    def is_precombat_main(self) -> bool: 
        return self.phase == Phase.PRECOMBAT_MAIN 
    def is_postcombat_main(self) -> bool: 
        return self.phase == Phase.POSTCOMBAT_MAIN 
    def is_combat_phase(self) -> bool: 
        return self.phase == Phase.COMBAT 
    def is_end_step(self) -> bool: 
        return self.phase == Phase.ENDING and self.step == Step.END