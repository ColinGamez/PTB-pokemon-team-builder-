"""
Switch era trading implementation.
Handles trading for Sword/Shield, Brilliant Diamond/Shining Pearl, Legends Arceus, and Scarlet/Violet.
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


class SwitchTrading(BaseTradingInterface):
    """Trading interface for Switch era Pokemon games."""
    
    def __init__(self, era: TeamEra):
        # Initialize attributes before calling parent constructor
        self.local_connected = False
        self.online_connected = False
        self.gts_connected = False
        self.home_connected = False
        self.bot_connected = False
        self.nintendo_online_active = False
        self.gts_offers: Dict[str, TradingOffer] = {}
        self.home_pokemon: Dict[str, Pokemon] = {}
        
        super().__init__(era)
        
    def _get_supported_methods(self) -> List[TradingMethod]:
        """Get supported trading methods for Switch era."""
        methods = []
        
        # All Switch games support local trading
        methods.append(TradingMethod.SWITCH_LOCAL)
        
        # Online trading requires Nintendo Online
        if self.nintendo_online_active:
            methods.append(TradingMethod.SWITCH_ONLINE)
        
        # GTS and Wonder Trade for most games
        if self.era in [
            TeamEra.SWORD_SHIELD, TeamEra.BRILLIANT_DIAMOND_SHINING_PEARL,
            TeamEra.SCARLET_VIOLET
        ]:
            if self.nintendo_online_active:
                methods.extend([
                    TradingMethod.SWITCH_GTS,
                    TradingMethod.SWITCH_WONDER_TRADE
                ])
        
        # Pokemon Home for compatible games
        if self.era in [
            TeamEra.SWORD_SHIELD, TeamEra.BRILLIANT_DIAMOND_SHINING_PEARL,
            TeamEra.LEGENDS_ARCEUS, TeamEra.SCARLET_VIOLET
        ]:
            methods.append(TradingMethod.SWITCH_HOME)
        
        # Bot trading for Scarlet/Violet
        if self.era == TeamEra.SCARLET_VIOLET:
            methods.append(TradingMethod.SWITCH_BOT_TRADE)
        
        return methods
    
    def initialize_connection(self, method: TradingMethod) -> bool:
        """Initialize connection for Switch trading."""
        if not self.is_method_supported(method):
            return False
        
        if method == TradingMethod.SWITCH_LOCAL:
            self.local_connected = True
            print("Switch local connection established")
            return True
        
        elif method == TradingMethod.SWITCH_ONLINE:
            if not self.nintendo_online_active:
                print("Nintendo Online subscription required for online trading")
                return False
            self.online_connected = True
            print("Switch online connection established")
            return True
        
        elif method == TradingMethod.SWITCH_GTS:
            if not self.nintendo_online_active:
                print("Nintendo Online subscription required for GTS")
                return False
            self.gts_connected = True
            print("Switch GTS connection established")
            return True
        
        elif method == TradingMethod.SWITCH_WONDER_TRADE:
            if not self.nintendo_online_active:
                print("Nintendo Online subscription required for Wonder Trade")
                return False
            self.online_connected = True
            print("Switch Wonder Trade connection established")
            return True
        
        elif method == TradingMethod.SWITCH_HOME:
            self.home_connected = True
            print("Pokemon Home connection established")
            return True
        
        elif method == TradingMethod.SWITCH_BOT_TRADE:
            self.bot_connected = True
            print("Switch bot trading connection established")
            return True
        
        return False
    
    def activate_nintendo_online(self) -> bool:
        """Activate Nintendo Online subscription."""
        self.nintendo_online_active = True
        print("Nintendo Online subscription activated")
        return True
    
    def deactivate_nintendo_online(self) -> bool:
        """Deactivate Nintendo Online subscription."""
        self.nintendo_online_active = False
        self.online_connected = False
        self.gts_connected = False
        print("Nintendo Online subscription deactivated")
        return True
    
    def create_trading_session(self, method: TradingMethod) -> Optional[TradingSession]:
        """Create a new Switch trading session."""
        if not self.is_method_supported(method):
            return None
        
        session_id = str(uuid.uuid4())
        
        if method == TradingMethod.SWITCH_LOCAL:
            protocol = TradingProtocol.LOCAL_WIRELESS
        elif method == TradingMethod.SWITCH_ONLINE:
            protocol = TradingProtocol.ONLINE_SERVICES
        elif method == TradingMethod.SWITCH_BOT_TRADE:
            protocol = TradingProtocol.BOT_INTERFACE
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
        print(f"Switch trading session created: {session_id}")
        return session
    
    def join_trading_session(self, session_id: str) -> bool:
        """Join an existing Switch trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if len(session.participants) >= session.max_participants:
            return False
        
        session.participants.append(f"Player_{len(session.participants) + 1}")
        print(f"Joined Switch trading session: {session_id}")
        return True
    
    def send_pokemon(self, session_id: str, pokemon: Pokemon) -> bool:
        """Send a Pokemon in a Switch trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if not session.is_active:
            return False
        
        # Validate Pokemon for Switch trading
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot trade {pokemon.name}: {', '.join(issues)}")
            return False
        
        print(f"Sent {pokemon.name} via Switch trading")
        return True
    
    def receive_pokemon(self, session_id: str) -> Optional[Pokemon]:
        """Receive a Pokemon in a Switch trading session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        if not session.is_active:
            return None
        
        print("Received Pokemon via Switch trading")
        return None
    
    def close_session(self, session_id: str) -> bool:
        """Close a Switch trading session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.is_active = False
        print(f"Closed Switch trading session: {session_id}")
        return True
    
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
        print(f"Created Switch GTS offer: {offer_id}")
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
        print(f"Accepted Switch GTS offer: {offer_id}")
        return True
    
    def wonder_trade(self, pokemon: Pokemon) -> Optional[Pokemon]:
        """Perform a Wonder Trade."""
        if not self.online_connected:
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
    
    def transfer_to_home(self, pokemon: Pokemon) -> bool:
        """Transfer Pokemon to Pokemon Home."""
        if not self.home_connected:
            return False
        
        # Validate Pokemon for Home transfer
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot transfer {pokemon.name} to Home: {', '.join(issues)}")
            return False
        
        pokemon_id = str(uuid.uuid4())
        self.home_pokemon[pokemon_id] = pokemon
        print(f"Transferred {pokemon.name} to Pokemon Home")
        return True
    
    def transfer_from_home(self, pokemon_id: str) -> Optional[Pokemon]:
        """Transfer Pokemon from Pokemon Home."""
        if not self.home_connected:
            return None
        
        if pokemon_id in self.home_pokemon:
            pokemon = self.home_pokemon[pokemon_id]
            del self.home_pokemon[pokemon_id]
            print(f"Transferred {pokemon.name} from Pokemon Home")
            return pokemon
        
        return None
    
    def get_home_pokemon(self) -> List[Pokemon]:
        """Get list of Pokemon in Home."""
        return list(self.home_pokemon.values())
    
    def bot_trade(self, pokemon: Pokemon, trade_code: str) -> Optional[Pokemon]:
        """Perform a bot trade (Scarlet/Violet specific)."""
        if not self.bot_connected:
            return None
        
        if self.era != TeamEra.SCARLET_VIOLET:
            print("Bot trading is only available in Scarlet/Violet")
            return None
        
        # Validate Pokemon for bot trading
        issues = self.validate_pokemon_for_trading(pokemon)
        if issues:
            print(f"Cannot bot trade {pokemon.name}: {', '.join(issues)}")
            return None
        
        # Simulate bot trade
        print(f"Bot traded {pokemon.name} with code {trade_code}")
        # In a real implementation, this would connect to a trading bot
        return None
    
    def validate_pokemon_for_trading(self, pokemon: Pokemon) -> List[str]:
        """Validate if a Pokemon can be traded in Switch era."""
        issues = super().validate_pokemon_for_trading(pokemon)
        
        # Switch-specific validation
        if self.era == TeamEra.SWORD_SHIELD:
            # Sword/Shield supports Pokemon up to Gen 8
            if pokemon.species_id > 898:
                issues.append(f"{pokemon.name} is not available in Sword/Shield")
        
        elif self.era == TeamEra.BRILLIANT_DIAMOND_SHINING_PEARL:
            # BDSP supports Pokemon up to Gen 4
            if pokemon.species_id > 493:
                issues.append(f"{pokemon.name} is not available in BDSP")
        
        elif self.era == TeamEra.LEGENDS_ARCEUS:
            # Legends Arceus has its own Pokemon list
            if pokemon.species_id > 242:  # Hisuian Pokemon
                issues.append(f"{pokemon.name} is not available in Legends Arceus")
        
        elif self.era == TeamEra.SCARLET_VIOLET:
            # Scarlet/Violet supports Pokemon up to Gen 9
            if pokemon.species_id > 1008:
                issues.append(f"{pokemon.name} is not available in Scarlet/Violet")
        
        return issues
