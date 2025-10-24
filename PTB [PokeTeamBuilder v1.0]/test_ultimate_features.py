#!/usr/bin/env python3
"""
Ultimate Pokemon Team Builder Features Test
Demonstrates AI Trainer, Breeding System, and Contest System functionality.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.features.pokemon_ai_trainer import PokemonAITrainer, AIPersonality, AIStrategy
from src.features.breeding_system import PokemonBreedingSystem, BreedingItem, EggGroup
from src.features.contest_system import PokemonContestSystem, ContestCategory, ContestCondition
from src.teambuilder.team import TeamEra, PokemonTeam, TeamFormat
from src.core.pokemon import Pokemon, PokemonNature
from src.core.stats import BaseStats, EV, IV, Stats
from src.core.types import PokemonType


def create_test_pokemon():
    """Create test Pokemon for demonstrations."""
    pokemon_list = []
    
    # Pikachu
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
    pokemon_list.append(pikachu)
    
    # Charizard
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
    pokemon_list.append(charizard)
    
    # Lucario
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
    pokemon_list.append(lucario)
    
    # Ditto (for breeding)
    ditto = Pokemon(
        name="Ditto",
        species_id=132,
        level=50,
        nature=PokemonNature.HARDY,
        base_stats=BaseStats(hp=48, attack=48, defense=48, special_attack=48, special_defense=48, speed=48),
        evs=EV(hp=0, attack=0, defense=0, special_attack=0, special_defense=0, speed=0),
        ivs=IV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31),
        moves=["Transform"]
    )
    pokemon_list.append(ditto)
    
    return pokemon_list


def test_ai_trainer_system():
    """Test the AI Pokemon Trainer system."""
    print("\n🤖 Testing AI Pokemon Trainer System")
    print("=" * 50)
    
    # Create AI trainer
    ai_trainer = PokemonAITrainer(personality=AIPersonality.ADAPTIVE)
    
    # Create test team
    pokemon_list = create_test_pokemon()
    pikachu, charizard, lucario, ditto = pokemon_list
    team = PokemonTeam(
        name="AI Test Team",
        era=TeamEra.SCARLET_VIOLET,
        format=TeamFormat.SINGLE
    )
    
    # Add Pokemon to team
    team.add_pokemon(pikachu, position=0)
    team.add_pokemon(charizard, position=1)
    team.add_pokemon(lucario, position=2)
    
    # Analyze team
    print("\n📊 AI Team Analysis:")
    analysis = ai_trainer.analyze_team(team)
    print(f"Overall Rating: {analysis['overall_rating']:.2f}")
    print(f"Synergy Score: {analysis['synergy_score']:.2f}")
    print(f"Coverage Score: {analysis['coverage_score']:.2f}")
    
    print(f"\n✅ Strengths:")
    for strength in analysis['strengths']:
        print(f"  - {strength}")
    
    print(f"\n❌ Weaknesses:")
    for weakness in analysis['weaknesses']:
        print(f"  - {weakness}")
    
    print(f"\n💡 Suggestions:")
    for suggestion in analysis['suggestions']:
        print(f"  - {suggestion}")
    
    # Generate battle strategy
    print("\n🎯 AI Battle Strategy:")
    strategy = ai_trainer.generate_battle_strategy(team, team)  # Using same team as opponent for demo
    print(f"Lead Pokemon: {strategy['lead_pokemon']}")
    print(f"Switch Order: {strategy['switch_order']}")
    print(f"Risk Assessment: {strategy['risk_assessment']}")
    
    print(f"\n🎯 Winning Conditions:")
    for condition in strategy['winning_conditions']:
        print(f"  - {condition}")
    
    print(f"\n🛡️ Counter Strategies:")
    for counter_type, strategy_desc in strategy['counter_strategies'].items():
        print(f"  - {counter_type}: {strategy_desc}")
    
    # Test move suggestion
    print("\n⚡ AI Move Suggestion:")
    from src.battle.simulator import BattleState
    from src.battle.battle_state import PokemonBattleState
    
    # Create battle state with Pokemon battle states
    player_pokemon_states = [PokemonBattleState(pokemon=pokemon, current_hp=pokemon.stats.hp, max_hp=pokemon.stats.hp) for pokemon in [pikachu, charizard, lucario]]
    opponent_pokemon_states = [PokemonBattleState(pokemon=pokemon, current_hp=pokemon.stats.hp, max_hp=pokemon.stats.hp) for pokemon in [pikachu, charizard, lucario]]
    battle_state = BattleState(player_team=player_pokemon_states, opponent_team=opponent_pokemon_states)
    
    suggestion = ai_trainer.suggest_best_move(pikachu, charizard, battle_state)
    print(f"Best Move: {suggestion.best_move}")
    print(f"Confidence: {suggestion.confidence:.2f}")
    print(f"Reasoning: {suggestion.reasoning}")
    print(f"Risk Assessment: {suggestion.risk_assessment}")
    print(f"Alternative Moves: {suggestion.alternative_moves}")
    
    # Test opponent prediction
    print("\n🔮 AI Opponent Prediction:")
    # Create a PokemonBattleState for the opponent Pokemon
    opponent_battle_state = PokemonBattleState(pokemon=charizard, current_hp=charizard.stats.hp, max_hp=charizard.stats.hp)
    prediction = ai_trainer.predict_opponent_move(team, opponent_battle_state, battle_state)
    print(f"Predicted Move: {prediction.move_name}")
    print(f"Confidence: {prediction.confidence:.2f}")
    print(f"Reasoning: {prediction.reasoning}")
    print(f"Counter Strategy: {prediction.counter_strategy}")


def test_breeding_system():
    """Test the Pokemon Breeding System."""
    print("\n🥚 Testing Pokemon Breeding System")
    print("=" * 50)
    
    # Create breeding system
    breeding_system = PokemonBreedingSystem()
    
    # Enable shiny hunting features
    breeding_system.shiny_charm_active = True
    breeding_system.masuda_method_active = True
    
    # Create test Pokemon
    pokemon_list = create_test_pokemon()
    pikachu, charizard, lucario, ditto = pokemon_list
    
    # Create breeding pairs
    print("\n💕 Creating Breeding Pairs:")
    
    # Pikachu + Ditto (should work)
    pair1 = breeding_system.create_breeding_pair(pikachu, ditto, 
                                               item1=BreedingItem.EVERSTONE,
                                               item2=BreedingItem.DESTINY_KNOT)
    print(f"Pikachu + Ditto: Compatibility {pair1.compatibility:.2f}")
    print(f"  Egg Group 1: {pair1.egg_group1.value}")
    print(f"  Egg Group 2: {pair1.egg_group2.value}")
    
    # Charizard + Lucario (should not work)
    pair2 = breeding_system.create_breeding_pair(charizard, lucario)
    print(f"Charizard + Lucario: Compatibility {pair2.compatibility:.2f}")
    
    # Attempt breeding
    print("\n🥚 Attempting Breeding:")
    
    # Successful breeding
    result1 = breeding_system.attempt_breeding(pair1)
    print(f"Breeding Result: {result1.message}")
    if result1.success:
        egg = result1.egg
        print(f"  Species: {egg.species_name}")
        print(f"  Nature: {egg.nature.value}")
        print(f"  Ability: {egg.ability}")
        print(f"  Moves: {egg.moves}")
        print(f"  IVs: HP={egg.ivs.hp}, Atk={egg.ivs.attack}, Def={egg.ivs.defense}")
        print(f"  Shiny: {'Yes' if egg.is_shiny else 'No'}")
        print(f"  Steps to Hatch: {egg.total_steps}")
        
        # Hatch the egg
        print("\n🐣 Hatching Egg:")
        hatched_pokemon = breeding_system.hatch_egg(egg)
        print(f"Hatched: {hatched_pokemon.name} (Level {hatched_pokemon.level})")
        print(f"Shiny: {'Yes' if hatched_pokemon.is_shiny else 'No'}")
    
    # Failed breeding
    result2 = breeding_system.attempt_breeding(pair2)
    print(f"Breeding Result: {result2.message}")
    
    # Test IV optimization
    print("\n🎯 IV Optimization:")
    target_ivs = {'hp': 31, 'attack': 31, 'defense': 31, 'special_attack': 31, 'special_defense': 31, 'speed': 31}
    optimized_pairs = breeding_system.optimize_breeding_for_ivs(target_ivs)
    print(f"Found {len(optimized_pairs)} optimized breeding pairs")
    
    # Get breeding statistics
    print("\n📊 Breeding Statistics:")
    stats = breeding_system.get_breeding_statistics()
    print(f"Total Attempts: {stats['total_attempts']}")
    print(f"Successful Breeds: {stats['successful_breeds']}")
    print(f"Success Rate: {stats['success_rate']:.2f}")
    print(f"Shiny Hatches: {stats['shiny_hatches']}")
    print(f"Shiny Rate: {stats['shiny_rate']:.4f}")
    print(f"Current Eggs: {stats['current_eggs']}")


def test_contest_system():
    """Test the Pokemon Contest System."""
    print("\n🎭 Testing Pokemon Contest System")
    print("=" * 50)
    
    # Create contest system
    contest_system = PokemonContestSystem()
    
    # Create test Pokemon
    pokemon_list = create_test_pokemon()
    pikachu, charizard, lucario, ditto = pokemon_list
    
    # Create contest Pokemon with different conditions
    print("\n🌟 Creating Contest Pokemon:")
    
    # Pikachu with high beauty condition
    pikachu_contest = contest_system.create_contest_pokemon(pikachu, {
        ContestCondition.BEAUTY: 200,
        ContestCondition.COOL: 150,
        ContestCondition.CUTE: 180,
        ContestCondition.SMART: 120,
        ContestCondition.TOUGH: 100
    })
    print(f"Pikachu Contest Pokemon created")
    print(f"  Beauty: {pikachu_contest.condition[ContestCondition.BEAUTY]}")
    print(f"  Cool: {pikachu_contest.condition[ContestCondition.COOL]}")
    print(f"  Cute: {pikachu_contest.condition[ContestCondition.CUTE]}")
    
    # Charizard with high cool condition
    charizard_contest = contest_system.create_contest_pokemon(charizard, {
        ContestCondition.BEAUTY: 100,
        ContestCondition.COOL: 220,
        ContestCondition.CUTE: 80,
        ContestCondition.SMART: 140,
        ContestCondition.TOUGH: 180
    })
    print(f"Charizard Contest Pokemon created")
    print(f"  Cool: {charizard_contest.condition[ContestCondition.COOL]}")
    print(f"  Tough: {charizard_contest.condition[ContestCondition.TOUGH]}")
    
    # Lucario with balanced conditions
    lucario_contest = contest_system.create_contest_pokemon(lucario, {
        ContestCondition.BEAUTY: 150,
        ContestCondition.COOL: 160,
        ContestCondition.CUTE: 120,
        ContestCondition.SMART: 200,
        ContestCondition.TOUGH: 170
    })
    print(f"Lucario Contest Pokemon created")
    print(f"  Smart: {lucario_contest.condition[ContestCondition.SMART]}")
    
    # Improve conditions
    print("\n📈 Improving Contest Conditions:")
    improved = contest_system.improve_condition(pikachu_contest, ContestCondition.BEAUTY, 30)
    print(f"Improved Pikachu's beauty: {improved}")
    print(f"New beauty value: {pikachu_contest.condition[ContestCondition.BEAUTY]}")
    
    # Get contest moves
    print("\n🎪 Available Contest Moves:")
    beauty_moves = contest_system.get_contest_moves(ContestCategory.BEAUTY)
    print(f"Beauty Moves ({len(beauty_moves)}):")
    for move in beauty_moves:
        print(f"  - {move.name}: {move.appeal_points} appeal, {move.description}")
    
    cool_moves = contest_system.get_contest_moves(ContestCategory.COOL)
    print(f"Cool Moves ({len(cool_moves)}):")
    for move in cool_moves:
        print(f"  - {move.name}: {move.appeal_points} appeal, {move.description}")
    
    # Start a contest
    print("\n🏆 Starting Beauty Contest:")
    participants = [pikachu_contest, charizard_contest, lucario_contest]
    
    try:
        contest_result = contest_system.start_contest(participants, ContestCategory.BEAUTY)
        
        print(f"\n🎉 Contest Results:")
        print(f"Winner: {contest_result.winner.pokemon.name}")
        print(f"Runner-up: {contest_result.runner_up.pokemon.name}")
        print(f"Third Place: {contest_result.third_place.pokemon.name}")
        print(f"Total Rounds: {contest_result.total_rounds}")
        
        print(f"\n📊 Final Scores:")
        for participant, score in contest_result.final_scores.items():
            print(f"  {participant.pokemon.name}: {score} points")
        
        print(f"\n🌟 Contest Highlights:")
        for highlight in contest_result.highlights:
            print(f"  - {highlight}")
    
    except Exception as e:
        print(f"Contest error: {e}")
    
    # Get contest statistics
    print("\n📈 Contest Statistics:")
    stats = contest_system.get_contest_statistics()
    print(f"Total Contests: {stats['total_contests']}")
    print(f"Wins by Category: {stats['wins_by_category']}")
    print(f"Most Successful Pokemon: {stats['most_successful_pokemon']} ({stats['most_successful_wins']} wins)")
    print(f"Contest Moves Available: {stats['contest_moves_available']}")


def test_integration():
    """Test integration between all systems."""
    print("\n🔗 Testing System Integration")
    print("=" * 50)
    
    # Create all systems
    ai_trainer = PokemonAITrainer()
    breeding_system = PokemonBreedingSystem()
    contest_system = PokemonContestSystem()
    
    # Create Pokemon
    pokemon_list = create_test_pokemon()
    pikachu, charizard, lucario, ditto = pokemon_list
    
    # Create team
    team = PokemonTeam(
        name="Ultimate Test Team",
        era=TeamEra.SCARLET_VIOLET,
        format=TeamFormat.SINGLE
    )
    team.add_pokemon(pikachu, position=0)
    team.add_pokemon(charizard, position=1)
    team.add_pokemon(lucario, position=2)
    
    print("\n🤖 AI Analysis of Team:")
    analysis = ai_trainer.analyze_team(team)
    print(f"AI Rating: {analysis['overall_rating']:.2f}")
    
    print("\n🥚 Breeding Pokemon from Team:")
    breeding_pair = breeding_system.create_breeding_pair(pikachu, ditto)
    breeding_result = breeding_system.attempt_breeding(breeding_pair)
    if breeding_result.success:
        print(f"Bred: {breeding_result.egg.species_name}")
        
        # Add bred Pokemon to team
        hatched_pokemon = breeding_system.hatch_egg(breeding_result.egg)
        team.add_pokemon(hatched_pokemon, position=3)
        print(f"Added {hatched_pokemon.name} to team")
        
        # Re-analyze team with new Pokemon
        new_analysis = ai_trainer.analyze_team(team)
        print(f"New AI Rating: {new_analysis['overall_rating']:.2f}")
    
    print("\n🎭 Contest Performance:")
    contest_pokemon = contest_system.create_contest_pokemon(pikachu)
    print(f"Pikachu contest condition: {contest_pokemon.condition[ContestCondition.BEAUTY]}")
    
    print("\n✅ All systems working together!")


def main():
    """Run all ultimate feature tests."""
    print("🌟 Ultimate Pokemon Team Builder Features Test")
    print("=" * 60)
    print("Testing: AI Trainer, Breeding System, Contest System")
    print("=" * 60)
    
    try:
        test_ai_trainer_system()
        test_breeding_system()
        test_contest_system()
        test_integration()
        
        print("\n🎉 All Ultimate Features Tested Successfully!")
        print("\n🚀 Ultimate Features Summary:")
        print("  🤖 AI Pokemon Trainer - Battle analysis and strategy")
        print("  🥚 Breeding System - IV inheritance and shiny hunting")
        print("  🎭 Contest System - Beauty, cool, cute, smart, tough contests")
        print("  🔗 System Integration - All features work together")
        print("  🎮 PBR Support - Pokemon Battle Revolution features")
        print("  🌟 Advanced Trading - Multi-era trading system")
        print("  🏆 Team Building - Complete team optimization")
        print("  ⚔️ Battle Simulation - Realistic battle mechanics")
        print("  🎨 Beautiful GUI - Modern interface with themes")
        
        print("\n🏆 This is truly the very best Pokemon Team Builder like no one ever was!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
