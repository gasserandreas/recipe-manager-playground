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
        Format recipe data as markdown with German labels optimized for RAG.
        
        Args:
            recipe_data: Dictionary containing recipe information
            source_url: Source URL of the recipe
            
        Returns:
            Formatted markdown string optimized for German LLM processing and RAG
        """
        markdown_parts = []
        
        # Header with structured metadata for better RAG retrieval
        markdown_parts.append("---")
        markdown_parts.append(f"title: \"{recipe_data.get('title', 'Unbekanntes Rezept')}\"")
        markdown_parts.append(f"source: \"{source_url}\"")
        markdown_parts.append(f"prep_time: \"{recipe_data.get('prep_time', '')}\"")
        markdown_parts.append(f"cook_time: \"{recipe_data.get('cook_time', '')}\"")
        markdown_parts.append(f"servings: \"{recipe_data.get('servings', '')}\"")
        markdown_parts.append(f"cuisine: \"deutsch\"")
        markdown_parts.append(f"type: \"rezept\"")
        markdown_parts.append("---")
        markdown_parts.append("")
        
        # Main title
        markdown_parts.append("# Rezept")
        markdown_parts.append("")
        
        if recipe_data['title']:
            markdown_parts.append(f"## {recipe_data['title']}")
            markdown_parts.append("")
        
        # Source information with better formatting
        markdown_parts.append("### 📋 Quellinformation")
        markdown_parts.append(f"**Ursprung:** {source_url}")
        markdown_parts.append("")
        
        # Description with better semantic structure
        if recipe_data['description']:
            markdown_parts.append("### 📝 Beschreibung")
            markdown_parts.append(recipe_data['description'])
            markdown_parts.append("")
        
        # Recipe details with enhanced formatting and icons
        details = self._format_recipe_details(recipe_data)
        if details:
            markdown_parts.append("### ⏱️ Rezept-Details")
            markdown_parts.extend(details)
            markdown_parts.append("")
        
        # Ingredients with improved formatting and semantic structure
        if recipe_data['ingredients']:
            markdown_parts.append("### 🥘 Zutaten")
            markdown_parts.append("")
            formatted_ingredients = self._format_ingredients(recipe_data['ingredients'])
            markdown_parts.extend(formatted_ingredients)
            markdown_parts.append("")
        
        # Instructions with step-by-step formatting
        if recipe_data['instructions']:
            markdown_parts.append("### 👨‍🍳 Zubereitung")
            markdown_parts.append("")
            for i, instruction in enumerate(recipe_data['instructions'], 1):
                if instruction.strip():
                    # Clean up instruction text
                    clean_instruction = self._clean_instruction_text(instruction)
                    markdown_parts.append(f"**Schritt {i}:** {clean_instruction}")
                    markdown_parts.append("")
        
        # Add tags section for better RAG retrieval
        tags = self._generate_recipe_tags(recipe_data)
        if tags:
            markdown_parts.append("### 🏷️ Tags")
            markdown_parts.append(" ".join([f"`{tag}`" for tag in tags]))
            markdown_parts.append("")
        
        # Add nutritional info if available
        if recipe_data.get('nutrition'):
            markdown_parts.append("### 🔢 Nährwerte")
            for key, value in recipe_data['nutrition'].items():
                if value:
                    markdown_parts.append(f"- **{key.title()}:** {value}")
            markdown_parts.append("")
        
        return "\n".join(markdown_parts)
    
    def _format_recipe_details(self, recipe_data: Dict) -> list:
        """Format recipe timing and serving details with icons."""
        details = []
        if recipe_data['prep_time']:
            details.append(f"⏰ **Vorbereitungszeit:** {recipe_data['prep_time']}")
        if recipe_data['cook_time']:
            details.append(f"🔥 **Kochzeit:** {recipe_data['cook_time']}")
        if recipe_data['servings']:
            details.append(f"👥 **Portionen:** {recipe_data['servings']}")
        return details
    
    def _format_ingredients(self, ingredients: list) -> list:
        """Format ingredients with better spacing and structure."""
        formatted = []
        for ingredient in ingredients:
            if ingredient.strip():
                # Add proper spacing between quantity and ingredient
                formatted_ingredient = self._add_ingredient_spacing(ingredient.strip())
                formatted.append(f"- {formatted_ingredient}")
        return formatted
    
    def _add_ingredient_spacing(self, ingredient: str) -> str:
        """Add proper spacing between measurements and ingredients."""
        import re
        
        # Add space between numbers and letters (e.g., "200g" -> "200 g")
        ingredient = re.sub(r'(\d+)\s*([a-zA-ZäöüÄÖÜß])', r'\1 \2', ingredient)
        
        # Add space between measurement units and ingredients (e.g., "200 gMehl" -> "200 g Mehl")
        ingredient = re.sub(r'([a-zA-Z]+)([A-ZÄÖÜ][a-zäöüß])', r'\1 \2', ingredient)
        
        # Special handling for common German abbreviations
        ingredient = re.sub(r'(\d+)\s*([Ee][Ll])\s*([A-ZÄÖÜ])', r'\1 \2 \3', ingredient)  # EL -> EL 
        ingredient = re.sub(r'(\d+)\s*([Tt][Ll])\s*([A-ZÄÖÜ])', r'\1 \2 \3', ingredient)  # TL -> TL 
        ingredient = re.sub(r'(\d+)\s*([Dd][Ll])\s*([A-ZÄÖÜ])', r'\1 \2 \3', ingredient)  # dl -> dl 
        
        # Clean up multiple spaces
        ingredient = re.sub(r'\s+', ' ', ingredient)
        
        return ingredient.strip()
    
    def _clean_instruction_text(self, instruction: str) -> str:
        """Clean and format instruction text."""
        import re
        
        # Remove HTML entities and clean up text
        instruction = instruction.replace('&#40;', '(').replace('&#41;', ')')
        instruction = re.sub(r'&[a-zA-Z]+;', '', instruction)  # Remove other HTML entities
        
        # Ensure proper sentence structure
        instruction = instruction.strip()
        if instruction and not instruction.endswith('.'):
            instruction += '.'
        
        return instruction
    
    def _generate_recipe_tags(self, recipe_data: Dict) -> list:
        """Generate semantic tags for better RAG retrieval."""
        tags = ['deutsch', 'rezept']
        
        # Add time-based tags
        if recipe_data.get('prep_time'):
            prep_time = recipe_data['prep_time'].lower()
            if any(word in prep_time for word in ['schnell', 'minuten', '15', '10']):
                tags.append('schnell')
        
        # Add ingredient-based tags
        ingredients_text = ' '.join(recipe_data.get('ingredients', [])).lower()
        
        # Protein tags
        if any(word in ingredients_text for word in ['hähnchen', 'huhn', 'poulet']):
            tags.append('hähnchen')
        if any(word in ingredients_text for word in ['schwein', 'speck']):
            tags.append('schweinefleisch')
        if any(word in ingredients_text for word in ['rind', 'beef']):
            tags.append('rindfleisch')
        if any(word in ingredients_text for word in ['fisch', 'lachs', 'crevetten']):
            tags.append('fisch')
        
        # Vegetarian/Vegan indicators
        if not any(word in ingredients_text for word in ['fleisch', 'hähnchen', 'schwein', 'rind', 'speck', 'fisch']):
            tags.append('vegetarisch')
        
        # Cuisine style tags
        if any(word in ingredients_text for word in ['pasta', 'spaghetti', 'parmesan']):
            tags.append('italienisch')
        if any(word in ingredients_text for word in ['feta', 'oliven']):
            tags.append('griechisch')
        
        # Dish type tags
        if any(word in ingredients_text for word in ['salat']):
            tags.append('salat')
        if any(word in ingredients_text for word in ['suppe', 'eintopf']):
            tags.append('suppe')
        
        # Add title-based tags
        title = recipe_data.get('title', '').lower()
        if 'salat' in title:
            tags.append('salat')
        if any(word in title for word in ['kuchen', 'tarte']):
            tags.append('dessert')
        
        return list(set(tags))  # Remove duplicates
