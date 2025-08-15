"""
Weaviate Database Manager

This module provides the manager class for Weaviate database operations
using v4 API, including connection management and schema operations.
"""

import logging
from typing import Dict, Any, Optional

from ..config import WeaviateConfig
from ..schema import RecipeSchema

logger = logging.getLogger(__name__)

# Try to import weaviate with graceful fallback
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = None


class WeaviateManager:
    """Manager class for Weaviate database operations using v4 API."""
    
    def __init__(self, config: Optional[WeaviateConfig] = None):
        """
        Initialize the Weaviate manager.
        
        Args:
            config: Optional Weaviate configuration
        """
        self.config = config or WeaviateConfig()
        self.client = None
    
    def connect(self) -> bool:
        """
        Connect to Weaviate database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = self.config.get_client()
            if self.client.is_ready():
                logger.info("Successfully connected to Weaviate database")
                return True
            else:
                logger.error("Weaviate is not ready")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Weaviate database."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from Weaviate database")
    
    def create_schema(self) -> bool:
        """
        Create the recipe collection in Weaviate using v4 API.
        
        Returns:
            bool: True if schema created successfully, False otherwise
        """
        try:
            if not self.client:
                raise Exception("Client not connected")
            
            # Check if collection already exists
            if self.client.collections.exists(self.config.recipe_class_name):
                logger.info(f"Collection {self.config.recipe_class_name} already exists")
                return True
            
            # Create the Recipe collection using v4 API
            self.client.collections.create(
                name=self.config.recipe_class_name,
                properties=RecipeSchema.get_properties(),
                vectorizer_config=RecipeSchema.get_vectorizer_config(),
                vector_index_config=RecipeSchema.get_collection_config(),
                description="Recipe collection for RAG vector database"
            )
            
            logger.info(f"Created {self.config.recipe_class_name} collection in Weaviate")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False
    
    def delete_schema(self) -> bool:
        """
        Delete the recipe collection from Weaviate.
        
        Returns:
            bool: True if schema deleted successfully, False otherwise
        """
        try:
            if not self.client:
                raise Exception("Client not connected")
            
            if self.client.collections.exists(self.config.recipe_class_name):
                self.client.collections.delete(self.config.recipe_class_name)
                logger.info(f"Deleted {self.config.recipe_class_name} collection from Weaviate")
                return True
            else:
                logger.info(f"Collection {self.config.recipe_class_name} does not exist")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete schema: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Weaviate database.
        
        Returns:
            Dict containing health status and metadata
        """
        try:
            if not self.client:
                self.connect()
            
            if not self.client:
                return {"status": "error", "message": "Cannot connect to database"}
            
            # Check if Weaviate is ready
            is_ready = self.client.is_ready()
            is_live = self.client.is_live()
            
            if is_ready and is_live:
                # Get meta information
                meta = self.client.get_meta()
                
                # Check if recipe collection exists
                collection_exists = self.client.collections.exists(self.config.recipe_class_name)
                
                return {
                    "status": "healthy",
                    "ready": True,
                    "live": True,
                    "version": meta.get("version", "unknown"),
                    "weaviate_version": meta.get("version", "unknown"),
                    "collection_exists": collection_exists,
                    "collection_name": self.config.recipe_class_name,
                    "url": self.config.url
                }
            else:
                return {
                    "status": "not_ready", 
                    "ready": is_ready,
                    "live": is_live,
                    "message": "Weaviate is not ready"
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "ready": False, "live": False, "message": str(e)}
    
    def count_objects(self) -> int:
        """
        Count the number of recipe objects in the database.
        
        Returns:
            int: Number of objects, -1 if error
        """
        try:
            if not self.client:
                if not self.connect():
                    raise Exception("Failed to connect to database")
            
            if not self.client.collections.exists(self.config.recipe_class_name):
                logger.warning(f"Collection {self.config.recipe_class_name} does not exist")
                return 0
            
            collection = self.client.collections.get(self.config.recipe_class_name)
            
            # Use aggregate query to count objects in v4 API
            count_result = collection.aggregate.over_all(total_count=True)
            count = count_result.total_count if count_result.total_count else 0
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to count objects: {e}")
            return -1


def setup_database(config: Optional[WeaviateConfig] = None) -> WeaviateManager:
    """
    Setup and configure the Weaviate database.
    
    Args:
        config: Optional configuration object
        
    Returns:
        WeaviateManager: Configured database manager
    """
    manager = WeaviateManager(config)
    
    # Connect to database
    if not manager.connect():
        logger.error("Failed to connect to Weaviate database")
        return manager
    
    # Create schema if it doesn't exist
    if not manager.create_schema():
        logger.error("Failed to create database schema")
    
    return manager
