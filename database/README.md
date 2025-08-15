# Recipe RAG Database

Vector database implementation using Weaviate for the Recipe RAG system. This package provides a modular, well-structured solution for storing and retrieving recipes using vector embeddings.

## 🏗️ Package Structure

The database package is organized following Python best practices:

```
database/
├── __init__.py                    # Package initialization with clean exports
├── config/
│   ├── __init__.py               # Configuration module exports
│   ├── database_config.py        # WeaviateConfig class
│   └── settings.py               # Environment variables and constants
├── schema/
│   ├── __init__.py               # Schema module exports
│   └── recipe_schema.py          # RecipeSchema class definition
├── models/
│   ├── __init__.py               # Models module exports
│   └── recipe_document.py        # RecipeDocument dataclass
├── core/
│   ├── __init__.py               # Core module exports
│   ├── weaviate_manager.py       # WeaviateManager class
│   └── recipe_vector_database.py # RecipeVectorDatabase class
├── loaders/
│   ├── __init__.py               # Loaders module exports
│   ├── recipe_data_loader.py     # RecipeDataLoader class
│   └── markdown_recipe_parser.py # MarkdownRecipeParser class
├── utils/
│   ├── __init__.py               # Utilities module exports
│   └── logging_config.py         # Logging configuration
├── setup_db.py                   # Database setup script
├── load_recipes.py               # CLI for loading recipes
├── test_db.py                    # Test suite
└── docker-compose.yml            # Weaviate Docker setup
```

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Install all required packages
uv pip install -r requirements.txt
```

### 2. Start Weaviate Database
```bash
# Start Weaviate using Docker
docker-compose up -d
```

### 3. Setup Database Schema
```bash
# Create the database schema
python setup_db.py --setup-schema

# Or run full setup with health check
python setup_db.py --full-setup
```

### 4. Load Sample Data
```bash
# Load sample recipes from directory
python load_recipes.py --recipes-dir ../recipe-parser/data/recipes --batch-size 10

# Load recipes from CSV with metadata
python load_recipes.py --recipes-dir ../recipe-parser/data/recipes --csv-file recipe_list.csv
```

## 📚 Module Documentation

### Configuration (`config/`)
- **`WeaviateConfig`**: Database connection and configuration management
- **`DatabaseSettings`**: Centralized environment variable handling

### Schema (`schema/`)
- **`RecipeSchema`**: Weaviate collection schema definition with properties and vectorizer configuration

### Models (`models/`)
- **`RecipeDocument`**: Data class representing recipe documents with validation and conversion methods

### Core (`core/`)
- **`WeaviateManager`**: Low-level database operations, connection management, and schema creation
- **`RecipeVectorDatabase`**: High-level recipe operations (CRUD, search, batch operations)

### Loaders (`loaders/`)
- **`MarkdownRecipeParser`**: Parser for markdown recipe files with frontmatter support
- **`RecipeDataLoader`**: Batch loading from directories and CSV files

### Utilities (`utils/`)
- **`logging_config`**: Centralized logging setup and configuration

## 🔧 Usage Examples

### Basic Database Operations

```python
from database import RecipeVectorDatabase, RecipeDocument

# Create a recipe document
recipe = RecipeDocument(
    title="Spaghetti Carbonara",
    source="https://example.com/recipe",
    cuisine="Italian",
    content="Full recipe content here...",
    ingredients="pasta, eggs, cheese",
    instructions="1. Cook pasta..."
)

# Add to database
with RecipeVectorDatabase() as db:
    uuid = db.add_recipe(recipe)
    print(f"Added recipe with ID: {uuid}")
    
    # Search for recipes
    results = db.search_recipes("Italian pasta recipes", limit=5)
    for result in results:
        print(f"Found: {result['properties']['title']}")
```

### Loading Data from Files

```python
from database import RecipeDataLoader

# Load recipes from directory
loader = RecipeDataLoader()
stats = loader.load_recipes_from_directory("../recipe-parser/data/recipes")

print(f"Loaded {stats['successful']} recipes")
```

### Database Management

```python
from database import setup_database

# Setup database schema
manager = setup_database()

# Check health
health = manager.health_check()
print(f"Database status: {health['status']}")

manager.disconnect()
```

## 🛠️ Command Line Tools

### Database Setup Script
```bash
# Check dependencies
python setup_db.py --check-deps

# Setup schema
python setup_db.py --setup-schema

# Load sample data
python setup_db.py --load-data ../recipe-parser/data/recipes

# Full setup (all steps)
python setup_db.py --full-setup

# Check database health
python setup_db.py --health-check

# Count recipes
python setup_db.py --count
```

### Data Loader Script
```bash
# Load recipes from directory
python load_recipes.py --recipes-dir ../recipe-parser/data/recipes

# Load with custom batch size
python load_recipes.py --recipes-dir ../recipe-parser/data/recipes --batch-size 20

# Load from CSV file
python load_recipes.py --csv-file recipes.csv --recipes-dir ../recipe-parser/data/recipes

