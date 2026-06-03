# axis2/parsing/effects/registry.py

import logging
from typing import List
from .base import EffectParser, ParseResult
from axis2.schema import ParseContext
from axis2.parsing.base_registry import BaseParserRegistry

logger = logging.getLogger(__name__)

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
        
        from axis2.schema import UnparsedOracleEffect
        from axis2.validation import validate_effect
        from axis2.parsing.effects.fallback import FallbackParser

        candidates = self._find_candidates(text, ctx)

        for parser in candidates:
            result = parser.parse(text, ctx)
            if not result.is_success:
                continue
            if any(isinstance(e, UnparsedOracleEffect) for e in result.all_effects):
                return result
            validation_errors = []
            for effect in result.all_effects:
                validation_errors.extend(validate_effect(effect))
            if not validation_errors:
                return result
            logger.debug(
                "Parser %s validation failed: %s",
                type(parser).__name__,
                validation_errors,
            )

        # Guaranteed structural coverage
        return FallbackParser().parse(text, ctx)
    
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

