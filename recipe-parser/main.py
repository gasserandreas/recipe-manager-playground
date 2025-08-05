"""
German Recipe Parser - Main Entry Point

A command-line interface and batch processing functions for parsing German recipes
from web URLs into LLM-friendly markdown format.
"""

import asyncio
from typing import Optional, List, Dict, Any

try:
    # Try relative import first (when used as package)
    from .parser import GermanRecipeParser
except ImportError:
    # Fall back to absolute import (when run directly)
    from parser import GermanRecipeParser


class RecipeResult:
    """Result container for recipe parsing operations."""
    
    def __init__(self, success: bool, content: Optional[str] = None, error: Optional[str] = None, url: Optional[str] = None):
        self.success = success
        self.content = content
        self.error = error
        self.url = url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            'success': self.success,
            'content': self.content,
            'error': self.error,
            'url': self.url
        }


async def parse_recipe(url: str) -> RecipeResult:
    """
    Parse a single German recipe from a URL.
    
    Args:
        url: The URL of the German recipe page to parse
        
    Returns:
        RecipeResult object containing success status, content, and error information
    """
    parser = GermanRecipeParser()
    try:
        content = await parser.parse_recipe_from_url(url)
        if content:
            return RecipeResult(success=True, content=content, url=url)
        else:
            return RecipeResult(success=False, error="No content could be extracted", url=url)
    except Exception as e:
        return RecipeResult(success=False, error=str(e), url=url)


async def parse_recipes(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Parse multiple German recipes from a list of URLs.
    
    This function processes URLs concurrently and returns results in the same order
    as the input URLs. Failed URLs will have success=False with error information.
    
    Args:
        urls: List of URLs to parse recipes from
        
    Returns:
        List of dictionaries containing parsing results in the same order as input URLs.
        Each dictionary has keys: 'success', 'content', 'error', 'url'
    """
    if not urls:
        return []
    
    # Create tasks for concurrent processing
    tasks = [parse_recipe(url) for url in urls]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert results to dictionaries, handling any exceptions
    formatted_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            formatted_results.append({
                'success': False,
                'content': None,
                'error': f"Unexpected error: {str(result)}",
                'url': urls[i]
            })
        elif isinstance(result, RecipeResult):
            formatted_results.append(result.to_dict())
        else:
            # Fallback for unexpected result types
            formatted_results.append({
                'success': False,
                'content': None,
                'error': "Unexpected result type",
                'url': urls[i]
            })
    
    return formatted_results


async def parse_recipe_simple(url: str) -> Optional[str]:
    """
    Simple convenience function that returns just the content string (backward compatibility).
    
    Args:
        url: The URL of the German recipe page to parse
        
    Returns:
        Formatted markdown string containing the recipe in German, or None if parsing fails
    """
    result = await parse_recipe(url)
    return result.content if result.success else None


# def main():
#     """
#     Main function demonstrating basic usage.
    
#     For more comprehensive testing, run demo.py instead.
#     """
#     print("German Recipe Parser - Batch Processing")
#     print("For demo and testing, run: python demo.py")
#     print()
    
#     # Simple example with one URL
#     test_url = "https://www.bettybossi.ch/de/rezepte/rezept/veganes-sweet-and-sour-10010271/"
#     print(f"Testing single URL: {test_url}")
    
#     result = asyncio.run(parse_recipes([test_url]))
    
#     if result[0]['success']:
#         print("✅ Success!")
#         print(f"Content preview: {result[0]['content'][:200]}...")
#     else:
#         print("❌ Failed!")
#         print(f"Error: {result[0]['error']}")


# if __name__ == "__main__":
#     main()
