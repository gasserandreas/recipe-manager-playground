"""
Recipe Document Model

This module defines the data class for recipe documents that will be
stored in the vector database.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


@dataclass
class RecipeDocument:
    """Data class representing a recipe document."""
    
    title: str
    source: str
    cuisine: str
    content: str
    ingredients: str = ""
    instructions: str = ""
    prep_time: str = ""
    cook_time: str = ""
    servings: str = ""
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the recipe document to a dictionary for Weaviate.
        
        Returns:
            Dictionary representation suitable for database storage
        """
        now = datetime.now().replace(tzinfo=timezone.utc)
        return {
            "title": self.title,
            "source": self.source,
            "cuisine": self.cuisine,
            "content": self.content,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "servings": self.servings,
            "tags": self.tags,
            "created_at": now,
            "updated_at": now
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecipeDocument":
        """
        Create a RecipeDocument from a dictionary.
        
        Args:
            data: Dictionary containing recipe data
            
        Returns:
            RecipeDocument instance
        """
        return cls(
            title=data.get("title", ""),
            source=data.get("source", ""),
            cuisine=data.get("cuisine", ""),
            content=data.get("content", ""),
            ingredients=data.get("ingredients", ""),
            instructions=data.get("instructions", ""),
            prep_time=data.get("prep_time", ""),
            cook_time=data.get("cook_time", ""),
            servings=data.get("servings", ""),
            tags=data.get("tags", [])
        )
