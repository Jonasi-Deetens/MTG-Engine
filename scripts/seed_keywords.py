#!/usr/bin/env python3
"""
Seed the keywords table with MTG keyword abilities and their parameters.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from db.connection import SessionLocal
from db.models import Keyword

# Comprehensive list of MTG keywords with their parameters
KEYWORDS_DATA = [
    # Simple keywords (no parameters)
    {"name": "flying", "description": "This creature can only be blocked by creatures with flying or reach."},
    {"name": "haste", "description": "This creature can attack and tap the turn it comes under your control."},
    {"name": "trample", "description": "This creature can deal excess combat damage to the player or planeswalker it's attacking."},
    {"name": "vigilance", "description": "Attacking doesn't cause this creature to tap."},
    {"name": "deathtouch", "description": "Any amount of damage this deals to a creature is enough to destroy it."},
    {"name": "lifelink", "description": "Damage dealt by this creature also causes you to gain that much life."},
    {"name": "reach", "description": "This creature can block creatures with flying."},
    {"name": "menace", "description": "This creature can't be blocked except by two or more creatures."},
    {"name": "first strike", "description": "This creature deals combat damage before creatures without first strike."},
    {"name": "double strike", "description": "This creature deals both first-strike and regular combat damage."},
    {"name": "hexproof", "description": "This permanent can't be the target of spells or abilities your opponents control."},
    {"name": "indestructible", "description": "Effects that say 'destroy' don't destroy this permanent. A creature with indestructible can't be destroyed by damage."},
    {"name": "shroud", "description": "This permanent can't be the target of spells or abilities."},
    {"name": "defender", "description": "This creature can't attack."},
    {"name": "flash", "description": "You may cast this spell any time you could cast an instant."},
    
    # Keywords with mana costs
    {"name": "ward", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "number_type": "ward", "description": "Whenever this permanent becomes the target of a spell or ability an opponent controls, counter it unless that player pays the ward cost."},
    {"name": "kicker", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may pay an additional cost as you cast this spell."},
    {"name": "multikicker", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may pay an additional cost any number of times as you cast this spell."},
    {"name": "flashback", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card from your graveyard by paying its flashback cost."},
    {"name": "buyback", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may pay an additional cost as you cast this spell. If you do, put this card into your hand instead of your graveyard as it resolves."},
    {"name": "evoke", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its evoke cost. If you do, it's sacrificed when it enters the battlefield."},
    {"name": "morph", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card face down as a 2/2 creature for 3. Turn it face up any time for its morph cost."},
    {"name": "megamorph", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card face down as a 2/2 creature for 3. Turn it face up any time for its megamorph cost and put a +1/+1 counter on it."},
    {"name": "bestow", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "If you cast this card for its bestow cost, it's an Aura spell with enchant creature."},
    {"name": "awaken", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "If you cast this spell for its awaken cost, also put X +1/+1 counters on target land you control and it becomes a 0/0 Elemental creature with haste."},
    {"name": "overload", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its overload cost. If you do, change its text by replacing all instances of 'target' with 'each'."},
    {"name": "splice", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "As you cast an instant or sorcery spell, you may reveal this card from your hand and pay its splice cost. If you do, add this card's effects to that spell."},
    {"name": "entwine", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "If you cast this spell for its entwine cost, choose both modes instead of one."},
    {"name": "replicate", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "When you cast this spell, copy it for each time you paid its replicate cost."},
    {"name": "surge", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its surge cost if you or a teammate has cast another spell this turn."},
    {"name": "escape", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card from your graveyard by paying its escape cost."},
    {"name": "retrace", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card from your graveyard by discarding a land card in addition to paying its other costs."},
    {"name": "jump-start", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card from your graveyard by discarding a card in addition to paying its other costs."},
    {"name": "disturb", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Cast this card transformed from your graveyard by paying its disturb cost."},
    {"name": "embalm", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Exile this card from your graveyard: Create a token that's a copy of it, except it's white, it has no mana cost, and it's a Zombie in addition to its other types."},
    {"name": "eternalize", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Exile this card from your graveyard: Create a token that's a copy of it, except it's black, it's 4/4, it has no mana cost, and it's a Zombie in addition to its other types."},
    {"name": "unearth", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Return this card from your graveyard to the battlefield. It gains haste. Exile it at the beginning of the end step or if it would leave the battlefield."},
    {"name": "dash", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its dash cost. If you do, it gains haste, and it's returned from the battlefield to its owner's hand at the beginning of the next end step."},
    {"name": "ninjutsu", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Return an unblocked attacker you control to hand: Put this card onto the battlefield from your hand tapped and attacking."},
    {"name": "commander ninjutsu", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Return an unblocked attacker you control to hand: Put this card onto the battlefield from your hand or the command zone tapped and attacking."},
    {"name": "foretell", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "During your turn, you may pay 2 and exile this card from your hand face down. Cast it on a later turn for its foretell cost."},
    {"name": "suspend", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Rather than cast this card from your hand, you may pay its suspend cost and exile it with time counters on it."},
    {"name": "transmute", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Discard this card: Search your library for a card with the same mana value as this card, reveal it, put it into your hand, then shuffle."},
    {"name": "madness", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "If you discard this card, discard it into exile. When you do, cast it for its madness cost or put it into your graveyard."},
    {"name": "blitz", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its blitz cost. If you do, it gains haste and 'When this permanent is put into a graveyard from the battlefield, draw a card.'"},
    {"name": "cleave", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its cleave cost. If you do, remove the words in square brackets."},
    {"name": "spree", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its spree cost plus any number of additional costs."},
    {"name": "outlast", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Tap this creature and pay its outlast cost: Put a +1/+1 counter on it. Activate only as a sorcery."},
    {"name": "scavenge", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Exile this card from your graveyard: Put a number of +1/+1 counters equal to this card's power on target creature. Activate only as a sorcery."},
    {"name": "cycling", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Discard this card: Draw a card."},
    {"name": "equip", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Attach this Equipment to target creature you control. Activate only as a sorcery."},
    {"name": "fortify", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Attach this Fortification to target land you control. Activate only as a sorcery."},
    {"name": "reinforce", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Discard this card: Put a +1/+1 counter on target creature."},
    {"name": "cumulative upkeep", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "At the beginning of your upkeep, put an age counter on this permanent, then sacrifice it unless you pay its upkeep cost for each age counter on it."},
    {"name": "echo", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "At the beginning of your upkeep, if this came under your control since your last upkeep, sacrifice it unless you pay its echo cost."},
    {"name": "prototype", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell for its prototype cost. If you do, it enters the battlefield with the indicated characteristics."},
    {"name": "craft", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Exile this card, three or more other cards from among permanents you control and/or cards in your graveyard: Put this card onto the battlefield transformed."},
    {"name": "disguise", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card face down for 3 as a 2/2 creature with ward 2. Turn it face up any time for its disguise cost."},
    {"name": "plot", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this card from exile for its plot cost."},
    {"name": "saddle", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Tap any number of untapped creatures you control with total power N or greater: This permanent becomes a Mount until end of turn. Activate only as a sorcery."},
    {"name": "reconfigure", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Attach this Equipment to target creature you control. Activate only as a sorcery."},
    {"name": "mutate", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "If you cast this spell for its mutate cost, put it over or under target non-Human creature you own. They mutate into the creature on top plus all abilities from under it."},
    {"name": "encore", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "Exile this card from your graveyard: For each opponent, create a token that's a copy of this card that attacks that opponent this turn if able. They gain haste. Sacrifice them at the beginning of the next end step. Activate only as a sorcery."},
    {"name": "emerge", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "description": "You may cast this spell by sacrificing a creature and paying the emerge cost reduced by that creature's mana value."},
    
    # Keywords with life costs
    {"name": "dredge", "has_cost": True, "has_life_cost": True, "cost_type": "life", "has_number": True, "number_type": "dredge", "description": "If you would draw a card, you may instead mill N cards and return this card from your graveyard to your hand."},
    {"name": "recover", "has_cost": True, "has_life_cost": True, "cost_type": "life", "description": "When a creature is put into your graveyard from the battlefield, you may pay its recover cost. If you do, return this card from your graveyard to your hand. Otherwise, exile this card."},
    
    # Keywords with sacrifice costs
    {"name": "casualty", "has_cost": True, "has_sacrifice_cost": True, "cost_type": "sacrifice", "has_number": True, "number_type": "casualty", "description": "As you cast this spell, you may sacrifice a creature with power N or greater. When you do, copy this spell."},
    {"name": "bargain", "has_cost": True, "has_sacrifice_cost": True, "cost_type": "sacrifice", "description": "You may sacrifice an artifact, enchantment, or token as you cast this spell. If you do, copy it."},
    
    # Keywords with number parameters
    {"name": "annihilator", "has_number": True, "number_type": "annihilator", "description": "Whenever this creature attacks, defending player sacrifices N permanents."},
    {"name": "bloodthirst", "has_number": True, "number_type": "bloodthirst", "description": "This creature enters the battlefield with N +1/+1 counters on it if an opponent was dealt damage this turn."},
    {"name": "absorb", "has_number": True, "number_type": "absorb", "description": "If a source would deal damage to this permanent, prevent N of that damage."},
    {"name": "bushido", "has_number": True, "number_type": "bushido", "description": "Whenever this creature blocks or becomes blocked, it gets +N/+N until end of turn."},
    {"name": "frenzy", "has_number": True, "number_type": "frenzy", "description": "Whenever this creature attacks and isn't blocked, it gets +N/+0 until end of turn."},
    {"name": "melee", "has_number": True, "number_type": "melee", "description": "Whenever this creature attacks, it gets +N/+N until end of turn for each opponent you attacked this turn."},
    {"name": "poisonous", "has_number": True, "number_type": "poisonous", "description": "Whenever this creature deals combat damage to a player, that player gets N poison counters."},
    {"name": "renown", "has_number": True, "number_type": "renown", "description": "When this creature deals combat damage to a player, if it isn't renowned, put N +1/+1 counters on it and it becomes renowned."},
    {"name": "skulk", "has_number": True, "number_type": "skulk", "description": "This creature can't be blocked by creatures with power N or greater."},
    {"name": "toxic", "has_number": True, "number_type": "toxic", "description": "Players dealt combat damage by this creature also get N poison counters."},
    {"name": "modular", "has_number": True, "number_type": "modular", "description": "This enters the battlefield with N +1/+1 counters on it. When it dies, you may put its +1/+1 counters on target artifact creature."},
    {"name": "level up", "has_cost": True, "has_mana_cost": True, "cost_type": "mana", "has_number": True, "number_type": "level", "description": "Level up: Pay the level up cost. Activate only as a sorcery."},
    {"name": "bolster", "has_number": True, "number_type": "bolster", "description": "Choose a creature you control with the least toughness among creatures you control. Put N +1/+1 counters on it."},
    {"name": "support", "has_number": True, "number_type": "support", "description": "Put N +1/+1 counters on each of up to N other target creatures."},
    {"name": "fabricate", "has_number": True, "number_type": "fabricate", "description": "When this creature enters the battlefield, put N +1/+1 counters on it or create N 1/1 colorless Servo artifact creature tokens."},
    {"name": "devour", "has_number": True, "number_type": "devour", "description": "As this enters the battlefield, you may sacrifice any number of creatures. This creature enters the battlefield with N +1/+1 counters on it for each creature sacrificed this way."},
    {"name": "graft", "has_number": True, "number_type": "graft", "description": "This enters the battlefield with N +1/+1 counters on it. Whenever another creature enters the battlefield, you may move a +1/+1 counter from this creature onto it."},
    {"name": "vanishing", "has_number": True, "number_type": "vanishing", "description": "This permanent enters the battlefield with N time counters on it. At the beginning of your upkeep, remove a time counter from it. When the last is removed, sacrifice it."},
    {"name": "fading", "has_number": True, "number_type": "fading", "description": "This permanent enters the battlefield with N fade counters on it. At the beginning of your upkeep, remove a fade counter from it. If you can't, sacrifice it."},
    {"name": "rampage", "has_number": True, "number_type": "rampage", "description": "Whenever this creature becomes blocked, it gets +N/+N until end of turn for each creature blocking it beyond the first."},
    {"name": "afflict", "has_number": True, "number_type": "afflict", "description": "Whenever this creature becomes blocked, defending player loses N life."},
    {"name": "backup", "has_number": True, "number_type": "backup", "description": "When this creature enters the battlefield, put N +1/+1 counters on target creature. That creature gains the abilities of this creature until end of turn."},
    {"name": "squad", "has_number": True, "number_type": "squad", "description": "As an additional cost to cast this spell, you may pay N any number of times. When this creature enters the battlefield, create that many tokens that are copies of it."},
    {"name": "freerunning", "has_number": True, "number_type": "freerunning", "description": "This creature can't be blocked except by creatures with power N or greater."},
    {"name": "gift", "has_number": True, "number_type": "gift", "description": "When this creature enters the battlefield, target creature gets +N/+N until end of turn."},
    {"name": "offspring", "has_number": True, "number_type": "offspring", "description": "When this creature enters the battlefield, create N 1/1 colorless Egg artifact creature tokens."},
    {"name": "ravenous", "has_number": True, "number_type": "ravenous", "description": "When this creature enters the battlefield, if you cast it, you may have it fight target creature you don't control. If that creature would die this turn, exile it instead and put N +1/+1 counters on this creature."},
    
    # Keywords with no parameters
    {"name": "evolve", "description": "Whenever a creature enters the battlefield under your control, if that creature has greater power or toughness than this creature, put a +1/+1 counter on this creature."},
    {"name": "mentor", "description": "Whenever this creature attacks, put a +1/+1 counter on target attacking creature with lesser power."},
    {"name": "riot", "description": "This creature enters the battlefield with your choice of a +1/+1 counter or haste."},
    {"name": "proliferate", "description": "Choose any number of permanents and/or players, then give each another counter of each kind already there."},
    {"name": "undying", "description": "When this creature dies, if it had no +1/+1 counters on it, return it to the battlefield under its owner's control with a +1/+1 counter on it."},
    {"name": "persist", "description": "When this creature dies, if it had no -1/-1 counters on it, return it to the battlefield under its owner's control with a -1/-1 counter on it."},
    {"name": "wither", "description": "This deals damage to creatures in the form of -1/-1 counters."},
    {"name": "infect", "description": "This deals damage to creatures in the form of -1/-1 counters and to players in the form of poison counters."},
    {"name": "flanking", "description": "Whenever this creature becomes blocked by a creature without flanking, the blocking creature gets -1/-1 until end of turn."},
    {"name": "banding", "description": "Any creatures with banding, and up to one without, can attack in a band. Bands are blocked as a group."},
    {"name": "phasing", "description": "This phases in or out before you untap during each of your untap steps."},
    {"name": "aftermath", "description": "Cast this spell only from your graveyard. Then exile it."},
    {"name": "training", "description": "Whenever this creature attacks with another creature with greater power, put a +1/+1 counter on this creature."},
    {"name": "read ahead", "description": "As this Saga enters and after your draw step, add a lore counter. Sacrifice after III."},
    {"name": "impending", "description": "At the beginning of your upkeep, if this permanent has no time counters on it, sacrifice it. Otherwise, remove a time counter from it."},
    {"name": "extort", "description": "Whenever you cast a spell, you may pay {W/B}. If you do, each opponent loses 1 life and you gain life equal to the total life lost this way."},
    {"name": "fuse", "description": "You may cast one or both halves of this card from your hand."},
    {"name": "tribute", "description": "As this creature enters the battlefield, an opponent may have it enter with a +1/+1 counter on it. If that player doesn't, it enters with two +1/+1 counters on it."},
    {"name": "dethrone", "description": "Whenever this creature attacks the player with the most life or tied for most life, put a +1/+1 counter on it."},
    {"name": "enlist", "description": "As this creature attacks, you may tap a nonattacking creature you control without summoning sickness. When you do, this creature gets +X/+Y until end of turn, where X is the tapped creature's power and Y is its toughness."},
    {"name": "space sculptor", "description": "This creature can't be blocked by creatures with flying."},
    {"name": "visit", "description": "When this creature enters the battlefield, draw a card, then discard a card."},
    {"name": "living metal", "description": "As long as this permanent is a Vehicle, it's a 0/0 artifact creature."},
    {"name": "for mirrodin!", "description": "When this Equipment enters the battlefield, create a 2/2 red Rebel creature token, then attach this Equipment to it."},
    {"name": "for mirrodin", "description": "When this Equipment enters the battlefield, create a 2/2 red Rebel creature token, then attach this Equipment to it."},
    {"name": "compleated", "description": "You may pay {BP} rather than pay this spell's mana cost. If you do, it enters the battlefield with a number of oil counters on it equal to the amount of life you paid."},
    {"name": "myriad", "description": "Whenever this creature attacks, for each opponent besides the defending player, you may create a token that's a copy of this creature that's tapped and attacking that player or a planeswalker they control. Exile the tokens at end of combat."},
    {"name": "partner", "description": "You may have two commanders if both have partner."},
    {"name": "companion", "description": "Your starting deck can include one card chosen before the game that isn't part of your deck."},
    {"name": "exploit", "description": "When this creature enters the battlefield, you may sacrifice a creature."},
    {"name": "prowess", "description": "Whenever you cast a noncreature spell, this creature gets +1/+1 until end of turn."},
    {"name": "ingest", "description": "Whenever this creature deals combat damage to a player, that player exiles the top card of their library."},
    {"name": "devoid", "description": "This card has no color."},
    {"name": "improvise", "description": "Your artifacts can help cast this spell. Each artifact you tap after you're done activating mana abilities pays for {1}."},
    {"name": "convoke", "description": "Your creatures can help cast this spell. Each creature you tap while casting this spell pays for {1} or one mana of that creature's color."},
    {"name": "affinity", "description": "This spell costs {1} less to cast for each artifact you control."},
    {"name": "delve", "description": "Each card you exile from your graveyard while casting this spell pays for {1}."},
]

def seed_keywords():
    """Seed the keywords table."""
    db = SessionLocal()
    try:
        # Remove duplicates by name (keep first occurrence)
        seen = set()
        unique_keywords = []
        for kw_data in KEYWORDS_DATA:
            name_lower = kw_data["name"].lower()
            if name_lower not in seen:
                seen.add(name_lower)
                unique_keywords.append(kw_data)
        
        # Clear existing keywords
        db.query(Keyword).delete()
        
        # Insert all keywords
        for kw_data in unique_keywords:
            keyword = Keyword(**kw_data)
            db.add(keyword)
        
        db.commit()
        print(f"Successfully seeded {len(unique_keywords)} unique keywords!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding keywords: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_keywords()

