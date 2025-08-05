# German Recipe Parser

A modular Python-based recipe web scraper optimized for German recipe websites. Extracts recipe content from German web pages and converts it to LLM-friendly markdown format with German labels.

## Architecture

The parser follows a clean, modular architecture for better maintainability and testing:

```
recipe-parser/
├── __init__.py          # Package initialization
├── main.py              # Batch processing and CLI functions
├── demo.py              # Demo script with test URLs
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

### Batch Processing (Recommended)

Process multiple URLs concurrently with detailed error handling:

```python
import asyncio
from main import parse_recipes

async def main():
    urls = [
        "https://fooby.ch/de/rezepte/27566/sesam-chicken",
        "https://www.bettybossi.ch/de/rezepte/rezept/veganes-sweet-and-sour-10010271/",
        "https://invalid-url"  # This will fail gracefully
    ]
    
    results = await parse_recipes(urls)
    
    for result in results:
        if result['success']:
            print(f"✅ {result['url']}")
            print(f"Content: {result['content'][:100]}...")
        else:
            print(f"❌ {result['url']}")
            print(f"Error: {result['error']}")

asyncio.run(main())
```

### Single Recipe Processing

```python
import asyncio
from main import parse_recipe

async def main():
    result = await parse_recipe("https://fooby.ch/de/rezepte/27566/sesam-chicken")
    
    if result.success:
        print("✅ Recipe parsed successfully!")
        print(result.content)
    else:
        print(f"❌ Failed: {result.error}")

asyncio.run(main())
```

### Simple API (Backward Compatibility)

```python
import asyncio
from main import parse_recipe_simple

async def main():
    content = await parse_recipe_simple("https://fooby.ch/de/rezepte/27566/sesam-chicken")
    if content:
        print(content)
    else:
        print("Failed to parse recipe")

asyncio.run(main())
```

### Demo and Testing

Run the comprehensive demo:

```bash
python demo.py
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

## Result Format

### Batch Processing Results

The `parse_recipes()` function returns a list of dictionaries with the following structure:

```python
{
    'success': bool,        # True if parsing succeeded
    'content': str | None,  # Markdown content (if successful)
    'error': str | None,    # Error message (if failed)
    'url': str             # Original URL
}
```

### Single Recipe Results

The `parse_recipe()` function returns a `RecipeResult` object with:

```python
result.success  # bool: Whether parsing succeeded
result.content  # str | None: Markdown content
result.error    # str | None: Error message
result.url      # str: Original URL
```

## Error Handling

The parser provides robust error handling for common issues:

- **Invalid URLs**: Malformed or unreachable URLs
- **Network errors**: Connection timeouts, DNS failures
- **Parsing errors**: Missing recipe content, malformed HTML
- **Concurrent processing**: Errors in one URL don't affect others

All errors are captured and returned with descriptive messages, allowing you to:
- Identify which URLs failed and why
- Retry failed URLs if needed
- Log errors for debugging
- Continue processing successful results

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