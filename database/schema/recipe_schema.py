"""
Recipe Schema Definition for Weaviate Database

This module defines the schema configuration for recipe documents
in the Weaviate vector database using v4 API.
"""

from ..config.settings import DatabaseSettings

# Try to import weaviate with graceful fallback
try:
    from weaviate.classes.config import Configure, Property, DataType, VectorDistances
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    Configure = None
    Property = None
    DataType = None
    VectorDistances = None


class RecipeSchema:
    """Schema definition for recipe documents in Weaviate using v4 API."""
    
    @staticmethod
    def get_collection_config():
        """
        Get the vector configuration for Recipe objects using v4 API.
        
        Returns:
            Vector configuration for Weaviate v4
        """
        if not WEAVIATE_AVAILABLE:
            raise ImportError("weaviate package is required for schema configuration")
        
        return Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE
        )
    
    @staticmethod
    def get_vectorizer_config():
        """Get the vectorizer configuration for Recipe collection."""
        if not WEAVIATE_AVAILABLE:
            raise ImportError("weaviate package is required for vectorizer configuration")
        
        return Configure.Vectorizer.text2vec_openai(
            model=DatabaseSettings.DEFAULT_EMBEDDING_MODEL
        )
    
    @staticmethod
    def get_properties():
        """Get the properties configuration for Recipe collection."""
        if not WEAVIATE_AVAILABLE:
            raise ImportError("weaviate package is required for properties configuration")
        
        return [
            Property(name="title", data_type=DataType.TEXT, description="The title/name of the recipe"),
            Property(name="source", data_type=DataType.TEXT, description="The original URL or source of the recipe"),
            Property(name="cuisine", data_type=DataType.TEXT, description="The cuisine type (e.g., italienisch, deutsch, asiatisch)"),
            Property(name="prep_time", data_type=DataType.TEXT, description="Preparation time for the recipe"),
            Property(name="cook_time", data_type=DataType.TEXT, description="Cooking time for the recipe"),
            Property(name="servings", data_type=DataType.TEXT, description="Number of servings"),
            Property(name="ingredients", data_type=DataType.TEXT, description="Recipe ingredients"),
            Property(name="instructions", data_type=DataType.TEXT, description="Step-by-step cooking instructions"),
            Property(name="tags", data_type=DataType.TEXT_ARRAY, description="Recipe tags"),
            Property(name="content", data_type=DataType.TEXT, description="Full recipe content"),
            Property(name="created_at", data_type=DataType.DATE, description="Creation timestamp"),
            Property(name="updated_at", data_type=DataType.DATE, description="Last update timestamp"),
        ]
