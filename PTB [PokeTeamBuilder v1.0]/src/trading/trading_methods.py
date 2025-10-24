"""
Base trading methods and protocols for Pokemon games.
Defines the interface for different trading mechanisms.
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

from ..teambuilder.team import PokemonTeam, TeamEra
from ..core.pokemon import Pokemon


class TradingMethod(Enum):
    """Available trading methods."""
    # GameCube Era
    GAMECUBE_LINK_CABLE = "gamecube_link_cable"
    GAMECUBE_WIRELESS = "gamecube_wireless"
    
    # Wii Era
    WII_WIFI = "wii_wifi"
    WII_LOCAL = "wii_local"
    
    # DS Era
    DS_WIFI = "ds_wifi"
    DS_LOCAL = "ds_local"
    DS_GTS = "ds_gts"
    DS_WONDER_TRADE = "ds_wonder_trade"
    
    # 3DS Era
    THREEDS_WIFI = "3ds_wifi"
    THREEDS_LOCAL = "3ds_local"
    THREEDS_GTS = "3ds_gts"
    THREEDS_WONDER_TRADE = "3ds_wonder_trade"
    THREEDS_PASSPOWER = "3ds_passpower"
    
    # Switch Era
    SWITCH_LOCAL = "switch_local"
    SWITCH_ONLINE = "switch_online"
    SWITCH_GTS = "switch_gts"
    SWITCH_WONDER_TRADE = "switch_wonder_trade"
    SWITCH_HOME = "switch_home"
    SWITCH_BOT_TRADE = "switch_bot_trade"


class TradingProtocol(Enum):
    """Trading protocols and standards."""
    LINK_CABLE = "link_cable"
    WIRELESS_ADAPTER = "wireless_adapter"
    WIFI_CONNECTION = "wifi_connection"
    LOCAL_WIRELESS = "local_wireless"
    ONLINE_SERVICES = "online_services"
    BOT_INTERFACE = "bot_interface"


@dataclass
class TradingSession:
    """Represents an active trading session."""
    method: TradingMethod
    protocol: TradingProtocol
    era: TeamEra
    session_id: str
    is_active: bool = False
    participants: List[str] = None
    max_participants: int = 2
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []


@dataclass
class TradingOffer:
    """Represents a trading offer."""
    offer_id: str
    pokemon: Pokemon
    requesting_pokemon: Optional[Pokemon] = None
    requesting_item: Optional[str] = None
    level_range: Optional[Tuple[int, int]] = None
    shiny_preference: Optional[bool] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None


class BaseTradingInterface(ABC):
    """Abstract base class for trading interfaces."""
    
    def __init__(self, era: TeamEra):
        self.era = era
        self.supported_methods = self._get_supported_methods()
        self.active_sessions: Dict[str, TradingSession] = {}
    
    @abstractmethod
    def _get_supported_methods(self) -> List[TradingMethod]:
        """Get supported trading methods for this era."""
        pass
    
    @abstractmethod
    def initialize_connection(self, method: TradingMethod) -> bool:
        """Initialize connection for a trading method."""
        pass
    
    @abstractmethod
    def create_trading_session(self, method: TradingMethod) -> Optional[TradingSession]:
        """Create a new trading session."""
        pass
    
    @abstractmethod
    def join_trading_session(self, session_id: str) -> bool:
        """Join an existing trading session."""
        pass
    
    @abstractmethod
    def send_pokemon(self, session_id: str, pokemon: Pokemon) -> bool:
        """Send a Pokemon in a trading session."""
        pass
    
    @abstractmethod
    def receive_pokemon(self, session_id: str) -> Optional[Pokemon]:
        """Receive a Pokemon in a trading session."""
        pass
    
    @abstractmethod
    def close_session(self, session_id: str) -> bool:
        """Close a trading session."""
        pass
    
    def get_supported_methods(self) -> List[TradingMethod]:
        """Get list of supported trading methods."""
        return self.supported_methods.copy()
    
    def is_method_supported(self, method: TradingMethod) -> bool:
        """Check if a trading method is supported."""
        return method in self.supported_methods
    
    def get_active_sessions(self) -> Dict[str, TradingSession]:
        """Get all active trading sessions."""
        return self.active_sessions.copy()
    
    def validate_pokemon_for_trading(self, pokemon: Pokemon) -> List[str]:
        """Validate if a Pokemon can be traded in this era."""
        issues = []
        
        # Check if Pokemon exists in this era
        if self.era in [TeamEra.COLOSSEUM, TeamEra.XD_GALE]:
            if pokemon.species_id > 386:
                issues.append(f"{pokemon.name} is not available in {self.era.value}")
        
        # Check for banned Pokemon (e.g., event Pokemon, glitch Pokemon)
        if pokemon.species_id in [0, 999]:  # Example banned IDs
            issues.append(f"{pokemon.name} cannot be traded")
        
        # Check for invalid moves
        for move in pokemon.moves:
            if isinstance(move, str):
                # Skip string-based moves for now
                continue
            # Add move validation logic here
        
        return issues

