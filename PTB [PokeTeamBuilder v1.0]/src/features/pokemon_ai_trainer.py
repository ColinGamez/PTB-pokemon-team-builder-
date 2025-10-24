#!/usr/bin/env python3
"""
AI Pokemon Trainer System
Advanced AI that analyzes battle patterns, suggests optimal strategies, and simulates opponent behavior.
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

from ..core.pokemon import Pokemon
from ..core.types import PokemonType
from ..core.moves import Move
from ..teambuilder.team import PokemonTeam
from ..battle.simulator import BattleSimulator, BattleState


class AIStrategy(Enum):
    """AI battle strategies."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    STALL = "stall"
    SWEEP = "sweep"
    SUPPORT = "support"
    WEATHER = "weather"
    TRICK_ROOM = "trick_room"
    SETUP = "setup"
    REVENGE_KILL = "revenge_kill"


class AIPersonality(Enum):
    """AI trainer personalities."""
    CALCULATING = "calculating"  # Always chooses optimal moves
    PREDICTABLE = "predictable"  # Uses common strategies
    UNPREDICTABLE = "unpredictable"  # Random but smart
    AGGRESSIVE = "aggressive"  # Always attacks
    CAUTIOUS = "cautious"  # Prefers defensive moves
    ADAPTIVE = "adaptive"  # Changes strategy based on situation


@dataclass
class BattlePrediction:
    """Prediction of opponent's next move."""
    move_name: str
    confidence: float
    reasoning: str
    counter_strategy: str


@dataclass
class AIAnalysis:
    """AI analysis of a battle situation."""
    best_move: str
    confidence: float
    reasoning: str
    risk_assessment: str
    alternative_moves: List[str]
    team_synergy_score: float
    type_advantage_score: float


