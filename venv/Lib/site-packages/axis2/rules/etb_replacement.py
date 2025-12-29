import re
from axis2.schema import ReplacementEffect

AS_ENTERS_PATTERN = re.compile(
    r"as\s+this\s+.*?enters\s+the\s+battlefield[, ]\s*(.*)",
    re.IGNORECASE
)

COPY_AS_ENTERS_PATTERN = re.compile(
    r"enter\s+as\s+a\s+copy\s+of\s+any\s+creature\s+on\s+the\s+battlefield",
    re.IGNORECASE
)

YOU_MAY_HAVE_PATTERN = re.compile(
    r"you\s+may\s+have\s+this\s+enter\s+the\s+battlefield\s+as\s*(.*)",
    re.IGNORECASE
)

ENTERS_WITH_PATTERN = re.compile(
    r"(?:this creature|this|it)\s+enters(?:\s+the\s+battlefield)?\s+with\s+(.*?)(?:\s+counters?\b.*)?",
    re.IGNORECASE
)

def parse_primal_clay_options(text: str):
    """
    Extracts the three forms from Primal Clay's ETB text.
    """
    options = []
    parts = text.split(", or")
    for p in parts:
        p = p.strip().lstrip("a ").strip()
        # Extract P/T
        m = re.search(r"(\d+)/(\d+)", p)
        if not m:
            continue
        power = int(m.group(1))
        toughness = int(m.group(2))

        # Extract types
        types = []
        if "artifact" in p:
            types.append("Artifact")
        if "creature" in p:
            types.append("Creature")
        if "wall" in p:
            types.append("Wall")

        # Extract abilities
        abilities = []
        if "flying" in p:
            abilities.append("flying")
        if "defender" in p:
            abilities.append("defender")

        options.append({
            "power": power,
            "toughness": toughness,
            "types": types,
            "abilities": abilities,
        })

    return options

def derive_etb_replacement_effects(oracle_text: str):
    if not oracle_text:
        return []

    effects = []

    # 1. Choose a color
    if "choose a color" in oracle_text.lower():
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="choose_color",
                extra={"choices": ["white", "blue", "black", "red", "green"]}
            )
        )

    # 2. Choose a creature type
    if "choose a creature type" in oracle_text.lower():
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="choose_creature_type",
                extra={"choices": "all_creature_types"}  # Axis3 resolves this
            )
        )

    # 3. Choose a player
    if "choose an opponent" in oracle_text.lower() or "choose a player" in oracle_text.lower():
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="choose_player",
                extra={"choices": "players"}
            )
        )

    # 4. Enters with counters
    m = re.search(r"enters the battlefield with (.*) counters?", oracle_text, re.I)
    if m:
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="enters_with_counters",
                extra={"text": m.group(1)}
            )
        )

    # 5. Copy effects
    if "enter the battlefield as a copy" in oracle_text.lower():
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="copy_as_enters",
                extra={"legal_targets": ["creature", "artifact", "planeswalker"]}  # Axis3 filters
            )
        )

    # 5b. Copy-as-enters effects (Progenitor Mimic, Clone variants)
    if COPY_AS_ENTERS_PATTERN.search(oracle_text):
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="copy_as_enters",
                extra={
                    "legal_targets": ["creature"],
                    "optional": True
                }
            )
        )

    # 6. Special-case cards (Primal Clay, Primal Plasma)
    if "primal clay" in oracle_text.lower():
        payload = AS_ENTERS_PATTERN.search(oracle_text).group(1)
        options = parse_primal_clay_options(payload)
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="choose_form",
                extra={"options": options}
            )
        )

    m = ENTERS_WITH_PATTERN.search(oracle_text)
    if m:
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="enters_with_counters",
                extra={"text": m.group(1).strip()}
            )
        )

    m = AS_ENTERS_PATTERN.search(oracle_text)
    if m:
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="as_enters",
                extra={"text": m.group(1).strip()}
            )
        )

    m = YOU_MAY_HAVE_PATTERN.search(oracle_text)
    if m:
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="optional_as_enters",
                extra={"text": m.group(1).strip()}
            )
        )

    if "enters the battlefield tapped" in oracle_text or "enters tapped" in oracle_text:
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="enters_tapped",
                extra={}
            )
        )


    if "enters the battlefield as" in oracle_text.lower():
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="enters_as",
                extra={"text": oracle_text}
            )
        )

    m = re.search(r"enters(?: the battlefield)? with (?:a|an) ([a-z]+) counter", oracle_text, re.I)
    if m:
        effects.append(
            ReplacementEffect(
                type="enter_replacement",
                subject="this",
                event="enter_battlefield",
                replacement="enters_with_single_counter",
                extra={"counter": m.group(1)}
            )
        )

    return effects
