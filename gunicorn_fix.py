#!/usr/bin/env python3
"""
Gunicorn replacement that uses the working server
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def run():
    """Entry point that replaces gunicorn.app.wsgiapp.run"""
    print("Using gunicorn replacement...")
    
    # Import and run our working server
    try:
        from working_extractor import main
        main()
    except Exception as e:
        from main import run_server
        run_server()

if __name__ == '__main__':
    run()