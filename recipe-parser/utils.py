"""
URL validation utilities.

This module provides URL validation functionality for recipe parsing.
"""

from urllib.parse import urlparse
from typing import List


class URLValidator:
    """Validates URLs for recipe parsing."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate if the provided URL is properly formatted.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_urls(urls: List[str]) -> List[str]:
        """
        Validate a list of URLs and return only valid ones.
        
        Args:
            urls: List of URL strings to validate
            
        Returns:
            List of valid URLs
        """
        return [url for url in urls if URLValidator.is_valid_url(url)]
    
    @staticmethod
    def get_domain(url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain string or empty string if invalid
        """
        try:
            result = urlparse(url)
            return result.netloc
        except Exception:
            return ""
