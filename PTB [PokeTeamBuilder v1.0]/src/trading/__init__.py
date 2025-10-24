"""
Pokemon Trading package.
Handles different trading methods and protocols across Pokemon game eras.
"""

from .trading_methods import TradingMethod, TradingProtocol
from .gamecube_trading import GameCubeTrading
from .wii_trading import WiiTrading
from .ds_trading import DSTrading
from .switch_trading import SwitchTrading
from .trading_hub import TradingHub

__all__ = [
    'TradingMethod', 'TradingProtocol',
    'GameCubeTrading', 'WiiTrading', 'DSTrading', 'SwitchTrading',
    'TradingHub'
]

