"""
Start Backend Server
Launches the Pokemon Team Builder backend server for handling
user registration, email verification, and API requests.
"""

import os
import sys
import subprocess
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path('.env')
    
    if env_file.exists():
        print("✓ Loading configuration from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True
    else:
        print("⚠ No .env file found. Using default configuration (demo mode).")
        print("  For production email sending, create .env file from .env.example")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['flask', 'flask-cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print(f"\nInstall with: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Start the backend server."""
    print("="*60)
    print("Pokemon Team Builder - Backend Server")
    print("="*60)
    print()
    
    # Load environment variables
    has_env = load_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Display configuration
    print("\nServer Configuration:")
    print(f"  SMTP Server: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
    print(f"  Sender Email: {os.getenv('SENDER_EMAIL', 'pokemonteambuilder@gmail.com')}")
    print(f"  Base URL: {os.getenv('BASE_URL', 'http://localhost:5000')}")
    
    if os.getenv('SENDER_PASSWORD'):
        print(f"  Email Mode: ✓ Production (SMTP configured)")
    else:
        print(f"  Email Mode: ⚠ Demo (emails saved to logs/email_verifications.txt)")
    
    print()
    print("="*60)
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*60)
    print()
    
    # Start the server
    try:
        subprocess.run([sys.executable, 'backend_server.py'], check=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
