"""
Battle simulator for Pokemon Team Builder.
Provides automated battle simulation with AI opponents.
"""

from typing import List, Dict, Optional, Tuple
import random
import time

from .battle_state import BattleState, PokemonBattleState, BattleStatus
from .battle_engine import BattleEngine
from ..teambuilder.team import PokemonTeam
from ..core.pokemon import Pokemon, ShadowPokemon


class BattleLog:
    """Battle log for tracking battle events."""
    
    def __init__(self):
        self.events = []
        self.turn_logs = {}
    
    def add_event(self, turn: int, message: str, event_type: str = "info"):
        """Add an event to the battle log."""
        event = {
            'turn': turn,
            'message': message,
            'type': event_type,
            'timestamp': time.time()
        }
        self.events.append(event)
        
        if turn not in self.turn_logs:
            self.turn_logs[turn] = []
        self.turn_logs[turn].append(event)
    
    def get_turn_log(self, turn: int) -> List[Dict]:
        """Get all events for a specific turn."""
        return self.turn_logs.get(turn, [])
    
    def get_full_log(self) -> List[Dict]:
        """Get all battle events."""
        return self.events
    
    def get_summary(self) -> str:
        """Get a summary of the battle."""
        if not self.events:
            return "No battle events recorded."
        
        summary_lines = [f"Battle Log Summary ({len(self.events)} events):"]
        
        # Group by turn
        for turn in sorted(self.turn_logs.keys()):
            summary_lines.append(f"\nTurn {turn}:")
            for event in self.turn_logs[turn]:
                summary_lines.append(f"  [{event['type'].upper()}] {event['message']}")
        
        return "\n".join(summary_lines)


class BattleResult:
    """Result of a completed battle."""
    
    def __init__(
        self,
        winner: bool,  # True for player, False for opponent
        turns_taken: int,
        player_team_final_state: List[PokemonBattleState],
        opponent_team_final_state: List[PokemonBattleState],
        battle_log: BattleLog,
        battle_summary: str
    ):
        self.winner = winner
        self.turns_taken = turns_taken
        self.player_team_final_state = player_team_final_state
        self.opponent_team_final_state = opponent_team_final_state
        self.battle_log = battle_log
        self.battle_summary = battle_summary
    
    def get_result_text(self) -> str:
        """Get human-readable battle result."""
        if self.winner is True:
            return f"🎉 Victory! Battle won in {self.turns_taken} turns!"
        elif self.winner is False:
            return f"💀 Defeat! Battle lost in {self.turns_taken} turns!"
        else:
            return f"🤝 Draw! Battle ended in {self.turns_taken} turns!"
    
    def get_team_summary(self, is_player: bool) -> str:
        """Get summary of a team's final state."""
        team = self.player_team_final_state if is_player else self.opponent_team_final_state
        team_name = "Player" if is_player else "Opponent"
        
        summary_lines = [f"{team_name} Team Final State:"]
        for i, pokemon in enumerate(team):
            status = "Active" if pokemon.can_battle() else "Fainted"
            summary_lines.append(f"  {i+1}. {pokemon.pokemon.name}: {status} - {pokemon.get_status_description()}")
        
        return "\n".join(summary_lines)


