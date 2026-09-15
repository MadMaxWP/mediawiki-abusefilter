import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../../src"))

project = "mediawiki-abusefilter"
author = "Max <madmax.wp@proton.me>"
copyright = '2026, Max'
release = "0.1.3"
version = "0.1.3"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
	'sphinx.ext.autosectionlabel',
	'sphinx.ext.viewcode'
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"

html_context = {
    "display_github": True,
    "github_user": "MadMaxWP",
    "github_repo": "mediawiki-abusefilter",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}

master_doc = 'index'
