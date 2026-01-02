# axis2/parsing/replacement_effects/registry.py

from typing import List
from .base import ReplacementEffectParser, ParseResult

class ParserRegistry:
    """Manages all replacement effect parsers with priority ordering"""
    
    def __init__(self):
        self._parsers: List[ReplacementEffectParser] = []
    
    def register(self, parser: ReplacementEffectParser):
        """Register a parser (automatically sorted by priority)"""
        self._parsers.append(parser)
        self._parsers.sort(key=lambda p: p.priority, reverse=True)
    
    def parse(self, text: str) -> ParseResult:
        """Try all parsers in priority order, return the best match."""
        text = text.strip()
        if not text:
            return ParseResult()
        
        # Quick filter: only try parsers that might match
        candidates = [p for p in self._parsers if p.can_parse(text)]
        
        best = None
        for parser in candidates:
            result = parser.parse(text)
            if result.is_success:
                best = result
                break
        
        if best:
            return best
        
        return ParseResult(
            matched=False,
            errors=[f"No parser matched: {text[:50]}..."]
        )

# Global registry instance
_registry = ParserRegistry()

def register_parser(parser: ReplacementEffectParser):
    """Convenience function to register parsers"""
    _registry.register(parser)

def get_registry() -> ParserRegistry:
    """Get the global registry"""
    return _registry

