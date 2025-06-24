#!/bin/bash
# Git setup commands for rd_spiral

echo "Setting up Git repository..."

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: rd_spiral - reaction-diffusion solver

- Pseudo-spectral method implementation
- Stable and turbulent spiral examples
- Clean GitHub-based distribution"

# Create tag for version
git tag -a v0.1.0 -m "Version 0.1.0 - Initial release"

echo ""
echo "✅ Local git setup complete!"
echo ""
echo "Now:"
echo "1. Go to https://github.com/new"
echo "2. Create new repository named: rd_spiral"
echo "3. Make it PUBLIC"
echo "4. DON'T initialize with README"
echo "5. Run these commands:"
echo ""
echo "git remote add origin https://github.com/sandyherho/rd_spiral.git"
echo "git branch -M main"
echo "git push -u origin main"
echo "git push origin v0.1.0"
echo ""
echo "Then people can install with:"
echo "pip install git+https://github.com/sandyherho/rd_spiral.git"
