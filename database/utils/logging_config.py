"""
Logging Configuration for Database Module

This module provides centralized logging configuration for the database package.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> None:
    """
    Set up logging configuration for the database module.
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        include_timestamp: Whether to include timestamp in logs
    """
    if format_string is None:
        if include_timestamp:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            format_string = '%(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger for database module
    logger = logging.getLogger('database')
    logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f'database.{name}')


def set_debug_mode(enabled: bool = True) -> None:
    """
    Enable or disable debug mode for database logging.
    
    Args:
        enabled: Whether to enable debug mode
    """
    level = logging.DEBUG if enabled else logging.INFO
    
    # Update all database loggers
    root_logger = logging.getLogger('database')
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers:
        handler.setLevel(level)
