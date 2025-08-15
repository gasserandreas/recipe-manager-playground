"""
Environment variables and application settings for the database module.
"""

import os


class DatabaseSettings:
    """Central configuration settings for the database module."""
    
    # Weaviate Connection Settings
    WEAVIATE_URL = os.getenv('WEAVIATE_URL', 'http://localhost:8080')
    WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY', '')
    WEAVIATE_TIMEOUT = int(os.getenv('WEAVIATE_TIMEOUT', '30'))
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv('OPENAI_APIKEY', '')
    
    # Batch Processing Settings
    WEAVIATE_BATCH_SIZE = int(os.getenv('WEAVIATE_BATCH_SIZE', '100'))
    
    # Collection Settings
    RECIPE_CLASS_NAME = os.getenv('RECIPE_CLASS_NAME', 'Recipe')
    
    # Default embedding model
    DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
