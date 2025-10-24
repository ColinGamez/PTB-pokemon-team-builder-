#!/usr/bin/env python3
"""
Test script for core Pokemon classes.
This will verify that all our core classes work correctly.
"""

import sys
import traceback

def test_pokemon_core():
    """Test the core Pokemon classes."""
    print("Testing Pokemon core classes...")
    
    try:
        # Test imports
        from src.core.pokemon import Pokemon, ShadowPokemon, PokemonNature, PokemonStatus
        from src.core.moves import Move, MoveCategory, MoveType, MoveTarget
        from src.core.types import PokemonType, TypeEffectiveness
        from src.core.abilities import Ability, AbilityCategory, AbilityTrigger
        from src.core.stats import BaseStats, EV, IV, Stats, StatType
        
        print("✓ All imports successful")
        
        # Test BaseStats
        print("\nTesting BaseStats...")
        base_stats = BaseStats(hp=45, attack=49, defense=49, special_attack=65, special_defense=65, speed=45)
        print(f"✓ BaseStats created: {base_stats}")
        print(f"✓ Total base stats: {base_stats.get_total()}")
        print(f"✓ Average base stats: {base_stats.get_average():.1f}")
        
        # Test EV
        print("\nTesting EV...")
        evs = EV(attack=252, speed=252, hp=6)
        print(f"✓ EV created: {evs}")
        print(f"✓ Total EVs: {evs.get_total()}")
        print(f"✓ Remaining EVs: {evs.get_remaining()}")
        
        # Test IV
        print("\nTesting IV...")
        ivs = IV(attack=31, speed=31, hp=31, defense=31, special_attack=31, special_defense=31)
        print(f"✓ IV created: {ivs}")
        print(f"✓ Perfect IVs: {ivs.is_perfect()}")
        print(f"✓ Perfect count: {ivs.get_perfect_count()}")
        
        # Test Stats
        print("\nTesting Stats...")
        stats = Stats(base_stats, level=100, evs=evs, ivs=ivs)
        print(f"✓ Stats calculated: {stats}")
        print(f"✓ HP stat: {stats.get_stat(StatType.HP)}")
        print(f"✓ Attack stat: {stats.get_stat(StatType.ATTACK)}")
        print(f"✓ Speed stat: {stats.get_stat(StatType.SPEED)}")
        
        # Test Pokemon
        print("\nTesting Pokemon...")
        pokemon = Pokemon(
            name="Bulbasaur",
            species_id=1,
            level=100,
            nature=PokemonNature.MODEST,
            base_stats=base_stats,
            evs=evs,
            ivs=ivs,
            moves=["Tackle", "Growl", "Vine Whip", "Solar Beam"],
            ability="Overgrow"
        )
        print(f"✓ Pokemon created: {pokemon}")
        print(f"✓ Pokemon is legal: {pokemon.is_legal()}")
        print(f"✓ Pokemon stats: {pokemon.stats}")
        
        # Test Shadow Pokemon
        print("\nTesting Shadow Pokemon...")
        shadow_pokemon = ShadowPokemon(
            name="Shadow Bulbasaur",
            species_id=1,
            level=100,
            nature=PokemonNature.MODEST,
            base_stats=base_stats,
            evs=evs,
            ivs=ivs,
            moves=["Shadow Rush", "Shadow Blast"],
            shadow_level=3,
            purification_progress=0.3
        )
        print(f"✓ Shadow Pokemon created: {shadow_pokemon}")
        print(f"✓ Shadow level: {shadow_pokemon.shadow_level}")
        print(f"✓ Purification progress: {shadow_pokemon.purification_progress:.1%}")
        print(f"✓ Shadow moves available: {shadow_pokemon.get_shadow_moves()}")
        
        # Test Move
        print("\nTesting Move...")
        move = Move(
            name="Shadow Rush",
            move_type=MoveType.SHADOW,
            category=MoveCategory.PHYSICAL,
            power=55,
            accuracy=100,
            pp=15,
            description="A shadow move that may cause flinching",
            is_shadow_move=True,
            game_era="gamecube"
        )
        print(f"✓ Move created: {move}")
        print(f"✓ Move is shadow move: {move.is_shadow_move}")
        print(f"✓ Move is legal for GameCube: {move.is_legal_for_era('gamecube')}")
        
        # Test Type Effectiveness
        print("\nTesting Type Effectiveness...")
        effectiveness, descriptions = TypeEffectiveness.calculate_effectiveness(
            PokemonType.FIRE, [PokemonType.GRASS, PokemonType.WATER]
        )
        print(f"✓ Fire vs Grass/Water: {effectiveness}x")
        print(f"✓ Effectiveness descriptions: {descriptions}")
        
        # Test Ability
        print("\nTesting Ability...")
        ability = Ability(
            name="Shadow Boost",
            description="Increases the power of Shadow moves by 50%",
            category=AbilityCategory.MOVES,
            game_era="gamecube",
            is_gamecube_specific=True
        )
        print(f"✓ Ability created: {ability}")
        print(f"✓ Ability is GameCube specific: {ability.is_gamecube_specific}")
        print(f"✓ Ability is legal for GameCube: {ability.is_legal_for_era('gamecube')}")
        
        print("\n🎉 All core tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_error_handling():
    """Test error handling and validation."""
    print("\nTesting error handling and validation...")
    
    try:
        from src.core.pokemon import Pokemon, PokemonNature
        from src.core.stats import BaseStats, EV, IV
        
        # Test invalid BaseStats
        try:
            invalid_stats = BaseStats(hp=0, attack=300, defense=50, special_attack=60, special_defense=70, speed=80)
            print("❌ Should have failed with invalid stats")
            return False
        except ValueError:
            print("✓ Invalid BaseStats properly rejected")
        
        # Test invalid EV total
        try:
            invalid_evs = EV(attack=300, speed=300, hp=100)
            print("❌ Should have failed with invalid EV total")
            return False
        except ValueError:
            print("✓ Invalid EV total properly rejected")
        
        # Test invalid Pokemon parameters
        try:
            invalid_pokemon = Pokemon(
                name="",  # Empty name
                species_id=0,  # Invalid species ID
                level=0,  # Invalid level
                nature=PokemonNature.HARDY
            )
            print("❌ Should have failed with invalid Pokemon parameters")
            return False
        except ValueError:
            print("✓ Invalid Pokemon parameters properly rejected")
        
        print("✓ All error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Pokemon Team Builder - Core Classes Test")
    print("=" * 50)
    
    # Test core functionality
    core_success = test_pokemon_core()
    
    # Test error handling
    error_success = test_error_handling()
    
    # Overall result
    if core_success and error_success:
        print("\n🎉 All tests passed! Core classes are working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
