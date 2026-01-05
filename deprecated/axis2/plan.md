# Refactoring Plan: effects.py

## Current Problems

1. **1308 lines** - Too large to maintain
2. **Hardcoded parser chain** (lines 92-281) - 30+ sequential if-statements
3. **No error handling** - Crashes on malformed input
4. **Debug prints** - 8 print statements left in code
5. **No abstraction** - Each parser is standalone, no common interface
6. **Inconsistent returns** - Some return None, some return lists, some return single objects
7. **Regex scattered** - Patterns defined near usage, hard to find/reuse
8. **Tight coupling** - Direct imports and calls to other modules
9. **No priority system** - Parser order matters but isn't explicit
10. **Recursive calls** - `parse_effect_text` calls itself (lines 117, 125) without depth limit
    - ⚠️ **RULE**: Dispatcher must never recurse. If recursion needed, it belongs in specific parsers with bounded depth.

## Proposed Structure

```
axis2/parsing/effects/
├── __init__.py              # Public API
├── base.py                  # Parser interface, Result types
├── registry.py              # Parser registry with priority
├── dispatcher.py            # Main entry point (replaces parse_effect_text)
├── utils.py                 # Shared utilities (split_effect_sentences, etc.)
├── damage.py                # Damage effects
├── search.py                # Search effects
├── tokens.py                # Token creation
├── zone_changes.py          # ChangeZoneEffect, Transform, Destroy
├── counters.py              # Counter effects
├── life.py                  # Life gain effects
├── draw.py                  # Draw effects
├── mana.py                  # Mana effects
├── look_pick.py             # LookAndPickEffect
├── protection.py            # Protection effects
└── patterns.py              # Shared regex patterns
```

## Implementation Strategy

### Phase 1: Create Base Infrastructure

#### 1.1 Create `base.py` - Parser Interface

```python
from typing import Protocol, Optional, List
from dataclasses import dataclass, field
from axis2.schema import Effect, ParseContext

# NOTE: ParseContext should have current_effect_text field for diagnostics
# This gives us:
# - Error reports with context
# - Better test failure messages
# - Easier AST migration later
#
# If ParseContext doesn't have this yet, we'll need to add it or create
# a wrapper that includes it.

@dataclass
class ParseResult:
    """Standardized return type for all parsers"""
    matched: bool = False  # Explicit intent: did parser recognize this pattern?
    effect: Optional[Effect] = None
    effects: List[Effect] = None  # For parsers that return multiple
    consumed_text: Optional[str] = None  # Text that was parsed
    # NOTE: consumed_text may later be a substring once partial parsing /
    # remainder parsing is supported. Currently it's the full text, but
    # parsers that consume only part of the input will set it to the consumed portion.
    errors: List[str] = None

    @property
    def is_success(self) -> bool:
        """
        Success means: parser matched AND produced valid effect(s) AND no errors.

        This allows for:
        - matched=True, effect=None, errors=[...] → "recognized but invalid"
        - matched=False → "didn't recognize this pattern"
        - matched=True, effect=Effect, errors=[] → "success"
        """
        return self.matched and not self.errors and \
               (self.effect is not None or
                (self.effects is not None and len(self.effects) > 0))

    @property
    def all_effects(self) -> List[Effect]:
        """Returns all effects as a list"""
        result = []
        if self.effect:
            result.append(self.effect)
        if self.effects:
            result.extend(self.effects)
        return result

class EffectParser(Protocol):
    """Interface all effect parsers must implement"""
    priority: int  # Higher = tried first

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        """
        Quick check if this parser might match.

        ⚠️ CRITICAL: This must be CHEAP - no expensive operations!

        MUST NOT:
        - Run regex with groups
        - Call subject parsing
        - Allocate schema objects
        - Do any actual parsing work

        SHOULD:
        - Simple keyword checks: "damage" in text.lower()
        - Basic string operations
        - Fast boolean logic

        This is called for EVERY parser on EVERY text, so performance matters.
        """
        ...

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """Parse the text, return ParseResult"""
        ...
```

#### 1.2 Create `registry.py` - Parser Registry

