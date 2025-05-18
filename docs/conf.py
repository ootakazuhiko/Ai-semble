import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'Ai-semble'
copyright = '2024, AI-semble Team'
author = 'AI-semble Team'
release = '0.1.0'
language = 'ja'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme' 