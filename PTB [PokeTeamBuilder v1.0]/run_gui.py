#!/usr/bin/env python3
"""
Pokemon Team Builder GUI Launcher
Run this script to start the Pokemon Team Builder application.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Initialize logging first
from utils.logging_config import initialize_application_logging
logger_manager = initialize_application_logging("INFO")

def main():
    """Main entry point for the GUI application."""
    import logging
    logger = logging.getLogger('ptb.launcher')
    
    try:
        logger.info("Starting Pokemon Team Builder v1.0...")
        logger.info("Loading GUI components...")
        
        # Initialize performance optimizations
        from utils.performance import optimize_startup
        optimize_startup()
        
        # Import and run the main window
        from gui.main_window import main as run_gui
        run_gui()
        
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
