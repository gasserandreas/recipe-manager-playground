"""
Demo script for testing the German Recipe Parser.

This script reads recipe URLs from a CSV file, parses them, and saves
the parsed markdown content as individual files.
"""

import asyncio
import csv
import os
import re
from pathlib import Path
from urllib.parse import urlparse

# Try importing from installed package first
from main import parse_recipes

def sanitize_filename(title: str, url: str) -> str:
    """Create a safe filename from recipe title and URL."""
    # Use title if available, otherwise extract from URL
    if title and title.strip() and title != "title":
        filename = title.strip()
    else:
        # Extract filename from URL path
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        filename = path_parts[-1] if path_parts and path_parts[-1] else parsed_url.netloc
    
    # Clean up the filename
    # Remove or replace invalid characters
    filename = re.sub(r'[^\w\s\-äöüÄÖÜß]', '', filename)
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = filename.strip('_')  # Remove leading/trailing underscores
    
    # Ensure it's not empty and not too long
    if not filename:
        filename = "recipe"
    filename = filename[:100]  # Limit length
    
    return f"{filename}.md"


def load_recipe_urls(csv_path: str) -> list[tuple[str, str]]:
    """Load recipe URLs and titles from CSV file."""
    recipes = []
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = row.get('title', '').strip()
            url = row.get('url', '').strip()
            
            if url:  # Only add if URL is present
                recipes.append((title, url))
    
    return recipes


async def save_parsed_recipes(recipes: list[tuple[str, str]], output_dir: str = "./data/recipes/"):
    """Parse recipes and save as individual markdown files."""
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🇩🇪 German Recipe Parser - Batch Processing")
    print("=" * 60)
    print(f"📂 Input: {len(recipes)} recipes from CSV")
    print(f"📁 Output directory: {output_path.absolute()}")
    print("-" * 60)
    
    # Extract URLs for batch processing
    urls = [url for _, url in recipes]
    
    # Parse all recipes in batch
    print("🔄 Starting batch parsing...")
    results = await parse_recipes(urls)
    
    # Process and save results
    saved_count = 0
    failed_count = 0
    
    for (title, url), result in zip(recipes, results):
        print(f"\n📄 Processing: {title or 'Untitled'}")
        print(f"🔗 URL: {url}")
        
        if result['success']:
            # Generate filename
            filename = sanitize_filename(title, url)
            filepath = output_path / filename
            
            # Handle duplicate filenames
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                stem = original_filepath.stem
                suffix = original_filepath.suffix
                filepath = output_path / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Save content
            try:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(result['content'])
                
                print(f"✅ Saved: {filepath.name}")
                print(f"📊 Size: {len(result['content'])} characters")
                saved_count += 1
                
            except Exception as e:
                print(f"❌ Failed to save: {e}")
                failed_count += 1
        else:
            print(f"❌ Parse failed: {result['error']}")
            failed_count += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 BATCH PROCESSING SUMMARY:")
    print(f"✅ Successfully saved: {saved_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total processed: {len(recipes)}")
    print(f"📁 Files saved in: {output_path.absolute()}")
    
    if saved_count > 0:
        print(f"\n💡 You can now find your parsed recipes in the output directory!")


async def demo():
    """Main demo function that processes recipes from CSV."""
    try:
        # Load recipes from CSV
        csv_path = "./data/recipe_list.csv"
        recipes = load_recipe_urls(csv_path)
        
        if not recipes:
            print("❌ No recipes found in CSV file.")
            return
        
        # Process and save recipes
        await save_parsed_recipes(recipes)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("� Make sure the CSV file exists at ./data/recipe_list.csv")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(demo())
