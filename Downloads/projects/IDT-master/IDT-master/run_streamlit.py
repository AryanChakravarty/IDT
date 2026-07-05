#!/usr/bin/env python3
"""
Runner script for the Streamlit Financial Statement Analyzer
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit application."""
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found!")
        print("Please create a .env file with your GEMINI_API_KEY")
        print("Format: GEMINI_API_KEY=your_api_key_here")
        print()
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Error: Streamlit not installed!")
        print("Please install requirements: pip install -r requirements_streamlit.txt")
        sys.exit(1)
    
    # Run streamlit app
    print("Starting IDT GenAI Financial Statement Analyzer...")
    print("The app will open in your default web browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 