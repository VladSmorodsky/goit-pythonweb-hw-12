"""
Pytest configuration file for shared fixtures and settings.
"""
import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)
