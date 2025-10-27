"""
Tournament System for Pokemon Team Builder.
Manages tournament brackets, seeding, elimination rounds, and leaderboards.
"""

import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

from src.teambuilder.team import PokemonTeam

logger = logging.getLogger(__name__)

class TournamentFormat(Enum):
    """Tournament format types."""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"

class TournamentStatus(Enum):
    """Tournament status types."""
    REGISTRATION = "registration"
    SEEDING = "seeding"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MatchStatus(Enum):
    """Match status types."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    DISPUTED = "disputed"

@dataclass
class Player:
    """Tournament player information."""
    id: str
    name: str
    team: Optional[PokemonTeam] = None
    rating: int = 1000
    wins: int = 0
    losses: int = 0
    matches_played: int = 0
    seed: Optional[int] = None
    
    def get_win_rate(self) -> float:
        """Calculate player's win rate."""
        if self.matches_played == 0:
            return 0.0
        return self.wins / self.matches_played
    
    def update_record(self, won: bool):
        """Update player's win/loss record."""
        if won:
            self.wins += 1
            self.rating += 25
        else:
            self.losses += 1
            self.rating = max(100, self.rating - 25)
        self.matches_played += 1

@dataclass
class Match:
    """Tournament match information."""
    id: str
    round_number: int
    player1: Player
    player2: Optional[Player]  # None for bye matches
    winner: Optional[Player] = None
    loser: Optional[Player] = None
    status: MatchStatus = MatchStatus.SCHEDULED
    score: str = "0-0"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str = ""
    
    def is_bye(self) -> bool:
        """Check if this is a bye match."""
        return self.player2 is None
    
    def complete_match(self, winner: Player, score: str = "1-0"):
        """Complete the match with a winner."""
        if self.is_bye():
            self.winner = self.player1
            self.status = MatchStatus.COMPLETED
            return
        
        self.winner = winner
        self.loser = self.player2 if winner == self.player1 else self.player1
        self.score = score
        self.status = MatchStatus.COMPLETED
        self.end_time = datetime.now()
        
        # Update player records
        winner.update_record(True)
        if self.loser:
            self.loser.update_record(False)

@dataclass
class TournamentRound:
    """Tournament round information."""
    number: int
    name: str
    matches: List[Match]
    completed: bool = False
    
    def get_completion_percentage(self) -> float:
        """Get round completion percentage."""
        if not self.matches:
            return 100.0
        completed_matches = sum(1 for match in self.matches if match.status == MatchStatus.COMPLETED)
        return (completed_matches / len(self.matches)) * 100