# Enable verbose logging
python load_recipes.py --recipes-dir ../recipe-parser/data/recipes --verbose
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEAVIATE_URL` | Weaviate database URL | `http://localhost:8080` |
| `WEAVIATE_API_KEY` | Optional Weaviate API key | _(empty)_ |
| `OPENAI_APIKEY` | OpenAI API key for vectorization | _(required)_ |
| `RECIPE_CLASS_NAME` | Weaviate collection name | `Recipe` |
| `WEAVIATE_BATCH_SIZE` | Batch size for operations | `100` |
| `WEAVIATE_TIMEOUT` | Connection timeout | `30` |

## 🏗️ Database Schema

The Recipe collection in Weaviate contains:

- `title` (text) - Recipe name
- `source` (text) - Original URL/source  
- `cuisine` (text) - Cuisine type
- `prep_time` (text) - Preparation time
- `cook_time` (text) - Cooking time
- `servings` (text) - Number of servings
- `ingredients` (text) - Recipe ingredients
- `instructions` (text) - Cooking instructions
- `tags` (text[]) - Recipe tags
- `content` (text) - Full recipe content
- `created_at` (date) - Creation timestamp
- `updated_at` (date) - Last update timestamp

## 🐛 Troubleshooting

### Weaviate Connection Issues
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Check Weaviate logs
docker-compose logs weaviate

# Restart Weaviate
docker-compose restart
```

### Import Errors
```bash
# Test module imports
python -c "import database; print('All imports successful')"

# Check dependencies
python setup_db.py --check-deps

# Reinstall dependencies
uv pip install -r requirements.txt
```

### Schema Issues
```bash
# Reset schema
python setup_db.py --setup-schema

# Check database health
python setup_db.py --health-check
```

### Data Loading Issues
```bash
# Check recipe directory exists
ls -la ../recipe-parser/data/recipes/

# Load with verbose output and smaller batches
python load_recipes.py --recipes-dir ../recipe-parser/data/recipes --batch-size 5 --verbose
```

## 📖 API Reference

### Core Classes

#### `RecipeVectorDatabase`
High-level interface for recipe database operations:

- `add_recipe(recipe: RecipeDocument) -> str` - Add single recipe
- `add_recipes_batch(recipes: List[RecipeDocument]) -> Dict` - Add multiple recipes
- `search_recipes(query: str, limit: int, certainty: float) -> List[Dict]` - Vector search
- `get_recipe_by_id(uuid: str) -> Dict` - Get specific recipe
- `count_recipes() -> int` - Count total recipes
- `get_all_recipes(limit: int, offset: int) -> List[Dict]` - Get all recipes
- `delete_recipe(uuid: str) -> bool` - Delete recipe
- `update_recipe(uuid: str, recipe: RecipeDocument) -> bool` - Update recipe

#### `RecipeDataLoader`
Data loading utilities:

- `load_recipes_from_directory(directory_path: str, pattern: str, batch_size: int) -> Dict` - Load from directory
- `load_recipe_from_csv(csv_path: str, recipes_dir: str) -> Dict` - Load from CSV

#### `WeaviateManager`
Low-level database management:

- `connect() -> bool` - Connect to database
- `disconnect()` - Disconnect from database
- `create_schema() -> bool` - Create database schema
- `delete_schema() -> bool` - Delete database schema
- `health_check() -> Dict` - Check database health
- `count_objects() -> int` - Count objects in database

## 🔄 Migration from Old Structure

If you're upgrading from the previous single-file structure, update your imports:

```python
# Old imports
from config import WeaviateConfig, WeaviateManager, RecipeSchema
from client import RecipeVectorDatabase, RecipeDocument
from loader import RecipeDataLoader

# New imports
from database.config import WeaviateConfig
from database.core import WeaviateManager, RecipeVectorDatabase  
from database.schema import RecipeSchema
from database.models import RecipeDocument
from database.loaders import RecipeDataLoader

# Or use the package-level imports
from database import (
    WeaviateConfig, 
    WeaviateManager, 
    RecipeVectorDatabase,
    RecipeSchema,
    RecipeDocument, 
    RecipeDataLoader
)
```

### RecipeDocument Fields

All fields are optional except `title`, `source`, `cuisine`, and `content`.

### MarkdownRecipeParser Methods

- `parse_recipe_file(file_path)` - Parse markdown file
- `parse_frontmatter(content)` - Extract YAML frontmatter
- `extract_sections(content)` - Extract recipe sections

## 🔗 Integration

This database module integrates with:

- **Recipe Parser** (`../recipe-parser/`) - Source of recipe data
- **Playground** (`../playground/`) - Jupyter notebook experiments
- **Weaviate** - Vector database backend
- **OpenAI** - Text vectorization

## 📝 Development

### Running Tests
```bash
# Run basic tests
python test_db.py

# Run with pytest (if installed)
pytest test_db.py -v
```

### Adding New Features

1. Update schema in `config.py` if needed
2. Add methods to `client.py` for new operations
3. Update `loader.py` for new data sources
4. Add tests to `test_db.py`
5. Update this README

---

For more information, see the main project README or the playground documentation.
