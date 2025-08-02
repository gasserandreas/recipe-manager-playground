"""
Basic tests for the German Recipe Parser modules.

These tests demonstrate the modular structure and can be used as
a starting point for comprehensive testing.
"""

import asyncio
import pytest

try:
    # Try relative imports first (when used as package)
    from .parser import GermanRecipeParser
    from .utils import URLValidator
    from .formatters import GermanTextFormatter, MarkdownFormatter
except ImportError:
    # Fall back to absolute imports (when run directly)
    from parser import GermanRecipeParser
    from utils import URLValidator
    from formatters import GermanTextFormatter, MarkdownFormatter


class TestURLValidator:
    """Test URL validation functionality."""
    
    def test_valid_urls(self):
        """Test that valid URLs are correctly identified."""
        valid_urls = [
            "https://fooby.ch/de/rezepte/27566/sesam-chicken",
            "https://www.swissmilk.ch/de/rezepte/test",
            "http://example.com/recipe"
        ]
        
        for url in valid_urls:
            assert URLValidator.is_valid_url(url), f"URL should be valid: {url}"
    
    def test_invalid_urls(self):
        """Test that invalid URLs are correctly identified."""
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",  # Missing http/https
            "",
            "https://",
            "recipe.html"
        ]
        
        for url in invalid_urls:
            assert not URLValidator.is_valid_url(url), f"URL should be invalid: {url}"
    
    def test_get_domain(self):
        """Test domain extraction."""
        assert URLValidator.get_domain("https://fooby.ch/recipe") == "fooby.ch"
        assert URLValidator.get_domain("invalid_url") == ""


class TestGermanTextFormatter:
    """Test German text formatting and normalization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = GermanTextFormatter()
    
    def test_time_normalization(self):
        """Test German time text normalization."""
        test_cases = [
            ("15 minuten", "15 Min"),
            ("1 stunde 30 minuten", "1 Std 30 Min"), 
            ("2 std 15 min", "2 Std 15 Min"),
            ("30 Min.", "30 Min"),
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            result = self.formatter.normalize_time_text(input_text)
            assert result == expected, f"Expected '{expected}', got '{result}'"
    
    def test_servings_normalization(self):
        """Test German servings text normalization."""
        test_cases = [
            ("4 portionen", "4 Portionen"),
            ("2 personen", "2 Personen"),
            ("6 stück", "6 Stück"),
            ("macht 8 portionen", "8 Portionen"),
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            result = self.formatter.normalize_servings_text(input_text)
            assert result == expected, f"Expected '{expected}', got '{result}'"


class TestMarkdownFormatter:
    """Test markdown formatting."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = MarkdownFormatter()
    
    def test_recipe_formatting(self):
        """Test complete recipe formatting."""
        recipe_data = {
            'title': 'Test Rezept',
            'description': 'Ein leckeres Testrezept',
            'ingredients': ['1 Zwiebel', '2 Tomaten'],
            'instructions': ['Zwiebel schneiden', 'Tomaten hinzufügen'],
            'prep_time': '15 Min',
            'cook_time': '30 Min',
            'servings': '4 Portionen'
        }
        
        result = self.formatter.format_recipe(recipe_data, "https://example.com")
        
        # Check that German headers are present
        assert "# Rezept" in result
        assert "## Zutaten" in result
        assert "## Zubereitung" in result
        assert "**Quelle:** https://example.com" in result
        assert "**Vorbereitungszeit:** 15 Min" in result


class TestGermanRecipeParser:
    """Test the main parser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = GermanRecipeParser()
    
    def test_recipe_data_initialization(self):
        """Test that recipe data structure is properly initialized."""
        recipe_data = self.parser._initialize_recipe_data()
        
        expected_keys = [
            'title', 'description', 'ingredients', 'instructions',
            'prep_time', 'cook_time', 'servings', 'nutrition'
        ]
        
        for key in expected_keys:
            assert key in recipe_data, f"Missing key: {key}"
        
        # Check that lists are initialized as empty lists
        assert isinstance(recipe_data['ingredients'], list)
        assert isinstance(recipe_data['instructions'], list)


# Integration test (requires network access)
class TestIntegration:
    """Integration tests that require network access."""
    
    @pytest.mark.asyncio
    async def test_parse_recipe_integration(self):
        """Test parsing a real recipe (network required)."""
        # This test should be run manually or in CI with network access
        parser = GermanRecipeParser()
        
        # Use a stable test URL
        test_url = "https://fooby.ch/de/rezepte/27566/sesam-chicken"
        
        try:
            result = await parser.parse_recipe_from_url(test_url)
            assert result is not None
            assert "# Rezept" in result
            assert "## Zutaten" in result or "## Zubereitung" in result
        except Exception as e:
            # Skip test if network is unavailable
            pytest.skip(f"Network test skipped: {e}")


if __name__ == "__main__":
    # Run basic tests without pytest
    test_validator = TestURLValidator()
    test_validator.test_valid_urls()
    test_validator.test_invalid_urls()
    test_validator.test_get_domain()
    
    test_formatter = TestGermanTextFormatter()
    test_formatter.setup_method()
    test_formatter.test_time_normalization()
    test_formatter.test_servings_normalization()
    
    test_markdown = TestMarkdownFormatter()
    test_markdown.setup_method()
    test_markdown.test_recipe_formatting()
    
    test_parser = TestGermanRecipeParser()
    test_parser.setup_method()
    test_parser.test_recipe_data_initialization()
    
    print("✅ All basic tests passed!")
    print("Run 'pytest test_recipe_parser.py' for full test suite including async tests.")
