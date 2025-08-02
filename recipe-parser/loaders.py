"""
Web content loader for recipe parsing.

This module handles downloading and loading web content using langchain's
AsyncHtmlLoader for efficient recipe content retrieval.
"""

from typing import List
from langchain_community.document_loaders import AsyncHtmlLoader


class RecipeContentLoader:
    """Handles loading web content for recipe parsing."""
    
    async def load_content(self, url: str) -> str:
        """
        Download HTML content from the given URL.
        
        Args:
            url: The URL to download content from
            
        Returns:
            Raw HTML content as string
            
        Raises:
            Exception: If content cannot be loaded
        """
        loader = AsyncHtmlLoader([url])
        documents = await loader.aload()
        
        if not documents:
            raise Exception("No content could be loaded from the URL")
        
        return documents[0].page_content
    
    async def load_multiple_contents(self, urls: List[str]) -> List[str]:
        """
        Download HTML content from multiple URLs.
        
        Args:
            urls: List of URLs to download content from
            
        Returns:
            List of HTML content strings
            
        Raises:
            Exception: If no content could be loaded
        """
        loader = AsyncHtmlLoader(urls)
        documents = await loader.aload()
        
        if not documents:
            raise Exception("No content could be loaded from the URLs")
        
        return [doc.page_content for doc in documents]