class Tournament:
    """Main tournament management class."""
    
    def __init__(self, name: str, format: TournamentFormat, max_players: int = 32):
        self.id = f"tournament_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.name = name
        self.format = format
        self.max_players = max_players
        self.players: List[Player] = []
        self.rounds: List[TournamentRound] = []
        self.status = TournamentStatus.REGISTRATION
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.settings = {
            "allow_late_registration": False,
            "auto_advance_byes": True,
            "match_time_limit": 30,  # minutes
            "seeding_method": "rating"  # "rating", "random", "manual"
        }
    
    def add_player(self, player: Player) -> bool:
        """Add a player to the tournament."""
        if self.status != TournamentStatus.REGISTRATION:
            logger.warning(f"Cannot add player {player.name}: registration closed")
            return False
        
        if len(self.players) >= self.max_players:
            logger.warning(f"Cannot add player {player.name}: tournament full")
            return False
        
        if any(p.id == player.id for p in self.players):
            logger.warning(f"Player {player.name} already registered")
            return False
        
        self.players.append(player)
        logger.info(f"Player {player.name} registered for tournament {self.name}")
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the tournament."""
        if self.status != TournamentStatus.REGISTRATION:
            logger.warning(f"Cannot remove player: registration closed")
            return False
        
        self.players = [p for p in self.players if p.id != player_id]
        return True
    
    def start_tournament(self) -> bool:
        """Start the tournament."""
        if len(self.players) < 2:
            logger.error("Cannot start tournament: need at least 2 players")
            return False
        
        self.status = TournamentStatus.SEEDING
        self._seed_players()
        
        self.status = TournamentStatus.IN_PROGRESS
        self.started_at = datetime.now()
        
        # Generate first round
        self._generate_next_round()
        
        logger.info(f"Tournament {self.name} started with {len(self.players)} players")
        return True
    
    def _seed_players(self):
        """Seed players based on tournament settings."""
        if self.settings["seeding_method"] == "rating":
            # Sort by rating (highest first)
            self.players.sort(key=lambda p: p.rating, reverse=True)
        elif self.settings["seeding_method"] == "random":
            # Random seeding
            random.shuffle(self.players)
        # Manual seeding would be handled externally
        
        # Assign seed numbers
        for i, player in enumerate(self.players, 1):
            player.seed = i
    
    def _generate_next_round(self):
        """Generate the next round of matches."""
        if self.format == TournamentFormat.SINGLE_ELIMINATION:
            self._generate_single_elimination_round()
        elif self.format == TournamentFormat.DOUBLE_ELIMINATION:
            self._generate_double_elimination_round()
        elif self.format == TournamentFormat.ROUND_ROBIN:
            self._generate_round_robin_round()
        elif self.format == TournamentFormat.SWISS:
            self._generate_swiss_round()
    
    def _generate_single_elimination_round(self):
        """Generate single elimination round."""
        if not self.rounds:
            # First round - pair all players
            active_players = self.players.copy()
        else:
            # Subsequent rounds - winners from previous round
            last_round = self.rounds[-1]
            active_players = [match.winner for match in last_round.matches if match.winner]
        
        if len(active_players) <= 1:
            # Tournament complete
            self._complete_tournament()
            return
        
        round_number = len(self.rounds) + 1
        round_name = self._get_round_name(round_number, len(active_players))
        
        matches = []
        
        # If odd number of players, highest seed gets bye
        if len(active_players) % 2 == 1:
            bye_player = active_players.pop(0)  # Highest remaining seed
            bye_match = Match(
                id=f"match_{round_number}_bye",
                round_number=round_number,
                player1=bye_player,
                player2=None
            )
            bye_match.complete_match(bye_player)  # Auto-complete bye
            matches.append(bye_match)
        
        # Pair remaining players
        for i in range(0, len(active_players), 2):
            match = Match(
                id=f"match_{round_number}_{i//2 + 1}",
                round_number=round_number,
                player1=active_players[i],
                player2=active_players[i + 1] if i + 1 < len(active_players) else None
            )
            matches.append(match)
        
        tournament_round = TournamentRound(
            number=round_number,
            name=round_name,
            matches=matches
        )
        
        self.rounds.append(tournament_round)
        logger.info(f"Generated {round_name} with {len(matches)} matches")
    
    def _get_round_name(self, round_number: int, players_remaining: int) -> str:
        """Get appropriate round name based on format and players."""
        if self.format == TournamentFormat.SINGLE_ELIMINATION:
            if players_remaining <= 2:
                return "Finals"
            elif players_remaining <= 4:
                return "Semifinals"
            elif players_remaining <= 8:
                return "Quarterfinals"
            elif players_remaining <= 16:
                return "Round of 16"
            else:
                return f"Round {round_number}"
        else:
            return f"Round {round_number}"
    
    def _generate_double_elimination_round(self):
        """Generate double elimination round (simplified implementation)."""
        # This would require more complex bracket management
        # For now, fall back to single elimination
        self._generate_single_elimination_round()
    
    def _generate_round_robin_round(self):
        """Generate round robin round."""
        # Round robin generates all matches upfront
        if self.rounds:
            return  # Already generated
        
        matches = []
        match_id = 1
        
        for i, player1 in enumerate(self.players):
            for j, player2 in enumerate(self.players[i+1:], i+1):
                match = Match(
                    id=f"match_rr_{match_id}",
                    round_number=1,
                    player1=player1,
                    player2=player2
                )
                matches.append(match)
                match_id += 1
        
        tournament_round = TournamentRound(
            number=1,
            name="Round Robin",
            matches=matches
        )
        
        self.rounds.append(tournament_round)
    
    def _generate_swiss_round(self):
        """Generate Swiss system round."""
        round_number = len(self.rounds) + 1
        
        if round_number == 1:
            # First round - random pairings
            players = self.players.copy()
            random.shuffle(players)
        else:
            # Subsequent rounds - pair by score/rating
            players = sorted(self.players, key=lambda p: (p.wins, p.rating), reverse=True)
        
        matches = []
        paired_players = set()
        
        for i, player1 in enumerate(players):
            if player1.id in paired_players:
                continue
            
            # Find best opponent
            for j, player2 in enumerate(players[i+1:], i+1):
                if player2.id not in paired_players:
                    match = Match(
                        id=f"match_swiss_{round_number}_{len(matches) + 1}",
                        round_number=round_number,
                        player1=player1,
                        player2=player2
                    )
                    matches.append(match)
                    paired_players.add(player1.id)
                    paired_players.add(player2.id)
                    break
        
        tournament_round = TournamentRound(
            number=round_number,
            name=f"Swiss Round {round_number}",
            matches=matches
        )
        
        self.rounds.append(tournament_round)
    
    def complete_match(self, match_id: str, winner_id: str, score: str = "1-0") -> bool:
        """Complete a match with results."""
        for tournament_round in self.rounds:
            for match in tournament_round.matches:
                if match.id == match_id:
                    if match.status != MatchStatus.SCHEDULED:
                        logger.warning(f"Match {match_id} is not schedulced")
                        return False
                    
                    winner = match.player1 if match.player1.id == winner_id else match.player2
                    if not winner:
                        logger.error(f"Winner {winner_id} not found in match {match_id}")
                        return False
                    
                    match.complete_match(winner, score)
                    logger.info(f"Match {match_id} completed: {winner.name} wins")
                    
                    # Check if round is complete
                    self._check_round_completion(tournament_round)
                    return True
        
        logger.error(f"Match {match_id} not found")
        return False
    
    def _check_round_completion(self, tournament_round: TournamentRound):
        """Check if a round is complete and advance tournament."""
        completed_matches = sum(1 for match in tournament_round.matches 
                              if match.status == MatchStatus.COMPLETED)
        
        if completed_matches == len(tournament_round.matches):
            tournament_round.completed = True
            logger.info(f"{tournament_round.name} completed")
            
            # Generate next round if tournament not complete
            if not self._is_tournament_complete():
                self._generate_next_round()
            else:
                self._complete_tournament()
    
    def _is_tournament_complete(self) -> bool:
        """Check if tournament is complete."""
        if self.format == TournamentFormat.SINGLE_ELIMINATION:
            # Complete when only one player remains undefeated
            active_players = self._get_active_players()
            return len(active_players) <= 1
        elif self.format == TournamentFormat.ROUND_ROBIN:
            # Complete when all matches played
            return all(r.completed for r in self.rounds)
        elif self.format == TournamentFormat.SWISS:
            # Complete after predetermined number of rounds
            max_rounds = min(len(self.players) - 1, 7)  # Swiss standard
            return len(self.rounds) >= max_rounds
        
        return False
    
    def _get_active_players(self) -> List[Player]:
        """Get players still active in the tournament."""
        if not self.rounds:
            return self.players
        
        # For single elimination, active players are those who haven't lost
        eliminated_players = set()
        for tournament_round in self.rounds:
            for match in tournament_round.matches:
                if match.loser:
                    eliminated_players.add(match.loser.id)
        
        return [p for p in self.players if p.id not in eliminated_players]
    
    def _complete_tournament(self):
        """Complete the tournament and determine final standings."""
        self.status = TournamentStatus.COMPLETED
        self.completed_at = datetime.now()
        
        # Determine final standings
        if self.format == TournamentFormat.SINGLE_ELIMINATION:
            active_players = self._get_active_players()
            if active_players:
                champion = active_players[0]
                logger.info(f"Tournament {self.name} completed! Champion: {champion.name}")
        
        logger.info(f"Tournament {self.name} completed")
    
    def get_standings(self) -> List[Dict[str, Any]]:
        """Get current tournament standings."""
        standings = []
        
        for i, player in enumerate(sorted(self.players, 
                                        key=lambda p: (p.wins, p.rating), 
                                        reverse=True), 1):
            standings.append({
                'position': i,
                'player': player.name,
                'seed': player.seed,
                'wins': player.wins,
                'losses': player.losses,
                'win_rate': player.get_win_rate(),
                'rating': player.rating
            })
        
        return standings
    
    def get_bracket_data(self) -> Dict[str, Any]:
        """Get tournament bracket data for visualization."""
        return {
            'tournament_id': self.id,
            'name': self.name,
            'format': self.format.value,
            'status': self.status.value,
            'players': len(self.players),
            'rounds': [
                {
                    'number': r.number,
                    'name': r.name,
                    'completed': r.completed,
                    'matches': [
                        {
                            'id': m.id,
                            'player1': m.player1.name if m.player1 else None,
                            'player2': m.player2.name if m.player2 else None,
                            'winner': m.winner.name if m.winner else None,
                            'score': m.score,
                            'status': m.status.value
                        }
                        for m in r.matches
                    ]
                }
                for r in self.rounds
            ]
        }
    
    def export_results(self) -> Dict[str, Any]:
        """Export tournament results."""
        return {
            'tournament': {
                'id': self.id,
                'name': self.name,
                'format': self.format.value,
                'status': self.status.value,
                'created_at': self.created_at.isoformat(),
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'total_players': len(self.players)
            },
            'standings': self.get_standings(),
            'bracket': self.get_bracket_data(),
            'statistics': {
                'total_matches': sum(len(r.matches) for r in self.rounds),
                'completed_matches': sum(len([m for m in r.matches if m.status == MatchStatus.COMPLETED]) for r in self.rounds),
                'average_rating': sum(p.rating for p in self.players) / len(self.players) if self.players else 0
            }
        }

class TournamentManager:
    """Manages multiple tournaments and leaderboards."""
    
    def __init__(self):
        self.tournaments: Dict[str, Tournament] = {}
        self.player_database: Dict[str, Player] = {}
        self.global_leaderboard: List[Player] = []
    
    def create_tournament(self, name: str, format: TournamentFormat, 
                         max_players: int = 32) -> Tournament:
        """Create a new tournament."""
        tournament = Tournament(name, format, max_players)
        self.tournaments[tournament.id] = tournament
        logger.info(f"Created tournament: {name} ({format.value})")
        return tournament
    
    def get_tournament(self, tournament_id: str) -> Optional[Tournament]:
        """Get tournament by ID."""
        return self.tournaments.get(tournament_id)
    
    def register_player(self, tournament_id: str, player_name: str, 
                       team: Optional[PokemonTeam] = None) -> bool:
        """Register a player for a tournament."""
        tournament = self.get_tournament(tournament_id)
        if not tournament:
            return False
        
        # Create or get existing player
        player_id = f"player_{player_name.lower().replace(' ', '_')}"
        if player_id not in self.player_database:
            player = Player(id=player_id, name=player_name, team=team)
            self.player_database[player_id] = player
        else:
            player = self.player_database[player_id]
            if team:
                player.team = team
        
        return tournament.add_player(player)
    
    def get_active_tournaments(self) -> List[Tournament]:
        """Get all active tournaments."""
        return [t for t in self.tournaments.values() 
                if t.status in [TournamentStatus.REGISTRATION, TournamentStatus.IN_PROGRESS]]
    
    def get_completed_tournaments(self) -> List[Tournament]:
        """Get all completed tournaments."""
        return [t for t in self.tournaments.values() 
                if t.status == TournamentStatus.COMPLETED]
    
    def update_global_leaderboard(self):
        """Update the global leaderboard based on all tournament results."""
        self.global_leaderboard = sorted(
            self.player_database.values(),
            key=lambda p: (p.wins, p.rating),
            reverse=True
        )
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get global leaderboard."""
        self.update_global_leaderboard()
        
        leaderboard = []
        for i, player in enumerate(self.global_leaderboard[:limit], 1):
            leaderboard.append({
                'rank': i,
                'name': player.name,
                'rating': player.rating,
                'wins': player.wins,
                'losses': player.losses,
                'tournaments': player.matches_played,
                'win_rate': player.get_win_rate()
            })
        
        return leaderboard

