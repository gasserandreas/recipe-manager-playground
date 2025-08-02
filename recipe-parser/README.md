# German Recipe Parser

A Python-based recipe web scraper optimized for German recipe websites. Extracts recipe content from German web pages and converts it to LLM-friendly markdown format with German labels.

## Features

- **German-optimized extraction**: Supports German recipe selectors (`.rezept`, `.zutaten`, `.zubereitung`, etc.)
- **German terminology handling**: Recognizes German time formats (Std, Min) and serving terms (Portionen, Personen)
- **JSON-LD support**: Handles structured data common in German recipe websites
- **German markdown output**: Uses German labels (Zutaten, Zubereitung, Kochzeit, etc.)
- **Smart fallback parsing**: Multiple extraction strategies for different German site layouts
- **Time normalization**: Converts German time expressions to consistent format
- **AsyncHtmlLoader integration**: Uses langchain-community for efficient web scraping

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

### Advanced Usage

```python
from main import RecipeParser

parser = RecipeParser()
markdown_recipe = await parser.parse_recipe_from_url(url)
```

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

## Supported German Recipe Sites

The parser is optimized for common German recipe website patterns including:
- fooby.ch
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