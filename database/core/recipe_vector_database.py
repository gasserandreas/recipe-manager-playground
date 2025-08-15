"""
Recipe Vector Database Client

This module provides high-level operations for storing, retrieving,
and searching recipes in the Weaviate vector database using v4 API.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..config import WeaviateConfig
from ..models import RecipeDocument
from .weaviate_manager import WeaviateManager

logger = logging.getLogger(__name__)

# Try to import weaviate with graceful fallback
try:
    import weaviate
    from weaviate.classes.query import MetadataQuery
    WEAVIATE_AVAILABLE = True
except ImportError:
    weaviate = None
    MetadataQuery = None
    WEAVIATE_AVAILABLE = False


class RecipeVectorDatabase:
    """High-level interface for recipe vector database operations using Weaviate v4."""
    
    def __init__(self, config: Optional[WeaviateConfig] = None):
        """
        Initialize the recipe vector database.
        
        Args:
            config: Optional Weaviate configuration
        """
        self.config = config or WeaviateConfig()
        self.manager = WeaviateManager(self.config)
        self.client = None
        self._collection = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def connect(self) -> bool:
        """
        Connect to the Weaviate database.
        
        Returns:
            bool: True if connection successful
        """
        if self.manager.connect():
            self.client = self.manager.client
            self._collection = self.client.collections.get(self.config.recipe_class_name)
            return True
        return False
    
    def disconnect(self):
        """Disconnect from the database."""
        self.manager.disconnect()
        self.client = None
        self._collection = None
    
    def add_recipe(self, recipe: RecipeDocument) -> Optional[str]:
        """
        Add a single recipe to the database.
        
        Args:
            recipe: Recipe document to add
            
        Returns:
            str: UUID of the added recipe, None if failed
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            recipe_data = recipe.to_dict()
            uuid = self._collection.data.insert(recipe_data)
            
            logger.info(f"Added recipe '{recipe.title}' with UUID: {uuid}")
            return str(uuid)
            
        except Exception as e:
            logger.error(f"Failed to add recipe '{recipe.title}': {e}")
            return None
    
    def add_recipes_batch(self, recipes: List[RecipeDocument]) -> Dict[str, Any]:
        """
        Add multiple recipes to the database in batch.
        
        Args:
            recipes: List of recipe documents to add
            
        Returns:
            Dict with success count and any errors
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            # Prepare batch data
            batch_data = [recipe.to_dict() for recipe in recipes]
            
            # Insert batch
            response = self._collection.data.insert_many(batch_data)
            
            successful = 0
            errors = []
            
            # Process response
            if hasattr(response, 'uuids'):
                successful = len(response.uuids)
            if hasattr(response, 'errors'):
                errors = response.errors
            
            logger.info(f"Batch insert: {successful} successful, {len(errors)} errors")
            
            return {
                "successful": successful,
                "total": len(recipes),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Failed to add recipe batch: {e}")
            return {"successful": 0, "total": len(recipes), "errors": [str(e)]}
    
    def search_recipes(
        self, 
        query: str, 
        limit: int = 10, 
        certainty: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for recipes using vector similarity.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            certainty: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of recipe documents with similarity scores
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            if not WEAVIATE_AVAILABLE:
                raise ImportError("weaviate package is required for search operations")
            
            # Perform vector search using v4 API
            response = self._collection.query.near_text(
                query=query,
                limit=limit,
                certainty=certainty,
                return_metadata=MetadataQuery(score=True, distance=True)
            )
            
            results = []
            for obj in response.objects:
                result = {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties,
                    "metadata": obj.metadata
                }
                results.append(result)
            
            logger.info(f"Vector search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search recipes: {e}")
            return []
    
    def get_recipe_by_id(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific recipe by its UUID.
        
        Args:
            uuid: Recipe UUID
            
        Returns:
            Recipe document or None if not found
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            obj = self._collection.query.fetch_object_by_id(uuid)
            
            if obj:
                return {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get recipe by ID {uuid}: {e}")
            return None
    
    def count_recipes(self) -> int:
        """
        Count the total number of recipes in the database.
        
        Returns:
            int: Number of recipes
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            # Use aggregate query to count objects in v4 API
            count_result = self._collection.aggregate.over_all(total_count=True)
            count = count_result.total_count if count_result.total_count else 0
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to count recipes: {e}")
            return 0
    
    def get_all_recipes(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all recipes from the database.
        
        Args:
            limit: Maximum number of recipes to return
            offset: Number of recipes to skip
            
        Returns:
            List of recipe documents
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            response = self._collection.query.fetch_objects(
                limit=limit,
                offset=offset
            )
            
            results = []
            for obj in response.objects:
                result = {
                    "uuid": str(obj.uuid),
                    "properties": obj.properties
                }
                results.append(result)
            
            logger.info(f"Retrieved {len(results)} recipes (limit: {limit}, offset: {offset})")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get all recipes: {e}")
            return []
    
    def delete_recipe(self, uuid: str) -> bool:
        """
        Delete a recipe by its UUID.
        
        Args:
            uuid: Recipe UUID to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            success = self._collection.data.delete_by_id(uuid)
            
            if success:
                logger.info(f"Deleted recipe with UUID: {uuid}")
            else:
                logger.warning(f"Recipe with UUID {uuid} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete recipe {uuid}: {e}")
            return False
    
    def update_recipe(self, uuid: str, recipe: RecipeDocument) -> bool:
        """
        Update a recipe by its UUID.
        
        Args:
            uuid: Recipe UUID to update
            recipe: Updated recipe document
            
        Returns:
            bool: True if updated successfully
        """
        try:
            if self._collection is None:
                raise Exception("Not connected to database")
            
            recipe_data = recipe.to_dict()
            recipe_data["updated_at"] = datetime.now()
            
            success = self._collection.data.update(uuid, recipe_data)
            
            if success:
                logger.info(f"Updated recipe '{recipe.title}' with UUID: {uuid}")
            else:
                logger.warning(f"Recipe with UUID {uuid} not found for update")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update recipe {uuid}: {e}")
            return False
