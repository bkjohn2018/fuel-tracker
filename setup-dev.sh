#!/bin/bash

# Fuel Tracker Development Environment Setup
# Run this script to set up the development environment

echo "🔧 Setting up Fuel Tracker development environment..."

# Install development dependencies
echo "Installing development dependencies..."
pip install -r requirements.txt
pip install pre-commit detect-secrets ruff

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Initialize secrets baseline
echo "Initializing secrets baseline..."
if [ -f ".secrets.baseline" ]; then
    echo "  .secrets.baseline already exists, skipping..."
else
    detect-secrets scan > .secrets.baseline
    echo "  Created .secrets.baseline"
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your EIA_API_KEY in .env file"
echo "2. Run 'make help' to see available commands"
echo "3. Pre-commit hooks are now active on git commit"
echo ""
echo "Note: .secrets.baseline has been created and added to .gitignore"
