# axis2/parsing/static_effects/registry.py

from typing import List
from .base import StaticEffectParser, ParseResult
from axis2.schema import ParseContext
from axis2.parsing.base_registry import BaseParserRegistry

class ParserRegistry(BaseParserRegistry):
    """Manages all static effect parsers with priority ordering"""
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """
        Try all parsers in priority order, return the best match.
        """
        text = text.strip()
        if not text:
            return ParseResult()
        
        # Find candidates using base class method
        candidates = self._find_candidates(text, ctx)
        
        # Try parsers using base class method
        best = self._try_parsers(candidates, lambda p: p.parse(text, ctx))
        
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

