# Configuration file for the Sphinx documentation builder.
#
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
              "sphinx.ext.viewcode"]               # Lien vers le code source]

templates_path = ['_templates']
exclude_patterns = []

# -- napoleon configuration -------------------------------------------------



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
