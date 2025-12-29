# axis3/rules/events/types.py

class EventType:
    # ─────────────────────────────────────────────
    # ZONE & OBJECT MOVEMENT
    # ─────────────────────────────────────────────
    ZONE_CHANGE = "zone_change"                 # any object moves zones
    ENTERS_BATTLEFIELD = "enters_battlefield"   # derived from zone change
    LEAVES_BATTLEFIELD = "leaves_battlefield"   # derived from zone change

    # ─────────────────────────────────────────────
    # CARD FLOW
    # ─────────────────────────────────────────────
    DRAW = "draw"                               # player draws cards
    CARD_DRAWN = "card_drawn"
    DISCARD = "discard"                         # player discards
    MILL = "mill"                               # library → graveyard
    SEARCH_LIBRARY = "search_library"
    SHUFFLE_LIBRARY = "shuffle_library"

    # ─────────────────────────────────────────────
    # LIFE & DAMAGE
    # ─────────────────────────────────────────────
    DAMAGE = "damage"              
    DAMAGE_DEALT = "damage_dealt"             # damage dealt
    LIFE_CHANGE = "life_change"    
    LIFE_CHANGED = "life_changed"                 # life gain or loss
    PREVENT_DAMAGE = "prevent_damage"           # optional (replacement-heavy)

    # ─────────────────────────────────────────────
    # COUNTERS & CHARACTERISTICS
    # ─────────────────────────────────────────────
    ADD_COUNTER = "add_counter"
    REMOVE_COUNTER = "remove_counter"
    SET_POWER_TOUGHNESS = "set_power_toughness"
    MODIFY_POWER_TOUGHNESS = "modify_power_toughness"

    # ─────────────────────────────────────────────
    # TAP / UNTAP / STATUS
    # ─────────────────────────────────────────────
    TAP = "tap"
    UNTAP = "untap"
    BECOMES_TAPPED = "becomes_tapped"
    BECOMES_UNTAPPED = "becomes_untapped"

    # ─────────────────────────────────────────────
    # STACK & SPELLS
    # ─────────────────────────────────────────────
    CAST_SPELL = "cast_spell"
    PUT_ON_STACK = "put_on_stack"               # spell or ability
    RESOLVE_STACK_OBJECT = "resolve_stack_object"
    COUNTER_SPELL = "counter_spell"

    # ─────────────────────────────────────────────
    # ABILITIES
    # ─────────────────────────────────────────────
    TRIGGERED_ABILITY = "triggered_ability"     # put on stack
    ACTIVATED_ABILITY = "activated_ability"     # optional (mostly for UI/logging)
    STATIC_ABILITY_APPLIED = "static_ability_applied"

    # ─────────────────────────────────────────────
    # COMBAT
    # ─────────────────────────────────────────────
    DECLARE_ATTACKERS = "declare_attackers"
    DECLARE_BLOCKERS = "declare_blockers"
    COMBAT_DAMAGE = "combat_damage"
    CREATURE_DIES = "creature_dies"              # shortcut for LTB → graveyard

    # ─────────────────────────────────────────────
    # TURN STRUCTURE
    # ─────────────────────────────────────────────
    BEGIN_STEP = "begin_step"
    END_STEP = "end_step"
    BEGIN_PHASE = "begin_phase"
    END_PHASE = "end_phase"
