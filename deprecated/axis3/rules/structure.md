axis3/rules/
│
├── events/
│   ├── __init__.py
│   ├── event.py           # Event base class
│   ├── types.py           # ZONE_CHANGE, DAMAGE, DRAW, LIFE_CHANGE
│   ├── bus.py             # publish / subscribe
│   └── queue.py           # ordered resolution
│
├── atomic/                # Smallest rule units
│   ├── __init__.py
│   ├── zone_change.py     # apply_zone_change(event)
│   ├── damage.py          # apply_damage(event)
│   ├── draw.py            # apply_draw(event)
│   └── life.py            # apply_life_change(event)
│
├── replacement/
│   ├── __init__.py
│   └── apply.py           # apply_replacements(event)
│
├── triggers/
│   ├── __init__.py
│   ├── registry.py        # watches events
│   └── runtime.py         # RuntimeTriggeredAbility
│
├── sba/
│   ├── __init__.py
│   ├── checker.py
│   └── rules.py           # lethal damage, 0 toughness, legend rule
│
├── layers/
│   ├── __init__.py
│   ├── system.py
│   └── layer7.py
│
├── costs/
│   └── mana.py
│
├── stack/
│   ├── __init__.py
│   ├── item.py
│   └── resolver.py
│
└── orchestrator.py        # formerly actions.py
