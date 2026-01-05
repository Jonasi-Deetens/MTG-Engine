"""
Base registry class for parser registries.

This module provides a base class that eliminates duplication across
different parser registry implementations.
"""

from typing import List, Optional, Any, Callable

class BaseParserRegistry:
    """
    Base class for parser registries.
    
    Provides common functionality:
    - Parser registration with priority sorting
    - Candidate filtering via can_parse
    - Common parsing loop logic
    
    Subclasses should call _try_parsers() in their parse() method.
    """
    
    def __init__(self):
        self._parsers: List[Any] = []
    
    def register(self, parser: Any):
        """
        Register a parser (automatically sorted by priority).
        
        Args:
            parser: Parser instance with priority attribute
        """
        self._parsers.append(parser)
        self._parsers.sort(key=lambda p: p.priority, reverse=True)
    
    def _find_candidates(self, text: str, ctx: Optional[Any] = None) -> List[Any]:
        """
        Find parsers that might match the text.
        
        Args:
            text: Text to parse
            ctx: Optional parse context (some parsers don't use it)
            
        Returns:
            List of candidate parsers
        """
        text = text.strip()
        if not text:
            return []
        
        # Quick filter: only try parsers that might match
        # Different parser types have different can_parse signatures
        candidates = []
        if ctx is not None:
            for p in self._parsers:
                try:
                    if p.can_parse(text, ctx):
                        candidates.append(p)
                except Exception as e:
                    # Log but don't fail - some parsers might have bugs in can_parse
                    import logging
                    logging.getLogger(__name__).debug(f"Exception in {type(p).__name__}.can_parse: {e}")
        else:
            for p in self._parsers:
                try:
                    if p.can_parse(text):
                        candidates.append(p)
                except Exception as e:
                    # Log but don't fail - some parsers might have bugs in can_parse
                    import logging
                    logging.getLogger(__name__).debug(f"Exception in {type(p).__name__}.can_parse: {e}")
        
        return candidates
    
    def _try_parsers(
        self, 
        candidates: List[Any], 
        parse_func: Callable[[Any], Any]
    ) -> Optional[Any]:
        """
        Try parsers in order, return first successful match.
        
        Args:
            candidates: List of candidate parsers
            parse_func: Function that calls parser.parse() with appropriate signature
                        Should take a parser and return ParseResult
        
        Returns:
            ParseResult if successful, None otherwise
        """
        for parser in candidates:
            result = parse_func(parser)
            if result.is_success:
                return result
        return None
    
    def _get_error_message(self, text: str, parser_name: Optional[str] = None) -> str:
        """
        Get error message when no parser matches.
        
        Args:
            text: The text that failed to parse
            parser_name: Optional parser name for more specific errors
            
        Returns:
            Error message string
        """
        if parser_name:
            return f"Parser {parser_name} failed to match: {text[:50]}..."
        return f"No parser matched: {text[:50]}..."

