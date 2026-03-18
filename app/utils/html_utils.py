"""Utility functions for HTML processing."""

from typing import Set


def extract_visible_text(text: str) -> str:
    """
    Extract and clean visible text from HTML content.
    
    Normalizes whitespace and removes excess formatting.
    
    Args:
        text: Raw text extracted from HTML
        
    Returns:
        Cleaned visible text
    """
    # Normalize whitespace
    text = " ".join(text.split())
    return text


def count_words(text: str) -> int:
    """
    Count words in text safely.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    if not text:
        return 0
    return len(text.split())


def extract_domain_from_url(url: str) -> str:
    """
    Extract domain name from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain name (e.g., 'example.com')
    """
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    return parsed.netloc or ""


def normalize_domain(domain: str) -> str:
    """
    Normalize domain for comparison by removing www prefix.
    
    Args:
        domain: Domain name (e.g., 'www.example.com')
        
    Returns:
        Normalized domain (e.g., 'example.com')
    """
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def is_valid_href(href: str) -> bool:
    """
    Check if href is valid and should be processed.
    
    Rejects empty, anchor, javascript, mailto, and tel links.
    
    Args:
        href: The href attribute value
        
    Returns:
        True if valid, False otherwise
    """
    if not href or not href.strip():
        return False
    
    href_lower = href.lower()
    
    # Reject invalid link types
    if href_lower.startswith(("#", "javascript:", "mailto:", "tel:")):
        return False
    
    return True
