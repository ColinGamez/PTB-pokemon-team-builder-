"""
Enhanced web integration for Online Multiplayer Battle System.
Extends the Flask web application with real-time multiplayer capabilities.
"""


# Ensure src directory is in Python path
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import request, jsonify, render_template, session, redirect, url_for

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
    import eventlet
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    raise

try:
    from features.online_multiplayer import (
        OnlineBattleManager, BattlePlayer, BattleMode, BattleFormat,
        PlayerStatus, BattlePhase, BattleMessage
    )
    from teambuilder.team import PokemonTeam
except ImportError as e:
    logging.error(f"Failed to import Pokemon modules: {e}")
    # Create dummy classes for development
    class BattleMode:
        SINGLES = "singles"
        DOUBLES = "doubles"
    class BattleFormat:
        CASUAL = "casual"
        RANKED = "ranked"

logger = logging.getLogger(__name__)

class WebMultiplayerIntegration:
    """Web integration for multiplayer battle system."""
    
    def __init__(self, app, socketio: SocketIO):
        self.app = app
        self.socketio = socketio
        self.battle_manager = OnlineBattleManager()
        self.connected_users: Dict[str, Dict[str, Any]] = {}  # session_id -> user_info
        
        # Register routes and socket events
        self.register_routes()
        self.register_socket_events()
        
        logger.info("Web multiplayer integration initialized")
    
    def register_routes(self):
        """Register Flask routes for multiplayer."""
        
        @self.app.route('/multiplayer')
        def multiplayer_lobby():
            """Main multiplayer lobby page."""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            return render_template('multiplayer/lobby.html', 
                                 user=session,
                                 battle_modes=[mode.value for mode in BattleMode],
                                 battle_formats=[fmt.value for fmt in BattleFormat])
        
        @self.app.route('/multiplayer/battle/<battle_id>')
        def battle_room(battle_id):
            """Battle room page."""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Check if battle exists
            battle_state = self.battle_manager.get_battle_state(battle_id)
            if not battle_state:
                return redirect(url_for('multiplayer_lobby'))
            
            return render_template('multiplayer/battle.html',
                                 battle_id=battle_id,
                                 battle_state=battle_state,
                                 user=session)
        
        @self.app.route('/api/multiplayer/battles')
        def get_battles():
            """Get list of active battles."""
            battles = self.battle_manager.get_battle_list()
            return jsonify(battles)
        
        @self.app.route('/api/multiplayer/battle/<battle_id>')
        def get_battle_state(battle_id):
            """Get current battle state."""
            battle_state = self.battle_manager.get_battle_state(battle_id)
            if battle_state:
                return jsonify(battle_state)
            return jsonify({'error': 'Battle not found'}), 404
        
        @self.app.route('/api/multiplayer/create_battle', methods=['POST'])
        def create_battle():
            """Create a new private battle."""
            if 'user_id' not in session:
                return jsonify({'error': 'Not logged in'}), 401
            
            data = request.json
            mode = BattleMode(data.get('mode', 'singles'))
            format = BattleFormat(data.get('format', 'casual'))
            settings = data.get('settings', {})
            
            # Create player
            player = BattlePlayer(
                id=session['user_id'],
                username=session['username'],
                rating=session.get('rating', 1200),
                team=None  # Would load from session/database
            )
            
            # Create battle
            battle_id = self.battle_manager.create_private_battle(player, mode, format, settings)
            
            return jsonify({'battle_id': battle_id})
        
        @self.app.route('/api/multiplayer/join_battle', methods=['POST'])
        def join_battle():
            """Join an existing battle."""
            if 'user_id' not in session:
                return jsonify({'error': 'Not logged in'}), 401
            
            data = request.json
            battle_id = data.get('battle_id')
            
            if not battle_id:
                return jsonify({'error': 'Battle ID required'}), 400
            
            # Create player
            player = BattlePlayer(
                id=session['user_id'],
                username=session['username'],
                rating=session.get('rating', 1200),
                team=None  # Would load from session/database
            )
            
            # Join battle
            if self.battle_manager.join_battle(battle_id, player):
                return jsonify({'success': True})
            
            return jsonify({'error': 'Failed to join battle'}), 400
        
        @self.app.route('/api/multiplayer/submit_moves', methods=['POST'])
        def submit_moves():
            """Submit moves for current turn."""
            if 'user_id' not in session:
                return jsonify({'error': 'Not logged in'}), 401
            
            data = request.json
            battle_id = data.get('battle_id')
            moves = data.get('moves', [])
            
            if not battle_id or not moves:
                return jsonify({'error': 'Battle ID and moves required'}), 400
            
            # Submit moves
            if self.battle_manager.submit_moves(battle_id, session['user_id'], moves):
                return jsonify({'success': True})
            
            return jsonify({'error': 'Failed to submit moves'}), 400
        
        @self.app.route('/api/multiplayer/queue', methods=['POST'])
        def queue_for_match():
            """Queue for matchmaking."""
            if 'user_id' not in session:
                return jsonify({'error': 'Not logged in'}), 401
            
            data = request.json
            mode = BattleMode(data.get('mode', 'singles'))
            format = BattleFormat(data.get('format', 'casual'))
            
            # Create player
            player = BattlePlayer(
                id=session['user_id'],
                username=session['username'],
                rating=session.get('rating', 1200),
                team=None  # Would load from session/database
            )
            
            # Queue for battle
            if self.battle_manager.queue_for_battle(player, mode, format):
                return jsonify({'success': True})
            
            return jsonify({'error': 'Failed to join queue'}), 400
        
        @self.app.route('/api/multiplayer/cancel_queue', methods=['POST'])
        def cancel_queue():
            """Cancel matchmaking queue."""
            if 'user_id' not in session:
                return jsonify({'error': 'Not logged in'}), 401
            
            if self.battle_manager.cancel_queue(session['user_id']):
                return jsonify({'success': True})
            
            return jsonify({'error': 'Failed to cancel queue'}), 400
    
    def register_socket_events(self):
        """Register Socket.IO events for real-time communication."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            if 'user_id' in session:
                user_id = session['user_id']
                
                # Store connection info
                self.connected_users[request.sid] = {
                    'user_id': user_id,
                    'username': session['username'],
                    'connected_at': datetime.now()
                }
                
                # Register with battle manager
                self.battle_manager.register_connection(user_id, request.sid)
                
                logger.info(f"User {session['username']} connected via WebSocket")
                emit('connected', {'status': 'success'})
            else:
                emit('error', {'message': 'Not authenticated'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            if request.sid in self.connected_users:
                user_info = self.connected_users[request.sid]
                user_id = user_info['user_id']
                
                # Handle disconnection in battle manager
                self.battle_manager.handle_disconnect(request.sid)
                
                # Clean up
                del self.connected_users[request.sid]
                
                logger.info(f"User {user_info['username']} disconnected")
        
        @self.socketio.on('join_battle')
        def handle_join_battle(data):
            """Handle joining a battle room."""
            battle_id = data.get('battle_id')
            if battle_id:
                join_room(f"battle_{battle_id}")
                emit('joined_battle', {'battle_id': battle_id})
                logger.info(f"User joined battle room {battle_id}")
        
        @self.socketio.on('leave_battle')
        def handle_leave_battle(data):
            """Handle leaving a battle room."""
            battle_id = data.get('battle_id')
            if battle_id:
                leave_room(f"battle_{battle_id}")
                emit('left_battle', {'battle_id': battle_id})
        
        @self.socketio.on('spectate_battle')
        def handle_spectate_battle(data):
            """Handle spectating a battle."""
            battle_id = data.get('battle_id')
            if battle_id and 'user_id' in session:
                # Add as spectator
                if battle_id in self.battle_manager.battles:
                    battle = self.battle_manager.battles[battle_id]
                    if battle.add_spectator(session['user_id']):
                        join_room(f"battle_{battle_id}")
                        emit('spectating_battle', {'battle_id': battle_id})
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            """Handle chat message in battle."""
            battle_id = data.get('battle_id')
            message = data.get('message', '').strip()
            
            if battle_id and message and 'username' in session:
                # Broadcast to battle room
                self.socketio.emit('chat_message', {
                    'username': session['username'],
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }, room=f"battle_{battle_id}")
        
        @self.socketio.on('ping')
        def handle_ping():
            """Handle ping for connection keepalive."""
            if request.sid in self.connected_users:
                user_id = self.connected_users[request.sid]['user_id']
                
                # Update ping in battle manager
                for battle in self.battle_manager.battles.values():
                    if user_id in battle.players:
                        battle.players[user_id].ping()
                
                emit('pong')
        
        # Register battle manager callbacks
        self.register_battle_callbacks()
    
    def register_battle_callbacks(self):
        """Register callbacks for battle events."""
        
        def on_player_message(player_id: str, message: BattleMessage):
            """Handle player message."""
            # Find battle for this player
            battle_id = None
            for bid, battle in self.battle_manager.battles.items():
                if player_id in battle.players:
                    battle_id = bid
                    break
            
            if battle_id:
                # Send to specific player's connection
                for sid, user_info in self.connected_users.items():
                    if user_info['user_id'] == player_id:
                        self.socketio.emit('battle_message', message.to_dict(), room=sid)
                        break
        
        def on_spectator_message(spectator_id: str, message: BattleMessage):
            """Handle spectator message."""
            # Send to specific spectator's connection
            for sid, user_info in self.connected_users.items():
                if user_info['user_id'] == spectator_id:
                    self.socketio.emit('battle_message', message.to_dict(), room=sid)
                    break
        
        # Register callbacks with battle manager
        for battle in self.battle_manager.battles.values():
            battle.register_callback('player_message', on_player_message)
            battle.register_callback('spectator_message', on_spectator_message)
    
    def broadcast_to_battle(self, battle_id: str, event: str, data: Dict[str, Any]):
        """Broadcast event to all users in a battle."""
        self.socketio.emit(event, data, room=f"battle_{battle_id}")
    
    def send_to_user(self, user_id: str, event: str, data: Dict[str, Any]):
        """Send event to specific user."""
        for sid, user_info in self.connected_users.items():
            if user_info['user_id'] == user_id:
                self.socketio.emit(event, data, room=sid)
                break
    
    def get_connected_users(self) -> List[Dict[str, Any]]:
        """Get list of connected users."""
        return [
            {
                'user_id': info['user_id'],
                'username': info['username'],
                'connected_at': info['connected_at'].isoformat()
            }
            for info in self.connected_users.values()
        ]
    
    def shutdown(self):
        """Shutdown the web multiplayer integration."""
        self.battle_manager.shutdown()
        logger.info("Web multiplayer integration shutdown")

def create_multiplayer_templates():
    """Create HTML templates for multiplayer interface."""
    
    # Lobby template
    lobby_template = """
{% extends "base.html" %}

