# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = 'BlueObserver'
copyright = '2025, Ines, Chloe'
author = 'Ines'

# --- Racine du projet = dossier "BlueObserver" -----------------------------
ROOT = Path(__file__).resolve().parents[1]

# Ajout de la racine au PYTHONPATH
sys.path.insert(0, str(ROOT)) # pour pouvoir faire "import main", "import exemple"

# A

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx_rtd_theme",
              "sphinx.ext.autodoc",
              "sphinx.ext.githubpages"]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
