"""
Online Multiplayer Battle System for Pokemon Team Builder.
Manages real-time battles between players with networking, matchmaking, and synchronization.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

try:
    from core.pokemon import Pokemon
    from core.types import PokemonType
    from core.moves import Move
    from teambuilder.team import PokemonTeam
    from battle.battle_engine import BattleEngine, BattleState
    from battle.battle_ai import BattleAI
except ImportError as e:
    print(f"Some imports failed: {e}. Using mock classes for development.")
    # Create mock classes for development/testing
    class Pokemon:
        def __init__(self, name="MockPokemon"):
            self.name = name
    class PokemonTeam:
        def __init__(self, name="MockTeam"):
            self.name = name
            self.pokemon = []
    class BattleEngine:
        def initialize_battle(self, team1, team2):
            pass
        def execute_turn(self, moves):
            return {"success": True}
    class BattleAI:
        pass

logger = logging.getLogger(__name__)

class BattleMode(Enum):
    """Battle mode types."""
    SINGLES = "singles"
    DOUBLES = "doubles"
    TRIPLES = "triples"
    ROTATION = "rotation"
    MULTI = "multi"

class BattleFormat(Enum):
    """Battle format types."""
    CASUAL = "casual"
    RANKED = "ranked"
    TOURNAMENT = "tournament"
    CUSTOM = "custom"

class PlayerStatus(Enum):
    """Player status in battle."""
    WAITING = "waiting"
    CONNECTED = "connected"
    SELECTING = "selecting"
    READY = "ready"
    BATTLING = "battling"
    DISCONNECTED = "disconnected"
    FINISHED = "finished"

class BattlePhase(Enum):
    """Battle phase types."""
    TEAM_PREVIEW = "team_preview"
    TURN_START = "turn_start"
    MOVE_SELECTION = "move_selection"
    MOVE_EXECUTION = "move_execution"
    TURN_END = "turn_end"
    BATTLE_END = "battle_end"

@dataclass
class BattlePlayer:
    """Online battle player information."""
    id: str
    username: str
    rating: int
    team: Optional[PokemonTeam]
    status: PlayerStatus = PlayerStatus.WAITING
    connection_id: str = ""
    last_ping: float = 0.0
    moves_selected: List[str] = None
    ready: bool = False
    
    def __post_init__(self):
        if self.moves_selected is None:
            self.moves_selected = []
        self.last_ping = time.time()
    
    def is_connected(self) -> bool:
        """Check if player is connected (last ping within 30 seconds)."""
        return time.time() - self.last_ping < 30.0
    
    def ping(self):
        """Update last ping time."""
        self.last_ping = time.time()

@dataclass
class BattleMessage:
    """Battle message for communication."""
    type: str
    data: Dict[str, Any]
    timestamp: float
    sender_id: str = ""
    target_id: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'data': self.data,
            'timestamp': self.timestamp,
            'sender_id': self.sender_id,
            'target_id': self.target_id
        }

class OnlineBattle:
    """Online multiplayer battle session."""
    
    def __init__(self, battle_id: str, mode: BattleMode, format: BattleFormat):
        self.battle_id = battle_id
        self.mode = mode
        self.format = format
        self.players: Dict[str, BattlePlayer] = {}
        self.spectators: List[str] = []
        self.battle_engine = BattleEngine()
        self.current_phase = BattlePhase.TEAM_PREVIEW
        self.turn_number = 0
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.winner_id: Optional[str] = None
        self.battle_log: List[BattleMessage] = []
        self.move_timeout = 60  # seconds
        self.turn_timer_start = 0.0
        self.settings = {
            'timer_enabled': True,
            'move_time_limit': 60,
            'team_preview_time': 90,
            'allow_spectators': True,
            'private_battle': False
        }
        
        # Synchronization
        self._lock = threading.Lock()
        self._message_queue = queue.Queue()
        self._callbacks: Dict[str, List[Callable]] = {}
        
    def add_player(self, player: BattlePlayer) -> bool:
        """Add a player to the battle."""
        with self._lock:
            if len(self.players) >= 2:  # Max 2 players for now
                logger.warning(f"Battle {self.battle_id} already has maximum players")
                return False
            
            if player.id in self.players:
                logger.warning(f"Player {player.id} already in battle {self.battle_id}")
                return False
            
            self.players[player.id] = player
            player.status = PlayerStatus.CONNECTED
            
            self._broadcast_message(BattleMessage(
                type='player_joined',
                data={
                    'player_id': player.id,
                    'username': player.username,
                    'rating': player.rating
                }
            ))
            
            logger.info(f"Player {player.username} joined battle {self.battle_id}")
            
            # Start battle if both players ready
            if len(self.players) == 2 and all(p.team for p in self.players.values()):
                self._start_battle()
            
            return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the battle."""
        with self._lock:
            if player_id not in self.players:
                return False
            
            player = self.players[player_id]
            player.status = PlayerStatus.DISCONNECTED
            
            # Handle disconnection during battle
            if self.current_phase in [BattlePhase.MOVE_SELECTION, BattlePhase.BATTLING]:
                self._handle_player_disconnect(player_id)
            
            self._broadcast_message(BattleMessage(
                type='player_left',
                data={
                    'player_id': player_id,
                    'username': player.username
                }
            ))
            
            logger.info(f"Player {player.username} left battle {self.battle_id}")
            return True
    
    def add_spectator(self, spectator_id: str) -> bool:
        """Add a spectator to the battle."""
        if not self.settings['allow_spectators']:
            return False
        
        with self._lock:
            if spectator_id not in self.spectators:
                self.spectators.append(spectator_id)
                
                self._send_message_to_spectator(spectator_id, BattleMessage(
                    type='spectator_joined',
                    data={'battle_state': self._get_battle_state()}
                ))
                
                return True
        return False
    
    def submit_moves(self, player_id: str, moves: List[str]) -> bool:
        """Submit moves for a player."""
        with self._lock:
            if player_id not in self.players:
                return False
            
            player = self.players[player_id]
            
            if self.current_phase != BattlePhase.MOVE_SELECTION:
                logger.warning(f"Player {player_id} tried to submit moves in wrong phase")
                return False
            
            # Validate moves
            if not self._validate_moves(player, moves):
                logger.warning(f"Invalid moves submitted by player {player_id}")
                return False
            
            player.moves_selected = moves
            player.ready = True
            player.status = PlayerStatus.READY
            
            self._broadcast_message(BattleMessage(
                type='moves_submitted',
                data={
                    'player_id': player_id,
                    'ready': True
                }
            ))
            
            # Check if all players ready
            if all(p.ready for p in self.players.values()):
                self._execute_moves()
            
            return True
    
    def _start_battle(self):
        """Start the battle when both players are ready."""
        self.started_at = datetime.now()
        self.current_phase = BattlePhase.TEAM_PREVIEW
        
        # Initialize battle engine
        player_teams = [p.team for p in self.players.values()]
        self.battle_engine.initialize_battle(player_teams[0], player_teams[1])
        
        self._broadcast_message(BattleMessage(
            type='battle_started',
            data={
                'battle_id': self.battle_id,
                'mode': self.mode.value,
                'format': self.format.value,
                'players': [
                    {
                        'id': p.id,
                        'username': p.username,
                        'rating': p.rating
                    }
                    for p in self.players.values()
                ]
            }
        ))
        
        # Start team preview phase
        self._start_team_preview()
    
    def _start_team_preview(self):
        """Start team preview phase."""
        self.current_phase = BattlePhase.TEAM_PREVIEW
        
        # Send team preview data to each player
        for player_id, player in self.players.items():
            opponent = next(p for p in self.players.values() if p.id != player_id)
            
            self._send_message_to_player(player_id, BattleMessage(
                type='team_preview',
                data={
                    'your_team': self._serialize_team(player.team),
                    'opponent_team': self._serialize_team_preview(opponent.team),
                    'preview_time': self.settings['team_preview_time']
                }
            ))
        
        # Start preview timer
        if self.settings['timer_enabled']:
            threading.Timer(
                self.settings['team_preview_time'],
                self._end_team_preview
            ).start()
    
    def _end_team_preview(self):
        """End team preview and start first turn."""
        self.current_phase = BattlePhase.TURN_START
        self.turn_number = 1
        self._start_turn()
    
    def _start_turn(self):
        """Start a new turn."""
        self.current_phase = BattlePhase.MOVE_SELECTION
        self.turn_timer_start = time.time()
        
        # Reset player ready states
        for player in self.players.values():
            player.ready = False
            player.moves_selected = []
            player.status = PlayerStatus.SELECTING
        
        self._broadcast_message(BattleMessage(
            type='turn_start',
            data={
                'turn_number': self.turn_number,
                'battle_state': self._get_battle_state(),
                'time_limit': self.settings['move_time_limit']
            }
        ))
        
        # Start move selection timer
        if self.settings['timer_enabled']:
            threading.Timer(
                self.settings['move_time_limit'],
                self._handle_move_timeout
            ).start()
    
    def _execute_moves(self):
        """Execute submitted moves."""
        self.current_phase = BattlePhase.MOVE_EXECUTION
        
        # Get moves from both players
        player_moves = {}
        for player_id, player in self.players.items():
            player_moves[player_id] = player.moves_selected
        
        # Execute moves using battle engine
        try:
            battle_result = self.battle_engine.execute_turn(player_moves)
            
            # Broadcast turn results
            self._broadcast_message(BattleMessage(
                type='turn_executed',
                data={
                    'turn_number': self.turn_number,
                    'moves': player_moves,
                    'results': battle_result,
                    'battle_state': self._get_battle_state()
                }
            ))
            
            # Check for battle end conditions
            if self._check_battle_end():
                self._end_battle()
            else:
                # Start next turn
                self.turn_number += 1
                self._start_turn()
                
        except Exception as e:
            logger.error(f"Error executing moves in battle {self.battle_id}: {e}")
            self._broadcast_message(BattleMessage(
                type='battle_error',
                data={'error': 'Failed to execute moves'}
            ))
    
    def _handle_move_timeout(self):
        """Handle move selection timeout."""
        with self._lock:
            if self.current_phase != BattlePhase.MOVE_SELECTION:
                return
            
            # Auto-select moves for players who didn't submit
            for player in self.players.values():
                if not player.ready:
                    # Use AI to select moves
                    ai_moves = self._get_ai_moves(player)
                    player.moves_selected = ai_moves
                    player.ready = True
                    
                    self._send_message_to_player(player.id, BattleMessage(
                        type='moves_auto_selected',
                        data={'moves': ai_moves}
                    ))
            
            # Execute moves
            self._execute_moves()
    
    def _get_ai_moves(self, player: BattlePlayer) -> List[str]:
        """Get AI-selected moves for a player."""
        try:
            ai = BattleAI()
            # Simplified AI move selection
            return ['Tackle']  # Would implement proper AI logic
        except Exception as e:
            logger.error(f"AI move selection failed: {e}")
            return ['Tackle']  # Fallback move
    
    def _validate_moves(self, player: BattlePlayer, moves: List[str]) -> bool:
        """Validate submitted moves."""
        if not moves:
            return False
        
        # Basic validation - would implement comprehensive move validation
        for move in moves:
            if not isinstance(move, str) or not move.strip():
                return False
        
        return True
    
    def _check_battle_end(self) -> bool:
        """Check if battle should end."""
        # Simplified end condition - would implement proper battle end logic
        return self.turn_number >= 10  # Example: end after 10 turns
    
    def _end_battle(self):
        """End the battle and determine winner."""
        self.current_phase = BattlePhase.BATTLE_END
        self.ended_at = datetime.now()
        
        # Determine winner (simplified)
        player_ids = list(self.players.keys())
        self.winner_id = player_ids[0]  # Would implement proper winner determination
        
        winner = self.players[self.winner_id]
        loser = next(p for p in self.players.values() if p.id != self.winner_id)
        
        # Update ratings (simplified Elo system)
        self._update_ratings(winner, loser)
        
        # Broadcast battle end
        self._broadcast_message(BattleMessage(
            type='battle_ended',
            data={
                'winner_id': self.winner_id,
                'winner_name': winner.username,
                'final_state': self._get_battle_state(),
                'battle_duration': (self.ended_at - self.started_at).total_seconds()
            }
        ))
        
        logger.info(f"Battle {self.battle_id} ended. Winner: {winner.username}")
    
    def _update_ratings(self, winner: BattlePlayer, loser: BattlePlayer):
        """Update player ratings using Elo system."""
        K = 32  # K-factor
        
        # Calculate expected scores
        expected_winner = 1 / (1 + 10 ** ((loser.rating - winner.rating) / 400))
        expected_loser = 1 - expected_winner
        
        # Update ratings
        winner.rating += K * (1 - expected_winner)
        loser.rating += K * (0 - expected_loser)
        
        # Ensure ratings don't go below minimum
        winner.rating = max(100, int(winner.rating))
        loser.rating = max(100, int(loser.rating))
    
    def _handle_player_disconnect(self, player_id: str):
        """Handle player disconnection during battle."""
        # Give player 60 seconds to reconnect
        threading.Timer(60.0, self._force_disconnect, args=[player_id]).start()
        
        self._broadcast_message(BattleMessage(
            type='player_disconnected',
            data={
                'player_id': player_id,
                'reconnect_time': 60
            }
        ))
    
    def _force_disconnect(self, player_id: str):
        """Force disconnect player and end battle."""
        if player_id in self.players and not self.players[player_id].is_connected():
            # Award victory to opponent
            opponent_id = next(p_id for p_id in self.players.keys() if p_id != player_id)
            self.winner_id = opponent_id
            self._end_battle()
    
    def _get_battle_state(self) -> Dict[str, Any]:
        """Get current battle state."""
        return {
            'battle_id': self.battle_id,
            'phase': self.current_phase.value,
            'turn_number': self.turn_number,
            'players': {
                p_id: {
                    'username': p.username,
                    'status': p.status.value,
                    'ready': p.ready
                }
                for p_id, p in self.players.items()
            },
            'timer': {
                'enabled': self.settings['timer_enabled'],
                'remaining': max(0, self.settings['move_time_limit'] - (time.time() - self.turn_timer_start))
                if self.current_phase == BattlePhase.MOVE_SELECTION else 0
            }
        }
    
    def _serialize_team(self, team: PokemonTeam) -> Dict[str, Any]:
        """Serialize team for network transmission."""
        return {
            'name': team.name,
            'pokemon': [
                {
                    'name': pokemon.name,
                    'level': getattr(pokemon, 'level', 50),
                    'types': [t.value for t in pokemon.types],
                    'stats': pokemon.stats,
                    'moves': [move.name for move in pokemon.moves]
                }
                for pokemon in team.pokemon
            ]
        }
    
    def _serialize_team_preview(self, team: PokemonTeam) -> Dict[str, Any]:
        """Serialize team preview (limited info) for opponent."""
        return {
            'name': team.name,
            'pokemon': [
                {
                    'name': pokemon.name,
                    'level': getattr(pokemon, 'level', 50),
                    'types': [t.value for t in pokemon.types]
                    # No stats, moves, or abilities revealed
                }
                for pokemon in team.pokemon
            ]
        }
    
    def _broadcast_message(self, message: BattleMessage):
        """Broadcast message to all participants."""
        self.battle_log.append(message)
        
        # Send to players
        for player_id in self.players.keys():
            self._send_message_to_player(player_id, message)
        
        # Send to spectators
        for spectator_id in self.spectators:
            self._send_message_to_spectator(spectator_id, message)
    
    def _send_message_to_player(self, player_id: str, message: BattleMessage):
        """Send message to specific player."""
        message.target_id = player_id
        self._message_queue.put(('player', player_id, message))
        
        # Trigger callbacks
        self._trigger_callbacks('player_message', player_id, message)
    
    def _send_message_to_spectator(self, spectator_id: str, message: BattleMessage):
        """Send message to specific spectator."""
        message.target_id = spectator_id
        self._message_queue.put(('spectator', spectator_id, message))
        
        # Trigger callbacks
        self._trigger_callbacks('spectator_message', spectator_id, message)
    
    def _trigger_callbacks(self, event_type: str, *args):
        """Trigger registered callbacks."""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(*args)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for events."""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)

class BattleMatchmaker:
    """Matchmaking system for finding battle opponents."""
    
    def __init__(self):
        self.waiting_players: Dict[str, BattlePlayer] = {}
        self.rating_tolerance = 100  # Initial rating difference tolerance
        self.max_wait_time = 120  # Maximum wait time in seconds
        self._lock = threading.Lock()
    
    def add_to_queue(self, player: BattlePlayer, mode: BattleMode, format: BattleFormat) -> bool:
        """Add player to matchmaking queue."""
        with self._lock:
            queue_key = f"{mode.value}_{format.value}"
            player_key = f"{player.id}_{queue_key}"
            
            if player_key in self.waiting_players:
                return False
            
            player.status = PlayerStatus.WAITING
            self.waiting_players[player_key] = player
            
            logger.info(f"Player {player.username} added to {queue_key} queue")
            return True
    
    def remove_from_queue(self, player_id: str) -> bool:
        """Remove player from matchmaking queue."""
        with self._lock:
            removed = False
            keys_to_remove = [k for k in self.waiting_players.keys() if k.startswith(player_id)]
            
            for key in keys_to_remove:
                del self.waiting_players[key]
                removed = True
            
            return removed
    
    def find_match(self, mode: BattleMode, format: BattleFormat) -> Optional[Tuple[BattlePlayer, BattlePlayer]]:
        """Find a match between waiting players."""
        with self._lock:
            queue_key = f"{mode.value}_{format.value}"
            candidates = []
            
            # Find players in this queue
            for key, player in self.waiting_players.items():
                if key.endswith(queue_key):
                    candidates.append((key, player))
            
            if len(candidates) < 2:
                return None
            
            # Sort by rating for better matching
            candidates.sort(key=lambda x: x[1].rating)
            
            # Find best match
            for i, (key1, player1) in enumerate(candidates):
                for j, (key2, player2) in enumerate(candidates[i+1:], i+1):
                    rating_diff = abs(player1.rating - player2.rating)
                    
                    if rating_diff <= self.rating_tolerance:
                        # Remove from queue
                        del self.waiting_players[key1]
                        del self.waiting_players[key2]
                        
                        logger.info(f"Match found: {player1.username} vs {player2.username}")
                        return player1, player2
            
            return None

class OnlineBattleManager:
    """Main manager for online multiplayer battles."""
    
    def __init__(self):
        self.battles: Dict[str, OnlineBattle] = {}
        self.matchmaker = BattleMatchmaker()
        self.player_connections: Dict[str, str] = {}  # player_id -> connection_id
        self.connection_players: Dict[str, str] = {}  # connection_id -> player_id
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._running = True
        
        # Start background tasks
        threading.Thread(target=self._matchmaking_loop, daemon=True).start()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
    
    def create_private_battle(self, host_player: BattlePlayer, mode: BattleMode, 
                            format: BattleFormat, settings: Dict[str, Any] = None) -> str:
        """Create a private battle room."""
        battle_id = f"battle_{uuid.uuid4().hex[:8]}"
        battle = OnlineBattle(battle_id, mode, format)
        
        if settings:
            battle.settings.update(settings)
            battle.settings['private_battle'] = True
        
        battle.add_player(host_player)
        self.battles[battle_id] = battle
        
        logger.info(f"Private battle {battle_id} created by {host_player.username}")
        return battle_id
    
    def join_battle(self, battle_id: str, player: BattlePlayer) -> bool:
        """Join an existing battle."""
        if battle_id not in self.battles:
            return False
        
        battle = self.battles[battle_id]
        return battle.add_player(player)
    
    def queue_for_battle(self, player: BattlePlayer, mode: BattleMode, format: BattleFormat) -> bool:
        """Queue player for matchmaking."""
        return self.matchmaker.add_to_queue(player, mode, format)
    
    def cancel_queue(self, player_id: str) -> bool:
        """Cancel player's matchmaking queue."""
        return self.matchmaker.remove_from_queue(player_id)
    
    def submit_moves(self, battle_id: str, player_id: str, moves: List[str]) -> bool:
        """Submit moves for a player in battle."""
        if battle_id not in self.battles:
            return False
        
        battle = self.battles[battle_id]
        return battle.submit_moves(player_id, moves)
    
    def register_connection(self, player_id: str, connection_id: str):
        """Register player connection."""
        self.player_connections[player_id] = connection_id
        self.connection_players[connection_id] = player_id
        
        # Update player ping in active battles
        for battle in self.battles.values():
            if player_id in battle.players:
                battle.players[player_id].connection_id = connection_id
                battle.players[player_id].ping()
    
    def handle_disconnect(self, connection_id: str):
        """Handle player disconnection."""
        if connection_id in self.connection_players:
            player_id = self.connection_players[connection_id]
            
            # Remove from matchmaking
            self.matchmaker.remove_from_queue(player_id)
            
            # Handle battle disconnection
            for battle in self.battles.values():
                if player_id in battle.players:
                    battle.remove_player(player_id)
            
            # Clean up connections
            del self.connection_players[connection_id]
            if player_id in self.player_connections:
                del self.player_connections[player_id]
    
    def get_battle_list(self) -> List[Dict[str, Any]]:
        """Get list of active battles."""
        battle_list = []
        
        for battle in self.battles.values():
            if not battle.settings.get('private_battle', False):
                battle_list.append({
                    'battle_id': battle.battle_id,
                    'mode': battle.mode.value,
                    'format': battle.format.value,
                    'players': len(battle.players),
                    'spectators': len(battle.spectators),
                    'phase': battle.current_phase.value,
                    'created_at': battle.created_at.isoformat()
                })
        
        return battle_list
    
    def get_battle_state(self, battle_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a battle."""
        if battle_id in self.battles:
            return self.battles[battle_id]._get_battle_state()
        return None
    
    def _matchmaking_loop(self):
        """Background matchmaking loop."""
        while self._running:
            try:
                # Try to find matches for each mode/format combination
                for mode in BattleMode:
                    for format in BattleFormat:
                        match = self.matchmaker.find_match(mode, format)
                        
                        if match:
                            player1, player2 = match
                            
                            # Create battle
                            battle_id = f"battle_{uuid.uuid4().hex[:8]}"
                            battle = OnlineBattle(battle_id, mode, format)
                            
                            battle.add_player(player1)
                            battle.add_player(player2)
                            
                            self.battles[battle_id] = battle
                            
                            logger.info(f"Matchmaking created battle {battle_id}")
                
                # Increase rating tolerance for waiting players
                self.matchmaker.rating_tolerance = min(500, self.matchmaker.rating_tolerance + 10)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Matchmaking loop error: {e}")
                time.sleep(10)
    
    def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                current_time = datetime.now()
                battles_to_remove = []
                
                # Clean up finished battles
                for battle_id, battle in self.battles.items():
                    # Remove battles that ended more than 1 hour ago
                    if (battle.ended_at and 
                        current_time - battle.ended_at > timedelta(hours=1)):
                        battles_to_remove.append(battle_id)
                    
                    # Remove abandoned battles (no players for 10 minutes)
                    elif (not any(p.is_connected() for p in battle.players.values()) and
                          current_time - battle.created_at > timedelta(minutes=10)):
                        battles_to_remove.append(battle_id)
                
                # Remove old battles
                for battle_id in battles_to_remove:
                    del self.battles[battle_id]
                    logger.info(f"Cleaned up battle {battle_id}")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                time.sleep(60)
    
    def shutdown(self):
        """Shutdown the battle manager."""
        self._running = False
        self._executor.shutdown(wait=True)
        logger.info("Online battle manager shutdown")

# Example usage
if __name__ == "__main__":
    # Create battle manager
    battle_manager = OnlineBattleManager()
    
    # Create test players
    player1 = BattlePlayer(
        id="player1",
        username="Ash",
        rating=1200,
        team=None  # Would have actual team
    )
    
    player2 = BattlePlayer(
        id="player2", 
        username="Gary",
        rating=1180,
        team=None  # Would have actual team
    )
    
    # Queue for battle
    battle_manager.queue_for_battle(player1, BattleMode.SINGLES, BattleFormat.CASUAL)
    battle_manager.queue_for_battle(player2, BattleMode.SINGLES, BattleFormat.CASUAL)
    
    # Wait for matchmaking
    time.sleep(10)
    
    # Check battle list
    battles = battle_manager.get_battle_list()
    print(f"Active battles: {len(battles)}")
    
    if battles:
        battle_id = battles[0]['battle_id']
        state = battle_manager.get_battle_state(battle_id)
        print(f"Battle state: {state}")
    
    # Shutdown
    battle_manager.shutdown()