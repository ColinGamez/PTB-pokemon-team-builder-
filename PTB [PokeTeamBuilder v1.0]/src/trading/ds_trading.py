"""
DS era trading implementation.
Handles trading for Diamond/Pearl, Platinum, HeartGold/SoulSilver, Black/White, and Black2/White2.
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


class DSTrading(BaseTradingInterface):
    """Trading interface for DS era Pokemon games."""
    
    def __init__(self, era: TeamEra):
        super().__init__(era)
        self.wifi_connected = False
        self.local_connected = False
        self.gts_connected = False
        self.friend_codes = []
        self.gts_offers: Dict[str, TradingOffer] = {}
        
    def _get_supported_methods(self) -> List[TradingMethod]:
        """Get supported trading methods for DS era."""
        methods = []
        
        # All DS games support local and WiFi trading
        methods.extend([
            TradingMethod.DS_LOCAL,
            TradingMethod.DS_WIFI
        ])
        
        # GTS and Wonder Trade for Gen 4 and 5
        if self.era in [
            TeamEra.DIAMOND_PEARL, TeamEra.PLATINUM,
            TeamEra.HEARTGOLD_SOULSILVER, TeamEra.BLACK_WHITE, TeamEra.BLACK2_WHITE2
        ]:
            methods.extend([
                TradingMethod.DS_GTS,
                TradingMethod.DS_WONDER_TRADE
            ])
        
        return methods
    
    def initialize_connection(self, method: TradingMethod) -> bool:
        """Initialize connection for DS trading."""
        if not self.is_method_supported(method):
            return False
        
        if method == TradingMethod.DS_WIFI:
            self.wifi_connected = True
            print("DS WiFi connection established")
            return True
        
        elif method == TradingMethod.DS_LOCAL:
            self.local_connected = True
            print("DS local connection established")
            return True
        
        elif method == TradingMethod.DS_GTS:
            self.gts_connected = True
            print("DS GTS connection established")
            return True
        
        elif method == TradingMethod.DS_WONDER_TRADE:
            # Wonder Trade uses WiFi connection
            if not self.wifi_connected:
                self.wifi_connected = True
            print("DS Wonder Trade connection established")
            return True
        
        return False
    
    def create_trading_session(self, method: TradingMethod) -> Optional[TradingSession]:
        """Create a new DS trading session."""
        if not self.is_method_supported(method):
            return None
        
        session_id = str(uuid.uuid4())
        
        if method == TradingMethod.DS_WIFI:
            protocol = TradingProtocol.WIFI_CONNECTION
        elif method == TradingMethod.DS_LOCAL:
            protocol = TradingProtocol.LOCAL_WIRELESS
        else:
            protocol = TradingProtocol.ONLINE_SERVICES
        
        session = TradingSession(
            method=method,
            protocol=protocol,
            era=self.era,
            session_id=session_id,
            is_active=True,
            max_participants=2
        )
        
        self.active_sessions[session_id] = session
        print(f"DS trading session created: {session_id}")
        return session
    
    def join_trading_session(self, session_id: str) -> bool:
        """Join an existing DS trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if len(session.participants) >= session.max_participants:
            return False
        
        session.participants.append(f"Player_{len(session.participants) + 1}")
        print(f"Joined DS trading session: {session_id}")
        return True
    
    def send_pokemon(self, session_id: str, pokemon: Pokemon) -> bool:
        """Send a Pokemon in a DS trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if not session.is_active:
            return False
        
        # Validate Pokemon for DS trading
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot trade {pokemon.name}: {', '.join(issues)}")
            return False
        
        print(f"Sent {pokemon.name} via DS trading")
        return True
    
    def receive_pokemon(self, session_id: str) -> Optional[Pokemon]:
        """Receive a Pokemon in a DS trading session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        if not session.is_active:
            return None
        
        print("Received Pokemon via DS trading")
        return None
    
    def close_session(self, session_id: str) -> bool:
        """Close a DS trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.is_active = False
        print(f"Closed DS trading session: {session_id}")
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
    
    def create_gts_offer(self, pokemon: Pokemon, requesting_pokemon: Optional[Pokemon] = None,
                        requesting_item: Optional[str] = None, level_range: Optional[tuple] = None,
                        shiny_preference: Optional[bool] = None) -> Optional[str]:
        """Create a GTS offer."""
        if not self.gts_connected:
            return None
        
        # Validate Pokemon for GTS
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot create GTS offer for {pokemon.name}: {', '.join(issues)}")
            return None
        
        offer_id = str(uuid.uuid4())
        offer = TradingOffer(
            offer_id=offer_id,
            pokemon=pokemon,
            requesting_pokemon=requesting_pokemon,
            requesting_item=requesting_item,
            level_range=level_range,
            shiny_preference=shiny_preference,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=7)).isoformat()
        )
        
        self.gts_offers[offer_id] = offer
        print(f"Created GTS offer: {offer_id}")
        return offer_id
    
    def search_gts_offers(self, pokemon_name: str = None, level_range: tuple = None) -> List[TradingOffer]:
        """Search for GTS offers."""
        if not self.gts_connected:
            return []
        
        results = []
        for offer in self.gts_offers.values():
            if pokemon_name and offer.requesting_pokemon:
                if offer.requesting_pokemon.name.lower() != pokemon_name.lower():
                    continue
            
            if level_range and offer.level_range:
                if not (level_range[0] <= offer.level_range[1] and level_range[1] >= offer.level_range[0]):
                    continue
            
            results.append(offer)
        
        return results
    
    def accept_gts_offer(self, offer_id: str, offering_pokemon: Pokemon) -> bool:
        """Accept a GTS offer."""
        if offer_id not in self.gts_offers:
            return False
        
        offer = self.gts_offers[offer_id]
        
        # Validate offering Pokemon
        issues = self.validate_pokemon_for_trading(offering_pokemon)
        if issues:
            print(f"Cannot accept GTS offer with {offering_pokemon.name}: {', '.join(issues)}")
            return False
        
        # Check if offering Pokemon matches request
        if offer.requesting_pokemon:
            if offering_pokemon.species_id != offer.requesting_pokemon.species_id:
                print(f"Offering Pokemon does not match GTS request")
                return False
        
        if offer.level_range:
            if not (offer.level_range[0] <= offering_pokemon.level <= offer.level_range[1]):
                print(f"Offering Pokemon level does not match GTS request")
                return False
        
        if offer.shiny_preference is not None:
            if offering_pokemon.is_shiny != offer.shiny_preference:
                print(f"Offering Pokemon shiny status does not match GTS request")
                return False
        
        # Complete the trade
        del self.gts_offers[offer_id]
        print(f"Accepted GTS offer: {offer_id}")
        return True
    
    def cancel_gts_offer(self, offer_id: str) -> bool:
        """Cancel a GTS offer."""
        if offer_id in self.gts_offers:
            del self.gts_offers[offer_id]
            print(f"Cancelled GTS offer: {offer_id}")
            return True
        
        return False
    
    def wonder_trade(self, pokemon: Pokemon) -> Optional[Pokemon]:
        """Perform a Wonder Trade."""
        if not self.wifi_connected:
            return None
        
        # Validate Pokemon for Wonder Trade
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot Wonder Trade {pokemon.name}: {', '.join(issues)}")
            return None
        
        # Simulate Wonder Trade
        print(f"Wonder Traded {pokemon.name}")
        # In a real implementation, this would match with another player's Pokemon
        return None
    
    def validate_pokemon_for_trading(self, pokemon: Pokemon) -> List[str]:
        """Validate if a Pokemon can be traded in DS era."""
        issues = super().validate_pokemon_for_trading(pokemon)
        
        # DS-specific validation
        if self.era in [TeamEra.DIAMOND_PEARL, TeamEra.PLATINUM, TeamEra.HEARTGOLD_SOULSILVER]:
            # Gen 4 games support Pokemon up to Gen 4
            if pokemon.species_id > 493:
                issues.append(f"{pokemon.name} is not available in {self.era.value}")
        
        elif self.era in [TeamEra.BLACK_WHITE, TeamEra.BLACK2_WHITE2]:
            # Gen 5 games support Pokemon up to Gen 5
            if pokemon.species_id > 649:
                issues.append(f"{pokemon.name} is not available in {self.era.value}")
        
        return issues

