# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'Cryptnox Hardware Wallet'
copyright = '2026, Cryptnox SA'
author = 'Cryptnox'
release = '1.6.1'

# -- General configuration ---------------------------------------------------

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# -- SEO meta tags -----------------------------------------------------------

html_baseurl = 'https://docs.cryptnox.com/hardware-wallet/'

html_meta = {
    'description': 'Cryptnox Hardware Wallet v1.6.1 — APDU command reference, secure channel protocol, key derivation, signing, and authentication for JavaCard-based crypto wallet cards.',
    'keywords': 'Cryptnox, hardware wallet, smartcard, JavaCard, APDU, secure channel, BIP32, SLIP10, ECDSA, Schnorr, key derivation, cryptocurrency, NFC, cold storage',
    'author': 'Cryptnox',
    'robots': 'index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large',
}

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

# Logo configuration
html_logo = "_static/cryptnox-logo.png"
html_favicon = "_static/favicon.png"

# Custom CSS and JS
html_css_files = [
    'custom.css',
]

html_js_files = [
    'custom.js',
]

# Theme options
html_theme_options = {
    'analytics_id': 'GT-PJ7HDFB',
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#101f2e',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Sitemap / SEO
html_show_sourcelink = False
html_copy_source = False
