import re
from typing import List
from axis1.schema import Axis1Face
from axis2.schema import ActivatedAbility, TriggeredAbility
from axis2.parsing.keywords import extract_keywords

def cleaned_oracle_text(face: Axis1Face) -> str:
    """
    DEPRECATED: Use get_remaining_text_for_parsing from axis2.parsing.text_extraction instead.
    
    This function is kept for backward compatibility but will be removed in a future version.
    
    Return oracle text with activated and triggered ability text removed.
    Leaves only static/continuous-effect text.
    """
    # Use the new implementation for consistency
    from axis2.parsing.text_extraction import get_remaining_text_for_parsing
    # Create empty lists since we don't have parsed abilities here
    # This maintains backward compatibility
    remaining_text, _, _ = get_remaining_text_for_parsing(face, [], [], None)
    return remaining_text
