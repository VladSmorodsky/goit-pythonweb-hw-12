# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so Sphinx can find the modules
sys.path.insert(0, os.path.abspath('..'))

# Load environment variables for Sphinx documentation build
# This allows autodoc to import modules that read environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Contact REST'
copyright = '2025, Vlad'
author = 'Vlad'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

# Autodoc settings to handle import issues - mock only what's necessary
# Note: We don't mock fastapi/sqlalchemy/pydantic as they are installed and needed for autodoc to see decorators
autodoc_mock_imports = [
    'fastapi_mail',
    'pydantic_settings',
    'cloudinary',
    'cloudinary.uploader',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "nature"
html_static_path = ["_static"]
