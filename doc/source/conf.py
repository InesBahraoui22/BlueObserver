# Configuration file for the Sphinx documentation builder.
#

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BlueObserver'
copyright = '2025, Ines et Chloé'
author = 'Ines et Chloé'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx_rtd_theme",
              "sphinx.ext.autodoc",      # Documentation automatique depuis les docstrings
              "sphinx.ext.githubpages",  # Pour GitHub Pages
              "sphinx.ext.napoleon",     # Support des docstrings Google/NumPy style
              "sphinxcontrib.mermaid",     
              "sphinx.ext.viewcode"]     # Lien vers le code source]

templates_path = ['_templates']
exclude_patterns = []

# -- napoleon configuration  -------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_logo = '_static/logo_final.jpg'  # Votre logo
html_favicon = '_static/logo_final.jpg'

# -- Options autodoc --------------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autoclass_content = 'both'  # Combine class et __init__ docstrings