#!/usr/bin/env python3
"""
Command-line interface for loading recipe data into the database.

This script provides a CLI for loading recipes from various sources
into the Weaviate vector database.
"""

import argparse
import logging
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loaders import RecipeDataLoader
from utils import setup_logging


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Load recipes into Weaviate database")
    parser.add_argument("--recipes-dir", required=True, help="Directory containing recipe markdown files")
    parser.add_argument("--csv-file", help="CSV file with recipe metadata")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    
    logger = logging.getLogger(__name__)
    
    loader = RecipeDataLoader()
    
    # Load recipes
    if args.csv_file:
        logger.info(f"Loading recipes from CSV: {args.csv_file}")
        stats = loader.load_recipe_from_csv(args.csv_file, args.recipes_dir)
    else:
        logger.info(f"Loading recipes from directory: {args.recipes_dir}")
        stats = loader.load_recipes_from_directory(args.recipes_dir, batch_size=args.batch_size)
    
    # Print results
    print(f"\nLoading completed:")
    print(f"Status: {stats['status']}")
    print(f"Total files: {stats.get('total_files', stats.get('total_recipes', 0))}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    
    if stats.get('errors'):
        print(f"\nErrors:")
        for error in stats['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more errors")


if __name__ == "__main__":
    main()
