"""
Simplified and improved web application with better multiplayer integration.
"""


# Ensure src directory is in Python path
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import json
import os
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import secrets
import uuid

# Configure paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize SocketIO conditionally
socketio = None
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    logger.info("SocketIO initialized successfully")
except ImportError as e:
    logger.warning(f"SocketIO not available: {e}. Multiplayer features will be limited.")

# Try to import Pokemon modules
try:
    from teambuilder.team import PokemonTeam
    from teambuilder.analyzer import TeamAnalyzer
    from features.breeding_calculator import BreedingCalculator
    from features.tournament_system import TournamentManager, TournamentFormat
    logger.info("Pokemon modules imported successfully")
except ImportError as e:
    logger.warning(f"Pokemon modules not available: {e}. Using mock data.")
    # Create mock classes
    class PokemonTeam:
        def __init__(self, name="MockTeam"):
            self.name = name
            self.pokemon = []
    class TeamAnalyzer:
        def analyze_team(self, team):
            return {"coverage": "Good", "weaknesses": ["None"]}
    class BreedingCalculator:
        def calculate_breeding_path(self, pokemon):
            return {"steps": ["Mock breeding step"]}
    class TournamentManager:
        def create_tournament(self, name, format):
            return {"id": "mock_tournament", "name": name}
    class TournamentFormat:
        SINGLE_ELIMINATION = "single_elimination"

# Global managers
team_analyzer = TeamAnalyzer()
breeding_calculator = BreedingCalculator()
tournament_manager = TournamentManager()

# In-memory storage (in production, use a proper database)
users_db = {}
teams_db = {}
battles_db = {}

class WebUser:
    """Web application user."""
    
    def __init__(self, username: str):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = ""
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.teams = []
        self.rating = 1200
        self.wins = 0
        self.losses = 0
        self.battles = 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat(),
            'rating': self.rating,
            'wins': self.wins,
            'losses': self.losses,
            'battles': self.battles
        }

def get_current_user() -> Optional[WebUser]:
    """Get the current logged-in user."""
    if 'user_id' in session:
        return users_db.get(session['user_id'])
    return None

def login_required(f):
    """Decorator to require user login."""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes

@app.route('/')
def index():
    """Main page."""
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Username is required', 'error')
            return render_template('login.html')
        
        # Find or create user
        user = None
        for u in users_db.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            user = WebUser(username)
            users_db[user.id] = user
            logger.info(f"Created new user: {username}")
        
        user.last_active = datetime.now()
        session['user_id'] = user.id
        session['username'] = user.username
        session['rating'] = user.rating
        
        flash(f'Welcome, {username}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    user = get_current_user()
    user_teams = [teams_db[team_id] for team_id in user.teams if team_id in teams_db]
    
    return render_template('dashboard.html', 
                         user=user, 
                         teams=user_teams,
                         recent_activity=[])

# Multiplayer routes (simplified without complex integration)
@app.route('/multiplayer')
@login_required
def multiplayer_lobby():
    """Multiplayer lobby."""
    user = get_current_user()
    
    # Mock battle modes and formats if modules not available
    battle_modes = ['singles', 'doubles']
    battle_formats = ['casual', 'ranked']
    
    return render_template('multiplayer/lobby.html',
                         user=user.to_dict(),
                         battle_modes=battle_modes,
                         battle_formats=battle_formats)

@app.route('/multiplayer/battle/<battle_id>')
@login_required
def battle_room(battle_id):
    """Battle room."""
    user = get_current_user()
    
    # Mock battle state
    battle_state = {
        'battle_id': battle_id,
        'phase': 'team_preview',
        'turn_number': 1,
        'players': {
            user.id: {
                'username': user.username,
                'status': 'connected',
                'ready': False
            }
        },
        'timer': {
            'enabled': True,
            'remaining': 60
        }
    }
    
    return render_template('multiplayer/battle.html',
                         battle_id=battle_id,
                         battle_state=battle_state,
                         user=user.to_dict())

# API Routes
@app.route('/api/battles')
@login_required
def api_get_battles():
    """Get list of active battles."""
    # Mock battle list
    battles = [
        {
            'battle_id': 'battle001',
            'mode': 'singles',
            'format': 'casual',
            'players': 2,
            'spectators': 0,
            'phase': 'battling',
            'created_at': datetime.now().isoformat()
        }
    ]
    return jsonify(battles)

@app.route('/api/multiplayer/battles')
@login_required
def api_multiplayer_battles():
    """Get multiplayer battles."""
    return jsonify([])

@app.route('/api/multiplayer/create_battle', methods=['POST'])
@login_required
def api_create_battle():
    """Create a new battle."""
    data = request.json or {}
    battle_id = f"battle_{uuid.uuid4().hex[:8]}"
    
    # Store battle info
    battles_db[battle_id] = {
        'id': battle_id,
        'creator': session['user_id'],
        'mode': data.get('mode', 'singles'),
        'format': data.get('format', 'casual'),
        'settings': data.get('settings', {}),
        'created_at': datetime.now()
    }
    
    logger.info(f"Created battle {battle_id} by user {session['username']}")
    return jsonify({'battle_id': battle_id})

@app.route('/api/multiplayer/join_battle', methods=['POST'])
@login_required
def api_join_battle():
    """Join an existing battle."""
    data = request.json or {}
    battle_id = data.get('battle_id')
    
    if battle_id in battles_db:
        logger.info(f"User {session['username']} joined battle {battle_id}")
        return jsonify({'success': True})
    
    return jsonify({'error': 'Battle not found'}), 404

@app.route('/api/multiplayer/battle/<battle_id>')
@login_required
def api_get_battle_state(battle_id):
    """Get battle state."""
    if battle_id in battles_db:
        battle = battles_db[battle_id]
        return jsonify({
            'battle_id': battle_id,
            'phase': 'move_selection',
            'turn_number': 1,
            'players': {
                session['user_id']: {
                    'username': session['username'],
                    'status': 'connected',
                    'ready': False
                }
            }
        })
    
    return jsonify({'error': 'Battle not found'}), 404

@app.route('/api/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'multiplayer': socketio is not None,
            'authentication': True,
            'battles': True
        }
    })

# Socket.IO events (if available)
if socketio:
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        if 'user_id' in session:
            logger.info(f"User {session['username']} connected via WebSocket")
            emit('connected', {'status': 'success'})
        else:
            emit('error', {'message': 'Not authenticated'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        if 'username' in session:
            logger.info(f"User {session['username']} disconnected")
    
    @socketio.on('join_battle')
    def handle_join_battle(data):
        """Handle joining a battle room."""
        battle_id = data.get('battle_id')
        if battle_id:
            join_room(f"battle_{battle_id}")
            emit('joined_battle', {'battle_id': battle_id})
            logger.info(f"User {session.get('username', 'Unknown')} joined battle room {battle_id}")
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle chat message in battle."""
        battle_id = data.get('battle_id')
        message = data.get('message', '').strip()
        
        if battle_id and message and 'username' in session:
            # Broadcast to battle room
            socketio.emit('chat_message', {
                'username': session['username'],
                'message': message,
                'timestamp': datetime.now().isoformat()
            }, room=f"battle_{battle_id}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template('base.html'), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('templates/multiplayer', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Run the application
    logger.info("Starting Pokemon Team Builder Web Application")
    
    if socketio:
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    else:
        app.run(debug=False, host='0.0.0.0', port=5000)