#!/usr/bin/env python3
"""
Simple launcher for Pokemon Team Builder.
This script sets up the module path correctly and launches the application.
"""

import sys
import os
import logging

def main():
    """Launch the Pokemon Team Builder application."""
    try:
        # Setup path
        project_root = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(project_root, 'src')
        
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Configure basic logging to avoid Unicode issues
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(project_root, 'logs', 'launch.log'), encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger('ptb.launch')
        logger.info("Starting Pokemon Team Builder...")
        
        # Import and run the main GUI
        import tkinter as tk
        from gui.main_window import MainWindow
        
        # Create and run the application
        app = MainWindow()
        logger.info("GUI initialized successfully")
        app.run()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    
    except Exception as e:
        print(f"Failed to start Pokemon Team Builder: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())