# Example usage
if __name__ == "__main__":
    # Create tournament manager
    manager = TournamentManager()
    
    # Create a tournament
    tournament = manager.create_tournament(
        "Pokemon Championship 2025",
        TournamentFormat.SINGLE_ELIMINATION,
        16
    )
    
    # Register players
    player_names = [
        "Ash Ketchum", "Gary Oak", "Misty", "Brock",
        "Lance", "Cynthia", "Steven Stone", "Leon"
    ]
    
    for name in player_names:
        manager.register_player(tournament.id, name)
    
    # Start tournament
    tournament.start_tournament()
    
    # Simulate some matches
    if tournament.rounds:
        first_round = tournament.rounds[0]
        for match in first_round.matches[:2]:  # Complete first 2 matches
            winner = random.choice([match.player1, match.player2])
            tournament.complete_match(match.id, winner.id)
    
    # Print bracket
    bracket_data = tournament.get_bracket_data()
    print(f"Tournament: {bracket_data['name']}")
    print(f"Status: {bracket_data['status']}")
    print(f"Players: {bracket_data['players']}")
    
    for round_data in bracket_data['rounds']:
        print(f"\n{round_data['name']}:")
        for match in round_data['matches']:
            player1 = match['player1'] or "BYE"
            player2 = match['player2'] or "BYE"
            status = match['status']
            winner = f" - Winner: {match['winner']}" if match['winner'] else ""
            print(f"  {player1} vs {player2} ({status}){winner}")