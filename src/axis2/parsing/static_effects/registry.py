# axis2/parsing/static_effects/registry.py

from typing import List
from .base import StaticEffectParser, ParseResult
from axis2.schema import ParseContext

class ParserRegistry:
    """Manages all static effect parsers with priority ordering"""
    
    def __init__(self):
        self._parsers: List[StaticEffectParser] = []
    
    def register(self, parser: StaticEffectParser):
        """Register a parser (automatically sorted by priority)"""
        self._parsers.append(parser)
        self._parsers.sort(key=lambda p: p.priority, reverse=True)
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """
        Try all parsers in priority order, return the best match.
        """
        text = text.strip()
        if not text:
            return ParseResult()
        
        # Quick filter: only try parsers that might match
        candidates = [p for p in self._parsers if p.can_parse(text, ctx)]
        
        # Keep track of best match (currently = first success)
        best = None
        for parser in candidates:
            result = parser.parse(text, ctx)
            if result.is_success:
                best = result
                break
        
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

def register_parser(parser: StaticEffectParser):
    """Convenience function to register parsers"""
    _registry.register(parser)

def get_registry() -> ParserRegistry:
    """Get the global registry"""
    return _registry

