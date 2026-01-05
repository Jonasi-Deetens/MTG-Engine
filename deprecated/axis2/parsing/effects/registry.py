# axis2/parsing/effects/registry.py

from typing import List
from .base import EffectParser, ParseResult
from axis2.schema import ParseContext
from axis2.parsing.base_registry import BaseParserRegistry

class ParserRegistry(BaseParserRegistry):
    """Manages all effect parsers with priority ordering"""
    
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
        
        # Find candidates using base class method
        candidates = self._find_candidates(text, ctx)
        
        # Try parsers using base class method
        best = self._try_parsers(candidates, lambda p: p.parse(text, ctx))
        
        if best:
            print(f"[DEBUG Registry] Parser matched, got {len(best.all_effects)} effects")
            # Validate the parsed effect(s) before returning
            from axis2.validation import validate_effect
            validation_errors = []
            for effect in best.all_effects:
                errors = validate_effect(effect)
                validation_errors.extend(errors)
                if errors:
                    print(f"[DEBUG Registry] Validation errors for effect {type(effect).__name__}: {errors}")
            if validation_errors:
                print(f"[DEBUG Registry] Validation failed, marking as not matched. Errors: {validation_errors}")
                best.errors.extend(validation_errors)
                # Don't mark as success if validation fails
                best.matched = False
            else:
                print(f"[DEBUG Registry] Validation passed, returning {len(best.all_effects)} effects. matched={best.matched}, is_success={best.is_success}")
            return best
        
        # No parser matched - include parser names in error for better diagnostics
        parser_names = [type(p).__name__ for p in candidates[:3]]  # Show first 3 attempted
        error_msg = self._get_error_message(text)
        if parser_names:
            error_msg += f" (tried: {', '.join(parser_names)})"
        
        return ParseResult(
            matched=False,
            errors=[error_msg]
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

