"""
Weaviate Database Configuration

This module provides the database configuration class for connecting
to Weaviate vector database using v4 API.
"""

import logging
from typing import Optional

from .settings import DatabaseSettings

logger = logging.getLogger(__name__)

# Try to import weaviate with graceful fallback
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = None


class WeaviateConfig:
    """Configuration class for Weaviate database connection."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        batch_size: Optional[int] = None,
        timeout: Optional[int] = None,
        recipe_class_name: Optional[str] = None
    ):
        """
        Initialize Weaviate configuration.
        
        Args:
            url: Weaviate instance URL
            api_key: Weaviate API key
            openai_api_key: OpenAI API key for vectorization
            batch_size: Batch size for bulk operations
            timeout: Connection timeout in seconds
            recipe_class_name: Name of the recipe collection
        """
        self.url = url or DatabaseSettings.WEAVIATE_URL
        self.api_key = api_key or DatabaseSettings.WEAVIATE_API_KEY
        self.openai_api_key = openai_api_key or DatabaseSettings.OPENAI_API_KEY
        self.batch_size = batch_size or DatabaseSettings.WEAVIATE_BATCH_SIZE
        self.timeout = timeout or DatabaseSettings.WEAVIATE_TIMEOUT
        self.recipe_class_name = recipe_class_name or DatabaseSettings.RECIPE_CLASS_NAME
    
    def get_client(self):
        """Create and return a Weaviate client instance."""
        if not WEAVIATE_AVAILABLE:
            raise ImportError("weaviate package is required. Install with: pip install weaviate-client")
        
        headers = {}
        if self.openai_api_key:
            headers["X-OpenAI-Api-Key"] = self.openai_api_key
        
        # Extract host and port from URL
        url_parts = self.url.replace('http://', '').replace('https://', '')
        if ':' in url_parts:
            host, port = url_parts.split(':')
            port = int(port)
        else:
            host = url_parts
            port = 8080
        
        # Use Weaviate v4 client connection
        if self.api_key:
            client = weaviate.connect_to_local(
                host=host,
                port=port,
                headers=headers,
                auth_credentials=weaviate.auth.AuthApiKey(self.api_key)
            )
        else:
            client = weaviate.connect_to_local(
                host=host,
                port=port,
                headers=headers
            )
        
        return client
