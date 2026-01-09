"""
Input Sanitization Module
Prevents XSS attacks by sanitizing user-generated content
"""

import bleach
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Allowed HTML tags for user content
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code'
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
}

# Allowed protocols for links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(text: str, strip_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        text: Input text to sanitize
        strip_tags: If True, remove all HTML tags
        
    Returns:
        Sanitized text safe for rendering
    """
    if not text:
        return ""
    
    if strip_tags:
        # Remove all HTML tags
        return bleach.clean(text, tags=[], strip=True)
    
    # Clean with allowed tags and attributes
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    
    return cleaned


def sanitize_text(text: str) -> str:
    """
    Sanitize plain text by removing all HTML
    
    Args:
        text: Input text
        
    Returns:
        Plain text with HTML stripped
    """
    if not text:
        return ""
    
    return bleach.clean(text, tags=[], strip=True)


def sanitize_url(url: str) -> Optional[str]:
    """
    Sanitize and validate URLs
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL or None if invalid
    """
    if not url:
        return None
    
    # Remove any HTML
    url = bleach.clean(url, tags=[], strip=True)
    
    # Validate protocol
    if not url.startswith(('http://', 'https://', 'mailto:')):
        return None
    
    return url


def sanitize_list(items: List[str], strip_tags: bool = True) -> List[str]:
    """
    Sanitize a list of strings
    
    Args:
        items: List of strings to sanitize
        strip_tags: If True, remove all HTML tags
        
    Returns:
        List of sanitized strings
    """
    if not items:
        return []
    
    return [sanitize_html(item, strip_tags=strip_tags) for item in items if item]


class SanitizationMiddleware:
    """
    Middleware to automatically sanitize request data
    Can be applied to specific fields in request models
    """
    
    @staticmethod
    def sanitize_dict(data: dict, fields_to_sanitize: List[str], strip_tags: bool = False) -> dict:
        """
        Sanitize specific fields in a dictionary
        
        Args:
            data: Dictionary to sanitize
            fields_to_sanitize: List of field names to sanitize
            strip_tags: If True, remove all HTML tags
            
        Returns:
            Dictionary with sanitized fields
        """
        sanitized = data.copy()
        
        for field in fields_to_sanitize:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = sanitize_html(sanitized[field], strip_tags=strip_tags)
            elif field in sanitized and isinstance(sanitized[field], list):
                sanitized[field] = sanitize_list(sanitized[field], strip_tags=strip_tags)
        
        return sanitized


# Export commonly used functions
__all__ = [
    'sanitize_html',
    'sanitize_text',
    'sanitize_url',
    'sanitize_list',
    'SanitizationMiddleware'
]
