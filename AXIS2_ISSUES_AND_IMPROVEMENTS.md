# Axis2 Schema and Parser Issues & Improvements

## Critical Schema Issues (FIXED)

### 1. ✅ **Duplicate Field Definition (BUG) - FIXED**
**Location:** `schema.py` lines 408 and 410
- **Problem:** `ContinuousEffect` had `rule_change` defined twice with different types
- **Fix:** Removed duplicate, kept only `Optional[RuleChangeData]`

### 2. ✅ **Type Mismatch: DealDamageEffect.subject - FIXED**
**Location:** `schema.py` line 239
- **Problem:** Schema said `str` but parser creates `Subject` object
- **Fix:** Changed schema to `subject: Subject` for consistency

### 3. ✅ **Type Mismatch: TriggeredAbility.event - FIXED**
**Location:** `schema.py` line 328
- **Problem:** Type said `str` but code uses event objects or string `"attacks"`
- **Fix:** Changed to `Optional[Union[ZoneChangeEvent, DealsDamageEvent, EntersBattlefieldEvent, LeavesBattlefieldEvent, CastSpellEvent, str]]`

### 4. ✅ **GainLifeEffect.amount Type - FIXED**
**Location:** `schema.py` line 276
- **Problem:** Was `str`, inconsistent with other effects
- **Fix:** Changed to `Union[int, SymbolicValue]` for consistency

### 5. ✅ **ContinuousEffect.abilities Type - FIXED**
**Location:** `schema.py` line 403
- **Problem:** Was `Optional[list[str]]` but should be `List[GrantedAbility]`
- **Fix:** Changed to `Optional[List[GrantedAbility]]`

### 6. ✅ **ContinuousEffect.applies_to - FIXED**
**Location:** `schema.py` line 395
- **Problem:** Was `Subject | str` (required), should be optional
- **Fix:** Changed to `Optional[Union[Subject, str]]` with default `None`

## Parser Issues (FIXED)

### 7. ✅ **Debug Print Statements - FIXED**
**Location:** Multiple files
- **Removed from:**
  - `subject.py` (2 prints)
  - `conditional_effects.py` (9 prints)
  - `targeting.py` (1 print)
  - `spell_continuous_effects.py` (1 print)
- **Still need to remove from:** `effects.py` (old file - 13 prints)

### 8. ✅ **GainLifeEffect Amount Parsing - FIXED**
**Location:** `parsing/effects/life.py`
- **Problem:** Was parsing as string, now parses as integer
- **Fix:** Updated regex to capture digits and convert to int

## Remaining Issues

### 9. **Old effects.py File Still Exists**
**Location:** `src/axis2/parsing/effects.py` (1307 lines)
- **Problem:** Old monolithic file still exists alongside new `effects/` package
- **Impact:** Python will use the package, but the old file is confusing and has debug prints
- **Fix:** Should be deleted or replaced with simple re-export (like we did for other modules)

### 10. **Inconsistent Type Annotations**
**Location:** Throughout `schema.py`
- **Problem:** Mix of `Optional[T]` and `T | None`, `Dict` and `dict`, `List` and `list`
- **Recommendation:** Standardize on one style (prefer `Optional[T]`, `Dict`, `List` for Python < 3.9 compatibility)

### 11. **Missing Type Hints**
**Location:** Various functions
- **Problem:** Some functions missing return type hints
- **Examples:**
  - `parse_modes()` - missing return type hint
  - `parse_cost_string()` - returns `List` but not typed
  - Various helper functions

### 12. **Subject Serialization**
**Problem:** No standard way to convert `Subject` to string when needed
- **Current:** Some effects expect `str`, some expect `Subject`
- **Fix:** Add `Subject.to_string()` method or `subject_to_string()` helper

### 13. **Shared Constants Duplication**
**Problem:** Constants like `NUMBER_WORDS`, `COLOR_MAP` are duplicated across modules
- **Location:** `continuous_effects/patterns.py`, `static_effects/patterns.py`, `effects/patterns.py`, etc.
- **Fix:** Create `axis2/parsing/common.py` or `axis2/constants.py` for shared constants

### 14. **Validation Layer Missing**
**Problem:** No validation that parsed effects are semantically valid
- **Examples:**
  - Negative damage amounts
  - Invalid zone names
  - Invalid subject scopes
- **Fix:** Add validation methods to Effect classes or create validator functions

### 15. **Error Messages Could Be Better**
**Problem:** Error messages in `ParseResult` are generic
- **Current:** `"No parser matched: {text[:50]}..."`
- **Better:** Include parser name, what was tried, context, etc.

### 16. **Type Safety Issues**
**Problem:** Many fields use `Any`, `object`, or untyped `dict`
- **Examples:**
  - `SpecialAction.cost: Optional[object]`
  - `SpecialAction.effects: List[object]`
  - `ConditionalEffect.effects: List[object]`
- **Fix:** Use proper types (e.g., `Dict[str, Any]` instead of `dict`, typed dicts for specific structures)

### 17. **Inconsistent Error Handling**
**Problem:** Some parsers catch exceptions, some don't. Some return errors, some don't.
- **Fix:** Standardize error handling across all parsers

### 18. **Missing Validation in Parsers**
**Problem:** No validation that parsed values are reasonable
- **Examples:**
  - Damage amount > 0
  - Valid zone names
  - Valid subject scopes
- **Fix:** Add validation in parsers or schema constructors

## Structural Improvements Needed

### 19. **Subject Helper Functions**
**Problem:** No standard way to:
- Convert Subject to string representation
- Check if Subject matches a filter
- Serialize Subject for storage
- **Fix:** Add helper functions or methods to Subject class

### 20. **Better Abstraction for Event Types**
**Problem:** Trigger events are mixed types (objects vs strings)
- **Fix:** Create a base `TriggerEvent` class or use a tagged union pattern

### 21. **Parser Testing Infrastructure**
**Problem:** No standardized way to test parsers
- **Fix:** Create test utilities for parser testing (mock ParseContext, test fixtures, etc.)

### 22. **Documentation**
**Problem:** Missing docstrings for many schema classes
- **Fix:** Add comprehensive docstrings explaining what each field means and valid values

## Priority Summary

### ✅ High Priority (FIXED)
1. ✅ Fix duplicate `rule_change` field
2. ✅ Fix `DealDamageEffect.subject` type
3. ✅ Fix `TriggeredAbility.event` type
4. ✅ Remove debug print statements (mostly done)
5. ✅ Fix `GainLifeEffect.amount` type
6. ✅ Fix `ContinuousEffect.abilities` type

### Medium Priority (Remaining)
7. Delete or update old `effects.py` file
8. Standardize type annotations
9. Add missing type hints
10. Create shared constants module
11. Add Subject serialization helper

### Low Priority (Future Improvements)
12. Add validation layer
13. Improve error messages
14. Better error handling standardization
15. Add comprehensive documentation
