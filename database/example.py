#!/usr/bin/env python3
"""
Example usage of the Recipe Vector Database

This script demonstrates how to use the refactored database module.
"""

import logging
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    RecipeVectorDatabase, 
    RecipeDocument,
    setup_logging,
    get_logger
)

# Set up logging
setup_logging(level=logging.INFO)
logger = get_logger(__name__)


def main():
    """Example usage of the RecipeVectorDatabase."""
    
    # Example recipe
    recipe = RecipeDocument(
        title="Spaghetti Carbonara",
        source="https://example.com/carbonara",
        cuisine="Italian",
        content="Classic Italian pasta dish with eggs, cheese, and pancetta.",
        ingredients="400g spaghetti, 4 eggs, 100g pancetta, 100g Parmesan cheese",
        instructions="1. Cook pasta. 2. Fry pancetta. 3. Mix eggs and cheese. 4. Combine all.",
        prep_time="10 minutes",
        cook_time="15 minutes",
        servings="4",
        tags=["pasta", "italian", "quick"]
    )
    
    try:
        with RecipeVectorDatabase() as db:
            # Add a recipe
            uuid = db.add_recipe(recipe)
            print(f"Added recipe with UUID: {uuid}")
            
            # Search for recipes
            if uuid:  # Only search if we successfully added a recipe
                results = db.search_recipes("Italian pasta recipes", limit=5)
                print(f"Found {len(results)} recipes")
                
                for result in results:
                    title = result.get('properties', {}).get('title', 'Unknown')
                    score = result.get('metadata', {}).get('score', 0)
                    print(f"  - {title} (score: {score:.3f})")
            
            # Count recipes
            count = db.count_recipes()
            print(f"Total recipes in database: {count}")
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
