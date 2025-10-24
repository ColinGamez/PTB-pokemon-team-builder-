"""
Main trading hub that coordinates all trading interfaces.
Provides a unified interface for trading across all Pokemon game eras.
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum

from .trading_methods import (
    BaseTradingInterface, TradingMethod, TradingProtocol,
    TradingSession, TradingOffer
)
from .gamecube_trading import GameCubeTrading
from .wii_trading import WiiTrading
from .ds_trading import DSTrading
from .switch_trading import SwitchTrading
from ..teambuilder.team import TeamEra
from ..core.pokemon import Pokemon


class TradingHub:
    """Main trading hub that coordinates all trading interfaces."""
    
    def __init__(self):
        self.trading_interfaces: Dict[TeamEra, BaseTradingInterface] = {}
        self.active_era: Optional[TeamEra] = None
        self.active_interface: Optional[BaseTradingInterface] = None
        
    def initialize_era(self, era: TeamEra) -> bool:
        """Initialize trading interface for a specific era."""
        if era in self.trading_interfaces:
            self.active_era = era
            self.active_interface = self.trading_interfaces[era]
            print(f"Trading hub initialized for {era.value}")
            return True
        
        # Create new trading interface for the era
        interface = self._create_trading_interface(era)
        if interface:
            self.trading_interfaces[era] = interface
            self.active_era = era
            self.active_interface = interface
            print(f"Trading hub initialized for {era.value}")
            return True
        
        return False
    
    def _create_trading_interface(self, era: TeamEra) -> Optional[BaseTradingInterface]:
        """Create appropriate trading interface for the era."""
        if era in [TeamEra.COLOSSEUM, TeamEra.XD_GALE, TeamEra.POKEMON_BOX]:
            return GameCubeTrading(era)
        
        elif era in [TeamEra.BATTLE_REVOLUTION, TeamEra.POKEMON_RANCH]:
            return WiiTrading(era)
        
        elif era in [
            TeamEra.DIAMOND_PEARL, TeamEra.PLATINUM, TeamEra.HEARTGOLD_SOULSILVER,
            TeamEra.BLACK_WHITE, TeamEra.BLACK2_WHITE2
        ]:
            return DSTrading(era)
        
        elif era in [
            TeamEra.SWORD_SHIELD, TeamEra.BRILLIANT_DIAMOND_SHINING_PEARL,
            TeamEra.LEGENDS_ARCEUS, TeamEra.SCARLET_VIOLET
        ]:
            return SwitchTrading(era)
        
        return None
    
    def get_supported_eras(self) -> List[TeamEra]:
        """Get list of supported game eras."""
        return list(self.trading_interfaces.keys())
    
    def get_supported_methods(self, era: Optional[TeamEra] = None) -> List[TradingMethod]:
        """Get supported trading methods for an era."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return []
        
        return self.trading_interfaces[target_era].get_supported_methods()
    
    def initialize_connection(self, method: TradingMethod, era: Optional[TeamEra] = None) -> bool:
        """Initialize connection for a trading method."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        return self.trading_interfaces[target_era].initialize_connection(method)
    
    def create_trading_session(self, method: TradingMethod, era: Optional[TeamEra] = None) -> Optional[TradingSession]:
        """Create a new trading session."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return None
        
        return self.trading_interfaces[target_era].create_trading_session(method)
    
    def join_trading_session(self, session_id: str, era: Optional[TeamEra] = None) -> bool:
        """Join an existing trading session."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        return self.trading_interfaces[target_era].join_trading_session(session_id)
    
    def send_pokemon(self, session_id: str, pokemon: Pokemon, era: Optional[TeamEra] = None) -> bool:
        """Send a Pokemon in a trading session."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        return self.trading_interfaces[target_era].send_pokemon(session_id, pokemon)
    
    def receive_pokemon(self, session_id: str, era: Optional[TeamEra] = None) -> Optional[Pokemon]:
        """Receive a Pokemon in a trading session."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return None
        
        return self.trading_interfaces[target_era].receive_pokemon(session_id)
    
    def close_session(self, session_id: str, era: Optional[TeamEra] = None) -> bool:
        """Close a trading session."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        return self.trading_interfaces[target_era].close_session(session_id)
    
    def get_active_sessions(self, era: Optional[TeamEra] = None) -> Dict[str, TradingSession]:
        """Get all active trading sessions for an era."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return {}
        
        return self.trading_interfaces[target_era].get_active_sessions()
    
    def validate_pokemon_for_trading(self, pokemon: Pokemon, era: Optional[TeamEra] = None) -> List[str]:
        """Validate if a Pokemon can be traded in an era."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return [f"Trading interface not available for era"]
        
        return self.trading_interfaces[target_era].validate_pokemon_for_trading(pokemon)
    
    # Era-specific methods
    def add_friend_code(self, friend_code: str, era: Optional[TeamEra] = None) -> bool:
        """Add a friend code for WiFi trading."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'add_friend_code'):
            return interface.add_friend_code(friend_code)
        
        return False
    
    def get_friend_codes(self, era: Optional[TeamEra] = None) -> List[str]:
        """Get list of registered friend codes."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return []
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'get_friend_codes'):
            return interface.get_friend_codes()
        
        return []
    
    def create_gts_offer(self, pokemon: Pokemon, requesting_pokemon: Optional[Pokemon] = None,
                        requesting_item: Optional[str] = None, level_range: Optional[tuple] = None,
                        shiny_preference: Optional[bool] = None, era: Optional[TeamEra] = None) -> Optional[str]:
        """Create a GTS offer."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return None
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'create_gts_offer'):
            return interface.create_gts_offer(
                pokemon, requesting_pokemon, requesting_item, level_range, shiny_preference
            )
        
        return None
    
    def search_gts_offers(self, pokemon_name: str = None, level_range: tuple = None, era: Optional[TeamEra] = None) -> List[TradingOffer]:
        """Search for GTS offers."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return []
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'search_gts_offers'):
            return interface.search_gts_offers(pokemon_name, level_range)
        
        return []
    
    def cancel_gts_offer(self, offer_id: str, era: Optional[TeamEra] = None) -> bool:
        """Cancel a GTS offer."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'cancel_gts_offer'):
            return interface.cancel_gts_offer(offer_id)
        
        return False
    
    def accept_gts_offer(self, offer_id: str, pokemon: Pokemon, era: Optional[TeamEra] = None) -> bool:
        """Accept a GTS offer."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'accept_gts_offer'):
            return interface.accept_gts_offer(offer_id, pokemon)
        
        return False
    
    def wonder_trade(self, pokemon: Pokemon, era: Optional[TeamEra] = None) -> Optional[Pokemon]:
        """Perform a Wonder Trade."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return None
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'wonder_trade'):
            return interface.wonder_trade(pokemon)
        
        return None
    
    # GameCube-specific methods
    def purify_shadow_pokemon(self, shadow_pokemon: 'ShadowPokemon', era: Optional[TeamEra] = None) -> bool:
        """Purify a Shadow Pokemon (Colosseum/XD specific)."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'purify_shadow_pokemon'):
            return interface.purify_shadow_pokemon(shadow_pokemon)
        
        return False
    
    # Wii/PBR-specific methods
    def create_battle_pass(self, pass_name: str, team: 'PokemonTeam', stadium: str = None, era: Optional[TeamEra] = None) -> Optional[str]:
        """Create a Battle Pass for PBR."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return None
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'create_battle_pass'):
            return interface.create_battle_pass(pass_name, team, stadium)
        
        return None
    
    def upload_team_to_pbr(self, team: 'PokemonTeam', era: Optional[TeamEra] = None) -> bool:
        """Upload team to Pokemon Battle Revolution."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'upload_team_to_pbr'):
            return interface.upload_team_to_pbr(team)
        
        return False
    
    def get_rental_pokemon(self, era: Optional[TeamEra] = None) -> List[Dict[str, Any]]:
        """Get available rental Pokemon in PBR."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return []
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'get_rental_pokemon'):
            return interface.get_rental_pokemon()
        
        return []
    
    def create_trainer_card(self, trainer_name: str, favorite_pokemon: Pokemon, 
                          custom_message: str = "", era: Optional[TeamEra] = None) -> bool:
        """Create a custom trainer card for PBR."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'create_trainer_card'):
            return interface.create_trainer_card(trainer_name, favorite_pokemon, custom_message)
        
        return False
    
    def record_battle_result(self, opponent_name: str, won: bool, stadium: str = None, era: Optional[TeamEra] = None) -> bool:
        """Record a battle result in PBR."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'record_battle_result'):
            return interface.record_battle_result(opponent_name, won, stadium)
        
        return False
    
    def get_battle_statistics(self, era: Optional[TeamEra] = None) -> Dict[str, Any]:
        """Get battle statistics for PBR."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return {}
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'get_battle_statistics'):
            return interface.get_battle_statistics()
        
        return {}
    
    # Switch-specific methods
    def activate_nintendo_online(self, era: Optional[TeamEra] = None) -> bool:
        """Activate Nintendo Online subscription."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'activate_nintendo_online'):
            return interface.activate_nintendo_online()
        
        return False
    
    def transfer_to_home(self, pokemon: Pokemon, era: Optional[TeamEra] = None) -> bool:
        """Transfer Pokemon to Pokemon Home."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return False
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'transfer_to_home'):
            return interface.transfer_to_home(pokemon)
        
        return False
    
    def get_home_pokemon(self, era: Optional[TeamEra] = None) -> List[Pokemon]:
        """Get Pokemon from Pokemon Home."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return []
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'get_home_pokemon'):
            return interface.get_home_pokemon()
        
        return []
    
    def bot_trade(self, pokemon: Pokemon, trade_code: str, era: Optional[TeamEra] = None) -> Optional[Pokemon]:
        """Perform a bot trade (Scarlet/Violet specific)."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return None
        
        interface = self.trading_interfaces[target_era]
        if hasattr(interface, 'bot_trade'):
            return interface.bot_trade(pokemon, trade_code)
        
        return None
    
    def get_trading_summary(self, era: Optional[TeamEra] = None) -> Dict[str, Any]:
        """Get comprehensive trading summary for an era."""
        target_era = era or self.active_era
        if not target_era or target_era not in self.trading_interfaces:
            return {}
        
        interface = self.trading_interfaces[target_era]
        summary = {
            'era': target_era.value,
            'supported_methods': [method.value for method in interface.get_supported_methods()],
            'active_sessions': len(interface.get_active_sessions()),
            'interface_type': interface.__class__.__name__
        }
        
        # Add era-specific information
        if hasattr(interface, 'friend_codes'):
            summary['friend_codes'] = len(interface.friend_codes)
        
        if hasattr(interface, 'gts_offers'):
            summary['gts_offers'] = len(interface.gts_offers)
        
        if hasattr(interface, 'home_pokemon'):
            summary['home_pokemon'] = len(interface.home_pokemon)
        
        if hasattr(interface, 'nintendo_online_active'):
            summary['nintendo_online'] = interface.nintendo_online_active
        
        return summary