```python
from typing import List
from .base import EffectParser, ParseResult
from axis2.schema import ParseContext

class ParserRegistry:
    """Manages all effect parsers with priority ordering"""

    def __init__(self):
        self._parsers: List[EffectParser] = []

    def register(self, parser: EffectParser):
        """Register a parser (automatically sorted by priority)"""
        self._parsers.append(parser)
        self._parsers.sort(key=lambda p: p.priority, reverse=True)

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """
        Try all parsers in priority order, return the best match.

        Currently returns first successful match (highest priority).
        This leaves room for future improvements:
        - Composite parsing (multiple parsers for one text)
        - Partial consumption (parser consumes part, remainder parsed separately)
        - Better diagnostics (track all attempts, not just first success)
        """
        text = text.strip()
        if not text:
            return ParseResult()

        # Quick filter: only try parsers that might match
        candidates = [p for p in self._parsers if p.can_parse(text, ctx)]

        # Keep track of best match (currently = first success)
        # Future: could track multiple matches, partial matches, etc.
        best = None
        for parser in candidates:
            result = parser.parse(text, ctx)
            if result.is_success:
                best = result
                break  # Current behavior: return first success
                # Future: could continue to find better matches or composite parsers

        if best:
            return best

        # No parser matched
        return ParseResult(
            matched=False,
            errors=[f"No parser matched: {text[:50]}..."]
        )

    def parse_all(self, texts: List[str], ctx: ParseContext) -> List[ParseResult]:
        """Parse multiple texts"""
        return [self.parse(text, ctx) for text in texts]

# Global registry instance
_registry = ParserRegistry()

def register_parser(parser: EffectParser):
    """Convenience function to register parsers"""
    _registry.register(parser)

def get_registry() -> ParserRegistry:
    """Get the global registry"""
    return _registry
```

#### 1.3 Create `dispatcher.py` - Main Entry Point

```python
from typing import List
from .base import ParseResult
from .registry import get_registry
from .utils import split_effect_sentences
from axis2.schema import Effect, ParseContext
from axis2.parsing.conditional_effects import parse_conditional
import logging

logger = logging.getLogger(__name__)

def parse_effect_text(text: str, ctx: ParseContext) -> List[Effect]:
    """
    Main entry point - replaces the old parse_effect_text.
    Now uses registry pattern instead of hardcoded chain.

    ⚠️ RULE: This function MUST NEVER call itself recursively.
    If recursion is needed (e.g., parsing remainder after partial match),
    it belongs inside a specific parser with bounded depth.
    """
    if not text:
        return []

    # Add current text to context for diagnostics
    # This enables better error messages and test failures
    # NOTE: Requires ParseContext.current_effect_text field in schema
    # If ParseContext is immutable, create new context with this field set
    if hasattr(ctx, 'current_effect_text'):
        # Set current text for diagnostic purposes
        # (Would need to create new context if immutable)
        pass  # Implementation depends on ParseContext mutability

    # Check for conditional effects first (special case)
    cond = parse_conditional(text, ctx)
    if cond:
        return [cond]

    # Split into sentences
    sentences = split_effect_sentences(text)

    # Special-case global effects that span sentences.
    # TODO: This should eventually become a parser-level concern.
    # For now, we handle look-and-pick effects that need the full text
    # before sentence splitting. This is technical debt, not architecture.
    registry = get_registry()
    look_pick_result = registry.parse(text, ctx)
    if look_pick_result.is_success and "look at" in text.lower():
        effects = look_pick_result.all_effects
    else:
        effects = []

    # Parse each sentence
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue

        # Try conditional first
        cond = parse_conditional(s, ctx)
        if cond:
            effects.append(cond)
            continue

        # Use registry to find matching parser
        result = registry.parse(s, ctx)
        if result.is_success:
            effects.extend(result.all_effects)
        else:
            logger.warning(f"Failed to parse: {s[:50]}...")
            if result.errors:
                logger.debug(f"Errors: {result.errors}")

    return effects
```

### Phase 2: Extract Individual Parsers

#### 2.1 Example: `damage.py`

```python
import re
from typing import Optional
from .base import EffectParser, ParseResult
from axis2.schema import DealDamageEffect, ParseContext
from axis2.parsing.subject import subject_from_text

DAMAGE_RE = re.compile(
    r"deals?\s+(?P<amount>\d+)\s+damage\s+to\s+(?P<subject>.+?)(?:\.|,|;|$)",
    re.IGNORECASE,
)

class DamageParser(EffectParser):
    """Parses damage effects: 'deals N damage to target creature'"""
    priority = 50  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY - no regex, no parsing
        return "damage" in text.lower() and "deal" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = DAMAGE_RE.search(text.lower())
        if not m:
            return ParseResult(matched=False)

        try:
            amount = int(m.group("amount"))
            subject_text = m.group("subject").strip()
            subject = subject_from_text(subject_text, ctx)

            return ParseResult(
                matched=True,
                effect=DealDamageEffect(amount=amount, subject=subject),
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,  # We recognized the pattern, but parsing failed
                errors=[f"Failed to parse damage: {e}"]
            )
```

