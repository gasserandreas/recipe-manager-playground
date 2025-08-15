"""
Markdown Recipe Parser

This module provides functionality to parse markdown recipe files
with frontmatter and extract structured recipe data.
"""

import re
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging

from ..models import RecipeDocument

logger = logging.getLogger(__name__)


class MarkdownRecipeParser:
    """Parser for markdown recipe files with frontmatter."""
    
    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from markdown content.
        
        Args:
            content: Raw markdown content with frontmatter
            
        Returns:
            Tuple of (frontmatter_dict, markdown_body)
        """
        frontmatter = {}
        body = content
        
        # Check for frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1].strip()
                body = parts[2].strip()
                
                # Simple YAML parsing for common cases
                for line in frontmatter_text.split('\n'):
                    line = line.strip()
                    if ':' in line and not line.startswith('#'):
                        key, value = line.split(':', 1)
                        key = key.strip().strip('"\'')
                        value = value.strip().strip('"\'')
                        frontmatter[key] = value
        
        return frontmatter, body
    
    @staticmethod
    def extract_sections(markdown_content: str) -> Dict[str, Any]:
        """
        Extract structured sections from markdown content.
        
        Args:
            markdown_content: Markdown text content
            
        Returns:
            Dict with extracted sections (ingredients, instructions, etc.)
        """
        sections = {
            'ingredients': '',
            'instructions': '',
            'tags': []
        }
        
        # Split content by headers
        lines = markdown_content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for section headers
            if line.startswith('##') or line.startswith('###'):
                # Save previous section
                if current_section and current_content:
                    content = '\n'.join(current_content).strip()
                    if current_section in sections:
                        sections[current_section] = content
                
                # Start new section
                header = line.strip('#').strip().lower()
                if 'zutat' in header or 'ingredient' in header:
                    current_section = 'ingredients'
                elif 'zubereitung' in header or 'anleitung' in header or 'instruction' in header:
                    current_section = 'instructions'
                else:
                    current_section = None
                current_content = []
            
            # Extract tags from special markdown syntax
            elif '`' in line:
                tags = re.findall(r'`([^`]+)`', line)
                sections['tags'].extend(tags)
            
            # Add content to current section
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            content = '\n'.join(current_content).strip()
            if current_section in sections:
                sections[current_section] = content
        
        return sections
    
    def parse_recipe_file(self, file_path: str) -> Optional[RecipeDocument]:
        """
        Parse a single markdown recipe file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            RecipeDocument or None if parsing failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and body
            frontmatter, body = self.parse_frontmatter(content)
            
            # Extract structured sections
            sections = self.extract_sections(body)
            
            # Create recipe document
            recipe = RecipeDocument(
                title=frontmatter.get('title', Path(file_path).stem),
                source=frontmatter.get('source', ''),
                cuisine=frontmatter.get('cuisine', ''),
                prep_time=frontmatter.get('prep_time', ''),
                cook_time=frontmatter.get('cook_time', ''),
                servings=frontmatter.get('servings', ''),
                ingredients=sections.get('ingredients', ''),
                instructions=sections.get('instructions', ''),
                tags=sections.get('tags', []),
                content=content
            )
            
            logger.debug(f"Parsed recipe: {recipe.title}")
            return recipe
            
        except Exception as e:
            logger.error(f"Failed to parse recipe file {file_path}: {e}")
            return None
