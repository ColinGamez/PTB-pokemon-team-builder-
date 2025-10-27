#!/usr/bin/env python3
"""
Pokemon Team Builder GUI Launcher
Run this script to start the Pokemon Team Builder application.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Initialize logging first
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point for the GUI application."""
    logger = logging.getLogger('ptb.launcher')
    
    try:
        logger.info("Starting Pokemon Team Builder v1.0...")
        logger.info("Loading GUI components...")
        
        # Import and run the main window
        from src.gui.main_window import MainWindow
        
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start GUI: {e}", exc_info=True)
        print(f"❌ Failed to start GUI: {e}")
        print("Please check the error logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
