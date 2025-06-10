import re
from typing import Optional

class InputValidator:
    @staticmethod
    def validate_prompt(prompt: str) -> tuple[bool, Optional[str]]:
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"
        
        if len(prompt) > 2000:
            return False, "Prompt too long (max 2000 characters)"
        
        # Check for potential injection attempts
        suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False, "Invalid characters detected"
        
        return True, None
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', prompt)
        return sanitized.strip()