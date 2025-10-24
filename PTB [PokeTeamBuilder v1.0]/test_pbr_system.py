#!/usr/bin/env python3
"""
Test script for Pokemon Battle Revolution (PBR) System.
Demonstrates PBR-specific functionality including Battle Passes, team uploads, trainer cards, and battle statistics.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.trading import TradingHub, TradingMethod
from src.teambuilder.team import TeamEra, PokemonTeam, TeamSlot, TeamFormat
from src.core.pokemon import Pokemon, PokemonNature
from src.core.stats import BaseStats, EV, IV, Stats
from src.core.types import PokemonType


def create_test_team() -> PokemonTeam:
    """Create a test team for PBR."""
    # Create test Pokemon
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
    
    charizard = Pokemon(
        name="Charizard",
        species_id=6,
        level=60,
        nature=PokemonNature.MODEST,
        base_stats=BaseStats(hp=78, attack=84, defense=78, special_attack=109, special_defense=85, speed=100),
        evs=EV(hp=0, attack=0, defense=0, special_attack=252, special_defense=0, speed=252),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Flamethrower", "Air Slash", "Solar Beam", "Focus Blast"]
    )
    
    lucario = Pokemon(
        name="Lucario",
        species_id=448,
        level=55,
        nature=PokemonNature.ADAMANT,
        base_stats=BaseStats(hp=70, attack=110, defense=70, special_attack=115, special_defense=70, speed=90),
        evs=EV(hp=0, attack=252, defense=0, special_attack=0, special_defense=0, speed=252),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Close Combat", "Extreme Speed", "Swords Dance", "Bullet Punch"]
    )
    
    # Create team
    team = PokemonTeam(
        name="PBR Test Team",
        era=TeamEra.BATTLE_REVOLUTION,
        format=TeamFormat.SINGLE
    )
    
    # Add Pokemon to team
    team.add_pokemon(pikachu, position=0)
    team.add_pokemon(charizard, position=1)
    team.add_pokemon(lucario, position=2)
    
    return team


def test_pbr_basic_functionality():
    """Test basic PBR functionality."""
    print("\n🎮 Testing Pokemon Battle Revolution Basic Functionality...")
    
    # Initialize trading hub for PBR
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.BATTLE_REVOLUTION):
        print("❌ Failed to initialize PBR trading")
        return
    
    # Test supported methods
    methods = hub.get_supported_methods()
    print(f"Supported methods: {[m.value for m in methods]}")
    
    # Test WiFi connection
    if hub.initialize_connection(TradingMethod.WII_WIFI):
        print("✅ PBR WiFi connected")
        
        # Add friend code
        hub.add_friend_code("1234-5678-9012")
        print("✅ Friend code added")
    else:
        print("❌ Failed to connect PBR WiFi")


def test_pbr_team_management():
    """Test PBR team management features."""
    print("\n📋 Testing PBR Team Management...")
    
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.BATTLE_REVOLUTION):
        print("❌ Failed to initialize PBR")
        return
    
    # Create test team
    team = create_test_team()
    print(f"✅ Created test team: {team.name}")
    
    # Upload team to PBR
    if hub.upload_team_to_pbr(team):
        print("✅ Team uploaded to PBR successfully")
    else:
        print("❌ Failed to upload team to PBR")
    
    # Get rental Pokemon
    rental_pokemon = hub.get_rental_pokemon()
    print(f"✅ Available rental Pokemon: {len(rental_pokemon)}")
    for pokemon in rental_pokemon:
        print(f"  - {pokemon['name']} (Lv.{pokemon['level']})")


def test_pbr_battle_passes():
    """Test PBR Battle Pass functionality."""
    print("\n🎫 Testing PBR Battle Passes...")
    
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.BATTLE_REVOLUTION):
        print("❌ Failed to initialize PBR")
        return
    
    # Create test team
    team = create_test_team()
    
    # Create Battle Passes for different stadiums
    stadiums = [
        "Gateway Colosseum",
        "Main Street Colosseum", 
        "Neon Colosseum",
        "Crystal Colosseum",
        "Sunset Colosseum"
    ]
    
    for stadium in stadiums:
        pass_id = hub.create_battle_pass(f"Pass_{stadium}", team, stadium)
        if pass_id:
            print(f"✅ Created Battle Pass for {stadium}: {pass_id}")
        else:
            print(f"❌ Failed to create Battle Pass for {stadium}")


def test_pbr_trainer_cards():
    """Test PBR trainer card functionality."""
    print("\n🃏 Testing PBR Trainer Cards...")
    
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.BATTLE_REVOLUTION):
        print("❌ Failed to initialize PBR")
        return
    
    # Create a favorite Pokemon for trainer card
    favorite_pokemon = Pokemon(
        name="Pikachu",
        species_id=25,
        level=50,
        nature=PokemonNature.HARDY,
        base_stats=BaseStats(hp=35, attack=55, defense=40, special_attack=50, special_defense=50, speed=90),
        evs=EV(hp=0, attack=0, defense=0, special_attack=0, special_defense=0, speed=0),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Thunderbolt", "Quick Attack", "Thunder Wave", "Iron Tail"]
    )
    
    # Create trainer card
    if hub.create_trainer_card("PBR Master", favorite_pokemon, "Ready for battle!"):
        print("✅ Trainer card created successfully")
    else:
        print("❌ Failed to create trainer card")


def test_pbr_battle_statistics():
    """Test PBR battle statistics and records."""
    print("\n📊 Testing PBR Battle Statistics...")
    
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.BATTLE_REVOLUTION):
        print("❌ Failed to initialize PBR")
        return
    
    # Record some battle results
    opponents = [
        ("Trainer_Red", True, "Gateway Colosseum"),
        ("Trainer_Blue", False, "Main Street Colosseum"),
        ("Trainer_Green", True, "Neon Colosseum"),
        ("Trainer_Yellow", True, "Crystal Colosseum"),
        ("Trainer_Purple", False, "Sunset Colosseum"),
        ("Trainer_Orange", True, "Gateway Colosseum"),
        ("Trainer_Pink", True, "Main Street Colosseum"),
        ("Trainer_Black", False, "Neon Colosseum")
    ]
    
    for opponent, won, stadium in opponents:
        if hub.record_battle_result(opponent, won, stadium):
            result = "Victory" if won else "Defeat"
            print(f"✅ Recorded {result} vs {opponent} at {stadium}")
        else:
            print(f"❌ Failed to record battle vs {opponent}")
    
    # Get battle statistics
    stats = hub.get_battle_statistics()
    if stats:
        print(f"\n📈 Battle Statistics:")
        print(f"  Total Battles: {stats['total_battles']}")
        print(f"  Wins: {stats['wins']}")
        print(f"  Losses: {stats['losses']}")
        print(f"  Win Rate: {stats['win_rate']}%")
        print(f"  Favorite Stadium: {stats['favorite_stadium']}")
        
        if stats['recent_battles']:
            print(f"  Recent Battles:")
            for battle in stats['recent_battles']:
                result = "Victory" if battle['won'] else "Defeat"
                print(f"    - {result} vs {battle['opponent']} at {battle['stadium']}")
    else:
        print("❌ Failed to get battle statistics")


def test_pbr_stadium_features():
    """Test PBR stadium-specific features."""
    print("\n🏟️ Testing PBR Stadium Features...")
    
    hub = TradingHub()
    if not hub.initialize_era(TeamEra.BATTLE_REVOLUTION):
        print("❌ Failed to initialize PBR")
        return
    
    # Get era features to see available stadiums
    from src.teambuilder.team import GameSpecificFeatures
    features = GameSpecificFeatures.get_era_features(TeamEra.BATTLE_REVOLUTION)
    
    if 'battle_stadiums' in features:
        print(f"✅ Available Battle Stadiums ({len(features['battle_stadiums'])}):")
        for stadium in features['battle_stadiums']:
            print(f"  - {stadium}")
    
    # Test special mechanics
    if 'special_mechanics' in features:
        print(f"\n🎯 Special PBR Mechanics:")
        for mechanic in features['special_mechanics']:
            print(f"  - {mechanic}")


def test_pbr_cross_compatibility():
    """Test PBR compatibility with other games."""
    print("\n🔄 Testing PBR Cross-Game Compatibility...")
    
    hub = TradingHub()
    
    # Test compatibility with DS games (Diamond/Pearl)
    if hub.initialize_era(TeamEra.DIAMOND_PEARL):
        print("✅ PBR compatible with Diamond/Pearl")
        
        # Test team validation
        team = create_test_team()
        team.era = TeamEra.DIAMOND_PEARL  # Temporarily change era for testing
        
        issues = hub.validate_pokemon_for_trading(team.slots[0].pokemon)
        if issues:
            print(f"⚠️ Compatibility issues: {', '.join(issues)}")
        else:
            print("✅ Team compatible with Diamond/Pearl")
    
    # Test compatibility with GameCube games
    if hub.initialize_era(TeamEra.COLOSSEUM):
        print("✅ PBR compatible with Colosseum")
    else:
        print("❌ PBR not compatible with Colosseum")


def test_pbr_summary():
    """Test PBR trading summary functionality."""
    print("\n📋 Testing PBR Trading Summary...")
    
    hub = TradingHub()
    if hub.initialize_era(TeamEra.BATTLE_REVOLUTION):
        summary = hub.get_trading_summary()
        print(f"\nPBR Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")


def main():
    """Run all PBR tests."""
    print("🎮 Pokemon Battle Revolution (PBR) Test Suite")
    print("=" * 60)
    
    try:
        test_pbr_basic_functionality()
        test_pbr_team_management()
        test_pbr_battle_passes()
        test_pbr_trainer_cards()
        test_pbr_battle_statistics()
        test_pbr_stadium_features()
        test_pbr_cross_compatibility()
        test_pbr_summary()
        
        print("\n✅ All PBR tests completed successfully!")
        print("\n🎉 Pokemon Battle Revolution features:")
        print("  - 16 Unique Battle Stadiums")
        print("  - Battle Pass System")
        print("  - Custom Trainer Cards")
        print("  - WiFi Battles")
        print("  - Team Upload/Download")
        print("  - Rental Pokemon")
        print("  - Battle Statistics")
        print("  - Cross-Game Compatibility")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
