# axis2/parsing/continuous_effects/registry.py

from typing import List, Optional
from .base import ContinuousEffectParser, ParseResult
from axis2.schema import ParseContext
from axis2.parsing.base_registry import BaseParserRegistry

class ParserRegistry(BaseParserRegistry):
    """Manages all continuous effect parsers with priority ordering"""
    
    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
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
        best = self._try_parsers(
            candidates, 
            lambda p: p.parse(text, ctx, applies_to, condition, duration)
        )
        
        if best:
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
    
    def parse_all(self, texts: List[str], ctx: ParseContext, 
                  applies_to: Optional[str] = None, condition=None, 
                  duration: Optional[str] = None) -> List[ParseResult]:
        """Parse multiple texts"""
        return [self.parse(text, ctx, applies_to, condition, duration) for text in texts]

# Global registry instance
_registry = ParserRegistry()

def register_parser(parser: ContinuousEffectParser):
    """Convenience function to register parsers"""
    _registry.register(parser)

def get_registry() -> ParserRegistry:
    """Get the global registry"""
    return _registry

