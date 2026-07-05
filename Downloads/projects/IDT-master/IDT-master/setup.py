#!/usr/bin/env python3
"""
Setup script for IDT GenAI Financial Statement Analyzer
Enhanced with Gemini AI and ChromaDB
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return
    
    print("🔧 Creating .env file...")
    env_content = """# Gemini API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional: Set model preferences
GEMINI_MODEL=models/gemini-1.5-flash-8b
EMBEDDING_MODEL=models/embedding-001
"""
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    print("⚠️  Please edit .env file and add your actual Gemini API key")

def create_directories():
    """Create necessary directories."""
    directories = ["financial_docs_chroma", "reports", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function."""
    print("🚀 Setting up IDT GenAI Financial Statement Analyzer")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Get your Gemini API key from: https://aistudio.google.com/app/apikey")
    print("2. Edit the .env file and replace 'your_actual_gemini_api_key_here' with your real API key")
    print("3. Run the application: python src/main.py")
    print("\n🎯 Your enhanced financial statement analyzer is ready!")

if __name__ == "__main__":
    main() 