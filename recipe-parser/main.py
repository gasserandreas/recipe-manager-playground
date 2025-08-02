"""
German Recipe Parser - Main Entry Point

A command-line interface and convenience functions for parsing German recipes
from web URLs into LLM-friendly markdown format.
"""

import asyncio
from typing import Optional

try:
    # Try relative import first (when used as package)
    from .parser import GermanRecipeParser
except ImportError:
    # Fall back to absolute import (when run directly)
    from parser import GermanRecipeParser


async def parse_recipe(url: str) -> Optional[str]:
    """
    Convenience function to parse a German recipe from a URL.
    
    Args:
        url: The URL of the German recipe page to parse
        
    Returns:
        Formatted markdown string containing the recipe in German, or None if parsing fails
    """
    parser = GermanRecipeParser()
    try:
        return await parser.parse_recipe_from_url(url)
    except Exception as e:
        print(f"Fehler beim Parsen des Rezepts: {e}")
        return None


def main():
    """Main function for testing the German recipe parser."""
    print("Deutscher Rezept-Parser initialisiert!")
    print("Verwende parse_recipe(url) Funktion um Rezepte von URLs zu parsen.")
    
    # Test URLs for different German recipe sites
    test_urls = [
        "https://fooby.ch/de/rezepte/27566/sesam-chicken",  # fooby.ch example
        "https://www.swissmilk.ch/de/rezepte-kochideen/rezepte/SM2021_DIVE_12/griechischer-salat/",  # swissmilk.ch example
        "https://www.bettybossi.ch/de/rezepte/rezept/veganes-sweet-and-sour-10010271/",  # bettybossi.ch example
        "https://1mal1japan.de/rezepte/yakimeshi/"  # random example
    ]
    
    # Use first test URL for demonstration
    test_url = test_urls[2]  # bettybossi.ch example

    # Example usage
    print(f"\nTeste mit: {test_url}")
    result = asyncio.run(parse_recipe(test_url))
    if result:
        print("\n" + "="*50)
        print("ERGEBNIS:")
        print("="*50)
        print(result)
    else:
        print("Fehler: Rezept konnte nicht geparst werden.")


if __name__ == "__main__":
    main()
