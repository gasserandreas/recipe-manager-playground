#!/usr/bin/env python3
"""
Test script for the Recipe RAG database setup

This script tests the basic functionality of the database modules.
"""

import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        import sys
        sys.path.append('.')
        from config import WeaviateConfig, DatabaseSettings
        from schema import RecipeSchema
        from core import WeaviateManager
        print("✅ config, schema, and core modules imported successfully")
    except Exception as e:
        print(f"❌ Failed to import config/schema/core: {e}")
        return False
    
    try:
        from models import RecipeDocument
        from core import RecipeVectorDatabase
        print("✅ models and core modules imported successfully")
    except Exception as e:
        print(f"❌ Failed to import models/core: {e}")
        return False
    
    try:
        from loaders import RecipeDataLoader, MarkdownRecipeParser
        print("✅ loaders module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import loaders: {e}")
        return False
    
    try:
        from utils import setup_logging, get_logger
        print("✅ utils module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import utils: {e}")
        return False
    
    return True

def test_weaviate_dependency():
    """Test if weaviate can be imported."""
    print("\n🧪 Testing Weaviate dependency...")
    
    try:
        import weaviate
        print("✅ weaviate-client is available")
        return True
    except ImportError:
        print("❌ weaviate-client is not installed")
        print("Install with: pip install weaviate-client")
        return False

def test_config_creation():
    """Test configuration creation."""
    print("\n🧪 Testing configuration creation...")
    
    try:
        from config import WeaviateConfig
        config = WeaviateConfig()
        print(f"✅ Configuration created: {config.url}")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        return False

def test_recipe_document():
    """Test recipe document creation."""
    print("\n🧪 Testing recipe document creation...")
    
    try:
        from models import RecipeDocument
        recipe = RecipeDocument(
            title="Test Recipe",
            source="test://example.com",
            cuisine="test",
            content="# Test Recipe\n\nThis is a test recipe.",
            ingredients="1 cup test ingredient",
            instructions="1. Test step"
        )
        data = recipe.to_dict()
        print(f"✅ Recipe document created: {recipe.title}")
        print(f"   Data keys: {list(data.keys())}")
        return True
    except Exception as e:
        print(f"❌ Failed to create recipe document: {e}")
        return False

def test_markdown_parser():
    """Test markdown parser."""
    print("\n🧪 Testing markdown parser...")
    
    try:
        from loaders import MarkdownRecipeParser
        parser = MarkdownRecipeParser()
        
        # Test frontmatter parsing
        content = """---
title: "Test Recipe"
cuisine: "test"
---

# Test Recipe

## Ingredients
- 1 cup test

## Instructions
1. Mix everything
"""
        frontmatter, body = parser.parse_frontmatter(content)
        sections = parser.extract_sections(body)
        
        print(f"✅ Markdown parser working")
        print(f"   Frontmatter: {frontmatter}")
        print(f"   Sections: {list(sections.keys())}")
        return True
    except Exception as e:
        print(f"❌ Failed to test markdown parser: {e}")
        return False

def test_package_imports():
    """Test package-level imports."""
    print("\n🧪 Testing package-level imports...")
    
    try:
        import sys
        import os
        # Add parent directory to path to import database as a package
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        import database
        from database import (
            WeaviateConfig, 
            RecipeDocument, 
            RecipeDataLoader,
            setup_logging
        )
        print("✅ Package-level imports working")
        print(f"   Database version: {database.__version__}")
        return True
    except Exception as e:
        print(f"❌ Failed to test package imports: {e}")
        return False

def main():
    """Run all tests."""
    print("🔬 Running database module tests...\n")
    
    tests = [
        test_imports,
        test_weaviate_dependency,
        test_config_creation,
        test_recipe_document,
        test_markdown_parser,
        test_package_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database modules are ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
