# Recipe RAG Database

Vector database implementation using Weaviate for the Recipe RAG system.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Install all required packages
uv pip install -r requirements.txt
```

### 2. Start Weaviate Database
```bash
# Start Weaviate using Docker
./setup.sh start
```

### 3. Setup Database Schema
```bash
# Create the database schema
python setup_db.py --setup-schema

# Or run full setup
python setup_db.py --full-setup
```

### 4. Load Sample Data
```bash
# Load sample recipes
python loader.py --recipes-dir ../recipe-parser/data/recipes --batch-size 10
```

## 📂 Files Overview

### Core Modules
- `config.py` - Database configuration and schema definitions
- `client.py` - High-level database client for recipe operations
- `loader.py` - Data loading utilities for importing recipes
- `__init__.py` - Package initialization

### Scripts
- `setup_db.py` - Database setup and management script
- `test_db.py` - Test script for verifying functionality
- `setup.sh` - Docker management script for Weaviate

### Configuration
- `docker-compose.yml` - Weaviate Docker configuration
- `requirements.txt` - Python dependencies
- `.env` / `.env.example` - Environment variables

## 🔧 Usage

### Basic Database Operations

```python
from client import RecipeVectorDatabase, RecipeDocument

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
from loader import RecipeDataLoader

# Load recipes from directory
loader = RecipeDataLoader()
stats = loader.load_recipes_from_directory("../recipe-parser/data/recipes")

print(f"Loaded {stats['successful']} recipes")
```

### Database Management

```python
from config import setup_database

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
python loader.py --recipes-dir ../recipe-parser/data/recipes

# Load with custom batch size
python loader.py --recipes-dir ../recipe-parser/data/recipes --batch-size 20

# Load from CSV file
python loader.py --csv-file recipes.csv --recipes-dir ../recipe-parser/data/recipes
```

### Docker Management
```bash
# Start Weaviate
./setup.sh start

# Stop Weaviate
./setup.sh stop

# Restart Weaviate
./setup.sh restart

# Check status
./setup.sh status

# View logs
./setup.sh logs

# Clean up (deletes all data!)
./setup.sh clean
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

The Recipe class in Weaviate contains:

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

# Check logs
./setup.sh logs

# Restart Weaviate
./setup.sh restart
```

### Import Errors
```bash
# Test module imports
python test_db.py

# Reinstall dependencies
uv pip install -r requirements.txt --force-reinstall
```

### Schema Issues
```bash
# Reset schema
python setup_db.py --setup-schema

# Check current schema
python -c "from config import WeaviateManager; m = WeaviateManager(); m.connect(); print(m.client.schema.get()); m.disconnect()"
```

### Data Loading Issues
```bash
# Check recipe directory exists
ls -la ../recipe-parser/data/recipes/

# Load with verbose output
python loader.py --recipes-dir ../recipe-parser/data/recipes --batch-size 5
```

## 📖 API Reference

### RecipeVectorDatabase Methods

- `add_recipe(recipe)` - Add single recipe
- `add_recipes_batch(recipes)` - Add multiple recipes
- `search_recipes(query, limit, certainty)` - Vector search
- `get_recipe_by_id(uuid)` - Get specific recipe
- `count_recipes()` - Count total recipes
- `get_all_recipes(limit, offset)` - Get all recipes

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
