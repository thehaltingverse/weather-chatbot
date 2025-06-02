#!/bin/bash

# Set your GitHub repo URL here
GITHUB_REPO_URL="git@github.com:thehaltingverse/weatherChatbot.git"

# Initialize git if not already
if [ ! -d .git ]; then
  echo "🧱 Initializing Git repository..."
  git init
fi

# Add remote if not already
if ! git remote | grep origin > /dev/null; then
  echo "🔗 Adding remote origin..."
  git remote add origin "$GITHUB_REPO_URL"
fi

# Create .gitignore
echo "📄 Creating .gitignore..."
cat > .gitignore <<EOL
.env
.venv/
models/*.gguf
__pycache__/
*.pyc
.DS_Store
EOL

# Add and commit
echo "📦 Staging files..."
git add .

echo "📝 Committing changes..."
git commit -m "Initial project upload"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main