class PokemonAITrainer:
    """Advanced AI Pokemon trainer that can analyze battles and suggest strategies."""
    
    def __init__(self, personality: AIPersonality = AIPersonality.ADAPTIVE):
        self.personality = personality
        self.battle_history: List[Dict] = []
        self.opponent_patterns: Dict[str, Dict] = {}
        self.strategy_memory: Dict[str, AIStrategy] = {}
        self.learning_rate = 0.1
        
    def analyze_team(self, team: PokemonTeam) -> Dict:
        """Analyze a team and provide strategic insights."""
        analysis = {
            'overall_rating': 0.0,
            'strengths': [],
            'weaknesses': [],
            'synergy_score': 0.0,
            'coverage_score': 0.0,
            'suggestions': []
        }
        
        # Calculate team synergy
        synergy_score = self._calculate_team_synergy(team)
        analysis['synergy_score'] = synergy_score
        
        # Analyze type coverage
        coverage_score = self._analyze_type_coverage(team)
        analysis['coverage_score'] = coverage_score
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_team_strengths_weaknesses(team)
        analysis['strengths'] = strengths
        analysis['weaknesses'] = weaknesses
        
        # Calculate overall rating
        analysis['overall_rating'] = (synergy_score + coverage_score) / 2
        
        # Generate suggestions
        analysis['suggestions'] = self._generate_team_suggestions(team, analysis)
        
        return analysis
    
    def predict_opponent_move(self, opponent_team: PokemonTeam, 
                            current_pokemon: Pokemon, 
                            battle_state: BattleState) -> BattlePrediction:
        """Predict what move the opponent will use next."""
        
        # Analyze opponent's patterns
        opponent_id = f"{opponent_team.name}_{current_pokemon.pokemon.name}"
        patterns = self.opponent_patterns.get(opponent_id, {})
        
        # Consider battle state
        health_ratio = current_pokemon.current_hp / current_pokemon.pokemon.stats.hp
        weather = battle_state.weather
        terrain = battle_state.terrain
        
        # Predict based on personality and situation
        if health_ratio < 0.3:
            # Low health - likely to switch or use recovery
            predicted_move = self._predict_low_health_move(current_pokemon, patterns)
            confidence = 0.8
            reasoning = "Opponent Pokemon is low on health, likely to switch or recover"
        elif health_ratio > 0.7:
            # High health - likely to attack or set up
            predicted_move = self._predict_high_health_move(current_pokemon, patterns)
            confidence = 0.7
            reasoning = "Opponent Pokemon is healthy, likely to attack or set up"
        else:
            # Medium health - mixed strategy
            predicted_move = self._predict_balanced_move(current_pokemon, patterns)
            confidence = 0.6
            reasoning = "Opponent Pokemon has moderate health, strategy unclear"
        
        # Generate counter strategy
        counter_strategy = self._generate_counter_strategy(predicted_move, current_pokemon)
        
        return BattlePrediction(
            move_name=predicted_move,
            confidence=confidence,
            reasoning=reasoning,
            counter_strategy=counter_strategy
        )
    
    def suggest_best_move(self, your_pokemon: Pokemon, 
                         opponent_pokemon: Pokemon,
                         battle_state: BattleState) -> AIAnalysis:
        """Suggest the best move to use in the current situation."""
        
        # Calculate move effectiveness for each move
        move_scores = {}
        for move_name in your_pokemon.moves:
            score = self._calculate_move_effectiveness(
                move_name, your_pokemon, opponent_pokemon, battle_state
            )
            move_scores[move_name] = score
        
        # Find best move
        best_move = max(move_scores, key=move_scores.get)
        best_score = move_scores[best_move]
        
        # Calculate confidence based on score difference
        scores = list(move_scores.values())
        scores.sort(reverse=True)
        confidence = (scores[0] - scores[1]) / max(scores[0], 1) if len(scores) > 1 else 1.0
        
        # Generate reasoning
        reasoning = self._generate_move_reasoning(best_move, your_pokemon, opponent_pokemon)
        
        # Assess risk
        risk_assessment = self._assess_move_risk(best_move, your_pokemon, opponent_pokemon)
        
        # Get alternative moves
        alternative_moves = [move for move, score in move_scores.items() 
                           if score > best_score * 0.8 and move != best_move]
        
        # Calculate synergy and type advantage scores
        team_synergy_score = self._calculate_pokemon_synergy(your_pokemon)
        type_advantage_score = self._calculate_type_advantage(your_pokemon, opponent_pokemon)
        
        return AIAnalysis(
            best_move=best_move,
            confidence=confidence,
            reasoning=reasoning,
            risk_assessment=risk_assessment,
            alternative_moves=alternative_moves,
            team_synergy_score=team_synergy_score,
            type_advantage_score=type_advantage_score
        )
    
    def learn_from_battle(self, battle_log: List[Dict], result: str):
        """Learn from battle results to improve future predictions."""
        self.battle_history.append({
            'log': battle_log,
            'result': result,
            'timestamp': len(self.battle_history)
        })
        
        # Analyze patterns in the battle
        for entry in battle_log:
            if 'opponent_move' in entry:
                opponent_id = entry.get('opponent_id', 'unknown')
                move_used = entry['opponent_move']
                
                if opponent_id not in self.opponent_patterns:
                    self.opponent_patterns[opponent_id] = {}
                
                if move_used not in self.opponent_patterns[opponent_id]:
                    self.opponent_patterns[opponent_id][move_used] = 0
                
                self.opponent_patterns[opponent_id][move_used] += 1
    
    def generate_battle_strategy(self, your_team: PokemonTeam, 
                               opponent_team: PokemonTeam) -> Dict:
        """Generate a comprehensive battle strategy."""
        
        strategy = {
            'lead_pokemon': None,
            'switch_order': [],
            'key_moves': {},
            'winning_conditions': [],
            'counter_strategies': {},
            'risk_assessment': 'medium'
        }
        
        # Choose lead Pokemon
        strategy['lead_pokemon'] = self._choose_lead_pokemon(your_team, opponent_team)
        
        # Determine switch order
        strategy['switch_order'] = self._determine_switch_order(your_team, opponent_team)
        
        # Identify key moves for each Pokemon
        for pokemon in your_team.slots:
            if pokemon.pokemon:
                strategy['key_moves'][pokemon.pokemon.name] = self._identify_key_moves(
                    pokemon.pokemon, opponent_team
                )
        
        # Define winning conditions
        strategy['winning_conditions'] = self._identify_winning_conditions(your_team, opponent_team)
        
        # Generate counter strategies
        strategy['counter_strategies'] = self._generate_counter_strategies(your_team, opponent_team)
        
        # Assess overall risk
        strategy['risk_assessment'] = self._assess_battle_risk(your_team, opponent_team)
        
        return strategy
    
    def _calculate_team_synergy(self, team: PokemonTeam) -> float:
        """Calculate how well the team works together."""
        synergy_score = 0.0
        pokemon_count = sum(1 for slot in team.slots if slot.pokemon)
        
        if pokemon_count < 2:
            return 0.5
        
        # Check for complementary abilities and moves
        for i, slot1 in enumerate(team.slots):
            if not slot1.pokemon:
                continue
            for j, slot2 in enumerate(team.slots[i+1:], i+1):
                if not slot2.pokemon:
                    continue
                
                # Check type synergy
                type_synergy = self._calculate_type_synergy(slot1.pokemon, slot2.pokemon)
                synergy_score += type_synergy
                
                # Check move synergy
                move_synergy = self._calculate_move_synergy(slot1.pokemon, slot2.pokemon)
                synergy_score += move_synergy
        
        return min(synergy_score / (pokemon_count * (pokemon_count - 1) / 2), 1.0)
    
    def _analyze_type_coverage(self, team: PokemonTeam) -> float:
        """Analyze how well the team covers different types."""
        type_coverage = set()
        total_moves = 0
        
        for slot in team.slots:
            if slot.pokemon:
                for move in slot.pokemon.moves:
                    # This is a simplified version - in reality, you'd check move types
                    type_coverage.add("coverage_move")
                    total_moves += 1
        
        return len(type_coverage) / max(total_moves, 1)
    
    def _identify_team_strengths_weaknesses(self, team: PokemonTeam) -> Tuple[List[str], List[str]]:
        """Identify team strengths and weaknesses."""
        strengths = []
        weaknesses = []
        
        # Analyze team composition
        pokemon_types = []
        for slot in team.slots:
            if slot.pokemon:
                pokemon_types.extend(slot.pokemon.types)
        
        # Check for type diversity
        unique_types = set(pokemon_types)
        if len(unique_types) >= 4:
            strengths.append("Good type diversity")
        elif len(unique_types) <= 2:
            weaknesses.append("Limited type diversity")
        
        # Check for balanced stats
        total_stats = {'attack': 0, 'defense': 0, 'special_attack': 0, 'special_defense': 0, 'speed': 0}
        pokemon_count = 0
        
        for slot in team.slots:
            if slot.pokemon:
                stats = slot.pokemon.stats
                total_stats['attack'] += stats.attack
                total_stats['defense'] += stats.defense
                total_stats['special_attack'] += stats.special_attack
                total_stats['special_defense'] += stats.special_defense
                total_stats['speed'] += stats.speed
                pokemon_count += 1
        
        if pokemon_count > 0:
            avg_stats = {stat: value / pokemon_count for stat, value in total_stats.items()}
            
            # Check for balanced offense
            if avg_stats['attack'] > avg_stats['special_attack'] * 1.5:
                strengths.append("Strong physical offense")
            elif avg_stats['special_attack'] > avg_stats['attack'] * 1.5:
                strengths.append("Strong special offense")
            else:
                strengths.append("Balanced offense")
            
            # Check for balanced defense
            if avg_stats['defense'] > avg_stats['special_defense'] * 1.5:
                strengths.append("Strong physical defense")
            elif avg_stats['special_defense'] > avg_stats['defense'] * 1.5:
                strengths.append("Strong special defense")
            else:
                strengths.append("Balanced defense")
        
        return strengths, weaknesses
    
    def _generate_team_suggestions(self, team: PokemonTeam, analysis: Dict) -> List[str]:
        """Generate suggestions for improving the team."""
        suggestions = []
        
        if analysis['synergy_score'] < 0.6:
            suggestions.append("Consider Pokemon with better type synergy")
        
        if analysis['coverage_score'] < 0.5:
            suggestions.append("Add moves to cover more types")
        
        if len(analysis['weaknesses']) > len(analysis['strengths']):
            suggestions.append("Team has more weaknesses than strengths - consider restructuring")
        
        if analysis['overall_rating'] < 0.7:
            suggestions.append("Overall team rating is low - consider major changes")
        
        return suggestions
    
    def _predict_low_health_move(self, pokemon: Pokemon, patterns: Dict) -> str:
        """Predict move when Pokemon has low health."""
        # Common low-health moves
        recovery_moves = ["Recover", "Rest", "Synthesis", "Roost", "Soft-Boiled"]
        switch_moves = ["U-turn", "Volt Switch", "Parting Shot"]
        
        # Check patterns first
        if patterns:
            most_used = max(patterns.items(), key=lambda x: x[1])[0]
            if most_used in recovery_moves or most_used in switch_moves:
                return most_used
        
        # Default prediction
        return random.choice(recovery_moves + switch_moves)
    
    def _predict_high_health_move(self, pokemon: Pokemon, patterns: Dict) -> str:
        """Predict move when Pokemon has high health."""
        # Common high-health moves
        attack_moves = ["Attack", "Special Attack", "Status Move"]
        setup_moves = ["Swords Dance", "Nasty Plot", "Calm Mind", "Bulk Up"]
        
        if patterns:
            most_used = max(patterns.items(), key=lambda x: x[1])[0]
            return most_used
        
        return random.choice(attack_moves + setup_moves)
    
    def _predict_balanced_move(self, pokemon: Pokemon, patterns: Dict) -> str:
        """Predict move when Pokemon has balanced health."""
        if patterns:
            # Use weighted random based on patterns
            moves = list(patterns.keys())
            weights = list(patterns.values())
            return random.choices(moves, weights=weights)[0]
        
        return "Attack"  # Default prediction
    
    def _generate_counter_strategy(self, predicted_move: str, current_pokemon: Pokemon) -> str:
        """Generate a counter strategy for the predicted move."""
        if predicted_move in ["Recover", "Rest", "Synthesis"]:
            return "Use a strong attack to KO before recovery"
        elif predicted_move in ["U-turn", "Volt Switch"]:
            return "Switch to a Pokemon that resists the predicted attack"
        elif predicted_move in ["Swords Dance", "Nasty Plot"]:
            return "Use a priority move or status effect to prevent setup"
        else:
            return "Use a move that's super effective or has priority"
    
    def _calculate_move_effectiveness(self, move_name: str, your_pokemon: Pokemon, 
                                    opponent_pokemon: Pokemon, battle_state: BattleState) -> float:
        """Calculate how effective a move would be."""
        score = 50.0  # Base score
        
        # Type effectiveness (simplified)
        if move_name in ["Attack", "Special Attack"]:
            # Check type advantage
            if any(your_type in opponent_pokemon.types for your_type in your_pokemon.types):
                score += 30
            elif any(opponent_type in your_pokemon.types for opponent_type in opponent_pokemon.types):
                score -= 20
        
        # Priority moves
        if move_name in ["Quick Attack", "Extreme Speed", "Bullet Punch"]:
            score += 15
        
        # Status moves
        if move_name in ["Thunder Wave", "Will-O-Wisp", "Toxic"]:
            score += 10
        
        # Setup moves
        if move_name in ["Swords Dance", "Nasty Plot", "Calm Mind"]:
            score += 20
        
        return score
    
    def _generate_move_reasoning(self, move_name: str, your_pokemon: Pokemon, 
                               opponent_pokemon: Pokemon) -> str:
        """Generate reasoning for why a move is recommended."""
        if move_name in ["Attack", "Special Attack"]:
            return f"Use {move_name} to deal maximum damage to {opponent_pokemon.name}"
        elif move_name in ["Quick Attack", "Extreme Speed"]:
            return f"Use {move_name} for priority to outspeed {opponent_pokemon.name}"
        elif move_name in ["Thunder Wave", "Will-O-Wisp"]:
            return f"Use {move_name} to cripple {opponent_pokemon.name} with status"
        elif move_name in ["Swords Dance", "Nasty Plot"]:
            return f"Use {move_name} to set up for a sweep"
        else:
            return f"Use {move_name} as it's the most effective option"
    
    def _assess_move_risk(self, move_name: str, your_pokemon: Pokemon, 
                         opponent_pokemon: Pokemon) -> str:
        """Assess the risk of using a move."""
        if move_name in ["Swords Dance", "Nasty Plot"]:
            return "High risk - setup move leaves you vulnerable"
        elif move_name in ["Recover", "Rest"]:
            return "Medium risk - recovery move but opponent may attack"
        elif move_name in ["Quick Attack", "Extreme Speed"]:
            return "Low risk - priority move with good damage"
        else:
            return "Medium risk - standard attack move"
    
    def _calculate_pokemon_synergy(self, pokemon: Pokemon) -> float:
        """Calculate how well a Pokemon fits in the team."""
        # Simplified synergy calculation
        return 0.7  # Placeholder
    
    def _calculate_type_advantage(self, your_pokemon: Pokemon, opponent_pokemon: Pokemon) -> float:
        """Calculate type advantage between Pokemon."""
        # Simplified type advantage calculation
        return 0.8  # Placeholder
    
    def _choose_lead_pokemon(self, your_team: PokemonTeam, opponent_team: PokemonTeam) -> str:
        """Choose the best Pokemon to lead with."""
        # Simplified lead selection
        for slot in your_team.slots:
            if slot.pokemon:
                return slot.pokemon.name
        return "No Pokemon available"
    
    def _determine_switch_order(self, your_team: PokemonTeam, opponent_team: PokemonTeam) -> List[str]:
        """Determine the optimal order to switch Pokemon."""
        order = []
        for slot in your_team.slots:
            if slot.pokemon:
                order.append(slot.pokemon.name)
        return order
    
    def _identify_key_moves(self, pokemon: Pokemon, opponent_team: PokemonTeam) -> List[str]:
        """Identify the most important moves for a Pokemon."""
        return pokemon.moves[:2]  # Simplified - just return first two moves
    
    def _identify_winning_conditions(self, your_team: PokemonTeam, opponent_team: PokemonTeam) -> List[str]:
        """Identify conditions that would lead to victory."""
        return ["KO all opponent Pokemon", "Set up a sweep", "Stall out opponent"]
    
    def _generate_counter_strategies(self, your_team: PokemonTeam, opponent_team: PokemonTeam) -> Dict:
        """Generate strategies to counter the opponent team."""
        return {
            "physical_attacker": "Use defensive Pokemon",
            "special_attacker": "Use special walls",
            "setup_sweeper": "Use priority moves or status"
        }
    
    def _assess_battle_risk(self, your_team: PokemonTeam, opponent_team: PokemonTeam) -> str:
        """Assess the overall risk of the battle."""
        return "medium"  # Simplified assessment
    
    def _calculate_type_synergy(self, pokemon1: Pokemon, pokemon2: Pokemon) -> float:
        """Calculate type synergy between two Pokemon."""
        return 0.6  # Placeholder
    
    def _calculate_move_synergy(self, pokemon1: Pokemon, pokemon2: Pokemon) -> float:
        """Calculate move synergy between two Pokemon."""
        return 0.5  # Placeholder
