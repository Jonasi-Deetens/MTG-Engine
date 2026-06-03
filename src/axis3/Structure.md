src/
│
├── axis3/
│ ├── **init**.py
│ │
│ ├── state/ # All runtime state lives here
│ │ ├── **init**.py
│ │ ├── game_state.py # GameState, PlayerState, TurnState
│ │ ├── zones.py # Zone enums + zone helpers
│ │ ├── objects.py # RuntimeObject, RuntimeSpell, RuntimePermanent
│ │ └── characteristics.py # P/T, colors, types, counters, etc.
│ │
│ ├── rules/ # All rules logic lives here
│ │ ├── **init**.py
│ │ ├── actions.py # Atomic actions (draw, cast, move, tap, etc.)
│ │ ├── events.py # Event bus + event definitions
│ │ ├── triggers.py # Trigger evaluation + queueing
│ │ ├── replacement.py # Replacement effect application
│ │ ├── sba.py # State-based actions
│ │ ├── layers.py # Layer system (7 layers + dependency)
│ │ ├── costs.py # Mana costs, alternative costs, reductions
│ │ ├── combat.py # Combat steps, damage assignment
│ │ └── stack.py # Stack object + resolution logic
│ │
│ ├── abilities/ # Runtime ability objects
│ │ ├── **init**.py
│ │ ├── activated.py # RuntimeActivatedAbility
│ │ ├── triggered.py # RuntimeTriggeredAbility
│ │ ├── static.py # RuntimeStaticAbility
│ │ └── keyword.py # Keyword ability runtime hooks
│ │
│ ├── engine/ # High-level engine orchestration
│ │ ├── **init**.py
│ │ ├── engine.py # Main game loop + priority system
│ │ ├── turn.py # Turn structure, phases, steps
│ │ └── controller.py # Player decision interface (AI or human)
│ │
│ └── translate/ # Axis2 → Axis3 translation layer
│ ├── **init**.py
│ ├── loader.py # Build RuntimeObjects from Axis2
│ └── ability_builder.py # Convert Axis2 abilities → runtime abilities
