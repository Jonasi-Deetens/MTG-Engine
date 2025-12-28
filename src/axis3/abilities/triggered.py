# axis3/abilities/triggered.py

class RuntimeTriggeredAbility:
    """
    Runtime representation of triggered abilities.
    Usually pushed to stack by triggers/registry.
    """
    def __init__(self, source_id: int, controller: int, axis2_trigger):
        self.source_id = source_id
        self.controller = controller
        self.axis2_trigger = axis2_trigger  # Original Axis2 trigger
