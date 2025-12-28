# axis3/rules/stack/resolver.py

from axis3.rules.stack.item import StackItem
from axis3.rules.events.event import Event
from axis3.rules.replacement.apply import apply_replacements
from axis3.rules.atomic import zone_change, draw, damage, life
from axis3.rules.sba import run_sbas
from axis3.abilities.triggered import resolve_runtime_triggered_ability

class Stack:
    """
    Represents the stack in the game. LIFO order.
    """
    def __init__(self):
        self.items = []

    def push(self, item: StackItem):
        self.items.append(item)

    def pop(self) -> StackItem:
        return self.items.pop() if self.items else None

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def peek(self) -> StackItem:
        return self.items[-1] if self.items else None


# -----------------------
# Resolver Functions
# -----------------------

def push_to_stack(game_state, stack_item: StackItem):
    """
    Push a spell or ability onto the stack.
    """
    if not hasattr(game_state, "stack") or game_state.stack is None:
        game_state.stack = Stack()
    game_state.stack.push(stack_item)

def resolve_top_of_stack(game_state):
    """
    Resolve the top item on the stack.
    """
    if not game_state.stack or game_state.stack.is_empty():
        return

    item = game_state.stack.pop()

    # Triggered ability? Resolve differently
    if item.is_triggered_ability():
        resolve_runtime_triggered_ability(game_state, item.triggered_ability)
        return

    # Spell or permanent
    obj_id = item.obj_id
    if obj_id is None:
        return

    rt_obj = game_state.objects[obj_id]

    # Determine if permanent (Creature, Artifact, Enchantment, Planeswalker, Land, Battle)
    is_permanent = any(t in ("Creature", "Artifact", "Enchantment", "Planeswalker", "Battle", "Land")
                       for t in rt_obj.characteristics.types)

    if is_permanent:
        # Move permanent to battlefield
        event = Event(
            type="zone_change",
            payload={
                "obj_id": rt_obj.id,
                "from_zone": rt_obj.zone,
                "to_zone": "BATTLEFIELD",
                "controller": item.controller
            }
        )
        event = apply_replacements(game_state, event)
        zone_change.apply_zone_change(game_state, event)
    else:
        # Non-permanent: move to graveyard
        event = Event(
            type="zone_change",
            payload={
                "obj_id": rt_obj.id,
                "from_zone": rt_obj.zone,
                "to_zone": "GRAVEYARD",
                "controller": item.controller
            }
        )
        event = apply_replacements(game_state, event)
        zone_change.apply_zone_change(game_state, event)

    # Run state-based actions after resolution
    run_sbas(game_state)

def resolve_stack(game_state):
    """
    Resolve all items on the stack (LIFO) until empty.
    """
    while game_state.stack and not game_state.stack.is_empty():
        resolve_top_of_stack(game_state)
