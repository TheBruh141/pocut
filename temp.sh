
#!/bin/bash

echo "Setting up Sphinx documentation for project..."

# Check for Sphinx installation
if ! command -v sphinx-quickstart &> /dev/null; then
    echo "Sphinx is not installed. Installing Sphinx..."
    pip install sphinx sphinx-rtd-theme
fi

# Run Sphinx quickstart
sphinx-quickstart docs --quiet \
    --project "Pocut" \
    --author "Your Name" \
    --release "0.1" \
    --language "en" \
    --ext-autodoc \
    --ext-viewcode

# Update conf.py for autodoc and theme
CONF_FILE="docs/conf.py"

echo "Updating Sphinx configuration..."
cat <<EOL >> $CONF_FILE

# Add Sphinx extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

# Theme configuration
html_theme = 'sphinx_rtd_theme'

# Path setup for autodoc
import os
import sys
sys.path.insert(0, os.path.abspath('../$PROJECT_NAME'))
EOL

# Generate API documentation
sphinx-apidoc -o docs/api $PROJECT_NAME

echo "Sphinx setup complete. You can now build your documentation using 'make html' inside the docs folder."

