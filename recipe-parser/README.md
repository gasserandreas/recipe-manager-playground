# German Recipe Parser

A modular Python-based recipe web scraper optimized for German recipe websites. Extracts recipe content from German web pages and converts it to LLM-friendly markdown format with German labels.

## Architecture

The parser follows a clean, modular architecture for better maintainability and testing:

```
recipe-parser/
├── __init__.py          # Package initialization
├── main.py              # CLI and convenience functions
├── parser.py            # Main orchestrator class
├── extractors.py        # JSON-LD and HTML content extractors
├── formatters.py        # German text and markdown formatters
├── loaders.py           # Web content loading utilities
├── utils.py             # URL validation and utilities
├── test_recipe_parser.py # Test suite
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Features

- **Modular Design**: Separated concerns for easier testing and maintenance
- **German-optimized extraction**: Supports German recipe selectors (`.rezept`, `.zutaten`, `.zubereitung`, etc.)
- **German terminology handling**: Recognizes German time formats (Std, Min) and serving terms (Portionen, Personen)
- **JSON-LD support**: Handles structured data common in German recipe websites
- **German markdown output**: Uses German labels (Zutaten, Zubereitung, Kochzeit, etc.)
- **Smart fallback parsing**: Multiple extraction strategies for different German site layouts
- **Time normalization**: Converts German time expressions to consistent format
- **AsyncHtmlLoader integration**: Uses langchain-community for efficient web scraping
- **Comprehensive testing**: Unit tests for all modules

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or if using uv:

```bash
uv sync
```

## Usage

### Basic Usage

```python
import asyncio
from main import parse_recipe

async def main():
    url = "https://fooby.ch/de/rezepte/27566/sesam-chicken"
    markdown_recipe = await parse_recipe(url)
    if markdown_recipe:
        print(markdown_recipe)

asyncio.run(main())
```

### Advanced Usage with Modules

```python
from parser import GermanRecipeParser
from utils import URLValidator

# Validate URL first
if URLValidator.is_valid_url(url):
    parser = GermanRecipeParser()
    markdown_recipe = await parser.parse_recipe_from_url(url)
```

### Using Individual Components

```python
from extractors import JSONLDExtractor, HTMLExtractor
from formatters import GermanTextFormatter, MarkdownFormatter
from loaders import RecipeContentLoader

# Use specific extractors
loader = RecipeContentLoader()
html_content = await loader.load_content(url)

json_extractor = JSONLDExtractor()
html_extractor = HTMLExtractor()

# Use formatters
text_formatter = GermanTextFormatter()
normalized_time = text_formatter.normalize_time_text("15 minuten")

markdown_formatter = MarkdownFormatter()
markdown_output = markdown_formatter.format_recipe(recipe_data, url)
```

## Module Overview

### `parser.py` - Main Orchestrator
- `GermanRecipeParser`: Main class that coordinates extraction and formatting
- Manages the extraction pipeline using specialized components

### `extractors.py` - Content Extractors
- `JSONLDExtractor`: Extracts recipe data from JSON-LD structured data
- `HTMLExtractor`: Extracts recipe data using CSS selectors
- German-aware selectors and fallback strategies

### `formatters.py` - Text and Markdown Formatters
- `GermanTextFormatter`: Normalizes German time and serving text
- `MarkdownFormatter`: Converts recipe data to German markdown format

### `loaders.py` - Web Content Loading
- `RecipeContentLoader`: Handles web content downloading via AsyncHtmlLoader
- Support for single and multiple URL loading

### `utils.py` - Utilities
- `URLValidator`: URL validation and domain extraction utilities

## German Output Format

The parser generates markdown with German labels optimized for LLM processing:

```markdown
# Rezept

## Recipe Title

**Quelle:** [URL]

## Beschreibung
[Recipe description if available]

## Rezept-Details
**Vorbereitungszeit:** [prep time]
**Kochzeit:** [cook time]
**Portionen:** [number of servings]

## Zutaten
- [ingredient 1]
- [ingredient 2]
- ...

## Zubereitung
1. [instruction 1]
2. [instruction 2]
...
```

## Testing

Run the test suite:

```bash
# Run with pytest (recommended)
pytest test_recipe_parser.py -v

# Or run basic tests directly
python test_recipe_parser.py
```

The test suite includes:
- Unit tests for all modules
- Integration tests for URL validation
- German text formatting tests
- Markdown generation tests
- Mock-based tests for network components

## Supported German Recipe Sites

The parser is optimized for common German recipe website patterns including:
- fooby.ch
- swissmilk.ch  
- bettybossi.ch
- chefkoch.de
- essen-und-trinken.de
- brigitte.de
- And many other German recipe sites using standard selectors

## German-Specific Features

### Time Format Handling
- Converts "Stunden" → "Std"
- Converts "Minuten" → "Min"
- Handles ISO 8601 durations (PT15M) → "15 Min"

### Serving Size Handling
- Recognizes "Portionen", "Personen", "Stück"
- Normalizes to consistent German format

### CSS Selectors
Includes German-specific selectors:
- `.rezept`, `.rezept-karte`
- `.zutaten`, `.zutatenliste`
- `.zubereitung`, `.anleitung`
- `.kochzeit`, `.vorbereitungszeit`

## Development

The modular architecture makes it easy to:

- **Add new extractors**: Implement extraction for specific recipe sites
- **Enhance formatters**: Add new output formats or improve text normalization
- **Extend utilities**: Add new validation or helper functions
- **Improve testing**: Add tests for specific scenarios or edge cases

### Code Quality Features

- **Type hints**: Full type annotations for better IDE support
- **Docstrings**: Comprehensive documentation for all functions
- **Error handling**: Robust exception handling with clear error messages
- **Separation of concerns**: Each module has a single, focused responsibility
- **Easy testing**: Modular design enables isolated unit testing