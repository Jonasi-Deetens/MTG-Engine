# axis2/parsing/continuous_effects/registry.py

from typing import List, Optional
from .base import ContinuousEffectParser, ParseResult
from axis2.schema import ParseContext

class ParserRegistry:
    """Manages all continuous effect parsers with priority ordering"""
    
    def __init__(self):
        self._parsers: List[ContinuousEffectParser] = []
    
    def register(self, parser: ContinuousEffectParser):
        """Register a parser (automatically sorted by priority)"""
        self._parsers.append(parser)
        self._parsers.sort(key=lambda p: p.priority, reverse=True)
    
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
        
        # Quick filter: only try parsers that might match
        candidates = [p for p in self._parsers if p.can_parse(text, ctx)]
        
        # Keep track of best match (currently = first success)
        # Future: could track multiple matches, partial matches, etc.
        best = None
        for parser in candidates:
            result = parser.parse(text, ctx, applies_to, condition, duration)
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

