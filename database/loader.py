"""
Recipe Data Loader for Weaviate Vector Database

This module provides functionality to load recipes from various sources
(markdown files, CSV files, etc.) and import them into the Weaviate database.
"""

import os
import re
import csv
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from .client import RecipeVectorDatabase, RecipeDocument
    from .config import WeaviateConfig
except ImportError:
    # Fallback for direct execution
    from client import RecipeVectorDatabase, RecipeDocument
    from config import WeaviateConfig


class MarkdownRecipeParser:
    """Parser for markdown recipe files with frontmatter."""
    
    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from markdown content.
        
        Args:
            content: Raw markdown content with frontmatter
            
        Returns:
            Tuple of (frontmatter_dict, markdown_body)
        """
        frontmatter = {}
        body = content
        
        # Check for frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1].strip()
                body = parts[2].strip()
                
                # Simple YAML parsing for common cases
                for line in frontmatter_text.split('\n'):
                    line = line.strip()
                    if ':' in line and not line.startswith('#'):
                        key, value = line.split(':', 1)
                        key = key.strip().strip('"\'')
                        value = value.strip().strip('"\'')
                        frontmatter[key] = value
        
        return frontmatter, body
    
    @staticmethod
    def extract_sections(markdown_content: str) -> Dict[str, Any]:
        """
        Extract structured sections from markdown content.
        
        Args:
            markdown_content: Markdown text content
            
        Returns:
            Dict with extracted sections (ingredients, instructions, etc.)
        """
        sections = {
            'ingredients': '',
            'instructions': '',
            'tags': []
        }
        
        # Split content by headers
        lines = markdown_content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for section headers
            if line.startswith('##') or line.startswith('###'):
                # Save previous section
                if current_section and current_content:
                    content = '\n'.join(current_content).strip()
                    if current_section in sections:
                        sections[current_section] = content
                
                # Start new section
                header = line.strip('#').strip().lower()
                if 'zutat' in header or 'ingredient' in header:
                    current_section = 'ingredients'
                elif 'zubereitung' in header or 'anleitung' in header or 'instruction' in header:
                    current_section = 'instructions'
                else:
                    current_section = None
                current_content = []
            
            # Extract tags from special markdown syntax
            elif '`' in line:
                tags = re.findall(r'`([^`]+)`', line)
                sections['tags'].extend(tags)
            
            # Add content to current section
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            content = '\n'.join(current_content).strip()
            if current_section in sections:
                sections[current_section] = content
        
        return sections
    
    def parse_recipe_file(self, file_path: str) -> Optional[RecipeDocument]:
        """
        Parse a single markdown recipe file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            RecipeDocument or None if parsing failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and body
            frontmatter, body = self.parse_frontmatter(content)
            
            # Extract structured sections
            sections = self.extract_sections(body)
            
            # Create recipe document
            recipe = RecipeDocument(
                title=frontmatter.get('title', Path(file_path).stem),
                source=frontmatter.get('source', ''),
                cuisine=frontmatter.get('cuisine', ''),
                prep_time=frontmatter.get('prep_time', ''),
                cook_time=frontmatter.get('cook_time', ''),
                servings=frontmatter.get('servings', ''),
                ingredients=sections.get('ingredients', ''),
                instructions=sections.get('instructions', ''),
                tags=sections.get('tags', []),
                content=content
            )
            
            logger.debug(f"Parsed recipe: {recipe.title}")
            return recipe
            
        except Exception as e:
            logger.error(f"Failed to parse recipe file {file_path}: {e}")
            return None


