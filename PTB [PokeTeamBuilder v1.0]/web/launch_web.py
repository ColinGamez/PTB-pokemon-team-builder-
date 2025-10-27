"""
Launch script for Pokemon Team Builder Web Application.
Handles dependency checking and graceful startup.
"""

import sys
import os
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'flask',
        'flask-cors'
    ]
    
    optional_packages = [
        'flask-socketio',
        'eventlet'
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_optional.append(package)
    
    return missing_required, missing_optional

def install_dependencies():
    """Install missing dependencies."""
    logger.info("Installing required dependencies...")
    
    try:
        # Install basic requirements
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            'flask>=2.3.0',
            'flask-cors>=4.0.0'
        ])
        
        # Try to install optional multiplayer dependencies
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                'flask-socketio>=5.3.0',
                'eventlet>=0.33.0',
                'python-socketio>=5.8.0'
            ])
            logger.info("Multiplayer dependencies installed successfully")
        except subprocess.CalledProcessError:
            logger.warning("Failed to install multiplayer dependencies. Multiplayer features will be limited.")
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def main():
    """Main launcher function."""
    logger.info("Starting Pokemon Team Builder Web Application...")
    
    # Check dependencies
    missing_required, missing_optional = check_dependencies()
    
    if missing_required:
        logger.warning(f"Missing required packages: {missing_required}")
        if input("Install missing dependencies? (y/n): ").lower() == 'y':
            if not install_dependencies():
                logger.error("Failed to install dependencies. Exiting.")
                return 1
        else:
            logger.error("Required dependencies not available. Exiting.")
            return 1
    
    if missing_optional:
        logger.info(f"Missing optional packages: {missing_optional}")
        logger.info("Multiplayer features may be limited.")
    
    # Set up paths
    web_dir = Path(__file__).parent
    project_root = web_dir.parent
    src_dir = project_root / 'src'
    
    # Add paths to Python path
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(src_dir))
    
    # Create necessary directories
    (web_dir / 'templates').mkdir(exist_ok=True)
    (web_dir / 'templates' / 'multiplayer').mkdir(exist_ok=True)
    (web_dir / 'static').mkdir(exist_ok=True)
    (web_dir / 'static' / 'css').mkdir(exist_ok=True)
    (web_dir / 'static' / 'js').mkdir(exist_ok=True)
    
    # Try to import and run the simplified app first
    try:
        logger.info("Loading simplified web application...")
        from app_simplified import app, socketio
        
        logger.info("Starting web server on http://localhost:5000")
        logger.info("Press Ctrl+C to stop the server")
        
        if socketio:
            logger.info("Running with SocketIO support (full multiplayer)")
            socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        else:
            logger.info("Running without SocketIO (limited multiplayer)")
            app.run(debug=False, host='0.0.0.0', port=5000)
            
    except ImportError as e:
        logger.warning(f"Failed to load simplified app: {e}")
        
        # Fallback to basic Flask app
        try:
            logger.info("Loading basic fallback application...")
            from flask import Flask, jsonify, render_template_string
            
            app = Flask(__name__)
            app.config['SECRET_KEY'] = 'fallback-key'
            
            @app.route('/')
            def index():
                return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Pokemon Team Builder</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="row justify-content-center">
                            <div class="col-md-8">
                                <div class="card">
                                    <div class="card-header bg-primary text-white">
                                        <h1 class="mb-0">🏆 Pokemon Team Builder</h1>
                                    </div>
                                    <div class="card-body">
                                        <div class="alert alert-warning">
                                            <h4>⚠️ Limited Mode</h4>
                                            <p>The web application is running in limited mode due to missing dependencies.</p>
                                            <p>To enable full features, please install the required packages:</p>
                                            <pre><code>pip install -r requirements.txt</code></pre>
                                        </div>
                                        
                                        <h3>Available Features:</h3>
                                        <ul class="list-group list-group-flush">
                                            <li class="list-group-item">
                                                <strong>Desktop Application:</strong> Run <code>python run_gui.py</code>
                                            </li>
                                            <li class="list-group-item">
                                                <strong>Team Building:</strong> Advanced Pokemon team analysis
                                            </li>
                                            <li class="list-group-item">
                                                <strong>Breeding Calculator:</strong> IV inheritance optimization
                                            </li>
                                            <li class="list-group-item">
                                                <strong>Tournament System:</strong> Bracket management
                                            </li>
                                        </ul>
                                        
                                        <div class="mt-4">
                                            <a href="/api/status" class="btn btn-info">API Status</a>
                                            <a href="https://github.com/pokemon-team-builder" class="btn btn-secondary">Documentation</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                </body>
                </html>
                ''')
            
            @app.route('/api/status')
            def api_status():
                return jsonify({
                    'status': 'running',
                    'mode': 'fallback',
                    'features': {
                        'web_interface': True,
                        'multiplayer': False,
                        'real_time': False
                    },
                    'message': 'Install requirements.txt for full functionality'
                })
            
            logger.info("Starting fallback web server on http://localhost:5000")
            app.run(debug=False, host='0.0.0.0', port=5000)
            
        except Exception as e:
            logger.error(f"Failed to start fallback application: {e}")
            return 1
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())