{% block title %}Multiplayer Lobby{% endblock %}

{% block extra_head %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.js"></script>
<style>
.battle-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    background: #f9f9f9;
}
.battle-card:hover {
    background: #f0f0f0;
    cursor: pointer;
}
.queue-status {
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
.queue-status.waiting {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
}
.queue-status.ready {
    background: #d4edda;
    border: 1px solid #c3e6cb;
}
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Quick Match Panel -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-bolt"></i> Quick Match</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">Battle Mode</label>
                        <select class="form-select" id="quickMode">
                            {% for mode in battle_modes %}
                            <option value="{{ mode }}">{{ mode.title() }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Format</label>
                        <select class="form-select" id="quickFormat">
                            {% for format in battle_formats %}
                            <option value="{{ format }}">{{ format.title() }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div id="queueStatus" class="queue-status" style="display: none;">
                        <div class="d-flex align-items-center">
                            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                            <span>Searching for opponent...</span>
                        </div>
                    </div>
                    <button class="btn btn-primary w-100" id="quickMatchBtn">Find Match</button>
                    <button class="btn btn-secondary w-100 mt-2" id="cancelQueueBtn" style="display: none;">Cancel Queue</button>
                </div>
            </div>
            
            <!-- Private Battle Panel -->
            <div class="card mt-3">
                <div class="card-header">
                    <h5><i class="fas fa-lock"></i> Private Battle</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">Battle Mode</label>
                        <select class="form-select" id="privateMode">
                            {% for mode in battle_modes %}
                            <option value="{{ mode }}">{{ mode.title() }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Format</label>
                        <select class="form-select" id="privateFormat">
                            {% for format in battle_formats %}
                            <option value="{{ format }}">{{ format.title() }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" id="enableTimer" checked>
                        <label class="form-check-label" for="enableTimer">Enable Timer</label>
                    </div>
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" id="allowSpectators" checked>
                        <label class="form-check-label" for="allowSpectators">Allow Spectators</label>
                    </div>
                    <button class="btn btn-success w-100 mb-2" id="createBattleBtn">Create Battle</button>
                    
                    <hr>
                    <div class="mb-3">
                        <label class="form-label">Join Battle</label>
                        <input type="text" class="form-control" id="battleIdInput" placeholder="Enter Battle ID">
                    </div>
                    <button class="btn btn-info w-100" id="joinBattleBtn">Join Battle</button>
                </div>
            </div>
        </div>
        
        <!-- Active Battles Panel -->
        <div class="col-md-8">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5><i class="fas fa-gamepad"></i> Active Battles</h5>
                    <button class="btn btn-outline-primary btn-sm" id="refreshBattles">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
                <div class="card-body">
                    <div id="battlesList">
                        <div class="text-center text-muted">
                            <i class="fas fa-spinner fa-spin"></i> Loading battles...
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Initialize Socket.IO
const socket = io();

// Elements
const quickMatchBtn = document.getElementById('quickMatchBtn');
const cancelQueueBtn = document.getElementById('cancelQueueBtn');
const createBattleBtn = document.getElementById('createBattleBtn');
const joinBattleBtn = document.getElementById('joinBattleBtn');
const refreshBattlesBtn = document.getElementById('refreshBattles');
const queueStatus = document.getElementById('queueStatus');
const battlesList = document.getElementById('battlesList');

// Socket events
socket.on('connect', function() {
    console.log('Connected to server');
    loadBattles();
});

socket.on('battle_message', function(data) {
    if (data.type === 'battle_started') {
        // Redirect to battle room
        window.location.href = `/multiplayer/battle/${data.data.battle_id}`;
    }
});

// Quick match
quickMatchBtn.addEventListener('click', function() {
    const mode = document.getElementById('quickMode').value;
    const format = document.getElementById('quickFormat').value;
    
    fetch('/api/multiplayer/queue', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode: mode, format: format})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showQueueStatus();
        } else {
            alert('Failed to join queue: ' + data.error);
        }
    });
});

// Cancel queue
cancelQueueBtn.addEventListener('click', function() {
    fetch('/api/multiplayer/cancel_queue', {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hideQueueStatus();
        }
    });
});

