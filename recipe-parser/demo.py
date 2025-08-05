"""
Demo script for testing the German Recipe Parser.

This script demonstrates the parser functionality using various German recipe URLs.
"""

import asyncio

try:
    # Try relative import first (when used as package)
    from .main import parse_recipes
except ImportError:
    # Fall back to absolute import (when run directly)
    from main import parse_recipes


async def demo():
    """Demonstrate the German recipe parser with various test URLs."""
    print("🇩🇪 German Recipe Parser - Demo")
    print("=" * 50)
    
    # Test URLs for different German recipe sites
    test_urls = [
        "https://fooby.ch/de/rezepte/27566/sesam-chicken",  # fooby.ch example
        "https://www.swissmilk.ch/de/rezepte-kochideen/rezepte/SM2021_DIVE_12/griechischer-salat/",  # swissmilk.ch example
        "https://www.bettybossi.ch/de/rezepte/rezept/veganes-sweet-and-sour-10010271/",  # bettybossi.ch example
        "https://1mal1japan.de/rezepte/yakimeshi/",  # random example
        "https://invalid-url-for-testing",  # invalid URL for error testing
    ]
    
    print(f"Testing with {len(test_urls)} URLs...")
    print("-" * 50)
    
    # Parse all recipes
    results = await parse_recipes(test_urls)
    
    # Display results
    for i, (url, result) in enumerate(zip(test_urls, results), 1):
        print(f"\n[{i}] {url}")
        print("-" * 80)
        
        if result['success']:
            print("✅ SUCCESS")
            print(f"Preview (first 200 chars):\n{result['content'][:200]}...")
            if len(result['content']) > 200:
                print(f"\n[Full content: {len(result['content'])} characters]")
        else:
            print("❌ FAILED")
            print(f"Error: {result['error']}")
    
    # Summary
    successful = sum(1 for result in results if result['success'])
    failed = len(results) - successful
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(results)}")


if __name__ == "__main__":
    asyncio.run(demo())
