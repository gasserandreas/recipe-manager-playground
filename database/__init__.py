"""
Weaviate Vector Database Package for Recipe RAG System

This package provides a complete solution for storing and retrieving
recipes using Weaviate as a vector database backend.

The package is organized into the following modules:
- config: Database configuration and settings
- schema: Database schema definitions  
- models: Data models and document classes
- core: Core database operations and managers
- loaders: Data loading utilities
- utils: Utility functions and helpers
"""

__version__ = "0.1.0"

# Try to import the main classes, but gracefully handle missing dependencies
try:
    from .config import WeaviateConfig, DatabaseSettings
    from .schema import RecipeSchema
    from .models import RecipeDocument
    from .core import WeaviateManager, RecipeVectorDatabase, setup_database
    from .loaders import RecipeDataLoader, MarkdownRecipeParser
    from .utils import setup_logging, get_logger, set_debug_mode
    
    __all__ = [
        # Configuration
        "WeaviateConfig",
        "DatabaseSettings",
        # Schema
        "RecipeSchema",
        # Models
        "RecipeDocument",
        # Core functionality
        "WeaviateManager", 
        "RecipeVectorDatabase",
        "setup_database",
        # Data loading
        "RecipeDataLoader",
        "MarkdownRecipeParser",
        # Utilities
        "setup_logging",
        "get_logger",
        "set_debug_mode"
    ]
except ImportError as e:
    print(f"Warning: Some database modules could not be imported: {e}")
    print("Install dependencies with: pip install weaviate-client")
    
    __all__ = []