// Create private battle
createBattleBtn.addEventListener('click', function() {
    const mode = document.getElementById('privateMode').value;
    const format = document.getElementById('privateFormat').value;
    const settings = {
        timer_enabled: document.getElementById('enableTimer').checked,
        allow_spectators: document.getElementById('allowSpectators').checked
    };
    
    fetch('/api/multiplayer/create_battle', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode: mode, format: format, settings: settings})
    })
    .then(response => response.json())
    .then(data => {
        if (data.battle_id) {
            window.location.href = `/multiplayer/battle/${data.battle_id}`;
        } else {
            alert('Failed to create battle: ' + data.error);
        }
    });
});

// Join private battle
joinBattleBtn.addEventListener('click', function() {
    const battleId = document.getElementById('battleIdInput').value.trim();
    if (!battleId) {
        alert('Please enter a Battle ID');
        return;
    }
    
    fetch('/api/multiplayer/join_battle', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({battle_id: battleId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/multiplayer/battle/${battleId}`;
        } else {
            alert('Failed to join battle: ' + data.error);
        }
    });
});

// Refresh battles
refreshBattlesBtn.addEventListener('click', loadBattles);

function showQueueStatus() {
    queueStatus.style.display = 'block';
    quickMatchBtn.style.display = 'none';
    cancelQueueBtn.style.display = 'block';
}

function hideQueueStatus() {
    queueStatus.style.display = 'none';
    quickMatchBtn.style.display = 'block';
    cancelQueueBtn.style.display = 'none';
}

function loadBattles() {
    fetch('/api/multiplayer/battles')
    .then(response => response.json())
    .then(battles => {
        if (battles.length === 0) {
            battlesList.innerHTML = '<div class="text-center text-muted">No active battles</div>';
            return;
        }
        
        let html = '';
        battles.forEach(battle => {
            html += `
                <div class="battle-card" data-battle-id="${battle.battle_id}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${battle.mode.toUpperCase()} - ${battle.format.toUpperCase()}</h6>
                            <small class="text-muted">Phase: ${battle.phase.replace('_', ' ')}</small>
                        </div>
                        <div class="text-end">
                            <div class="badge bg-primary">${battle.players}/2 Players</div>
                            <div class="badge bg-secondary">${battle.spectators} Spectators</div>
                        </div>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="spectate('${battle.battle_id}')">
                            <i class="fas fa-eye"></i> Spectate
                        </button>
                    </div>
                </div>
            `;
        });
        battlesList.innerHTML = html;
    });
}

function spectate(battleId) {
    window.location.href = `/multiplayer/battle/${battleId}`;
}

// Load battles on page load
loadBattles();
setInterval(loadBattles, 10000); // Refresh every 10 seconds
</script>
{% endblock %}
"""
    
    # Battle template
    battle_template = """
{% extends "base.html" %}

{% block title %}Battle Room{% endblock %}

{% block extra_head %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.js"></script>
<style>
.battle-field {
    background: linear-gradient(135deg, #74b9ff, #0984e3);
    border-radius: 10px;
    padding: 20px;
    color: white;
    min-height: 300px;
}
.pokemon-sprite {
    width: 80px;
    height: 80px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}
.move-button {
    margin: 5px;
    min-width: 120px;
}
.battle-log {
    height: 300px;
    overflow-y: auto;
    border: 1px solid #ddd;
    padding: 10px;
    background: #f8f9fa;
}
.chat-area {
    height: 200px;
    overflow-y: auto;
    border: 1px solid #ddd;
    padding: 10px;
    background: #f8f9fa;
}
.timer-display {
    font-size: 24px;
    font-weight: bold;
    color: #dc3545;
}
.phase-display {
    font-size: 18px;
    font-weight: bold;
    color: #198754;
}
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Battle Area -->
        <div class="col-md-8">
            <!-- Battle Status -->
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <span class="phase-display" id="phaseDisplay">{{ battle_state.phase|title }}</span>
                        </div>
                        <div class="col-md-3">
                            <strong>Turn:</strong> <span id="turnDisplay">{{ battle_state.turn_number }}</span>
                        </div>
                        <div class="col-md-3">
                            <strong>Timer:</strong> <span class="timer-display" id="timerDisplay">--</span>
                        </div>
                        <div class="col-md-3">
                            <button class="btn btn-outline-secondary btn-sm" onclick="location.href='/multiplayer'">
                                <i class="fas fa-arrow-left"></i> Back to Lobby
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Battle Field -->
            <div class="card mb-3">
                <div class="card-body">
                    <div class="battle-field">
                        <div class="row align-items-center">
                            <div class="col-md-4 text-center">
                                <div class="pokemon-sprite mx-auto mb-2">
                                    <i class="fas fa-dragon"></i>
                                </div>
                                <h6 id="playerPokemon">Your Pokemon</h6>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar bg-success" style="width: 100%" id="playerHP"></div>
                                </div>
                            </div>
                            <div class="col-md-4 text-center">
                                <h4>VS</h4>
                                <div id="battleStatus">Battle in Progress</div>
                            </div>
                            <div class="col-md-4 text-center">
                                <div class="pokemon-sprite mx-auto mb-2">
                                    <i class="fas fa-fire"></i>
                                </div>
                                <h6 id="opponentPokemon">Opponent Pokemon</h6>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar bg-success" style="width: 100%" id="opponentHP"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Move Selection -->
            <div class="card" id="moveSelection">
                <div class="card-header">
                    <h5><i class="fas fa-fist-raised"></i> Select Your Move</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <button class="btn btn-primary move-button w-100" data-move="0">
                                <strong>Tackle</strong><br>
                                <small>Normal • Physical • 40 BP</small>
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-primary move-button w-100" data-move="1">
                                <strong>Ember</strong><br>
                                <small>Fire • Special • 40 BP</small>
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-primary move-button w-100" data-move="2">
                                <strong>Growl</strong><br>
                                <small>Normal • Status • -- BP</small>
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-primary move-button w-100" data-move="3">
                                <strong>Scratch</strong><br>
                                <small>Normal • Physical • 40 BP</small>
                            </button>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-success w-100" id="submitMovesBtn" disabled>
                            <i class="fas fa-check"></i> Submit Move
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Side Panel -->
        <div class="col-md-4">
            <!-- Players -->
            <div class="card mb-3">
                <div class="card-header">
                    <h5><i class="fas fa-users"></i> Players</h5>
                </div>
                <div class="card-body" id="playersInfo">
                    {% for player_id, player in battle_state.players.items() %}
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <strong>{{ player.username }}</strong>
                            <small class="text-muted d-block">{{ player.status|title }}</small>
                        </div>
                        <div>
                            {% if player.ready %}
                            <span class="badge bg-success">Ready</span>
                            {% else %}
                            <span class="badge bg-warning">Waiting</span>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Battle Log -->
            <div class="card mb-3">
                <div class="card-header">
                    <h5><i class="fas fa-scroll"></i> Battle Log</h5>
                </div>
                <div class="card-body p-0">
                    <div class="battle-log" id="battleLog">
                        <div class="text-muted">Battle starting...</div>
                    </div>
                </div>
            </div>
            
            <!-- Chat -->
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-comments"></i> Chat</h5>
                </div>
                <div class="card-body p-0">
                    <div class="chat-area" id="chatArea">
                        <div class="text-muted">Chat is active</div>
                    </div>
                </div>
                <div class="card-footer p-2">
                    <div class="input-group">
                        <input type="text" class="form-control" id="chatInput" placeholder="Type a message...">
                        <button class="btn btn-primary" id="sendChatBtn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
const socket = io();
const battleId = '{{ battle_id }}';
let selectedMove = null;
let timerInterval = null;

// Join battle room
socket.emit('join_battle', {battle_id: battleId});

// Socket events
socket.on('battle_message', function(data) {
    addToBattleLog(data);
    updateBattleState(data);
});

socket.on('chat_message', function(data) {
    addToChatArea(data.username + ': ' + data.message);
});

// Move selection
document.querySelectorAll('.move-button').forEach(btn => {
    btn.addEventListener('click', function() {
        selectedMove = this.dataset.move;
        
        // Update button states
        document.querySelectorAll('.move-button').forEach(b => b.classList.remove('btn-warning'));
        this.classList.add('btn-warning');
        
        // Enable submit button
        document.getElementById('submitMovesBtn').disabled = false;
    });
});

// Submit moves
document.getElementById('submitMovesBtn').addEventListener('click', function() {
    if (selectedMove !== null) {
        fetch('/api/multiplayer/submit_moves', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                battle_id: battleId,
                moves: ['move_' + selectedMove]
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.disabled = true;
                document.querySelectorAll('.move-button').forEach(b => b.disabled = true);
                addToBattleLog({type: 'info', data: {message: 'Move submitted. Waiting for opponent...'}});
            }
        });
    }
});

// Chat
document.getElementById('sendChatBtn').addEventListener('click', sendChat);
document.getElementById('chatInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendChat();
    }
});

function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (message) {
        socket.emit('chat_message', {
            battle_id: battleId,
            message: message
        });
        input.value = '';
    }
}

function addToBattleLog(data) {
    const log = document.getElementById('battleLog');
    const timestamp = new Date().toLocaleTimeString();
    
    let message = '';
    if (data.type === 'turn_start') {
        message = `Turn ${data.data.turn_number} started`;
    } else if (data.type === 'moves_submitted') {
        message = `Player submitted moves`;
    } else if (data.type === 'turn_executed') {
        message = `Turn ${data.data.turn_number} executed`;
    } else {
        message = data.type.replace('_', ' ');
    }
    
    const div = document.createElement('div');
    div.innerHTML = `<small class="text-muted">[${timestamp}]</small> ${message}`;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

function addToChatArea(message) {
    const chat = document.getElementById('chatArea');
    const timestamp = new Date().toLocaleTimeString();
    
    const div = document.createElement('div');
    div.innerHTML = `<small class="text-muted">[${timestamp}]</small> ${message}`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function updateBattleState(data) {
    if (data.type === 'turn_start') {
        document.getElementById('turnDisplay').textContent = data.data.turn_number;
        document.getElementById('phaseDisplay').textContent = 'Move Selection';
        
        // Enable move selection
        document.querySelectorAll('.move-button').forEach(b => {
            b.disabled = false;
            b.classList.remove('btn-warning');
        });
        selectedMove = null;
        document.getElementById('submitMovesBtn').disabled = true;
        
        // Start timer
        if (data.data.time_limit) {
            startTimer(data.data.time_limit);
        }
    }
}

function startTimer(seconds) {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    let remaining = seconds;
    const timerDisplay = document.getElementById('timerDisplay');
    
    timerInterval = setInterval(() => {
        timerDisplay.textContent = remaining + 's';
        remaining--;
        
        if (remaining < 0) {
            clearInterval(timerInterval);
            timerDisplay.textContent = '--';
        }
    }, 1000);
}

// Periodic state updates
setInterval(() => {
    fetch(`/api/multiplayer/battle/${battleId}`)
    .then(response => response.json())
    .then(state => {
        if (state.phase) {
            document.getElementById('phaseDisplay').textContent = state.phase.replace('_', ' ');
        }
        if (state.turn_number) {
            document.getElementById('turnDisplay').textContent = state.turn_number;
        }
    });
}, 5000);
</script>
{% endblock %}
"""
    
    return {
        'multiplayer/lobby.html': lobby_template,
        'multiplayer/battle.html': battle_template
    }

# Example usage
if __name__ == "__main__":
    from flask import Flask
    from flask_socketio import SocketIO
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize multiplayer integration
    multiplayer = WebMultiplayerIntegration(app, socketio)
    
    # Create templates
    templates = create_multiplayer_templates()
    print("Templates created:")
    for template_name in templates.keys():
        print(f"  - {template_name}")
    
    if __name__ == "__main__":
        socketio.run(app, debug=True, port=5000)