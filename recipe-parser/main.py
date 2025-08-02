import asyncio
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from langchain_community.document_loaders import AsyncHtmlLoader
from markdownify import markdownify as md
from bs4 import BeautifulSoup


class RecipeParser:
    """
    A recipe parser that extracts recipe content from German web pages and converts it to markdown.
    
    This parser is optimized for German recipe websites and focuses on extracting structured 
    recipe data while ignoring non-recipe content. It provides output in German with a format 
    optimized for LLM processing.
    
    Features:
    - Supports German recipe selectors and terminology
    - Handles JSON-LD structured data common in German recipe sites
    - Normalizes German time and serving formats
    - Outputs markdown with German labels (Zutaten, Zubereitung, etc.)
    """
    
    def __init__(self):
        """Initialize the recipe parser with default configuration for German recipes."""
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
            # JSON-LD structured data
            'script[type="application/ld+json"]'
        ]
        
        # German recipe field mappings
        self.german_fields = {
            'zubereitungszeit': 'prep_time',
            'vorbereitungszeit': 'prep_time', 
            'kochzeit': 'cook_time',
            'backzeit': 'cook_time',
            'garzeit': 'cook_time',
            'portionen': 'servings',
            'personen': 'servings',
            'stück': 'servings',
            'zutaten': 'ingredients',
            'zutatenliste': 'ingredients',
            'zubereitung': 'instructions',
            'anleitung': 'instructions',
            'beschreibung': 'description',
            'titel': 'title'
        }
    
    async def parse_recipe_from_url(self, url: str) -> Optional[str]:
        """
        Parse a recipe from a given URL and return it as markdown.
        
        Args:
            url: The URL of the recipe page to parse
            
        Returns:
            Formatted markdown string containing the recipe, or None if parsing fails
            
        Raises:
            ValueError: If the URL is invalid
            Exception: If downloading or parsing fails
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL provided: {url}")
        
        try:
            # Download the web page content
            html_content = await self._download_page_content(url)
            
            # Extract recipe content from HTML
            recipe_data = self._extract_recipe_content(html_content)
            
            # Convert to markdown with LLM-friendly template
            markdown_recipe = self._format_as_markdown(recipe_data, url)
            
            return markdown_recipe
            
        except Exception as e:
            raise Exception(f"Failed to parse recipe from {url}: {str(e)}")
    
    async def _download_page_content(self, url: str) -> str:
        """
        Download HTML content from the given URL using AsyncHtmlLoader.
        
        Args:
            url: The URL to download content from
            
        Returns:
            Raw HTML content as string
        """
        loader = AsyncHtmlLoader([url])
        documents = await loader.aload()
        
        if not documents:
            raise Exception("No content could be loaded from the URL")
        
        return documents[0].page_content
    
    def _extract_recipe_content(self, html_content: str) -> Dict[str, Any]:
        """
        Extract recipe-specific content from HTML, optimized for German recipes.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Dictionary containing extracted recipe data
        """
        soup = BeautifulSoup(html_content, 'lxml')
        recipe_data = {
            'title': '',
            'description': '',
            'ingredients': [],
            'instructions': [],
            'prep_time': '',
            'cook_time': '',
            'servings': '',
            'nutrition': {}
        }
        
        # First try to extract from JSON-LD structured data (common in German sites)
        self._extract_from_json_ld(soup, recipe_data)
        
        # Try to find recipe content using common selectors
        recipe_container = None
        for selector in self.recipe_selectors:
            try:
                recipe_container = soup.select_one(selector)
                if recipe_container:
                    break
            except Exception:
                continue
        
        if recipe_container:
            # Extract title (try German and English variants)
            if not recipe_data['title']:
                title_selectors = [
                    '[itemprop="name"]', 'h1', 'h2', '.recipe-title', '.rezept-titel',
                    '.title', '.titel', '[data-recipe-title]'
                ]
                for selector in title_selectors:
                    title_elem = recipe_container.select_one(selector)
                    if title_elem:
                        recipe_data['title'] = title_elem.get_text(strip=True)
                        break
            
            # Extract description
            if not recipe_data['description']:
                desc_selectors = [
                    '[itemprop="description"]', '.recipe-description', '.rezept-beschreibung',
                    '.description', '.beschreibung', '.intro'
                ]
                for selector in desc_selectors:
                    desc_elem = recipe_container.select_one(selector)
                    if desc_elem:
                        recipe_data['description'] = desc_elem.get_text(strip=True)
                        break
            
            # Extract ingredients (German-aware)
            if not recipe_data['ingredients']:
                ingredient_selectors = [
                    '[itemprop="recipeIngredient"]', '.ingredient', '.zutat',
                    '.ingredients li', '.zutaten li', '.zutatenliste li',
                    '.recipe-ingredients li', '.rezept-zutaten li'
                ]
                for selector in ingredient_selectors:
                    ingredient_elems = recipe_container.select(selector)
                    if ingredient_elems:
                        recipe_data['ingredients'] = [elem.get_text(strip=True) for elem in ingredient_elems if elem.get_text(strip=True)]
                        break
            
            # Extract instructions (German-aware)
            if not recipe_data['instructions']:
                instruction_selectors = [
                    '[itemprop="recipeInstruction"]', '.instruction', '.step', '.schritt',
                    '.instructions li', '.anleitung li', '.zubereitung li',
                    '.recipe-instructions li', '.rezept-anleitung li',
                    '.instructions p', '.anleitung p', '.zubereitung p'
                ]
                for selector in instruction_selectors:
                    instruction_elems = recipe_container.select(selector)
                    if instruction_elems:
                        recipe_data['instructions'] = [elem.get_text(strip=True) for elem in instruction_elems if elem.get_text(strip=True)]
                        break
            
            # Extract timing information (German terms)
            if not recipe_data['prep_time']:
                prep_selectors = [
                    '[itemprop="prepTime"]', '.prep-time', '.vorbereitungszeit',
                    '.zubereitungszeit', '[data-prep-time]'
                ]
                for selector in prep_selectors:
                    prep_elem = recipe_container.select_one(selector)
                    if prep_elem:
                        recipe_data['prep_time'] = self._normalize_time_text(prep_elem.get_text(strip=True))
                        break
            
            if not recipe_data['cook_time']:
                cook_selectors = [
                    '[itemprop="cookTime"]', '.cook-time', '.kochzeit',
                    '.backzeit', '.garzeit', '[data-cook-time]'
                ]
                for selector in cook_selectors:
                    cook_elem = recipe_container.select_one(selector)
                    if cook_elem:
                        recipe_data['cook_time'] = self._normalize_time_text(cook_elem.get_text(strip=True))
                        break
            
            # Extract servings (German terms)
            if not recipe_data['servings']:
                servings_selectors = [
                    '[itemprop="recipeYield"]', '.servings', '.portionen',
                    '.personen', '.yield', '[data-servings]'
                ]
                for selector in servings_selectors:
                    servings_elem = recipe_container.select_one(selector)
                    if servings_elem:
                        recipe_data['servings'] = self._normalize_servings_text(servings_elem.get_text(strip=True))
                        break
        
        # Fallback: if no structured data found, try general extraction
        if not recipe_data['title']:
            title_elem = soup.find('h1')
            if title_elem:
                recipe_data['title'] = title_elem.get_text(strip=True)
        
        return recipe_data
    
    def _extract_from_json_ld(self, soup: BeautifulSoup, recipe_data: Dict[str, Any]) -> None:
        """
        Extract recipe data from JSON-LD structured data.
        
        Args:
            soup: BeautifulSoup object
            recipe_data: Dictionary to populate with extracted data
        """
        import json
        
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
                        # Extract title
                        if not recipe_data['title'] and 'name' in item:
                            recipe_data['title'] = item['name']
                        
                        # Extract description
                        if not recipe_data['description'] and 'description' in item:
                            recipe_data['description'] = item['description']
                        
                        # Extract ingredients
                        if not recipe_data['ingredients'] and 'recipeIngredient' in item:
                            recipe_data['ingredients'] = item['recipeIngredient']
                        
                        # Extract instructions
                        if not recipe_data['instructions'] and 'recipeInstructions' in item:
                            instructions = []
                            for instruction in item['recipeInstructions']:
                                if isinstance(instruction, dict):
                                    if 'text' in instruction:
                                        instructions.append(instruction['text'])
                                    elif 'name' in instruction:
                                        instructions.append(instruction['name'])
                                else:
                                    instructions.append(str(instruction))
                            recipe_data['instructions'] = instructions
                        
                        # Extract timing
                        if not recipe_data['prep_time'] and 'prepTime' in item:
                            recipe_data['prep_time'] = self._parse_duration(item['prepTime'])
                        
                        if not recipe_data['cook_time'] and 'cookTime' in item:
                            recipe_data['cook_time'] = self._parse_duration(item['cookTime'])
                        
                        # Extract servings
                        if not recipe_data['servings'] and 'recipeYield' in item:
                            yield_value = item['recipeYield']
                            if isinstance(yield_value, list):
                                recipe_data['servings'] = str(yield_value[0])
                            else:
                                recipe_data['servings'] = str(yield_value)
                        
                        break
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
    
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
    
    def _normalize_time_text(self, time_text: str) -> str:
        """
        Normalize German time text to consistent format.
        
        Args:
            time_text: Raw time text
            
        Returns:
            Normalized time string
        """
        if not time_text:
            return ""
        
        # Common German time patterns
        time_text = time_text.lower().strip()
        
        # Replace German words with standard abbreviations
        replacements = {
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
        
        for german, abbrev in replacements.items():
            time_text = time_text.replace(german, abbrev)
        
        return time_text.title()
    
    def _normalize_servings_text(self, servings_text: str) -> str:
        """
        Normalize German servings text to consistent format.
        
        Args:
            servings_text: Raw servings text
            
        Returns:
            Normalized servings string
        """
        if not servings_text:
            return ""
        
        # Extract numbers from German servings text
        import re
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
    
    def _format_as_markdown(self, recipe_data: Dict[str, Any], source_url: str) -> str:
        """
        Format recipe data as markdown following a template optimized for German recipe LLM processing.
        
        Args:
            recipe_data: Extracted recipe data
            source_url: Source URL of the recipe
            
        Returns:
            Formatted markdown string with German labels
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
        details = []
        if recipe_data['prep_time']:
            details.append(f"**Vorbereitungszeit:** {recipe_data['prep_time']}")
        if recipe_data['cook_time']:
            details.append(f"**Kochzeit:** {recipe_data['cook_time']}")
        if recipe_data['servings']:
            details.append(f"**Portionen:** {recipe_data['servings']}")
        
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
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if the provided URL is properly formatted.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


