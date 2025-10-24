#!/usr/bin/env python3
"""
Test script for the Pokemon Trading System.
Demonstrates trading functionality across different game eras.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.trading import TradingHub, TradingMethod
from src.teambuilder.team import TeamEra
from src.core.pokemon import Pokemon, PokemonNature
from src.core.stats import BaseStats, EV, IV, Stats
from src.core.types import PokemonType


def test_gamecube_trading():
    """Test GameCube era trading functionality."""
    print("\n🎮 Testing GameCube Era Trading...")
    
    # Initialize trading hub for Colosseum
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.COLOSSEUM):
        print("❌ Failed to initialize Colosseum trading")
        return
    
    # Create a test Pokemon
    pikachu = Pokemon(
        name="Pikachu",
        species_id=25,
        level=50,
        nature=PokemonNature.HARDY,
        base_stats=BaseStats(hp=35, attack=55, defense=40, special_attack=50, special_defense=50, speed=90),
        evs=EV(hp=0, attack=0, defense=0, special_attack=0, special_defense=0, speed=0),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Thunderbolt", "Quick Attack", "Thunder Wave", "Iron Tail"]
    )
    
    # Test supported methods
    methods = hub.get_supported_methods()
    print(f"Supported methods: {[m.value for m in methods]}")
    
    # Test link cable connection
    if hub.initialize_connection(TradingMethod.GAMECUBE_LINK_CABLE):
        print("✅ GameCube Link Cable connected")
        
        # Create trading session
        session = hub.create_trading_session(TradingMethod.GAMECUBE_LINK_CABLE)
        if session:
            print(f"✅ Trading session created: {session.session_id}")
            
            # Test sending Pokemon
            if hub.send_pokemon(session.session_id, pikachu):
                print("✅ Pokemon sent successfully")
            
            # Close session
            hub.close_session(session.session_id)
            print("✅ Trading session closed")
    else:
        print("❌ Failed to connect GameCube Link Cable")


def test_ds_trading():
    """Test DS era trading functionality."""
    print("\n📱 Testing DS Era Trading...")
    
    # Initialize trading hub for Diamond/Pearl
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.DIAMOND_PEARL):
        print("❌ Failed to initialize Diamond/Pearl trading")
        return
    
    # Create a test Pokemon
    lucario = Pokemon(
        name="Lucario",
        species_id=448,
        level=60,
        nature=PokemonNature.ADAMANT,
        base_stats=BaseStats(hp=70, attack=110, defense=70, special_attack=115, special_defense=70, speed=90),
        evs=EV(hp=0, attack=252, defense=0, special_attack=0, special_defense=0, speed=252),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Close Combat", "Extreme Speed", "Swords Dance", "Bullet Punch"]
    )
    
    # Test supported methods
    methods = hub.get_supported_methods()
    print(f"Supported methods: {[m.value for m in methods]}")
    
    # Test WiFi connection
    if hub.initialize_connection(TradingMethod.DS_WIFI):
        print("✅ DS WiFi connected")
        
        # Add friend code
        hub.add_friend_code("1234-5678-9012")
        print("✅ Friend code added")
        
        # Test GTS
        if hub.initialize_connection(TradingMethod.DS_GTS):
            print("✅ GTS connected")
            
            # Create GTS offer
            offer_id = hub.create_gts_offer(lucario, requesting_pokemon=None, level_range=(50, 70))
            if offer_id:
                print(f"✅ GTS offer created: {offer_id}")
                
                # Search for offers
                offers = hub.search_gts_offers()
                print(f"Found {len(offers)} GTS offers")
                
                # Cancel offer
                hub.cancel_gts_offer(offer_id)
                print("✅ GTS offer cancelled")
    
    # Test Wonder Trade
    if hub.initialize_connection(TradingMethod.DS_WONDER_TRADE):
        print("✅ Wonder Trade connected")
        received = hub.wonder_trade(lucario)
        if received:
            print(f"✅ Wonder Trade completed: received {received.name}")


def test_switch_trading():
    """Test Switch era trading functionality."""
    print("\n🎯 Testing Switch Era Trading...")
    
    # Initialize trading hub for Scarlet/Violet
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.SCARLET_VIOLET):
        print("❌ Failed to initialize Scarlet/Violet trading")
        return
    
    # Create a test Pokemon
    meowscarada = Pokemon(
        name="Meowscarada",
        species_id=908,
        level=70,
        nature=PokemonNature.TIMID,
        base_stats=BaseStats(hp=76, attack=110, defense=70, special_attack=81, special_defense=70, speed=123),
        evs=EV(hp=0, attack=0, defense=0, special_attack=252, special_defense=0, speed=252),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Flower Trick", "Night Slash", "U-turn", "Play Rough"]
    )
    
    # Test supported methods
    methods = hub.get_supported_methods()
    print(f"Supported methods: {[m.value for m in methods]}")
    
    # Activate Nintendo Online
    if hub.activate_nintendo_online():
        print("✅ Nintendo Online activated")
        
        # Test online trading
        if hub.initialize_connection(TradingMethod.SWITCH_ONLINE):
            print("✅ Switch online connected")
            
            # Create trading session
            session = hub.create_trading_session(TradingMethod.SWITCH_ONLINE)
            if session:
                print(f"✅ Online trading session created: {session.session_id}")
                
                # Test sending Pokemon
                if hub.send_pokemon(session.session_id, meowscarada):
                    print("✅ Pokemon sent via online trading")
                
                # Close session
                hub.close_session(session.session_id)
                print("✅ Online trading session closed")
    
    # Test Pokemon Home
    if hub.initialize_connection(TradingMethod.SWITCH_HOME):
        print("✅ Pokemon Home connected")
        
        if hub.transfer_to_home(meowscarada):
            print("✅ Pokemon transferred to Home")
            
            home_pokemon = hub.get_home_pokemon()
            print(f"Pokemon in Home: {len(home_pokemon)}")
    
    # Test bot trading (Scarlet/Violet specific)
    if hub.initialize_connection(TradingMethod.SWITCH_BOT_TRADE):
        print("✅ Bot trading connected")
        
        received = hub.bot_trade(meowscarada, "1234-5678-9012")
        if received:
            print(f"✅ Bot trade completed: received {received.name}")


def test_cross_era_compatibility():
    """Test cross-era Pokemon compatibility."""
    print("\n🔄 Testing Cross-Era Compatibility...")
    
    # Create a Pokemon that exists in multiple eras
    charizard = Pokemon(
        name="Charizard",
        species_id=6,
        level=50,
        nature=PokemonNature.MODEST,
        base_stats=BaseStats(hp=78, attack=84, defense=78, special_attack=109, special_defense=85, speed=100),
        evs=EV(hp=0, attack=0, defense=0, special_attack=252, special_defense=0, speed=252),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Flamethrower", "Air Slash", "Solar Beam", "Focus Blast"]
    )
    
    # Test compatibility across different eras
    eras_to_test = [
        TeamEra.COLOSSEUM,
        TeamEra.DIAMOND_PEARL,
        TeamEra.BLACK_WHITE,
        TeamEra.SWORD_SHIELD,
        TeamEra.SCARLET_VIOLET
    ]
    
    for era in eras_to_test:
        hub = TradingHub()
        if hub.initialize_era(era):
            issues = hub.validate_pokemon_for_trading(charizard)
            if issues:
                print(f"❌ {era.value}: {', '.join(issues)}")
            else:
                print(f"✅ {era.value}: Compatible")


def test_trading_summary():
    """Test trading summary functionality."""
    print("\n📊 Testing Trading Summary...")
    
    hub = TradingHub()
    
    # Test multiple eras
    for era in [TeamEra.COLOSSEUM, TeamEra.DIAMOND_PEARL, TeamEra.SCARLET_VIOLET]:
        if hub.initialize_era(era):
            summary = hub.get_trading_summary()
            print(f"\n{era.value} Summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")


def main():
    """Run all trading tests."""
    print("🚀 Pokemon Trading System Test Suite")
    print("=" * 50)
    
    try:
        test_gamecube_trading()
        test_ds_trading()
        test_switch_trading()
        test_cross_era_compatibility()
        test_trading_summary()
        
        print("\n✅ All trading tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
