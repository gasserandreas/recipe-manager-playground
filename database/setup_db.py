#!/usr/bin/env python3
"""
Simple setup script for the Recipe RAG database

This script helps set up and manage the Weaviate database for the Recipe RAG system.
"""

import os
import sys
import argparse
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import weaviate
        print("✅ weaviate-client is installed")
        return True
    except ImportError:
        print("❌ weaviate-client is not installed")
        print("Install with: pip install weaviate-client")
        return False

def setup_database_schema():
    """Set up the database schema."""
    try:
        from config import setup_database
        print("🔧 Setting up database schema...")
        manager = setup_database()
        print("✅ Database schema setup completed!")
        manager.disconnect()
        return True
    except Exception as e:
        print(f"❌ Failed to setup database schema: {e}")
        return False

def load_sample_data(recipes_dir, batch_size=10):
    """Load sample recipe data."""
    try:
        from loader import RecipeDataLoader
        print(f"📚 Loading sample recipes from: {recipes_dir}")
        loader = RecipeDataLoader()
        stats = loader.load_recipes_from_directory(recipes_dir, batch_size=batch_size)
        
        print(f"Loading completed:")
        print(f"  Successful: {stats['successful']}")
        print(f"  Failed: {stats['failed']}")
        
        if stats.get('errors'):
            print(f"  Errors: {len(stats['errors'])}")
            for error in stats['errors'][:3]:
                print(f"    - {error}")
        
        return stats['successful'] > 0
    except Exception as e:
        print(f"❌ Failed to load sample data: {e}")
        return False

def check_database_health():
    """Check database health and connection."""
    try:
        from config import WeaviateManager
        print("🔍 Checking database health...")
        
        manager = WeaviateManager()
        if manager.connect():
            health = manager.health_check()
            print(f"Status: {health['status']}")
            print(f"Ready: {health['ready']}")
            print(f"Live: {health['live']}")
            print(f"Version: {health.get('version', 'unknown')}")
            manager.disconnect()
            return health['status'] == 'healthy'
        else:
            print("❌ Failed to connect to database")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def count_recipes():
    """Count recipes in the database."""
    try:
        from client import RecipeVectorDatabase
        print("📊 Counting recipes in database...")
        
        with RecipeVectorDatabase() as db:
            count = db.count_recipes()
            print(f"Total recipes: {count}")
            return count
    except Exception as e:
        print(f"❌ Failed to count recipes: {e}")
        return 0

def main():
    """Main setup script."""
    parser = argparse.ArgumentParser(description="Setup Recipe RAG database")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    parser.add_argument("--setup-schema", action="store_true", help="Setup database schema")
    parser.add_argument("--load-data", help="Load sample data from directory")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for loading")
    parser.add_argument("--health-check", action="store_true", help="Check database health")
    parser.add_argument("--count", action="store_true", help="Count recipes in database")
    parser.add_argument("--full-setup", action="store_true", help="Run full setup process")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if args.check_deps or args.full_setup:
        if not check_dependencies():
            sys.exit(1)
    
    if args.health_check or args.full_setup:
        if not check_database_health():
            print("\n💡 Make sure Weaviate is running:")
            print("   ./setup.sh start")
            if not args.full_setup:
                sys.exit(1)
    
    if args.setup_schema or args.full_setup:
        if not setup_database_schema():
            sys.exit(1)
    
    if args.load_data or args.full_setup:
        data_dir = args.load_data or "../recipe-parser/data/recipes"
        if os.path.exists(data_dir):
            if not load_sample_data(data_dir, args.batch_size):
                print("⚠️  Failed to load some or all recipes")
        else:
            print(f"❌ Recipe directory not found: {data_dir}")
            if not args.full_setup:
                sys.exit(1)
    
    if args.count:
        count_recipes()
    
    if args.full_setup:
        print("\n🎉 Full setup completed!")
        print("You can now use the Recipe RAG system.")
        print("Open the playground notebook to start experimenting!")

if __name__ == "__main__":
    main()
