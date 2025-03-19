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
    "sphinx.ext.todo",           # Support for todo items
    "sphinx.ext.viewcode",       # Add links to highlighted source code
    "sphinx.ext.intersphinx",    # Link to other projects’ documentation
    # custom extentions
    "sphinx_copybutton",         # add a little “copy” button to the right of your code blocks
    "sphinx_design",             # for designing beautiful, screen-size responsive web-components
    "sphinx_favicon",
    "sphinx_togglebutton",
    # not used
    # "sphinx.ext.napoleon",     # Support for NumPy and Google style docstrings
    # "sphinx.ext.autodoc",      # Include documentation from docstrings  # check sphinx.ext.apidoc
    # "sphinx.ext.autosummary",  # Generate autodoc summaries
    # "sphinx.ext.graphviz",     # Add Graphviz graphs
]

exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_logo = "https://repository-images.githubusercontent.com/766241795/85494614-5974-4b26-bfec-03b8e393c7f0"

templates_path = ["_templates"]
html_static_path = ["_static"]
html_js_files = ["_js/custom-icon.js"]

html_theme_options = {
    "use_edit_page_button": True,

    "secondary_sidebar_items": {
      "**": ["page-toc", "sourcelink"],
      "index": ["globaltoc"],
    },

    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/pyctrl/izulu",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://www.pypi.org",
            "icon": "fa-custom fa-pypi",
        },
        {
            "name": "pyctrl",
            "url": "https://github.com/pyctrl",
            "icon": "https://github.com/pyctrl/pyctrl/blob/main/logo/pyctrl/gray-460x460.png?raw=true",
            "type": "url",
        },
    ],

}

html_context = {
    "github_url": "https://github.com",
    "github_user": "pyctrl",
    "github_repo": "izulu",
    "github_version": "main",
    "doc_path": "docs/source/",
}

favicons = [
   {
      "sizes": "16x16",
      "href": "https://github.com/pyctrl/pyctrl/blob/main/logo/izulu/izulu_logo_512.png?raw=true",
   },
   {
      "sizes": "32x32",
      "href": "https://github.com/pyctrl/pyctrl/blob/main/logo/izulu/izulu_logo_512.png?raw=true",
   },
]
