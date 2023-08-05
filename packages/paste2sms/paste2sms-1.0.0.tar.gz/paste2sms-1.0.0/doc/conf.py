# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Mock -------------------------------------------------------------------

from unittest.mock import Mock as MagicMock

# Mocking libraries not needed to build the documentation
# See:
# http://read-the-docs.readthedocs.io/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules


class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return Mock()


MOCK_MODULES = ["notify2"]
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)


# -- Project information -----------------------------------------------------

project = "paste2sms"
copyright = "2020, Louis Paternault"
author = "Louis Paternault"

# The full version, including alpha/beta/rc tags
release = "1.0.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autosummary",
    "sphinxarg.ext",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

master_doc = "index"

# -- Autosummary -------------------------------------------------------------

autosummary_generate = True

# -- Options for HTML output -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = "../desktop/paste2sms.svg"
html_favicon = "../desktop/paste2sms.ico"

# -- Options for LaTeX output -------------------------------------------------

latex_logo = "../logo.png"
