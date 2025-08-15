"""
Recipe Data Loader

This module provides functionality to load recipes from various sources
(markdown files, CSV files, etc.) and import them into the Weaviate database.
"""

import re
import csv
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from ..config import WeaviateConfig
from ..core import RecipeVectorDatabase
from .markdown_recipe_parser import MarkdownRecipeParser

logger = logging.getLogger(__name__)


class RecipeDataLoader:
    """Main class for loading recipe data into Weaviate database."""
    
    def __init__(self, config: Optional[WeaviateConfig] = None):
        """
        Initialize the data loader.
        
        Args:
            config: Optional Weaviate configuration
        """
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
                        result = db.add_recipes_batch(batch_recipes)
                        batch_successful = result.get("successful", 0)
                        batch_failed = result.get("total", 0) - batch_successful
                        
                        successful += batch_successful
                        failed += batch_failed
                        
                        if batch_failed > 0:
                            errors.append(f"Failed to insert {batch_failed} recipes from batch")
                            if result.get("errors"):
                                errors.extend(result["errors"][:3])  # Add first 3 errors
                    
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
                    result = db.add_recipes_batch(processed_recipes)
                    stats["successful"] = result.get("successful", 0)
                    batch_failed = result.get("total", 0) - stats["successful"]
                    stats["failed"] += batch_failed
                    
                    if batch_failed > 0:
                        stats["errors"].append(f"Failed to insert {batch_failed} recipes to database")
                        if result.get("errors"):
                            stats["errors"].extend(result["errors"][:3])  # Add first 3 errors
            
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
