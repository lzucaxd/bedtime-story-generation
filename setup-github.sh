#!/bin/bash

echo "🌟 Magical Story Generator - GitHub Setup"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Run 'git init' first."
    exit 1
fi

echo "📋 Repository Setup Instructions:"
echo ""
echo "1. 🌐 Go to https://github.com/new"
echo "2. 📝 Repository name: magical-story-generator"
echo "3. 📄 Description: 🌟 AI-powered bedtime story generator with LLM judge and advanced features"
echo "4. 🌍 Make it Public"
echo "5. ❌ Don't initialize with README (we already have one)"
echo "6. ✅ Click 'Create repository'"
echo ""

read -p "📝 Enter your GitHub username: " username

if [ -z "$username" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

echo ""
echo "🚀 Setting up remote and pushing to GitHub..."

# Add remote origin
git remote add origin https://github.com/$username/magical-story-generator.git

# Push to GitHub
git push -u origin main

echo ""
echo "✅ Repository pushed to GitHub!"
echo ""
echo "📋 Final step - Enable GitHub Pages:"
echo "1. Go to https://github.com/$username/magical-story-generator/settings/pages"
echo "2. Source: Deploy from a branch"
echo "3. Branch: main"
echo "4. Folder: / (root)"
echo "5. Click Save"
echo ""
echo "🎉 Your site will be available at:"
echo "https://$username.github.io/magical-story-generator"
echo ""
echo "🌟 Magical Story Generator is ready to go live!"
