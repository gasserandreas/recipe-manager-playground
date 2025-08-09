# Recipe RAG Playground

Interactive Jupyter notebook environment for experimenting with the Recipe RAG system using Weaviate vector database and Claude API.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Install all required packages
uv pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your API keys
nano .env  # or use your preferred editor
```

### 3. Start Weaviate Database
```bash
# Start the Weaviate database (from database folder)
cd ../database
./setup.sh start
cd ../playground
```

### 4. Setup Database Schema
```bash
# Create the database schema (one-time setup)
cd ../database
python -c "from config import setup_database; setup_database()"
cd ../playground
```

### 5. Load Sample Recipe Data (Optional)
```bash
# Load some sample recipes for testing
cd ../database
python loader.py --recipes-dir ../recipe-parser/data/recipes --batch-size 10
cd ../playground
```

### 6. Start Jupyter Lab
```bash
# Start Jupyter Lab
uv run jupyter lab

# Or use Jupyter Notebook
uv run jupyter notebook --port=8888 --ServerApp.password='test'

# Or start with specific port
uv run jupyter lab --port=8888
```

### 5. Login with default password
login using default password: `test`

## 📋 Required API Keys

Add these to your `.env` file:

- **OpenAI API Key** (`OPENAI_APIKEY`): Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic API Key** (`ANTHROPIC_API_KEY`): Get from [Anthropic Console](https://console.anthropic.com/)

## 📂 Files

- `recipe_rag_playground.ipynb` - Main playground notebook
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (your API keys)
- `.env.example` - Environment template

## 🎯 What You Can Do

1. **Connect to Weaviate** - Query your recipe database
2. **Use Claude API** - Generate recipe suggestions and analysis
3. **RAG Experiments** - Combine vector search with AI generation
4. **Data Analysis** - Explore recipe data with pandas/matplotlib

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEAVIATE_URL` | Weaviate database URL | `http://localhost:8080` |
| `OPENAI_APIKEY` | OpenAI API key for vectorization | Required |
| `ANTHROPIC_API_KEY` | Claude API key | Required |
| `DEFAULT_MODEL` | Claude model to use | `claude-3-haiku-20240307` |
| `RECIPE_CLASS_NAME` | Weaviate collection name | `Recipe` |

## 🐛 Troubleshooting

### Database Setup Issues
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Restart Weaviate
cd ../database && ./setup.sh restart

# Setup database schema
cd ../database && python -c "from config import setup_database; setup_database()"

# Check database status
cd ../database && ./setup.sh status
```

### No Recipe Data
```bash
# Load sample recipes
cd ../database && python loader.py --recipes-dir ../recipe-parser/data/recipes

# Check recipe count
cd ../database && python -c "from client import RecipeVectorDatabase; db = RecipeVectorDatabase(); db.connect(); print(f'Recipes: {db.count_recipes()}'); db.disconnect()"
```

### Weaviate Connection Issues
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Restart Weaviate
cd ../database && ./setup.sh restart
```

### Missing Dependencies
```bash
# Reinstall dependencies
uv pip install -r requirements.txt --force-reinstall
```

### Jupyter Not Starting
```bash
# Install Jupyter explicitly
uv pip install jupyter jupyterlab

# Start with verbose output
uv run jupyter lab --debug
```

## 📖 Next Steps

1. Load recipe data: `cd ../database && python loader.py --recipes-dir ../recipe-parser/data/recipes`
2. Open the playground notebook and start experimenting!
3. Check the [database README](../database/README.md) for more Weaviate setup options