async def parse_recipe(url: str) -> Optional[str]:
    """
    Convenience function to parse a German recipe from a URL.
    
    Args:
        url: The URL of the German recipe page to parse
        
    Returns:
        Formatted markdown string containing the recipe in German, or None if parsing fails
    """
    parser = RecipeParser()
    try:
        return await parser.parse_recipe_from_url(url)
    except Exception as e:
        print(f"Fehler beim Parsen des Rezepts: {e}")
        return None


def main():
    """Main function for testing the German recipe parser."""
    print("Deutscher Rezept-Parser initialisiert!")
    print("Verwende parse_recipe(url) Funktion um Rezepte von URLs zu parsen.")
    
    # test_url = "https://fooby.ch/de/rezepte/27566/sesam-chicken" # fooby.ch example
    # test_url = "https://www.swissmilk.ch/de/rezepte-kochideen/rezepte/SM2021_DIVE_12/griechischer-salat/" # swissmilk.ch example
    test_url = "https://www.bettybossi.ch/de/rezepte/rezept/veganes-sweet-and-sour-10010271/" # bettybossi.ch example
    # test_url = "https://1mal1japan.de/rezepte/yakimeshi/" # random example

    # Example usage
    print(f"\nTeste mit: {test_url}")
    result = asyncio.run(parse_recipe(test_url))
    if result:
        print("\n" + "="*50)
        print("ERGEBNIS:")
        print("="*50)
        print(result)
    else:
        print("Fehler: Rezept konnte nicht geparst werden.")


if __name__ == "__main__":
    main()
