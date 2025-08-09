"""
Weaviate Vector Database Package for Recipe RAG System

This package provides a complete solution for storing and retrieving
recipes using Weaviate as a vector database backend.
"""

__version__ = "0.1.0"

# Try to import the main classes, but gracefully handle missing dependencies
try:
    from .config import WeaviateConfig, WeaviateManager, RecipeSchema, setup_database
    from .client import RecipeVectorDatabase, RecipeDocument
    from .loader import RecipeDataLoader, MarkdownRecipeParser
    
    __all__ = [
        "WeaviateConfig",
        "WeaviateManager", 
        "RecipeSchema",
        "setup_database",
        "RecipeVectorDatabase",
        "RecipeDocument",
        "RecipeDataLoader",
        "MarkdownRecipeParser"
    ]
except ImportError as e:
    print(f"Warning: Some database modules could not be imported: {e}")
    print("Install dependencies with: pip install weaviate-client")
    
    __all__ = []
