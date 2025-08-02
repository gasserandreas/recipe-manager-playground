"""
German Recipe Parser Package

A modular recipe parser optimized for German recipe websites that extracts
structured recipe data and converts it to LLM-friendly markdown format.
"""

from .parser import GermanRecipeParser
from .extractors import JSONLDExtractor, HTMLExtractor
from .formatters import GermanTextFormatter, MarkdownFormatter
from .loaders import RecipeContentLoader
from .utils import URLValidator

__version__ = "0.1.0"
__author__ = "Recipe Manager Project"

# Public API
__all__ = [
    "GermanRecipeParser",
    "JSONLDExtractor", 
    "HTMLExtractor",
    "GermanTextFormatter",
    "MarkdownFormatter",
    "RecipeContentLoader",
    "URLValidator"
]
