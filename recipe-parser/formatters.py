"""
Text formatters for German recipe content.

This module handles normalization and formatting of German text content
such as time expressions, serving sizes, and recipe metadata.
"""

import re
from typing import Dict


class GermanTextFormatter:
    """Handles German text formatting and normalization for recipes."""
    
    def __init__(self):
        """Initialize with German text mappings."""
        self.time_replacements = {
            'stunden': 'Std',
            'stunde': 'Std',
            'std.': 'Std',
            'minuten': 'Min',
            'minute': 'Min',
            'min.': 'Min',
            'sekunden': 'Sek',
            'sekunde': 'Sek',
            'sek.': 'Sek'
        }
    
    def normalize_time_text(self, time_text: str) -> str:
        """
        Normalize German time text to consistent format.
        
        Args:
            time_text: Raw time text from recipe
            
        Returns:
            Normalized time string in German format
        """
        if not time_text:
            return ""
        
        # Common German time patterns
        time_text = time_text.lower().strip()
        
        # Replace German words with standard abbreviations
        for german, abbrev in self.time_replacements.items():
            time_text = time_text.replace(german, abbrev)
        
        return time_text.title()
    
    def normalize_servings_text(self, servings_text: str) -> str:
        """
        Normalize German servings text to consistent format.
        
        Args:
            servings_text: Raw servings text from recipe
            
        Returns:
            Normalized servings string in German
        """
        if not servings_text:
            return ""
        
        # Extract numbers from German servings text
        numbers = re.findall(r'\d+', servings_text.lower())
        
        if numbers:
            num = numbers[0]
            if 'person' in servings_text.lower():
                return f"{num} Personen"
            elif 'portion' in servings_text.lower():
                return f"{num} Portionen"
            elif 'stück' in servings_text.lower():
                return f"{num} Stück"
            else:
                return f"{num} Portionen"
        
        return servings_text


class MarkdownFormatter:
    """Formats recipe data as German markdown for LLM processing."""
    
    def format_recipe(self, recipe_data: Dict, source_url: str) -> str:
        """
        Format recipe data as markdown with German labels.
        
        Args:
            recipe_data: Dictionary containing recipe information
            source_url: Source URL of the recipe
            
        Returns:
            Formatted markdown string optimized for German LLM processing
        """
        markdown_parts = []
        
        # Header with metadata
        markdown_parts.append("# Rezept")
        markdown_parts.append("")
        
        if recipe_data['title']:
            markdown_parts.append(f"## {recipe_data['title']}")
            markdown_parts.append("")
        
        # Source information
        markdown_parts.append(f"**Quelle:** {source_url}")
        markdown_parts.append("")
        
        # Description
        if recipe_data['description']:
            markdown_parts.append("## Beschreibung")
            markdown_parts.append(recipe_data['description'])
            markdown_parts.append("")
        
        # Recipe details with German labels
        details = self._format_recipe_details(recipe_data)
        if details:
            markdown_parts.append("## Rezept-Details")
            markdown_parts.extend(details)
            markdown_parts.append("")
        
        # Ingredients with German header
        if recipe_data['ingredients']:
            markdown_parts.append("## Zutaten")
            for ingredient in recipe_data['ingredients']:
                if ingredient.strip():
                    markdown_parts.append(f"- {ingredient}")
            markdown_parts.append("")
        
        # Instructions with German header
        if recipe_data['instructions']:
            markdown_parts.append("## Zubereitung")
            for i, instruction in enumerate(recipe_data['instructions'], 1):
                if instruction.strip():
                    markdown_parts.append(f"{i}. {instruction}")
            markdown_parts.append("")
        
        return "\n".join(markdown_parts)
    
    def _format_recipe_details(self, recipe_data: Dict) -> list:
        """Format recipe timing and serving details."""
        details = []
        if recipe_data['prep_time']:
            details.append(f"**Vorbereitungszeit:** {recipe_data['prep_time']}")
        if recipe_data['cook_time']:
            details.append(f"**Kochzeit:** {recipe_data['cook_time']}")
        if recipe_data['servings']:
            details.append(f"**Portionen:** {recipe_data['servings']}")
        return details
