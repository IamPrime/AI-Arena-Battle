import html
import re
from typing import Tuple, Optional

class SecurityValidator:
    # Dangerous patterns that could indicate injection attempts
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'on\w+\s*=',
        r'expression\s*\(',
        r'import\s+os',
        r'__import__',
        r'eval\s*\(',
        r'exec\s*\(',
    ]
    
    @classmethod
    def validate_user_input(cls, user_input: str) -> Tuple[bool, Optional[str]]:
        if not user_input or len(user_input.strip()) == 0:
            return False, "Input cannot be empty"
        
        if len(user_input) > 10000:  # Prevent DoS
            return False, "Input too long (max 10,000 characters)"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE | re.DOTALL):
                return False, "Potentially dangerous content detected"
        
        return True, None
    
    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        # HTML escape
        sanitized = html.escape(user_input)
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        return sanitized.strip()