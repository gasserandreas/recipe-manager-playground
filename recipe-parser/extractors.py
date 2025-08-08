"""
Recipe content extractors for different data sources.

This module contains extractors that handle different methods of extracting
recipe data from HTML content, including JSON-LD structured data and CSS selectors.
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from bs4 import BeautifulSoup, Tag


class JSONLDExtractor:
    """Extracts recipe data from JSON-LD structured data."""
    
    def extract(self, soup: BeautifulSoup, recipe_data: Dict[str, Any]) -> None:
        """
        Extract recipe data from JSON-LD structured data.
        
        Args:
            soup: BeautifulSoup object
            recipe_data: Dictionary to populate with extracted data
        """
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle single object or list of objects
                if isinstance(data, list):
                    data_list = data
                else:
                    data_list = [data]
                
                for item in data_list:
                    if isinstance(item, dict) and item.get('@type') == 'Recipe':
                        self._extract_recipe_fields(item, recipe_data)
                        break
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
    
    def _extract_recipe_fields(self, recipe_json: Dict[str, Any], recipe_data: Dict[str, Any]) -> None:
        """Extract individual fields from JSON-LD recipe data."""
        # Extract title
        if not recipe_data['title'] and 'name' in recipe_json:
            recipe_data['title'] = recipe_json['name']
        
        # Extract description
        if not recipe_data['description'] and 'description' in recipe_json:
            recipe_data['description'] = recipe_json['description']
        
        # Extract ingredients
        if not recipe_data['ingredients'] and 'recipeIngredient' in recipe_json:
            recipe_data['ingredients'] = recipe_json['recipeIngredient']
        
        # Extract instructions
        if not recipe_data['instructions'] and 'recipeInstructions' in recipe_json:
            instructions = []
            for instruction in recipe_json['recipeInstructions']:
                if isinstance(instruction, dict):
                    if 'text' in instruction:
                        instructions.append(instruction['text'])
                    elif 'name' in instruction:
                        instructions.append(instruction['name'])
                else:
                    instructions.append(str(instruction))
            recipe_data['instructions'] = instructions
        
        # Extract timing
        if not recipe_data['prep_time'] and 'prepTime' in recipe_json:
            recipe_data['prep_time'] = self._parse_duration(recipe_json['prepTime'])
        
        if not recipe_data['cook_time'] and 'cookTime' in recipe_json:
            recipe_data['cook_time'] = self._parse_duration(recipe_json['cookTime'])
        
        # Extract servings
        if not recipe_data['servings'] and 'recipeYield' in recipe_json:
            yield_value = recipe_json['recipeYield']
            if isinstance(yield_value, list):
                recipe_data['servings'] = str(yield_value[0])
            else:
                recipe_data['servings'] = str(yield_value)
    
    def _parse_duration(self, duration_str: str) -> str:
        """
        Parse ISO 8601 duration format (PT15M) to readable German format.
        
        Args:
            duration_str: Duration string in ISO format
            
        Returns:
            Human-readable duration string in German
        """
        if not duration_str.startswith('PT'):
            return duration_str
        
        duration_str = duration_str[2:]  # Remove 'PT'
        hours = 0
        minutes = 0
        
        if 'H' in duration_str:
            parts = duration_str.split('H')
            hours = int(parts[0])
            duration_str = parts[1] if len(parts) > 1 else ''
        
        if 'M' in duration_str:
            minutes = int(duration_str.replace('M', ''))
        
        if hours > 0 and minutes > 0:
            return f"{hours} Std {minutes} Min"
        elif hours > 0:
            return f"{hours} Std"
        elif minutes > 0:
            return f"{minutes} Min"
        else:
            return duration_str


class HTMLExtractor:
    """Extracts recipe data from HTML using CSS selectors."""
    
    def __init__(self):
        """Initialize with German recipe selectors."""
        self.recipe_selectors = [
            # Common recipe structured data selectors
            '[itemtype*="Recipe"]',
            '[typeof*="Recipe"]',
            '.recipe',
            '.recipe-card',
            '.recipe-content',
            '.recipe-instructions',
            '.recipe-ingredients',
            # German-specific selectors
            '.rezept',
            '.rezept-karte',
            '.rezept-inhalt',
            '.zutatenliste',
            '.zubereitung',
            '.anleitung',
            '.kochzeit',
            '.vorbereitungszeit',
        ]
        
        self.field_selectors = {
            'title': [
                '[itemprop="name"]', 'h1', 'h2', '.recipe-title', '.rezept-titel',
                '.title', '.titel', '[data-recipe-title]'
            ],
            'description': [
                '[itemprop="description"]', '.recipe-description', '.rezept-beschreibung',
                '.description', '.beschreibung', '.intro'
            ],
            'ingredients': [
                '[itemprop="recipeIngredient"]', '.ingredient', '.zutat',
                '.ingredients li', '.zutaten li', '.zutatenliste li',
                '.recipe-ingredients li', '.rezept-zutaten li'
            ],
            'instructions': [
                '[itemprop="recipeInstruction"]', '.instruction', '.step', '.schritt',
                '.instructions li', '.anleitung li', '.zubereitung li',
                '.recipe-instructions li', '.rezept-anleitung li',
                '.instructions p', '.anleitung p', '.zubereitung p',
                # Additional selectors for SwissMilk and similar sites
                '.preparation-steps li', '.recipe-preparation li',
                'ol[data-recipe-steps] li', 'ul[data-recipe-steps] li'
            ],
            'prep_time': [
                '[itemprop="prepTime"]', '.prep-time', '.vorbereitungszeit',
                '.zubereitungszeit', '[data-prep-time]'
            ],
            'cook_time': [
                '[itemprop="cookTime"]', '.cook-time', '.kochzeit',
                '.backzeit', '.garzeit', '[data-cook-time]'
            ],
            'servings': [
                '[itemprop="recipeYield"]', '.servings', '.portionen',
                '.personen', '.yield', '[data-servings]'
            ]
        }
    
    def extract(self, soup: BeautifulSoup, recipe_data: Dict[str, Any]) -> None:
        """
        Extract recipe data from HTML using CSS selectors.
        
        Args:
            soup: BeautifulSoup object
            recipe_data: Dictionary to populate with extracted data
        """
        # Find recipe container
        recipe_container = self._find_recipe_container(soup)
        
        if recipe_container:
            self._extract_all_fields(recipe_container, recipe_data)
        
        # Fallback: try to extract title from page if not found
        if not recipe_data['title']:
            title_elem = soup.find('h1')
            if title_elem:
                recipe_data['title'] = title_elem.get_text(strip=True)
    
    def _find_recipe_container(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the main recipe container element."""
        for selector in self.recipe_selectors:
            try:
                container = soup.select_one(selector)
                if container:
                    return container
            except Exception:
                continue
        return None
    
    def _extract_all_fields(self, container: Tag, recipe_data: Dict[str, Any]) -> None:
        """Extract all recipe fields from the container."""
        # Extract single-value fields
        for field in ['title', 'description', 'prep_time', 'cook_time', 'servings']:
            if not recipe_data[field]:
                recipe_data[field] = self._extract_single_field(container, field)
        
        # Extract list fields
        for field in ['ingredients', 'instructions']:
            if not recipe_data[field]:
                recipe_data[field] = self._extract_list_field(container, field)
    
    def _extract_single_field(self, container: Tag, field: str) -> str:
        """Extract a single text field."""
        selectors = self.field_selectors.get(field, [])
        for selector in selectors:
            elem = container.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if field in ['prep_time', 'cook_time']:
                    try:
                        from .formatters import GermanTextFormatter
                    except ImportError:
                        from formatters import GermanTextFormatter
                    formatter = GermanTextFormatter()
                    return formatter.normalize_time_text(text)
                elif field == 'servings':
                    try:
                        from .formatters import GermanTextFormatter
                    except ImportError:
                        from formatters import GermanTextFormatter
                    formatter = GermanTextFormatter()
                    return formatter.normalize_servings_text(text)
                return text
        return ""
    
    def _extract_list_field(self, container: Tag, field: str) -> List[str]:
        """Extract a list field (ingredients or instructions)."""
        selectors = self.field_selectors.get(field, [])
        
        # Try primary selectors first
        for selector in selectors:
            elems = container.select(selector)
            if elems:
                texts = [elem.get_text(strip=True) for elem in elems if elem.get_text(strip=True)]
                if texts:
                    return texts
        
        # Enhanced fallback for instructions - be more aggressive
        if field == 'instructions':
            return self._fallback_instruction_extraction(container)
        
        # Enhanced fallback for ingredients
        if field == 'ingredients':
            return self._fallback_ingredient_extraction(container)
            
        return []
    
    def _fallback_instruction_extraction(self, container: Tag) -> List[str]:
        """More aggressive instruction extraction as fallback."""
        from bs4 import BeautifulSoup
        
        # Try to find ordered or unordered lists with step-like content
        potential_instruction_lists = container.find_all(['ol', 'ul'])
        for list_elem in potential_instruction_lists:
            items = list_elem.find_all('li')
            if len(items) >= 2:  # Likely instructions if multiple steps
                texts = []
                for item in items:
                    text = item.get_text(strip=True)
                    # Filter out very short texts that are likely not instructions
                    # Also check for cooking-related German keywords
                    if (len(text) > 20 and 
                        any(word in text.lower() for word in 
                           ['min', 'grad', 'ofen', 'pfanne', 'topf', 'rühren', 'braten', 
                            'kochen', 'schneiden', 'mischen', 'würzen', 'erhitzen', 'zutaten',
                            'aufkochen', 'garen', 'abgiessen', 'abtropfen', 'zugedeckt',
                            'weich', 'anbraten', 'dünsten', 'salzen', 'würzen']) and
                        # Exclude navigation or UI elements
                        not any(ui_word in text.lower() for ui_word in 
                               ['drucken', 'rezeptbuch', 'einkauf', 'startseite', 'navigation',
                                'sterne', 'bewertung', 'aktiv', 'gesamt', 'kontakt', 'impressum'])):
                        texts.append(text)
                
                # If we found good instruction texts, return them
                if len(texts) >= 2:
                    return texts
        
        # Look for numbered paragraphs or divs
        potential_steps = container.find_all(['p', 'div'], string=re.compile(r'^\d+\.'))
        if potential_steps:
            return [step.get_text(strip=True) for step in potential_steps]
        
        # Look for paragraphs with cooking-related keywords
        all_paragraphs = container.find_all('p')
        instruction_paragraphs = []
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if (len(text) > 30 and 
                any(word in text.lower() for word in 
                    ['erhitzen', 'braten', 'kochen', 'backen', 'rühren', 'mischen', 
                     'schneiden', 'würzen', 'zugeben', 'servieren', 'anbraten', 'dünsten',
                     'aufkochen', 'garen', 'abgiessen', 'abtropfen'])):
                instruction_paragraphs.append(text)
        
        return instruction_paragraphs
    
    def _fallback_ingredient_extraction(self, container: Tag) -> List[str]:
        """Enhanced ingredient extraction as fallback."""
        # Look for any lists that might contain ingredients
        potential_lists = container.find_all(['ul', 'ol'])
        for list_elem in potential_lists:
            items = list_elem.find_all('li')
            if items:
                texts = []
                for item in items:
                    text = item.get_text(strip=True)
                    # Check if text looks like an ingredient (has measurements or common words)
                    if (re.search(r'\d+\s*(g|kg|ml|l|tl|el|stück|stk|prise|bund)', text.lower()) or
                        any(word in text.lower() for word in 
                            ['salz', 'pfeffer', 'öl', 'butter', 'zwiebel', 'knoblauch', 'tomat'])):
                        texts.append(text)
                if len(texts) >= 3:  # Likely ingredients if multiple items found
                    return texts
        
        return []
