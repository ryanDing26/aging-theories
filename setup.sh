#!/bin/bash
# Setup script for Aging Research Agent

echo "=========================================="
echo "Aging Research Agent - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Create directories
echo ""
echo "Creating directories..."
mkdir -p output
mkdir -p cache
echo "✓ Created output/ and cache/ directories"

# Setup .env file
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo "   Get your API key from: https://console.anthropic.com/"
else
    echo "✓ .env file already exists"
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x run_agent.py
chmod +x setup.sh
echo "✓ Scripts are executable"

# Final instructions
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. (Optional) Add your PUBMED_EMAIL to .env"
echo "  3. Run the agent:"
echo ""
echo "     # Quick test"
echo "     python run_agent.py --target-papers 100 --max-iterations 3"
echo ""
echo "     # Full run"
echo "     python run_agent.py --target-papers 1000"
echo ""
echo "=========================================="