class BattleSimulator:
    """Simulates Pokemon battles with AI opponents."""
    
    def __init__(self):
        self.battle_engine = BattleEngine()
        self.battle_log = BattleLog()
    
    def simulate_battle(
        self,
        player_team: PokemonTeam,
        opponent_team: PokemonTeam,
        max_turns: int = 50,
        ai_difficulty: str = "medium"
    ) -> BattleResult:
        """
        Simulate a complete battle between two teams.
        
        Args:
            player_team: Player's Pokemon team
            opponent_team: Opponent's Pokemon team
            max_turns: Maximum number of turns before declaring a draw
            ai_difficulty: AI difficulty level ("easy", "medium", "hard")
            
        Returns:
            BattleResult containing the battle outcome
        """
        # Initialize battle state
        player_battle_team = [PokemonBattleState(pokemon) for pokemon in player_team.get_active_pokemon()]
        opponent_battle_team = [PokemonBattleState(pokemon) for pokemon in opponent_team.get_active_pokemon()]
        
        battle_state = BattleState(
            player_team=player_battle_team,
            opponent_team=opponent_battle_team
        )
        
        # Reset battle log
        self.battle_log = BattleLog()
        
        # Battle loop
        turn = 1
        while turn <= max_turns and not battle_state.is_battle_over():
            self.battle_log.add_event(turn, f"=== Turn {turn} ===", "turn_start")
            
            # Execute turn
            self._execute_turn(battle_state, turn, ai_difficulty)
            
            # Update battle state
            self.battle_engine.update_battle_state(battle_state)
            
            # Check for battle end
            if battle_state.is_battle_over():
                break
            
            turn += 1
        
        # Determine winner
        winner = battle_state.get_winner()
        
        # Create battle result
        result = BattleResult(
            winner=winner,
            turns_taken=turn,
            player_team_final_state=player_battle_team,
            opponent_team_final_state=opponent_battle_team,
            battle_log=self.battle_log,
            battle_summary=self.battle_engine.get_battle_summary(battle_state)
        )
        
        return result
    
    def _execute_turn(self, battle_state: BattleState, turn: int, ai_difficulty: str):
        """Execute a single battle turn."""
        # Get active Pokemon
        player_pokemon = battle_state.get_active_pokemon(True)
        opponent_pokemon = battle_state.get_active_pokemon(False)
        
        if not player_pokemon or not opponent_pokemon:
            return
        
        # Determine turn order based on speed
        player_first = self._determine_turn_order(player_pokemon, opponent_pokemon)
        
        # Execute moves in speed order
        if player_first:
            self._execute_player_move(battle_state, player_pokemon, opponent_pokemon, turn)
            if opponent_pokemon.can_battle():
                self._execute_ai_move(battle_state, opponent_pokemon, player_pokemon, turn, ai_difficulty)
        else:
            self._execute_ai_move(battle_state, opponent_pokemon, player_pokemon, turn, ai_difficulty)
            if player_pokemon.can_battle():
                self._execute_player_move(battle_state, player_pokemon, opponent_pokemon, turn)
    
    def _determine_turn_order(self, player_pokemon: PokemonBattleState, opponent_pokemon: PokemonBattleState) -> bool:
        """Determine which Pokemon goes first based on speed."""
        player_speed = player_pokemon.get_effective_stat('speed')
        opponent_speed = opponent_pokemon.get_effective_stat('speed')
        
        if player_speed > opponent_speed:
            return True
        elif opponent_speed > player_speed:
            return False
        else:
            # Speed tie - random
            return random.choice([True, False])
    
    def _execute_player_move(
        self,
        battle_state: BattleState,
        attacker: PokemonBattleState,
        defender: PokemonBattleState,
        turn: int
    ):
        """Execute a player move (simplified AI for now)."""
        # For now, use the same AI logic as opponent
        # In a real implementation, this would handle player input
        self._execute_ai_move(battle_state, attacker, defender, turn, "medium")
    
    def _execute_ai_move(
        self,
        battle_state: BattleState,
        attacker: PokemonBattleState,
        defender: PokemonBattleState,
        turn: int,
        difficulty: str
    ):
        """Execute an AI move."""
        # Select move based on difficulty
        move_name = self._select_ai_move(attacker, defender, difficulty)
        
        if not move_name or not attacker.has_move_pp(move_name):
            # Struggle if no moves available
            move_name = "Struggle"
            self.battle_log.add_event(turn, f"{attacker.pokemon.name} has no moves left!", "warning")
        
        # Check if move hits
        if not self.battle_engine.check_move_hit(move_name):
            self.battle_log.add_event(turn, f"{attacker.pokemon.name}'s {move_name} missed!", "miss")
            return
        
        # Check for critical hit
        is_critical = self.battle_engine.check_critical_hit(attacker, move_name)
        
        # Calculate and apply damage
        damage, modifiers = self.battle_engine.calculate_damage(
            attacker, defender, move_name, battle_state, is_critical
        )
        
        # Apply damage
        actual_damage = defender.apply_damage(damage)
        
        # Log the move
        critical_text = " Critical Hit!" if is_critical else ""
        effectiveness_text = self._get_effectiveness_text(modifiers['type_effectiveness'])
        
        self.battle_log.add_event(
            turn,
            f"{attacker.pokemon.name} used {move_name}!{critical_text} {effectiveness_text}",
            "move"
        )
        
        self.battle_log.add_event(
            turn,
            f"{defender.pokemon.name} took {actual_damage} damage!",
            "damage"
        )
        
        # Check if Pokemon fainted
        if defender.is_fainted():
            self.battle_log.add_event(
                turn,
                f"{defender.pokemon.name} fainted!",
                "faint"
            )
        
        # Use move PP
        if move_name != "Struggle":
            attacker.use_move(move_name)
    
    def _select_ai_move(
        self,
        attacker: PokemonBattleState,
        defender: PokemonBattleState,
        difficulty: str
    ) -> Optional[str]:
        """Select the best move for AI to use."""
        available_moves = [move for move in attacker.pokemon.moves if attacker.has_move_pp(move)]
        
        if not available_moves:
            return None
        
        if difficulty == "easy":
            # Random move selection
            return random.choice(available_moves)
        
        elif difficulty == "medium":
            # Basic strategy: prefer super effective moves
            best_moves = []
            for move in available_moves:
                # Calculate effectiveness
                damage, modifiers = self.battle_engine.calculate_damage(
                    attacker, defender, move, BattleState([attacker], [defender])
                )
                effectiveness = modifiers['type_effectiveness']
                
                if effectiveness > 1.0:
                    best_moves.append((move, effectiveness))
            
            if best_moves:
                # Choose from super effective moves
                best_moves.sort(key=lambda x: x[1], reverse=True)
                return best_moves[0][0]
            else:
                # Random move if no super effective options
                return random.choice(available_moves)
        
        elif difficulty == "hard":
            # Advanced strategy: consider multiple factors
            move_scores = []
            for move in available_moves:
                score = self._calculate_move_score(attacker, defender, move)
                move_scores.append((move, score))
            
            # Choose best scoring move
            move_scores.sort(key=lambda x: x[1], reverse=True)
            return move_scores[0][0]
        
        return random.choice(available_moves)
    
    def _calculate_move_score(
        self,
        attacker: PokemonBattleState,
        defender: PokemonBattleState,
        move_name: str
    ) -> float:
        """Calculate a score for a move to help AI decision making."""
        score = 0.0
        
        # Get move info
        move_info = self.battle_engine._get_move_info(move_name)
        
        # Base score from power
        score += move_info['power'] * 0.1
        
        # Type effectiveness bonus
        damage, modifiers = self.battle_engine.calculate_damage(
            attacker, defender, move_name, BattleState([attacker], [defender])
        )
        effectiveness = modifiers['type_effectiveness']
        
        if effectiveness > 1.0:
            score += effectiveness * 50  # Super effective bonus
        elif effectiveness < 1.0:
            score -= (1.0 - effectiveness) * 25  # Not very effective penalty
        
        # STAB bonus
        if modifiers['stab'] > 1.0:
            score += 20
        
        # Accuracy consideration
        score += move_info['accuracy'] * 0.1
        
        return score
    
    def _get_effectiveness_text(self, effectiveness: float) -> str:
        """Get text describing move effectiveness."""
        if effectiveness == 0.0:
            return "It had no effect!"
        elif effectiveness < 0.5:
            return "It's not very effective..."
        elif effectiveness < 1.0:
            return "It's not very effective."
        elif effectiveness == 1.0:
            return ""
        elif effectiveness < 2.0:
            return "It's super effective!"
        else:
            return "It's extremely effective!"
    
    def create_ai_opponent(self, difficulty: str = "medium") -> PokemonTeam:
        """Create an AI opponent team for testing."""
        # Create a simple opponent team
        opponent_team = PokemonTeam(
            name="AI Opponent",
            format="single",
            era="modern",
            max_size=6
        )
        
        # Add some basic Pokemon (simplified)
        pokemon_list = [
            ("Pikachu", 25, 50),
            ("Charmander", 4, 45),
            ("Squirtle", 7, 45),
            ("Bulbasaur", 1, 45),
            ("Rattata", 19, 40),
            ("Pidgey", 16, 42)
        ]
        
        for name, species_id, level in pokemon_list:
            pokemon = Pokemon(
                name=name,
                species_id=species_id,
                level=level,
                moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
            )
            opponent_team.add_pokemon(pokemon)
        
        return opponent_team
    
    def get_battle_statistics(self, battle_result: BattleResult) -> Dict[str, any]:
        """Get detailed battle statistics."""
        stats = {
            'winner': battle_result.winner,
            'turns_taken': battle_result.turns_taken,
            'player_pokemon_fainted': sum(1 for p in battle_result.player_team_final_state if p.is_fainted()),
            'opponent_pokemon_fainted': sum(1 for p in battle_result.opponent_team_final_state if p.is_fainted()),
            'total_events': len(battle_result.battle_log.events),
            'move_events': len([e for e in battle_result.battle_log.events if e['type'] == 'move']),
            'damage_events': len([e for e in battle_result.battle_log.events if e['type'] == 'damage']),
            'faint_events': len([e for e in battle_result.battle_log.events if e['type'] == 'faint'])
        }
        
        return stats
