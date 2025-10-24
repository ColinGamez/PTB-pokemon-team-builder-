"""
Wii era trading implementation.
Handles trading for Pokemon Battle Revolution and Pokemon Ranch.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .trading_methods import (
    BaseTradingInterface, TradingMethod, TradingProtocol,
    TradingSession, TradingOffer
)
from ..teambuilder.team import TeamEra
from ..core.pokemon import Pokemon


class WiiTrading(BaseTradingInterface):
    """Trading interface for Wii era Pokemon games."""
    
    def __init__(self, era: TeamEra):
        super().__init__(era)
        self.wifi_connected = False
        self.local_connected = False
        self.friend_codes = []
        
        # PBR-specific attributes
        self.battle_records = []
        self.uploaded_teams = []
        self.rental_pokemon = []
        self.battle_passes = []
        self.current_stadium = None
        self.trainer_card = None
        
    def _get_supported_methods(self) -> List[TradingMethod]:
        """Get supported trading methods for Wii era."""
        methods = []
        
        if self.era == TeamEra.BATTLE_REVOLUTION:
            methods.extend([
                TradingMethod.WII_WIFI,
                TradingMethod.WII_LOCAL
            ])
        
        if self.era == TeamEra.POKEMON_RANCH:
            methods.extend([
                TradingMethod.WII_WIFI,
                TradingMethod.WII_LOCAL
            ])
        
        return methods
    
    def initialize_connection(self, method: TradingMethod) -> bool:
        """Initialize connection for Wii trading."""
        if not self.is_method_supported(method):
            return False
        
        if method == TradingMethod.WII_WIFI:
            # Simulate WiFi connection
            self.wifi_connected = True
            print("Wii WiFi connection established")
            return True
        
        elif method == TradingMethod.WII_LOCAL:
            # Simulate local connection
            self.local_connected = True
            print("Wii local connection established")
            return True
        
        return False
    
    def create_trading_session(self, method: TradingMethod) -> Optional[TradingSession]:
        """Create a new Wii trading session."""
        if not self.is_method_supported(method):
            return None
        
        session_id = str(uuid.uuid4())
        protocol = TradingProtocol.WIFI_CONNECTION if method == TradingMethod.WII_WIFI else TradingProtocol.LOCAL_WIRELESS
        
        session = TradingSession(
            method=method,
            protocol=protocol,
            era=self.era,
            session_id=session_id,
            is_active=True,
            max_participants=2
        )
        
        self.active_sessions[session_id] = session
        print(f"Wii trading session created: {session_id}")
        return session
    
    def join_trading_session(self, session_id: str) -> bool:
        """Join an existing Wii trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if len(session.participants) >= session.max_participants:
            return False
        
        session.participants.append(f"Player_{len(session.participants) + 1}")
        print(f"Joined Wii trading session: {session_id}")
        return True
    
    def send_pokemon(self, session_id: str, pokemon: Pokemon) -> bool:
        """Send a Pokemon in a Wii trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if not session.is_active:
            return False
        
        # Validate Pokemon for Wii trading
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot trade {pokemon.name}: {', '.join(issues)}")
            return False
        
        print(f"Sent {pokemon.name} via Wii trading")
        return True
    
    def receive_pokemon(self, session_id: str) -> Optional[Pokemon]:
        """Receive a Pokemon in a Wii trading session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        if not session.is_active:
            return None
        
        # Simulate receiving a Pokemon
        print("Received Pokemon via Wii trading")
        return None
    
    def close_session(self, session_id: str) -> bool:
        """Close a Wii trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.is_active = False
        print(f"Closed Wii trading session: {session_id}")
        return True
    
    def add_friend_code(self, friend_code: str) -> bool:
        """Add a friend code for WiFi trading."""
        if not self.wifi_connected:
            return False
        
        if friend_code not in self.friend_codes:
            self.friend_codes.append(friend_code)
            print(f"Added friend code: {friend_code}")
            return True
        
        return False
    
    def remove_friend_code(self, friend_code: str) -> bool:
        """Remove a friend code."""
        if friend_code in self.friend_codes:
            self.friend_codes.remove(friend_code)
            print(f"Removed friend code: {friend_code}")
            return True
        
        return False
    
    def get_friend_codes(self) -> List[str]:
        """Get list of registered friend codes."""
        return self.friend_codes.copy()
    
    def battle_revolution_upload_team(self, team: 'PokemonTeam') -> bool:
        """Upload team to Pokemon Battle Revolution."""
        if self.era != TeamEra.BATTLE_REVOLUTION:
            return False
        
        # Validate team for Battle Revolution
        for slot in team.slots:
            if slot.pokemon:
                issues = self.validate_pokemon_for_trading(slot.pokemon)
                if issues:
                    print(f"Cannot upload {slot.pokemon.name}: {', '.join(issues)}")
                    return False
        
        print(f"Uploaded team '{team.name}' to Battle Revolution")
        return True
    
    def pokemon_ranch_upload_pokemon(self, pokemon: Pokemon) -> bool:
        """Upload Pokemon to Pokemon Ranch."""
        if self.era != TeamEra.POKEMON_RANCH:
            return False
        
        # Validate Pokemon for Pokemon Ranch
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot upload {pokemon.name} to Pokemon Ranch: {', '.join(issues)}")
            return False
        
        print(f"Uploaded {pokemon.name} to Pokemon Ranch")
        return True
    
    def pokemon_ranch_download_pokemon(self, pokemon_id: int) -> Optional[Pokemon]:
        """Download Pokemon from Pokemon Ranch."""
        if self.era != TeamEra.POKEMON_RANCH:
            return None
        
        # Simulate downloading Pokemon from Ranch
        print(f"Downloaded Pokemon {pokemon_id} from Pokemon Ranch")
        return None
    
    def validate_pokemon_for_trading(self, pokemon: Pokemon) -> List[str]:
        """Validate if a Pokemon can be traded in Wii era."""
        issues = super().validate_pokemon_for_trading(pokemon)
        
        # Wii-specific validation
        if self.era == TeamEra.BATTLE_REVOLUTION:
            # Battle Revolution supports Pokemon from Gen 4
            if pokemon.species_id > 493:
                issues.append(f"{pokemon.name} is not available in Battle Revolution")
        
        elif self.era == TeamEra.POKEMON_RANCH:
            # Pokemon Ranch supports Pokemon from Gen 4
            if pokemon.species_id > 493:
                issues.append(f"{pokemon.name} is not available in Pokemon Ranch")
        
        return issues
    
    # PBR-specific methods
    def create_battle_pass(self, pass_name: str, team: 'PokemonTeam', stadium: str = None) -> str:
        """Create a Battle Pass for PBR."""
        if self.era != TeamEra.BATTLE_REVOLUTION:
            return None
        
        pass_id = str(uuid.uuid4())
        battle_pass = {
            'pass_id': pass_id,
            'name': pass_name,
            'team': team,
            'stadium': stadium or 'Gateway Colosseum',
            'created_at': datetime.now().isoformat(),
            'wins': 0,
            'losses': 0
        }
        
        self.battle_passes.append(battle_pass)
        print(f"Created Battle Pass '{pass_name}' for {stadium}")
        return pass_id
    
    def upload_team_to_pbr(self, team: 'PokemonTeam') -> bool:
        """Upload team to Pokemon Battle Revolution."""
        if self.era != TeamEra.BATTLE_REVOLUTION:
            return False
        
        # Validate team for PBR
        for slot in team.slots:
            if slot.pokemon:
                issues = self.validate_pokemon_for_trading(slot.pokemon)
                if issues:
                    print(f"Cannot upload {slot.pokemon.name}: {', '.join(issues)}")
                    return False
        
        team_id = str(uuid.uuid4())
        uploaded_team = {
            'team_id': team_id,
            'team': team,
            'uploaded_at': datetime.now().isoformat(),
            'battles_won': 0,
            'battles_lost': 0
        }
        
        self.uploaded_teams.append(uploaded_team)
        print(f"Uploaded team '{team.name}' to PBR")
        return True
    
    def get_rental_pokemon(self) -> List[Dict[str, Any]]:
        """Get available rental Pokemon in PBR."""
        if self.era != TeamEra.BATTLE_REVOLUTION:
            return []
        
        # Simulate rental Pokemon
        rental_pokemon = [
            {'name': 'Pikachu', 'level': 50, 'moves': ['Thunderbolt', 'Quick Attack', 'Thunder Wave', 'Iron Tail']},
            {'name': 'Charizard', 'level': 60, 'moves': ['Flamethrower', 'Air Slash', 'Solar Beam', 'Dragon Pulse']},
            {'name': 'Blastoise', 'level': 55, 'moves': ['Hydro Pump', 'Ice Beam', 'Earthquake', 'Rock Slide']},
            {'name': 'Venusaur', 'level': 55, 'moves': ['Solar Beam', 'Sludge Bomb', 'Earthquake', 'Sleep Powder']},
            {'name': 'Lucario', 'level': 60, 'moves': ['Aura Sphere', 'Close Combat', 'Extreme Speed', 'Swords Dance']},
            {'name': 'Garchomp', 'level': 70, 'moves': ['Dragon Claw', 'Earthquake', 'Stone Edge', 'Swords Dance']}
        ]
        
        return rental_pokemon
    
    def create_trainer_card(self, trainer_name: str, favorite_pokemon: Pokemon, 
                          custom_message: str = "") -> bool:
        """Create a custom trainer card for PBR."""
        if self.era != TeamEra.BATTLE_REVOLUTION:
            return False
        
        self.trainer_card = {
            'trainer_name': trainer_name,
            'favorite_pokemon': favorite_pokemon,
            'custom_message': custom_message,
            'created_at': datetime.now().isoformat(),
            'total_battles': 0,
            'wins': 0,
            'losses': 0
        }
        
        print(f"Created trainer card for {trainer_name}")
        return True
    
    def record_battle_result(self, opponent_name: str, won: bool, stadium: str = None) -> bool:
        """Record a battle result in PBR."""
        if self.era != TeamEra.BATTLE_REVOLUTION:
            return False
        
        battle_record = {
            'opponent': opponent_name,
            'won': won,
            'stadium': stadium or 'Gateway Colosseum',
            'timestamp': datetime.now().isoformat()
        }
        
        self.battle_records.append(battle_record)
        
        if self.trainer_card:
            self.trainer_card['total_battles'] += 1
            if won:
                self.trainer_card['wins'] += 1
            else:
                self.trainer_card['losses'] += 1
        
        result = "Victory" if won else "Defeat"
        print(f"Recorded battle result: {result} vs {opponent_name} at {stadium}")
        return True
    
    def get_battle_statistics(self) -> Dict[str, Any]:
        """Get battle statistics for PBR."""
        if self.era != TeamEra.BATTLE_REVOLUTION:
            return {}
        
        total_battles = len(self.battle_records)
        wins = sum(1 for record in self.battle_records if record['won'])
        losses = total_battles - wins
        win_rate = (wins / total_battles * 100) if total_battles > 0 else 0
        
        return {
            'total_battles': total_battles,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'favorite_stadium': self._get_favorite_stadium(),
            'recent_battles': self.battle_records[-5:] if self.battle_records else []
        }
    
    def _get_favorite_stadium(self) -> str:
        """Get the most used stadium."""
        if not self.battle_records:
            return "Gateway Colosseum"
        
        stadium_counts = {}
        for record in self.battle_records:
            stadium = record['stadium']
            stadium_counts[stadium] = stadium_counts.get(stadium, 0) + 1
        
        return max(stadium_counts, key=stadium_counts.get)
