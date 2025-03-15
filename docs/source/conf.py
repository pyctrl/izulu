# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import datetime as dtm
from importlib import metadata

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "izulu"
author = "Dima Burmistrov"
copyright = "2023-%Y, " + author
# -- setuptools_scm ----------------------------------------------------------
version = metadata.version(project)
release = ".".join(version.split(".")[:3])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_logo = "https://repository-images.githubusercontent.com/766241795/85494614-5974-4b26-bfec-03b8e393c7f0"

html_theme_options = {
    "secondary_sidebar_items": {
      "**": ["page-toc", "sourcelink"],
      "index": ["globaltoc"],
    },
    "globaltoc_depth": "3",
    "globaltoc_includehidden": "true",
}