#### 2.2 Example: `search.py`

```python
import re
from .base import EffectParser, ParseResult
from axis2.schema import SearchEffect, ChangeZoneEffect, Subject, ParseContext

# All search-related regexes here
SEARCH_RE = re.compile(...)
SEARCH_BASIC_LAND_RE = re.compile(...)
# etc.

class SearchParser(EffectParser):
    """Parses search effects"""
    priority = 80  # High priority (search is specific)

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "search" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        # Try different search patterns
        # Return ParseResult with effects list if multiple effects

        # ⚠️ If this parser needs to parse remainder text (like Lightpaws search),
        # it can call registry.parse() internally with bounded depth:
        #
        # MAX_RECURSION_DEPTH = 3
        # if remainder and depth < MAX_RECURSION_DEPTH:
        #     remainder_result = registry.parse(remainder, ctx, depth=depth+1)
        #     effects.extend(remainder_result.all_effects)
        ...
```

#### 2.3 Example: `tokens.py`

```python
from .base import EffectParser, ParseResult
from axis2.schema import CreateTokenEffect, ParseContext

class TokenParser(EffectParser):
    priority = 60

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "create" in text.lower() and "token" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        # Parse token creation
        ...
```

### Phase 3: Create Utility Modules

#### 3.1 `utils.py` - Shared Utilities

```python
import re
from typing import List

def split_effect_sentences(text: str) -> List[str]:
    """Extracted from original - no changes needed"""
    text = text.replace("\n", " ")
    text = re.sub(r"(?<!this way,)\s+then\b", ". then", text, flags=re.I)
    parts = re.split(r"[.;]", text)
    return [p.strip() for p in parts if p.strip()]

# Other shared utilities...
```

#### 3.2 `patterns.py` - Shared Regex Patterns

```python
"""Centralized regex patterns for reuse across parsers"""
import re

# Number words
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
}

# Color mapping
COLOR_MAP = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

# Common patterns
OPTIONAL_RE = re.compile(r"you may", re.IGNORECASE)
TARGET_RE = re.compile(r"\btarget\b", re.IGNORECASE)
# etc.
```

### Phase 4: Migration Strategy

#### 4.1 Create `__init__.py` - Backward Compatibility

```python
"""
Backward-compatible API for effects parsing.
Old code can still import parse_effect_text from here.
"""
from .dispatcher import parse_effect_text
from .base import ParseResult, EffectParser
from .registry import register_parser, get_registry

# Register all parsers on import
from . import damage, search, tokens, zone_changes, counters, life, draw, mana, look_pick, protection

__all__ = ['parse_effect_text', 'ParseResult', 'EffectParser', 'register_parser']
```

#### 4.2 Register All Parsers - EXPLICIT REGISTRATION ONLY

⚠️ **IMPORTANT**: Use explicit registration in `__init__.py`. Do NOT use auto-registration on import.

**Why explicit registration:**

- Predictable import order
- Explicit control over parser priority/order
- No "why did this parser load twice?" bugs
- Easier to debug registration issues
- Implicit registration always causes problems later

```python
# effects/__init__.py
def _register_all_parsers():
    """
    Explicitly register all parsers in priority order.
    This gives us full control over registration and makes dependencies clear.
    """
    from . import damage, search, tokens, zone_changes, counters, life, draw, mana, look_pick, protection

    # Register in priority order (high to low)
    # Very specific patterns first
    register_parser(search.LightpawsSearchParser())  # priority 100+
    register_parser(look_pick.LookAndPickParser())   # priority 90+
    register_parser(search.SearchParser())            # priority 80+

    # Common effects
    register_parser(tokens.TokenParser())             # priority 60+
    register_parser(damage.DamageParser())            # priority 50+
    register_parser(counters.CounterParser())         # priority 50+

    # Generic effects
    register_parser(zone_changes.ZoneChangeParser())  # priority 40+
    register_parser(draw.DrawParser())                # priority 30+
    register_parser(mana.ManaParser())                # priority 30+

    # etc.

_register_all_parsers()
```

