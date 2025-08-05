"""
German Recipe Parser

Main parser class that orchestrates the recipe extraction process
using specialized extractors and formatters.
"""

from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

try:
    # Try relative imports first (when used as package)
    from .extractors import JSONLDExtractor, HTMLExtractor
    from .formatters import MarkdownFormatter
    from .loaders import RecipeContentLoader
    from .utils import URLValidator
except ImportError:
    # Fall back to absolute imports (when run directly)
    from extractors import JSONLDExtractor, HTMLExtractor
    from formatters import MarkdownFormatter
    from loaders import RecipeContentLoader
    from utils import URLValidator


class GermanRecipeParser:
    """
    A recipe parser optimized for German recipe websites.
    
    This parser extracts structured recipe data from German web pages
    and converts it to markdown format optimized for LLM processing.
    
    Features:
    - Supports German recipe selectors and terminology
    - Handles JSON-LD structured data common in German recipe sites
    - Normalizes German time and serving formats
    - Outputs markdown with German labels (Zutaten, Zubereitung, etc.)
    """
    
    def __init__(self):
        """Initialize the parser with German-specific extractors and formatters."""
        self.content_loader = RecipeContentLoader()
        self.json_ld_extractor = JSONLDExtractor()
        self.html_extractor = HTMLExtractor()
        self.markdown_formatter = MarkdownFormatter()
        self.url_validator = URLValidator()
    
    async def parse_recipe_from_url(self, url: str) -> Optional[str]:
        """
        Parse a recipe from a given URL and return it as German markdown.
        
        Args:
            url: The URL of the recipe page to parse
            
        Returns:
            Formatted markdown string containing the recipe, or None if parsing fails
            
        Raises:
            ValueError: If the URL is invalid
            Exception: If downloading or parsing fails
        """
        if not self.url_validator.is_valid_url(url):
            raise ValueError(f"Invalid URL provided: {url}")
        
        try:
            # Download the web page content
            html_content = await self.content_loader.load_content(url)
            
            # Extract recipe content from HTML
            recipe_data = self._extract_recipe_content(html_content)
            
            # Convert to markdown with German LLM-friendly template
            markdown_recipe = self.markdown_formatter.format_recipe(recipe_data, url)
            
            return markdown_recipe
            
        except Exception as e:
            raise Exception(f"Failed to parse recipe from {url}: {str(e)}")
    
    def _extract_recipe_content(self, html_content: str) -> Dict[str, Any]:
        """
        Extract recipe-specific content from HTML using multiple strategies.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Dictionary containing extracted recipe data
        """
        soup = BeautifulSoup(html_content, 'lxml')
        recipe_data = self._initialize_recipe_data()
        
        # Try JSON-LD extraction first (most reliable for structured data)
        self.json_ld_extractor.extract(soup, recipe_data)
        
        # Fill in missing data with HTML extraction
        self.html_extractor.extract(soup, recipe_data)
        
        return recipe_data
    
    def _initialize_recipe_data(self) -> Dict[str, Any]:
        """Initialize empty recipe data structure."""
        return {
            'title': '',
            'description': '',
            'ingredients': [],
            'instructions': [],
            'prep_time': '',
            'cook_time': '',
            'servings': '',
            'nutrition': {}
        }