class RecipeDataLoader:
    """Main class for loading recipe data into Weaviate database."""
    
    def __init__(self, config: Optional[WeaviateConfig] = None):
        """Initialize the data loader."""
        self.config = config or WeaviateConfig()
        self.parser = MarkdownRecipeParser()
    
    def load_recipes_from_directory(self, 
                                   directory_path: str,
                                   pattern: str = "*.md",
                                   batch_size: int = 10) -> Dict[str, Any]:
        """
        Load all recipe files from a directory.
        
        Args:
            directory_path: Path to directory containing recipe files
            pattern: File pattern to match (default: *.md)
            batch_size: Number of recipes to process in each batch
            
        Returns:
            Dict with loading statistics
        """
        try:
            directory = Path(directory_path)
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            # Find all matching files
            recipe_files = list(directory.glob(pattern))
            logger.info(f"Found {len(recipe_files)} recipe files in {directory_path}")
            
            if not recipe_files:
                return {
                    "status": "completed",
                    "total_files": 0,
                    "successful": 0,
                    "failed": 0,
                    "errors": []
                }
            
            # Process files in batches
            successful = 0
            failed = 0
            errors = []
            
            with RecipeVectorDatabase(self.config) as db:
                for i in range(0, len(recipe_files), batch_size):
                    batch_files = recipe_files[i:i + batch_size]
                    batch_recipes = []
                    
                    # Parse batch of files
                    for file_path in batch_files:
                        recipe = self.parser.parse_recipe_file(str(file_path))
                        if recipe:
                            batch_recipes.append(recipe)
                        else:
                            failed += 1
                            errors.append(f"Failed to parse: {file_path}")
                    
                    # Insert batch to database
                    if batch_recipes:
                        uuids = db.add_recipes_batch(batch_recipes)
                        batch_successful = len([u for u in uuids if u is not None])
                        batch_failed = len(batch_recipes) - batch_successful
                        
                        successful += batch_successful
                        failed += batch_failed
                        
                        if batch_failed > 0:
                            errors.append(f"Failed to insert {batch_failed} recipes from batch")
                    
                    logger.info(f"Processed batch {i//batch_size + 1}: "
                              f"{len(batch_recipes)} recipes parsed, "
                              f"{successful} total successful so far")
            
            return {
                "status": "completed",
                "total_files": len(recipe_files),
                "successful": successful,
                "failed": failed,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Failed to load recipes from directory: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "errors": [str(e)]
            }
    
    def load_recipe_from_csv(self, csv_path: str, recipes_dir: str) -> Dict[str, Any]:
        """
        Load recipes from a CSV file that contains recipe metadata.
        
        Args:
            csv_path: Path to CSV file with recipe list
            recipes_dir: Directory containing recipe markdown files
            
        Returns:
            Dict with loading statistics
        """
        try:
            stats = {
                "status": "completed",
                "total_recipes": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            # Read CSV file
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                recipes_data = list(reader)
            
            stats["total_recipes"] = len(recipes_data)
            logger.info(f"Found {len(recipes_data)} recipes in CSV file")
            
            recipes_path = Path(recipes_dir)
            processed_recipes = []
            
            # Process each recipe entry
            for row in recipes_data:
                title = row.get('title', '')
                url = row.get('url', '')
                
                if not title:
                    stats["failed"] += 1
                    stats["errors"].append("Recipe missing title")
                    continue
                
                # Try to find corresponding markdown file
                # Convert title to filename (simple normalization)
                filename = re.sub(r'[^\w\-_.]', '-', title.lower())
                filename = re.sub(r'-+', '-', filename).strip('-')
                
                # Look for matching files
                possible_files = [
                    recipes_path / f"{filename}.md",
                    recipes_path / f"{title.lower().replace(' ', '-')}.md",
                ]
                
                # Also search by partial filename match
                for recipe_file in recipes_path.glob("*.md"):
                    if filename in recipe_file.stem.lower():
                        possible_files.append(recipe_file)
                        break
                
                recipe_file = None
                for possible_file in possible_files:
                    if possible_file.exists():
                        recipe_file = possible_file
                        break
                
                if recipe_file:
                    recipe = self.parser.parse_recipe_file(str(recipe_file))
                    if recipe:
                        # Update source URL from CSV if not present
                        if not recipe.source and url:
                            recipe.source = url
                        processed_recipes.append(recipe)
                    else:
                        stats["failed"] += 1
                        stats["errors"].append(f"Failed to parse: {recipe_file}")
                else:
                    stats["failed"] += 1
                    stats["errors"].append(f"Recipe file not found for: {title}")
            
            # Insert all recipes to database
            if processed_recipes:
                with RecipeVectorDatabase(self.config) as db:
                    uuids = db.add_recipes_batch(processed_recipes)
                    stats["successful"] = len([u for u in uuids if u is not None])
                    batch_failed = len(processed_recipes) - stats["successful"]
                    stats["failed"] += batch_failed
                    
                    if batch_failed > 0:
                        stats["errors"].append(f"Failed to insert {batch_failed} recipes to database")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to load recipes from CSV: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_recipes": 0,
                "successful": 0,
                "failed": 0,
                "errors": [str(e)]
            }


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load recipes into Weaviate database")
    parser.add_argument("--recipes-dir", required=True, help="Directory containing recipe markdown files")
    parser.add_argument("--csv-file", help="CSV file with recipe metadata")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--clear", action="store_true", help="Clear database before loading")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
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