**DO NOT** add auto-registration in individual parser files. Keep parsers as pure classes.

## Priority Order (High to Low)

1. **100+**: Very specific patterns (Lightpaws search, specific card effects)
2. **80-99**: Specific effects (Search, LookAndPick, Transform)
3. **50-79**: Common effects (Damage, Tokens, Counters)
4. **30-49**: Generic effects (Zone changes, Draw)
5. **10-29**: Fallback parsers (Simple text matching)
6. **0-9**: Catch-all parsers (should rarely be needed)

## Future-Proofing Considerations

### 1. Registry Best Match (Not Just First Success)

- Current: Returns first successful match (highest priority)
- Future: Could track multiple matches for composite parsing
- Future: Could support partial consumption (parser consumes part, remainder parsed)
- Implementation leaves room for these improvements without breaking changes

### 2. Partial Consumption Support

- `consumed_text` currently = full text
- Future: May be substring when parsers only consume part of input
- Comment added to document this future capability

### 3. Global Effects Technical Debt

- Look-and-pick effects that span sentences are special-cased in dispatcher
- Marked as technical debt - should become parser-level concern eventually
- Isolated and documented, not architectural flaw

### 4. Diagnostic Context

- ParseContext should include `current_effect_text` for better error messages
- Enables better test failure messages and error reporting
- Optional but cheap to add - highly recommended
- **Implementation**: Add to `axis2/schema.py`:
  ```python
  @dataclass
  class ParseContext:
      # ... existing fields ...
      current_effect_text: Optional[str] = None  # For diagnostics
  ```

## Important Rules & Constraints

### 1. ParseResult.matched Flag

- **Always set `matched=True`** when parser recognizes a pattern (even if parsing fails)
- Allows distinction between "didn't recognize" vs "recognized but invalid"
- Enables better diagnostics and error reporting

### 2. can_parse() Must Stay Cheap

- **MUST NOT**: Run regex with groups, call subject parsing, allocate objects
- **MUST**: Use simple keyword checks, basic string operations
- Called for every parser on every text - performance critical

### 3. Explicit Registration Only

- **NO auto-registration** on import
- **YES explicit registration** in `__init__.py`
- Gives control over order, prevents duplicate registration bugs

### 4. No Recursion in Dispatcher

- `parse_effect_text()` must never call itself
- If recursion needed (e.g., parsing remainder after partial match), it belongs in specific parsers
- Recursive parsers must have bounded depth (e.g., MAX_DEPTH=3) to prevent infinite loops
- Example: Lightpaws search parser that needs to parse remainder text after finding search pattern

## Benefits of This Refactoring

1. **Modularity** - Each parser in its own file, easy to find/modify
2. **Testability** - Can test each parser independently
3. **Extensibility** - Add new parsers by creating new file and registering
4. **Maintainability** - 1308 lines → ~10 files of ~100-200 lines each
5. **Error Handling** - ParseResult includes errors, can track failures
6. **Priority System** - Explicit control over parser order
7. **No Hardcoded Chain** - Registry pattern is flexible
8. **Removes Debug Prints** - Use proper logging
9. **Consistent Returns** - All parsers return ParseResult
10. **Reusable Patterns** - Centralized regex patterns

## Migration Steps

1. Create new directory structure
2. Implement base.py, registry.py, dispatcher.py
3. Extract first parser (e.g., damage.py) as proof of concept
4. Test that it works with existing code
5. Extract remaining parsers one by one
6. Update imports in builder.py
7. Remove old effects.py
8. Add comprehensive tests

## Testing Strategy

```python
# tests/test_effects_damage.py
def test_damage_parser():
    parser = DamageParser()
    ctx = ParseContext(...)

    result = parser.parse("deals 3 damage to target creature", ctx)
    assert result.is_success
    assert isinstance(result.effect, DealDamageEffect)
    assert result.effect.amount == 3

def test_damage_parser_invalid():
    parser = DamageParser()
    ctx = ParseContext(...)

    result = parser.parse("not a damage effect", ctx)
    assert not result.is_success
    assert result.effect is None
```

This refactoring transforms a monolithic file into a maintainable, extensible parser system while preserving all existing functionality.
