#!/usr/bin/env python3
"""
Pokemon Contest & Performance System
Comprehensive contest system with beauty, coolness, cuteness, smartness, and toughness categories.
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

from ..core.pokemon import Pokemon
from ..core.types import PokemonType


class ContestCategory(Enum):
    """Pokemon contest categories."""
    BEAUTY = "beauty"
    COOL = "cool"
    CUTE = "cute"
    SMART = "smart"
    TOUGH = "tough"


class ContestMoveType(Enum):
    """Types of contest moves."""
    APPEAL = "appeal"  # Increases appeal points
    JAMMING = "jamming"  # Reduces opponent's appeal
    COMBINATION = "combination"  # Works with previous move
    SPECIAL = "special"  # Special effects


class ContestCondition(Enum):
    """Pokemon contest conditions."""
    BEAUTY = "beauty"
    COOL = "cool"
    CUTE = "cute"
    SMART = "smart"
    TOUGH = "tough"


@dataclass
class ContestMove:
    """A move used in contests."""
    name: str
    category: ContestCategory
    move_type: ContestMoveType
    appeal_points: int
    jam_points: int = 0
    combination_bonus: int = 0
    special_effect: str = ""
    description: str = ""


@dataclass
class ContestPokemon:
    """A Pokemon participating in a contest."""
    pokemon: Pokemon
    condition: Dict[ContestCondition, int]  # Condition values (0-255)
    appeal_points: int = 0
    jam_points: int = 0
    combo_count: int = 0
    last_move: Optional[ContestMove] = None
    is_nervous: bool = False
    excitement_level: int = 0


@dataclass
class ContestRound:
    """A round in a Pokemon contest."""
    round_number: int
    participants: List[ContestPokemon]
    moves_used: List[Tuple[ContestPokemon, ContestMove]]
    scores: Dict[ContestPokemon, int]
    eliminated: List[ContestPokemon] = None


@dataclass
class ContestResult:
    """Result of a Pokemon contest."""
    winner: ContestPokemon
    runner_up: ContestPokemon
    third_place: ContestPokemon
    final_scores: Dict[ContestPokemon, int]
    contest_category: ContestCategory
    total_rounds: int
    highlights: List[str]


class PokemonContestSystem:
    """Advanced Pokemon contest system with multiple categories and mechanics."""
    
    def __init__(self):
        self.contest_moves: Dict[str, ContestMove] = {}
        self.contest_history: List[ContestResult] = []
        self.contest_rankings: Dict[ContestCategory, List[ContestPokemon]] = {}
        
        # Initialize contest moves database
        self._initialize_contest_moves()
        
        # Contest mechanics
        self.max_condition = 255
        self.base_appeal_points = 10
        self.nervousness_threshold = 3
        self.excitement_bonus = 5
        
    def create_contest_pokemon(self, pokemon: Pokemon, 
                             condition_values: Dict[ContestCondition, int] = None) -> ContestPokemon:
        """Create a Pokemon for contest participation."""
        
        if condition_values is None:
            # Generate random condition values
            condition_values = {
                ContestCondition.BEAUTY: random.randint(0, self.max_condition),
                ContestCondition.COOL: random.randint(0, self.max_condition),
                ContestCondition.CUTE: random.randint(0, self.max_condition),
                ContestCondition.SMART: random.randint(0, self.max_condition),
                ContestCondition.TOUGH: random.randint(0, self.max_condition)
            }
        
        return ContestPokemon(
            pokemon=pokemon,
            condition=condition_values
        )
    
    def improve_condition(self, contest_pokemon: ContestPokemon, 
                         condition: ContestCondition, amount: int) -> bool:
        """Improve a Pokemon's contest condition."""
        current_value = contest_pokemon.condition.get(condition, 0)
        new_value = min(current_value + amount, self.max_condition)
        contest_pokemon.condition[condition] = new_value
        
        return new_value > current_value
    
    def get_contest_moves(self, category: ContestCategory = None) -> List[ContestMove]:
        """Get available contest moves, optionally filtered by category."""
        moves = list(self.contest_moves.values())
        
        if category:
            moves = [move for move in moves if move.category == category]
        
        return moves
    
    def start_contest(self, participants: List[ContestPokemon], 
                     category: ContestCategory) -> ContestResult:
        """Start and run a Pokemon contest."""
        
        if len(participants) < 2:
            raise ValueError("Need at least 2 participants for a contest")
        
        print(f"\n🎭 Starting {category.value.title()} Contest!")
        print(f"Participants: {len(participants)} Pokemon")
        
        # Initialize contest
        current_participants = participants.copy()
        round_number = 1
        highlights = []
        
        # Run contest rounds until we have a winner
        while len(current_participants) > 1:
            print(f"\n--- Round {round_number} ---")
            
            # Reset round scores
            for participant in current_participants:
                participant.appeal_points = 0
                participant.jam_points = 0
                participant.combo_count = 0
                participant.last_move = None
                participant.is_nervous = False
                participant.excitement_level = 0
            
            # Each participant uses a move
            moves_used = []
            for participant in current_participants:
                move = self._select_contest_move(participant, category)
                self._use_contest_move(participant, move, current_participants)
                moves_used.append((participant, move))
                
                print(f"{participant.pokemon.name} used {move.name}!")
                print(f"  Appeal: +{move.appeal_points}, Jam: {move.jam_points}")
            
            # Calculate round scores
            round_scores = self._calculate_round_scores(current_participants, category)
            
            # Eliminate lowest scoring participant
            eliminated = self._eliminate_lowest_scorer(current_participants, round_scores)
            
            # Add round highlight
            best_performer = max(round_scores.items(), key=lambda x: x[1])[0]
            highlights.append(f"Round {round_number}: {best_performer.pokemon.name} impressed with {best_performer.appeal_points} appeal points!")
            
            round_number += 1
        
        # Determine final results
        winner = current_participants[0]
        final_scores = {participant: participant.appeal_points for participant in participants}
        
        # Sort participants by final scores for runner-up and third place
        sorted_participants = sorted(participants, key=lambda p: final_scores[p], reverse=True)
        
        result = ContestResult(
            winner=winner,
            runner_up=sorted_participants[1] if len(sorted_participants) > 1 else winner,
            third_place=sorted_participants[2] if len(sorted_participants) > 2 else winner,
            final_scores=final_scores,
            contest_category=category,
            total_rounds=round_number - 1,
            highlights=highlights
        )
        
        # Update rankings
        self._update_rankings(result)
        self.contest_history.append(result)
        
        print(f"\n🏆 Contest Winner: {winner.pokemon.name}!")
        print(f"🥈 Runner-up: {result.runner_up.pokemon.name}")
        print(f"🥉 Third Place: {result.third_place.pokemon.name}")
        
        return result
    
    def get_contest_statistics(self) -> Dict:
        """Get contest statistics and history."""
        total_contests = len(self.contest_history)
        
        # Count wins by category
        wins_by_category = {}
        for category in ContestCategory:
            wins_by_category[category.value] = 0
        
        for result in self.contest_history:
            category = result.contest_category.value
            wins_by_category[category] += 1
        
        # Most successful Pokemon
        pokemon_wins = {}
        for result in self.contest_history:
            winner_name = result.winner.pokemon.name
            pokemon_wins[winner_name] = pokemon_wins.get(winner_name, 0) + 1
        
        most_successful = max(pokemon_wins.items(), key=lambda x: x[1]) if pokemon_wins else ("None", 0)
        
        return {
            'total_contests': total_contests,
            'wins_by_category': wins_by_category,
            'most_successful_pokemon': most_successful[0],
            'most_successful_wins': most_successful[1],
            'contest_moves_available': len(self.contest_moves)
        }
    
    def _initialize_contest_moves(self):
        """Initialize the database of contest moves."""
        
        # Beauty moves
        self.contest_moves["Petal Dance"] = ContestMove(
            name="Petal Dance",
            category=ContestCategory.BEAUTY,
            move_type=ContestMoveType.APPEAL,
            appeal_points=20,
            description="A beautiful dance with flower petals"
        )
        
        self.contest_moves["Moonlight"] = ContestMove(
            name="Moonlight",
            category=ContestCategory.BEAUTY,
            move_type=ContestMoveType.APPEAL,
            appeal_points=15,
            special_effect="calming",
            description="A serene moonlight display"
        )
        
        # Cool moves
        self.contest_moves["Dragon Claw"] = ContestMove(
            name="Dragon Claw",
            category=ContestCategory.COOL,
            move_type=ContestMoveType.APPEAL,
            appeal_points=18,
            description="A powerful and cool dragon attack"
        )
        
        self.contest_moves["Ice Beam"] = ContestMove(
            name="Ice Beam",
            category=ContestCategory.COOL,
            move_type=ContestMoveType.APPEAL,
            appeal_points=16,
            description="A freezing beam of ice"
        )
        
        # Cute moves
        self.contest_moves["Charm"] = ContestMove(
            name="Charm",
            category=ContestCategory.CUTE,
            move_type=ContestMoveType.APPEAL,
            appeal_points=17,
            description="A charming and adorable move"
        )
        
        self.contest_moves["Sweet Kiss"] = ContestMove(
            name="Sweet Kiss",
            category=ContestCategory.CUTE,
            move_type=ContestMoveType.APPEAL,
            appeal_points=14,
            special_effect="confusion",
            description="A sweet and loving kiss"
        )
        
        # Smart moves
        self.contest_moves["Psychic"] = ContestMove(
            name="Psychic",
            category=ContestCategory.SMART,
            move_type=ContestMoveType.APPEAL,
            appeal_points=19,
            description="A powerful psychic attack"
        )
        
        self.contest_moves["Calm Mind"] = ContestMove(
            name="Calm Mind",
            category=ContestCategory.SMART,
            move_type=ContestMoveType.APPEAL,
            appeal_points=12,
            special_effect="focus",
            description="A focused and intelligent move"
        )
        
        # Tough moves
        self.contest_moves["Rock Slide"] = ContestMove(
            name="Rock Slide",
            category=ContestCategory.TOUGH,
            move_type=ContestMoveType.APPEAL,
            appeal_points=18,
            description="A tough and powerful rock attack"
        )
        
        self.contest_moves["Iron Tail"] = ContestMove(
            name="Iron Tail",
            category=ContestCategory.TOUGH,
            move_type=ContestMoveType.APPEAL,
            appeal_points=16,
            description="A strong iron tail attack"
        )
        
        # Jamming moves
        self.contest_moves["Screech"] = ContestMove(
            name="Screech",
            category=ContestCategory.COOL,
            move_type=ContestMoveType.JAMMING,
            appeal_points=5,
            jam_points=10,
            description="A loud and disruptive screech"
        )
        
        self.contest_moves["Confuse Ray"] = ContestMove(
            name="Confuse Ray",
            category=ContestCategory.SMART,
            move_type=ContestMoveType.JAMMING,
            appeal_points=3,
            jam_points=12,
            description="A confusing ray of light"
        )
        
        # Combination moves
        self.contest_moves["Thunder Wave"] = ContestMove(
            name="Thunder Wave",
            category=ContestCategory.COOL,
            move_type=ContestMoveType.COMBINATION,
            appeal_points=8,
            combination_bonus=15,
            description="A thunder wave that can combo"
        )
        
        self.contest_moves["Thunderbolt"] = ContestMove(
            name="Thunderbolt",
            category=ContestCategory.COOL,
            move_type=ContestMoveType.COMBINATION,
            appeal_points=10,
            combination_bonus=20,
            description="A thunderbolt that can combo"
        )
    
    def _select_contest_move(self, participant: ContestPokemon, 
                           category: ContestCategory) -> ContestMove:
        """Select a contest move for a participant."""
        
        # Get available moves for the category
        available_moves = self.get_contest_moves(category)
        
        if not available_moves:
            # Fallback to any move
            available_moves = list(self.contest_moves.values())
        
        # Consider condition and strategy
        best_moves = []
        for move in available_moves:
            score = self._calculate_move_score(participant, move, category)
            best_moves.append((move, score))
        
        # Sort by score and select from top moves
        best_moves.sort(key=lambda x: x[1], reverse=True)
        top_moves = best_moves[:3]  # Consider top 3 moves
        
        # Random selection from top moves with weighted probability
        moves, scores = zip(*top_moves)
        total_score = sum(scores)
        weights = [score / total_score for score in scores]
        
        return random.choices(moves, weights=weights)[0]
    
    def _calculate_move_score(self, participant: ContestPokemon, 
                            move: ContestMove, category: ContestCategory) -> float:
        """Calculate how good a move is for a participant."""
        score = move.appeal_points
        
        # Bonus for matching category
        if move.category == category:
            score *= 1.2
        
        # Bonus for good condition
        condition_value = participant.condition.get(ContestCondition(category.value), 0)
        condition_bonus = condition_value / self.max_condition * 10
        score += condition_bonus
        
        # Bonus for combination moves
        if move.move_type == ContestMoveType.COMBINATION and participant.last_move:
            score += move.combination_bonus
        
        # Penalty for nervousness
        if participant.is_nervous:
            score *= 0.8
        
        return score
    
    def _use_contest_move(self, participant: ContestPokemon, move: ContestMove, 
                         all_participants: List[ContestPokemon]):
        """Use a contest move and apply its effects."""
        
        # Apply appeal points
        participant.appeal_points += move.appeal_points
        
        # Apply jamming to other participants
        if move.jam_points > 0:
            for other in all_participants:
                if other != participant:
                    other.appeal_points = max(0, other.appeal_points - move.jam_points)
        
        # Handle combination moves
        if move.move_type == ContestMoveType.COMBINATION and participant.last_move:
            participant.appeal_points += move.combination_bonus
            participant.combo_count += 1
        
        # Handle special effects
        if move.special_effect == "calming":
            participant.is_nervous = False
        elif move.special_effect == "focus":
            participant.excitement_level += 1
        elif move.special_effect == "confusion":
            # Apply confusion to random opponent
            opponents = [p for p in all_participants if p != participant]
            if opponents:
                confused_opponent = random.choice(opponents)
                confused_opponent.is_nervous = True
        
        # Update last move
        participant.last_move = move
        
        # Check for nervousness
        if participant.combo_count >= self.nervousness_threshold:
            participant.is_nervous = True
        
        # Apply excitement bonus
        if participant.excitement_level > 0:
            participant.appeal_points += self.excitement_bonus * participant.excitement_level
    
    def _calculate_round_scores(self, participants: List[ContestPokemon], 
                              category: ContestCategory) -> Dict[ContestPokemon, int]:
        """Calculate final scores for a contest round."""
        scores = {}
        
        for participant in participants:
            # Base score is appeal points
            score = participant.appeal_points
            
            # Bonus for good condition in the contest category
            condition_value = participant.condition.get(ContestCondition(category.value), 0)
            condition_bonus = condition_value / self.max_condition * 20
            score += condition_bonus
            
            # Bonus for combos
            combo_bonus = participant.combo_count * 5
            score += combo_bonus
            
            # Penalty for nervousness
            if participant.is_nervous:
                score *= 0.7
            
            scores[participant] = int(score)
        
        return scores
    
    def _eliminate_lowest_scorer(self, participants: List[ContestPokemon], 
                               scores: Dict[ContestPokemon, int]) -> ContestPokemon:
        """Eliminate the participant with the lowest score."""
        lowest_scorer = min(scores.items(), key=lambda x: x[1])[0]
        participants.remove(lowest_scorer)
        return lowest_scorer
    
    def _update_rankings(self, result: ContestResult):
        """Update contest rankings based on results."""
        category = result.contest_category
        
        if category not in self.contest_rankings:
            self.contest_rankings[category] = []
        
        # Add winner to rankings if not already present
        if result.winner not in self.contest_rankings[category]:
            self.contest_rankings[category].append(result.winner)
        
        # Sort rankings by contest performance (simplified)
        # In a real system, this would track more detailed statistics
        pass

