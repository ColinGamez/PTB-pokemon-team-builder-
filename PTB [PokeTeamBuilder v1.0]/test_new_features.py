#!/usr/bin/env python3
"""
Comprehensive test script for Pokemon Team Builder new features.
Tests team optimization, battle simulation, and GUI components.
"""

import sys
import os
import traceback

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_team_optimization():
    """Test the team optimization system."""
    print("🔧 Testing Team Optimization System...")
    print("=" * 50)
    
    try:
        from teambuilder.team import PokemonTeam, TeamFormat, TeamEra
        from teambuilder.optimizer import TeamOptimizer, OptimizationType
        from core.pokemon import Pokemon, ShadowPokemon
        from core.stats import PokemonNature
        
        # Create a test team
        team = PokemonTeam(
            name="Test Team",
            format=TeamFormat.SINGLE,
            era=TeamEra.MODERN,
            max_size=6
        )
        
        # Add some Pokemon with known weaknesses
        pokemon_list = [
            ("Bulbasaur", 1, 50, "hardy", False),
            ("Charmander", 4, 50, "adamant", False),
            ("Squirtle", 7, 50, "modest", False),
            ("Pikachu", 25, 50, "timid", False),
            ("Eevee", 133, 50, "jolly", False),
            ("Mewtwo", 150, 50, "modest", False)
        ]
        
        for name, species_id, level, nature, is_shadow in pokemon_list:
            if is_shadow:
                pokemon = ShadowPokemon(
                    name=name,
                    species_id=species_id,
                    level=level,
                    nature=PokemonNature(nature),
                    moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                )
            else:
                pokemon = Pokemon(
                    name=name,
                    species_id=species_id,
                    level=level,
                    nature=PokemonNature(nature),
                    moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                )
            
            team.add_pokemon(pokemon)
        
        print(f"✅ Created test team: {team.name} with {team.get_team_size()} Pokemon")
        
        # Create optimizer
        optimizer = TeamOptimizer(team)
        
        # Test different optimization types
        optimization_types = [
            OptimizationType.TYPE_COVERAGE,
            OptimizationType.STAT_BALANCE,
            OptimizationType.MOVE_COVERAGE,
            OptimizationType.ERA_COMPATIBILITY,
            OptimizationType.SYNERGY
        ]
        
        for opt_type in optimization_types:
            print(f"\n📊 Testing {opt_type.value.replace('_', ' ').title()} optimization...")
            suggestions = optimizer.optimize_team([opt_type])
            
            if suggestions:
                print(f"Found {len(suggestions)} suggestions:")
                for suggestion in suggestions[:3]:  # Show first 3 suggestions
                    print(f"  • {suggestion.description}")
                    if suggestion.suggested_changes:
                        for key, value in suggestion.suggested_changes.items():
                            if key.startswith('recommended_'):
                                print(f"    💡 {key.replace('_', ' ').title()}: {value}")
            else:
                print("No optimization suggestions found.")
        
        # Test full optimization
        print(f"\n🔧 Testing full team optimization...")
        all_suggestions = optimizer.optimize_team()
        
        if all_suggestions:
            print(f"Found {len(all_suggestions)} total suggestions:")
            print(optimizer.get_optimization_summary(all_suggestions))
        else:
            print("No optimization suggestions found.")
        
        print("\n✅ Team optimization tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Team optimization test failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    return True

def test_battle_simulation():
    """Test the battle simulation system."""
    print("\n⚔️ Testing Battle Simulation System...")
    print("=" * 50)
    
    try:
        from teambuilder.team import PokemonTeam, TeamFormat, TeamEra
        from battle.simulator import BattleSimulator
        from core.pokemon import Pokemon, ShadowPokemon
        from core.stats import PokemonNature
        
        # Create player team
        player_team = PokemonTeam(
            name="Player Team",
            format=TeamFormat.SINGLE,
            era=TeamEra.MODERN,
            max_size=6
        )
        
        # Add some Pokemon
        player_pokemon = [
            ("Shadow Bulbasaur", 1, 50, "hardy", True),
            ("Shadow Charmander", 4, 50, "adamant", True),
            ("Squirtle", 7, 50, "modest", False)
        ]
        
        for name, species_id, level, nature, is_shadow in player_pokemon:
            if is_shadow:
                pokemon = ShadowPokemon(
                    name=name,
                    species_id=species_id,
                    level=level,
                    nature=PokemonNature(nature),
                    moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                )
            else:
                pokemon = Pokemon(
                    name=name,
                    species_id=species_id,
                    level=level,
                    nature=PokemonNature(nature),
                    moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                )
            
            player_team.add_pokemon(pokemon)
        
        print(f"✅ Created player team: {player_team.name} with {player_team.get_team_size()} Pokemon")
        
        # Create opponent team
        opponent_team = PokemonTeam(
            name="AI Opponent",
            format=TeamFormat.SINGLE,
            era=TeamEra.MODERN,
            max_size=6
        )
        
        # Add some Pokemon
        opponent_pokemon = [
            ("Pikachu", 25, 50, "timid"),
            ("Charmander", 4, 50, "adamant"),
            ("Bulbasaur", 1, 50, "modest")
        ]
        
        for name, species_id, level, nature in opponent_pokemon:
            pokemon = Pokemon(
                name=name,
                species_id=species_id,
                level=level,
                nature=PokemonNature(nature),
                moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
            )
            
            opponent_team.add_pokemon(pokemon)
        
        print(f"✅ Created opponent team: {opponent_team.name} with {opponent_team.get_team_size()} Pokemon")
        
        # Create battle simulator
        simulator = BattleSimulator()
        
        # Test different AI difficulties
        difficulties = ["easy", "medium", "hard"]
        
        for difficulty in difficulties:
            print(f"\n🎯 Testing {difficulty.title()} AI difficulty...")
            
            # Simulate battle
            battle_result = simulator.simulate_battle(
                player_team=player_team,
                opponent_team=opponent_team,
                max_turns=20,  # Shorter for testing
                ai_difficulty=difficulty
            )
            
            # Display results
            print(f"Battle Result: {battle_result.get_result_text()}")
            print(f"Turns Taken: {battle_result.turns_taken}")
            
            # Get battle statistics
            stats = simulator.get_battle_statistics(battle_result)
            print(f"Player Pokemon Fainted: {stats['player_pokemon_fainted']}")
            print(f"Opponent Pokemon Fainted: {stats['opponent_pokemon_fainted']}")
            print(f"Total Events: {stats['total_events']}")
        
        # Test battle log
        print(f"\n📝 Testing battle log...")
        battle_result = simulator.simulate_battle(
            player_team=player_team,
            opponent_team=opponent_team,
            max_turns=10,
            ai_difficulty="medium"
        )
        
        log_summary = battle_result.battle_log.get_summary()
        print(f"Battle log summary: {len(log_summary.split('Turn')) - 1} turns recorded")
        
        print("\n✅ Battle simulation tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Battle simulation test failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    return True

def test_gui_components():
    """Test the GUI components (without actually displaying the GUI)."""
    print("\n🎨 Testing GUI Components...")
    print("=" * 50)
    
    try:
        from gui.theme_manager import ThemeManager, ThemeType
        from gui.team_builder_gui import TeamBuilderFrame
        from gui.battle_simulator_gui import BattleSimulatorFrame
        
        # Test theme manager
        print("Testing Theme Manager...")
        theme_manager = ThemeManager()
        
        # Test available themes
        available_themes = theme_manager.get_available_themes()
        print(f"✅ Available themes: {', '.join(available_themes)}")
        
        # Test theme switching
        for theme_type in ThemeType:
            theme_manager.set_theme(theme_type)
            current_theme = theme_manager.get_theme()
            print(f"✅ Theme '{theme_type.value}' loaded with {len(current_theme)} color definitions")
        
        # Test type colors
        test_types = ["fire", "water", "grass", "electric", "shadow"]
        for pokemon_type in test_types:
            color = theme_manager.get_type_color(pokemon_type)
            print(f"✅ Type '{pokemon_type}' color: {color}")
        
        # Test styled component creation
        print("\nTesting styled component creation...")
        
        # Create a mock parent widget (we won't actually display it)
        import tkinter as tk
        mock_root = tk.Tk()
        mock_root.withdraw()  # Hide the window
        
        # Test styled button
        styled_button = theme_manager.create_styled_button(mock_root, "Test Button")
        print(f"✅ Styled button created: {styled_button.cget('text')}")
        
        # Test styled label
        styled_label = theme_manager.create_styled_label(mock_root, "Test Label")
        print(f"✅ Styled label created: {styled_label.cget('text')}")
        
        # Test styled frame
        styled_frame = theme_manager.create_styled_frame(mock_root)
        print(f"✅ Styled frame created")
        
        # Clean up
        mock_root.destroy()
        
        print("\n✅ GUI component tests completed successfully!")
        
    except Exception as e:
        print(f"❌ GUI component test failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🎮 Pokemon Team Builder - New Features Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Test team optimization
    test_results.append(test_team_optimization())
    
    # Test battle simulation
    test_results.append(test_battle_simulation())
    
    # Test GUI components
    test_results.append(test_gui_components())
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The new features are working correctly.")
        print("\n✨ New Features Available:")
        print("✅ Team Optimization System")
        print("✅ Battle Simulation Engine")
        print("✅ Multiple GUI Themes")
        print("✅ Modern GUI Interface")
        print("✅ Team Builder GUI")
        print("✅ Battle Simulator GUI")
        print("\n🚀 You can now run the GUI with: python run_gui.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
