"""
Advanced Battle Predictor
Machine learning system that predicts battle outcomes based on team compositions,
movesets, abilities, historical battle data, and advanced meta analysis.
"""

import numpy as np
import json
import sqlite3
import time
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
import threading

class BattleFormat(Enum):
    """Battle format types."""
    SINGLES_OU = "singles_ou"
    SINGLES_UU = "singles_uu" 
    SINGLES_RU = "singles_ru"
    DOUBLES_VGC = "doubles_vgc"
    DOUBLES_DOU = "doubles_dou"
    MONOTYPE = "monotype"
    UBERS = "ubers"
    LITTLE_CUP = "little_cup"

class WeatherCondition(Enum):
    """Weather conditions affecting battles."""
    CLEAR = "clear"
    SUN = "sun"
    RAIN = "rain"
    SANDSTORM = "sandstorm"
    HAIL = "hail"
    SNOW = "snow"

class TerrainType(Enum):
    """Terrain types affecting battles."""
    NONE = "none"
    ELECTRIC = "electric"
    GRASSY = "grassy"
    MISTY = "misty"
    PSYCHIC = "psychic"

@dataclass
class PokemonAnalysis:
    """Detailed Pokemon analysis for prediction."""
    name: str
    types: List[str]
    stats: Dict[str, int]
    ability: str
    item: str
    moves: List[str]
    level: int
    nature: str
    evs: Dict[str, int]
    ivs: Dict[str, int]
    
    # Calculated metrics
    effective_stats: Dict[str, float]
    type_coverage: List[str]
    role: str  # "sweeper", "wall", "support", "pivot"
    threat_level: float
    versatility_score: float

@dataclass
class TeamAnalysis:
    """Comprehensive team analysis."""
    team_id: str
    pokemon: List[PokemonAnalysis]
    synergy_score: float
    offensive_rating: float
    defensive_rating: float
    speed_control: float
    type_coverage: Dict[str, int]
    weaknesses: List[str]
    strengths: List[str]
    predicted_playstyle: str
    meta_viability: float

@dataclass
class BattlePrediction:
    """Battle outcome prediction."""
    team1_win_probability: float
    team2_win_probability: float
    predicted_winner: str
    confidence_score: float
    key_factors: List[str]
    potential_scenarios: List[Dict[str, Any]]
    turn_prediction: int
    damage_predictions: Dict[str, float]
    critical_matchups: List[Tuple[str, str, float]]

@dataclass
class BattleSimulation:
    """Individual battle simulation result."""
    simulation_id: str
    turns: int
    winner: str
    final_pokemon_counts: Dict[str, int]
    key_moments: List[Dict[str, Any]]
    damage_dealt: Dict[str, int]
    status_effects: Dict[str, List[str]]
    weather_changes: List[str]
    terrain_changes: List[str]

class TypeEffectivenessCalculator:
    """Calculate type effectiveness and interactions."""
    
    def __init__(self):
        self.effectiveness_chart = self._initialize_type_chart()
    
    def _initialize_type_chart(self) -> Dict[str, Dict[str, float]]:
        """Initialize the complete type effectiveness chart."""
        # Simplified type chart (in practice, this would be the full 18x18 chart)
        return {
            "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
            "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
            "Water": {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
            "Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2.0, "Dragon": 0.5},
            "Grass": {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Ground": 2.0, "Dragon": 0.5, "Steel": 0.5},
            "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Fighting": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
            "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5},
            "Poison": {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2.0},
            "Ground": {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
            "Flying": {"Electric": 0.5, "Grass": 2.0, "Ice": 0.5, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
            "Psychic": {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0, "Steel": 0.5},
            "Bug": {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5},
            "Rock": {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
            "Ghost": {"Normal": 0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
            "Dragon": {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0},
            "Dark": {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5},
            "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
            "Fairy": {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5}
        }
    
    def get_effectiveness(self, attacking_type: str, defending_types: List[str]) -> float:
        """Calculate type effectiveness multiplier."""
        effectiveness = 1.0
        
        for defending_type in defending_types:
            type_matchup = self.effectiveness_chart.get(attacking_type, {})
            effectiveness *= type_matchup.get(defending_type, 1.0)
        
        return effectiveness
    
    def calculate_stab(self, move_type: str, pokemon_types: List[str]) -> float:
        """Calculate Same Type Attack Bonus."""
        return 1.5 if move_type in pokemon_types else 1.0

class StatCalculator:
    """Calculate Pokemon stats with nature, EVs, and IVs."""
    
    @staticmethod
    def calculate_stat(base_stat: int, level: int, iv: int, ev: int, nature_modifier: float = 1.0, is_hp: bool = False) -> int:
        """Calculate final stat value."""
        if is_hp:
            return int(((2 * base_stat + iv + (ev // 4)) * level) / 100 + level + 10)
        else:
            return int((((2 * base_stat + iv + (ev // 4)) * level) / 100 + 5) * nature_modifier)
    
    @staticmethod
    def calculate_all_stats(pokemon: PokemonAnalysis) -> Dict[str, int]:
        """Calculate all stats for a Pokemon."""
        nature_modifiers = {
            "Modest": {"sp_attack": 1.1, "attack": 0.9},
            "Adamant": {"attack": 1.1, "sp_attack": 0.9},
            "Timid": {"speed": 1.1, "attack": 0.9},
            "Jolly": {"speed": 1.1, "sp_attack": 0.9},
            "Bold": {"defense": 1.1, "attack": 0.9},
            "Calm": {"sp_defense": 1.1, "attack": 0.9}
        }
        
        modifiers = nature_modifiers.get(pokemon.nature, {})
        
        calculated_stats = {}
        stat_names = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
        
        for stat in stat_names:
            modifier = modifiers.get(stat, 1.0)
            iv = pokemon.ivs.get(stat, 31)
            ev = pokemon.evs.get(stat, 0)
            
            calculated_stats[stat] = StatCalculator.calculate_stat(
                pokemon.stats[stat], pokemon.level, iv, ev, modifier, is_hp=(stat == "hp")
            )
        
        return calculated_stats

class MoveAnalyzer:
    """Analyze moves and their effectiveness."""
    
    def __init__(self):
        self.move_database = self._initialize_move_database()
        self.type_calculator = TypeEffectivenessCalculator()
    
    def _initialize_move_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive move database."""
        return {
            "Earthquake": {"type": "Ground", "power": 100, "accuracy": 100, "category": "Physical", "priority": 0, "effects": []},
            "Thunderbolt": {"type": "Electric", "power": 90, "accuracy": 100, "category": "Special", "priority": 0, "effects": ["paralyze_10"]},
            "Ice Beam": {"type": "Ice", "power": 90, "accuracy": 100, "category": "Special", "priority": 0, "effects": ["freeze_10"]},
            "Flamethrower": {"type": "Fire", "power": 90, "accuracy": 100, "category": "Special", "priority": 0, "effects": ["burn_10"]},
            "Hydro Pump": {"type": "Water", "power": 110, "accuracy": 80, "category": "Special", "priority": 0, "effects": []},
            "Dragon Claw": {"type": "Dragon", "power": 80, "accuracy": 100, "category": "Physical", "priority": 0, "effects": []},
            "Shadow Ball": {"type": "Ghost", "power": 80, "accuracy": 100, "category": "Special", "priority": 0, "effects": ["sp_def_down_20"]},
            "Close Combat": {"type": "Fighting", "power": 120, "accuracy": 100, "category": "Physical", "priority": 0, "effects": ["def_sp_def_down"]},
            "Psychic": {"type": "Psychic", "power": 90, "accuracy": 100, "category": "Special", "priority": 0, "effects": ["sp_def_down_10"]},
            "Stone Edge": {"type": "Rock", "power": 100, "accuracy": 80, "category": "Physical", "priority": 0, "effects": ["high_crit"]},
            "U-turn": {"type": "Bug", "power": 70, "accuracy": 100, "category": "Physical", "priority": 0, "effects": ["switch_out"]},
            "Volt Switch": {"type": "Electric", "power": 70, "accuracy": 100, "category": "Special", "priority": 0, "effects": ["switch_out"]},
            "Stealth Rock": {"type": "Rock", "power": 0, "accuracy": 100, "category": "Status", "priority": 0, "effects": ["entry_hazard"]},
            "Spikes": {"type": "Ground", "power": 0, "accuracy": 100, "category": "Status", "priority": 0, "effects": ["entry_hazard"]},
            "Recover": {"type": "Normal", "power": 0, "accuracy": 100, "category": "Status", "priority": 0, "effects": ["heal_50"]},
            "Thunder Wave": {"type": "Electric", "power": 0, "accuracy": 90, "category": "Status", "priority": 0, "effects": ["paralyze"]},
            "Will-O-Wisp": {"type": "Fire", "power": 0, "accuracy": 85, "category": "Status", "priority": 0, "effects": ["burn"]},
            "Toxic": {"type": "Poison", "power": 0, "accuracy": 90, "category": "Status", "priority": 0, "effects": ["toxic_poison"]},
            "Dragon Dance": {"type": "Dragon", "power": 0, "accuracy": 100, "category": "Status", "priority": 0, "effects": ["attack_speed_up"]},
            "Calm Mind": {"type": "Psychic", "power": 0, "accuracy": 100, "category": "Status", "priority": 0, "effects": ["sp_attack_sp_def_up"]},
            "Extreme Speed": {"type": "Normal", "power": 80, "accuracy": 100, "category": "Physical", "priority": 2, "effects": []},
            "Quick Attack": {"type": "Normal", "power": 40, "accuracy": 100, "category": "Physical", "priority": 1, "effects": []},
            "Protect": {"type": "Normal", "power": 0, "accuracy": 100, "category": "Status", "priority": 4, "effects": ["protect"]},
            "Substitute": {"type": "Normal", "power": 0, "accuracy": 100, "category": "Status", "priority": 0, "effects": ["substitute"]},
        }
    
    def calculate_damage(
        self, 
        attacker: PokemonAnalysis, 
        defender: PokemonAnalysis, 
        move_name: str,
        conditions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate damage dealt by a move."""
        move = self.move_database.get(move_name)
        if not move or move["power"] == 0:
            return {"damage": 0, "effectiveness": 1.0, "is_critical": False}
        
        conditions = conditions or {}
        
        # Get stats
        attacker_stats = StatCalculator.calculate_all_stats(attacker)
        defender_stats = StatCalculator.calculate_all_stats(defender)
        
        # Determine attack and defense stats
        if move["category"] == "Physical":
            attack_stat = attacker_stats["attack"]
            defense_stat = defender_stats["defense"]
        else:
            attack_stat = attacker_stats["sp_attack"]
            defense_stat = defender_stats["sp_defense"]
        
        # Type effectiveness
        effectiveness = self.type_calculator.get_effectiveness(move["type"], defender.types)
        
        # STAB
        stab = self.type_calculator.calculate_stab(move["type"], attacker.types)
        
        # Critical hit chance (simplified)
        critical_chance = 0.0625  # 1/16 base chance
        if "high_crit" in move.get("effects", []):
            critical_chance = 0.125  # 1/8 for high crit moves
        
        is_critical = random.random() < critical_chance
        critical_modifier = 1.5 if is_critical else 1.0
        
        # Weather and terrain modifiers
        weather_modifier = 1.0
        terrain_modifier = 1.0
        
        weather = conditions.get("weather", WeatherCondition.CLEAR)
        if weather == WeatherCondition.SUN and move["type"] == "Fire":
            weather_modifier = 1.5
        elif weather == WeatherCondition.SUN and move["type"] == "Water":
            weather_modifier = 0.5
        elif weather == WeatherCondition.RAIN and move["type"] == "Water":
            weather_modifier = 1.5
        elif weather == WeatherCondition.RAIN and move["type"] == "Fire":
            weather_modifier = 0.5
        
        # Damage calculation (simplified Pokemon damage formula)
        level = attacker.level
        power = move["power"]
        
        damage = (((2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50 + 2) * \
                stab * effectiveness * critical_modifier * weather_modifier * terrain_modifier
        
        # Random factor (85-100%)
        damage *= random.uniform(0.85, 1.0)
        
        return {
            "damage": int(damage),
            "effectiveness": effectiveness,
            "is_critical": is_critical,
            "stab": stab,
            "weather_modifier": weather_modifier,
            "max_damage": int(damage / 0.85),  # Max possible damage
            "min_damage": int(damage * 0.85)   # Min possible damage
        }

class TeamAnalyzer:
    """Analyze team compositions and synergies."""
    
    def __init__(self):
        self.move_analyzer = MoveAnalyzer()
        self.type_calculator = TypeEffectivenessCalculator()
    
    def analyze_team(self, pokemon_list: List[Dict[str, Any]]) -> TeamAnalysis:
        """Perform comprehensive team analysis."""
        
        # Convert dictionaries to PokemonAnalysis objects
        analyzed_pokemon = []
        for pkmn_data in pokemon_list:
            pokemon = self._create_pokemon_analysis(pkmn_data)
            analyzed_pokemon.append(pokemon)
        
        # Calculate team metrics
        synergy_score = self._calculate_synergy_score(analyzed_pokemon)
        offensive_rating = self._calculate_offensive_rating(analyzed_pokemon)
        defensive_rating = self._calculate_defensive_rating(analyzed_pokemon)
        speed_control = self._calculate_speed_control(analyzed_pokemon)
        type_coverage = self._calculate_type_coverage(analyzed_pokemon)
        weaknesses = self._identify_weaknesses(analyzed_pokemon)
        strengths = self._identify_strengths(analyzed_pokemon)
        playstyle = self._predict_playstyle(analyzed_pokemon)
        meta_viability = self._calculate_meta_viability(analyzed_pokemon)
        
        return TeamAnalysis(
            team_id=f"team_{int(time.time())}",
            pokemon=analyzed_pokemon,
            synergy_score=synergy_score,
            offensive_rating=offensive_rating,
            defensive_rating=defensive_rating,
            speed_control=speed_control,
            type_coverage=type_coverage,
            weaknesses=weaknesses,
            strengths=strengths,
            predicted_playstyle=playstyle,
            meta_viability=meta_viability
        )
    
    def _create_pokemon_analysis(self, pkmn_data: Dict[str, Any]) -> PokemonAnalysis:
        """Create PokemonAnalysis from dictionary data."""
        # Default values if not provided
        stats = pkmn_data.get("stats", {
            "hp": 80, "attack": 80, "defense": 80, 
            "sp_attack": 80, "sp_defense": 80, "speed": 80
        })
        
        pokemon = PokemonAnalysis(
            name=pkmn_data.get("name", "Unknown"),
            types=pkmn_data.get("types", ["Normal"]),
            stats=stats,
            ability=pkmn_data.get("ability", "None"),
            item=pkmn_data.get("item", "None"),
            moves=pkmn_data.get("moves", []),
            level=pkmn_data.get("level", 50),
            nature=pkmn_data.get("nature", "Hardy"),
            evs=pkmn_data.get("evs", {"hp": 0, "attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0}),
            ivs=pkmn_data.get("ivs", {"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31}),
            effective_stats={},
            type_coverage=[],
            role="",
            threat_level=0.0,
            versatility_score=0.0
        )
        
        # Calculate derived metrics
        pokemon.effective_stats = StatCalculator.calculate_all_stats(pokemon)
        pokemon.type_coverage = self._calculate_pokemon_coverage(pokemon)
        pokemon.role = self._determine_pokemon_role(pokemon)
        pokemon.threat_level = self._calculate_threat_level(pokemon)
        pokemon.versatility_score = self._calculate_versatility_score(pokemon)
        
        return pokemon
    
    def _calculate_pokemon_coverage(self, pokemon: PokemonAnalysis) -> List[str]:
        """Calculate what types this Pokemon can effectively hit."""
        coverage = set()
        
        for move_name in pokemon.moves:
            move = self.move_analyzer.move_database.get(move_name)
            if move and move["power"] > 0:
                # Check which types this move is super effective against
                for defending_type in self.type_calculator.effectiveness_chart:
                    effectiveness = self.type_calculator.get_effectiveness(move["type"], [defending_type])
                    if effectiveness > 1.0:
                        coverage.add(defending_type)
        
        return list(coverage)
    
    def _determine_pokemon_role(self, pokemon: PokemonAnalysis) -> str:
        """Determine the Pokemon's primary battle role."""
        stats = pokemon.effective_stats
        
        # Calculate stat totals for different roles
        offensive_total = stats["attack"] + stats["sp_attack"] + stats["speed"]
        defensive_total = stats["hp"] + stats["defense"] + stats["sp_defense"]
        
        # Check moveset for clues
        status_moves = sum(1 for move in pokemon.moves 
                          if self.move_analyzer.move_database.get(move, {}).get("category") == "Status")
        
        if offensive_total > defensive_total + 100:
            if stats["speed"] > 110:
                return "sweeper"
            else:
                return "wallbreaker"
        elif defensive_total > offensive_total + 100:
            if status_moves >= 2:
                return "support"
            else:
                return "wall"
        elif stats["speed"] > 100 and status_moves >= 1:
            return "pivot"
        else:
            return "balanced"
    
    def _calculate_threat_level(self, pokemon: PokemonAnalysis) -> float:
        """Calculate how threatening this Pokemon is."""
        stats = pokemon.effective_stats
        
        # Base threat from stats
        offensive_threat = (stats["attack"] + stats["sp_attack"]) / 2
        speed_threat = stats["speed"]
        bulk_threat = (stats["hp"] * (stats["defense"] + stats["sp_defense"])) / 1000
        
        # Move quality bonus
        move_quality = 0
        for move_name in pokemon.moves:
            move = self.move_analyzer.move_database.get(move_name, {})
            if move.get("power", 0) >= 100:
                move_quality += 20
            elif move.get("power", 0) >= 80:
                move_quality += 15
            elif move.get("category") == "Status":
                move_quality += 10
        
        # Ability and item bonuses (simplified)
        ability_bonus = 10 if pokemon.ability != "None" else 0
        item_bonus = 10 if pokemon.item != "None" else 0
        
        threat_level = (offensive_threat * 0.4 + speed_threat * 0.3 + bulk_threat * 0.2 + 
                       move_quality * 0.1 + ability_bonus + item_bonus)
        
        return min(100.0, threat_level / 10)  # Scale to 0-100
    
    def _calculate_versatility_score(self, pokemon: PokemonAnalysis) -> float:
        """Calculate how versatile/flexible this Pokemon is."""
        # Type coverage diversity
        coverage_score = len(pokemon.type_coverage) * 5
        
        # Move diversity
        move_categories = set()
        for move_name in pokemon.moves:
            move = self.move_analyzer.move_database.get(move_name, {})
            move_categories.add(move.get("category", "Unknown"))
        
        category_score = len(move_categories) * 10
        
        # Stat spread balance
        stats = pokemon.effective_stats
        stat_values = [stats[stat] for stat in ["attack", "defense", "sp_attack", "sp_defense", "speed"]]
        stat_variance = np.var(stat_values)
        balance_score = max(0, 50 - stat_variance / 100)  # Lower variance = more balanced = higher score
        
        versatility = coverage_score + category_score + balance_score
        return min(100.0, versatility)
    
    def _calculate_synergy_score(self, pokemon_list: List[PokemonAnalysis]) -> float:
        """Calculate team synergy score."""
        if len(pokemon_list) < 2:
            return 0.0
        
        synergy_score = 0.0
        
        # Role diversity bonus
        roles = [pkmn.role for pkmn in pokemon_list]
        role_diversity = len(set(roles)) / len(roles)
        synergy_score += role_diversity * 25
        
        # Type synergy (defensive coverage)
        all_weaknesses = []
        for pokemon in pokemon_list:
            for weakness_type in self._get_pokemon_weaknesses(pokemon):
                all_weaknesses.append(weakness_type)
        
        weakness_counter = Counter(all_weaknesses)
        # Bonus if team members can cover each other's weaknesses
        coverage_bonus = 0
        for pokemon in pokemon_list:
            weaknesses = self._get_pokemon_weaknesses(pokemon)
            for weakness in weaknesses:
                # Check if any teammate resists this weakness
                for teammate in pokemon_list:
                    if teammate != pokemon:
                        resistances = self._get_pokemon_resistances(teammate)
                        if weakness in resistances:
                            coverage_bonus += 5
                            break
        
        synergy_score += min(50, coverage_bonus)
        
        # Speed tier diversity
        speeds = [pkmn.effective_stats["speed"] for pkmn in pokemon_list]
        speed_tiers = len(set(speed // 20 for speed in speeds))  # Group by speed tiers
        synergy_score += (speed_tiers / len(pokemon_list)) * 25
        
        return min(100.0, synergy_score)
    
    def _get_pokemon_weaknesses(self, pokemon: PokemonAnalysis) -> List[str]:
        """Get types that are super effective against this Pokemon."""
        weaknesses = []
        
        for attacking_type in self.type_calculator.effectiveness_chart:
            effectiveness = self.type_calculator.get_effectiveness(attacking_type, pokemon.types)
            if effectiveness > 1.0:
                weaknesses.append(attacking_type)
        
        return weaknesses
    
    def _get_pokemon_resistances(self, pokemon: PokemonAnalysis) -> List[str]:
        """Get types that this Pokemon resists."""
        resistances = []
        
        for attacking_type in self.type_calculator.effectiveness_chart:
            effectiveness = self.type_calculator.get_effectiveness(attacking_type, pokemon.types)
            if effectiveness < 1.0:
                resistances.append(attacking_type)
        
        return resistances
    
    def _calculate_offensive_rating(self, pokemon_list: List[PokemonAnalysis]) -> float:
        """Calculate team's offensive capabilities."""
        total_offensive = 0
        
        for pokemon in pokemon_list:
            stats = pokemon.effective_stats
            offensive_power = max(stats["attack"], stats["sp_attack"])
            speed_factor = min(2.0, stats["speed"] / 100)  # Speed multiplier
            coverage_bonus = len(pokemon.type_coverage) * 2
            
            pokemon_offensive = (offensive_power * speed_factor + coverage_bonus) / 10
            total_offensive += pokemon_offensive
        
        return min(100.0, total_offensive / len(pokemon_list))
    
    def _calculate_defensive_rating(self, pokemon_list: List[PokemonAnalysis]) -> float:
        """Calculate team's defensive capabilities."""
        total_defensive = 0
        
        for pokemon in pokemon_list:
            stats = pokemon.effective_stats
            bulk = stats["hp"] * (stats["defense"] + stats["sp_defense"]) / 1000
            resistances_bonus = len(self._get_pokemon_resistances(pokemon)) * 5
            
            pokemon_defensive = (bulk + resistances_bonus) / 10
            total_defensive += pokemon_defensive
        
        return min(100.0, total_defensive / len(pokemon_list))
    
    def _calculate_speed_control(self, pokemon_list: List[PokemonAnalysis]) -> float:
        """Calculate team's speed control capabilities."""
        speeds = [pkmn.effective_stats["speed"] for pkmn in pokemon_list]
        
        # Check for priority moves
        priority_moves = 0
        for pokemon in pokemon_list:
            for move_name in pokemon.moves:
                move = self.move_analyzer.move_database.get(move_name, {})
                if move.get("priority", 0) > 0:
                    priority_moves += 1
        
        # Speed tier coverage
        speed_ranges = {
            "slow": sum(1 for s in speeds if s < 60),
            "medium": sum(1 for s in speeds if 60 <= s < 100),
            "fast": sum(1 for s in speeds if s >= 100)
        }
        
        tier_coverage = len([tier for tier, count in speed_ranges.items() if count > 0])
        
        speed_control = (tier_coverage / 3) * 50 + (priority_moves / len(pokemon_list)) * 50
        
        return min(100.0, speed_control)
    
    def _calculate_type_coverage(self, pokemon_list: List[PokemonAnalysis]) -> Dict[str, int]:
        """Calculate overall type coverage of the team."""
        coverage = defaultdict(int)
        
        for pokemon in pokemon_list:
            for covered_type in pokemon.type_coverage:
                coverage[covered_type] += 1
        
        return dict(coverage)
    
    def _identify_weaknesses(self, pokemon_list: List[PokemonAnalysis]) -> List[str]:
        """Identify team weaknesses."""
        weaknesses = []
        
        # Common weaknesses across team members
        all_weaknesses = []
        for pokemon in pokemon_list:
            all_weaknesses.extend(self._get_pokemon_weaknesses(pokemon))
        
        weakness_counter = Counter(all_weaknesses)
        common_weaknesses = [wtype for wtype, count in weakness_counter.items() 
                           if count >= len(pokemon_list) / 2]
        
        weaknesses.extend(common_weaknesses)
        
        # Speed control issues
        speeds = [pkmn.effective_stats["speed"] for pkmn in pokemon_list]
        if max(speeds) < 80:
            weaknesses.append("Slow team vulnerable to faster threats")
        
        # Lack of defensive synergy
        if self._calculate_defensive_rating(pokemon_list) < 30:
            weaknesses.append("Poor defensive synergy")
        
        return weaknesses
    
    def _identify_strengths(self, pokemon_list: List[PokemonAnalysis]) -> List[str]:
        """Identify team strengths."""
        strengths = []
        
        offensive_rating = self._calculate_offensive_rating(pokemon_list)
        defensive_rating = self._calculate_defensive_rating(pokemon_list)
        speed_control = self._calculate_speed_control(pokemon_list)
        
        if offensive_rating > 80:
            strengths.append("High offensive pressure")
        
        if defensive_rating > 80:
            strengths.append("Strong defensive core")
        
        if speed_control > 80:
            strengths.append("Excellent speed control")
        
        # Type coverage
        coverage = self._calculate_type_coverage(pokemon_list)
        if len(coverage) > 12:  # Covers more than 12 types
            strengths.append("Excellent type coverage")
        
        return strengths
    
    def _predict_playstyle(self, pokemon_list: List[PokemonAnalysis]) -> str:
        """Predict the team's playstyle."""
        offensive_rating = self._calculate_offensive_rating(pokemon_list)
        defensive_rating = self._calculate_defensive_rating(pokemon_list)
        
        # Count roles
        roles = [pkmn.role for pkmn in pokemon_list]
        role_counter = Counter(roles)
        
        if offensive_rating > defensive_rating + 20:
            return "Hyper Offense"
        elif defensive_rating > offensive_rating + 20:
            return "Stall/Bulky Offense"
        elif role_counter.get("pivot", 0) >= 2:
            return "Balanced/Pivot"
        elif role_counter.get("sweeper", 0) >= 3:
            return "Offensive"
        else:
            return "Balanced"
    
    def _calculate_meta_viability(self, pokemon_list: List[PokemonAnalysis]) -> float:
        """Calculate how viable this team is in the current meta."""
        # This would typically use real meta data
        # For now, use general viability metrics
        
        viability_score = 0
        
        # Popular Pokemon bonus (simplified)
        popular_pokemon = {"Garchomp", "Rotom-Wash", "Ferrothorn", "Clefable", "Landorus-T"}
        for pokemon in pokemon_list:
            if pokemon.name in popular_pokemon:
                viability_score += 10
        
        # Stat total bonus
        for pokemon in pokemon_list:
            stat_total = sum(pokemon.stats.values())
            if stat_total > 580:  # Pseudo-legendary tier
                viability_score += 15
            elif stat_total > 500:  # Strong stats
                viability_score += 10
        
        # Synergy bonus
        synergy_score = self._calculate_synergy_score(pokemon_list)
        viability_score += synergy_score * 0.5
        
        return min(100.0, viability_score / len(pokemon_list))

class BattlePredictor:
    """Advanced battle outcome prediction system."""
    
    def __init__(self):
        self.team_analyzer = TeamAnalyzer()
        self.move_analyzer = MoveAnalyzer()
        self.simulation_cache = {}
        
        # Machine learning components (simplified)
        self.model_weights = self._initialize_model_weights()
        self.historical_data = []
    
    def _initialize_model_weights(self) -> Dict[str, float]:
        """Initialize ML model weights for prediction."""
        return {
            "offensive_advantage": 0.25,
            "defensive_advantage": 0.20,
            "speed_advantage": 0.15,
            "type_advantage": 0.20,
            "synergy_advantage": 0.10,
            "meta_advantage": 0.05,
            "experience_factor": 0.05
        }
    
    def predict_battle(
        self,
        team1: List[Dict[str, Any]],
        team2: List[Dict[str, Any]],
        battle_format: BattleFormat = BattleFormat.SINGLES_OU,
        conditions: Dict[str, Any] = None
    ) -> BattlePrediction:
        """Predict battle outcome between two teams."""
        
        conditions = conditions or {}
        
        # Analyze both teams
        team1_analysis = self.team_analyzer.analyze_team(team1)
        team2_analysis = self.team_analyzer.analyze_team(team2)
        
        # Calculate advantages
        advantages = self._calculate_team_advantages(team1_analysis, team2_analysis)
        
        # Run probability calculations
        probabilities = self._calculate_win_probabilities(advantages, conditions)
        
        # Identify key factors
        key_factors = self._identify_key_factors(team1_analysis, team2_analysis, advantages)
        
        # Generate scenarios
        scenarios = self._generate_battle_scenarios(team1_analysis, team2_analysis)
        
        # Predict critical matchups
        critical_matchups = self._predict_critical_matchups(team1_analysis, team2_analysis)
        
        # Estimate battle length
        turn_prediction = self._predict_battle_length(team1_analysis, team2_analysis)
        
        # Damage predictions
        damage_predictions = self._predict_damage_distribution(team1_analysis, team2_analysis)
        
        # Determine confidence
        confidence = self._calculate_confidence_score(advantages, probabilities)
        
        return BattlePrediction(
            team1_win_probability=probabilities["team1"],
            team2_win_probability=probabilities["team2"],
            predicted_winner="team1" if probabilities["team1"] > probabilities["team2"] else "team2",
            confidence_score=confidence,
            key_factors=key_factors,
            potential_scenarios=scenarios,
            turn_prediction=turn_prediction,
            damage_predictions=damage_predictions,
            critical_matchups=critical_matchups
        )
    
    def _calculate_team_advantages(
        self, 
        team1: TeamAnalysis, 
        team2: TeamAnalysis
    ) -> Dict[str, float]:
        """Calculate various advantages between teams."""
        
        advantages = {}
        
        # Offensive advantage
        advantages["offensive"] = (team1.offensive_rating - team2.offensive_rating) / 100
        
        # Defensive advantage  
        advantages["defensive"] = (team1.defensive_rating - team2.defensive_rating) / 100
        
        # Speed advantage
        advantages["speed"] = (team1.speed_control - team2.speed_control) / 100
        
        # Type advantage (complex calculation)
        advantages["type"] = self._calculate_type_advantage(team1, team2)
        
        # Synergy advantage
        advantages["synergy"] = (team1.synergy_score - team2.synergy_score) / 100
        
        # Meta advantage
        advantages["meta"] = (team1.meta_viability - team2.meta_viability) / 100
        
        return advantages
    
    def _calculate_type_advantage(self, team1: TeamAnalysis, team2: TeamAnalysis) -> float:
        """Calculate type matchup advantage."""
        team1_advantage = 0
        team2_advantage = 0
        
        # Calculate how well each team can hit the other
        team1_coverage = team1.type_coverage
        team2_coverage = team2.type_coverage
        
        # Team 1's advantage in hitting Team 2
        for pokemon in team2.pokemon:
            weaknesses = self.team_analyzer._get_pokemon_weaknesses(pokemon)
            for weakness in weaknesses:
                if weakness in team1_coverage:
                    team1_advantage += team1_coverage[weakness]
        
        # Team 2's advantage in hitting Team 1
        for pokemon in team1.pokemon:
            weaknesses = self.team_analyzer._get_pokemon_weaknesses(pokemon)
            for weakness in weaknesses:
                if weakness in team2_coverage:
                    team2_advantage += team2_coverage[weakness]
        
        # Normalize and return difference
        if team1_advantage + team2_advantage == 0:
            return 0.0
        
        return (team1_advantage - team2_advantage) / (team1_advantage + team2_advantage)
    
    def _calculate_win_probabilities(
        self, 
        advantages: Dict[str, float], 
        conditions: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate win probabilities using ML model."""
        
        # Weighted advantage score
        weighted_score = 0
        for factor, advantage in advantages.items():
            weight = self.model_weights.get(f"{factor}_advantage", 0.1)
            weighted_score += advantage * weight
        
        # Apply sigmoid function to convert to probability
        team1_prob = 1 / (1 + math.exp(-weighted_score * 5))  # Scale factor of 5
        team2_prob = 1 - team1_prob
        
        # Apply randomness factor (Pokemon battles have inherent randomness)
        randomness_factor = 0.1  # 10% randomness
        team1_prob = max(0.05, min(0.95, team1_prob + random.uniform(-randomness_factor, randomness_factor)))
        team2_prob = 1 - team1_prob
        
        return {"team1": team1_prob, "team2": team2_prob}
    
    def _identify_key_factors(
        self,
        team1: TeamAnalysis,
        team2: TeamAnalysis, 
        advantages: Dict[str, float]
    ) -> List[str]:
        """Identify the most important factors affecting the battle."""
        
        factors = []
        
        # Sort advantages by magnitude
        sorted_advantages = sorted(advantages.items(), key=lambda x: abs(x[1]), reverse=True)
        
        for factor, advantage in sorted_advantages[:3]:  # Top 3 factors
            if abs(advantage) > 0.1:  # Significant advantage
                direction = "advantage" if advantage > 0 else "disadvantage"
                team = "Team 1" if advantage > 0 else "Team 2"
                factors.append(f"{team} has {factor} {direction} ({abs(advantage):.2f})")
        
        # Specific team composition factors
        if len(team1.weaknesses) > len(team2.weaknesses):
            factors.append(f"Team 1 has more exploitable weaknesses ({len(team1.weaknesses)} vs {len(team2.weaknesses)})")
        elif len(team2.weaknesses) > len(team1.weaknesses):
            factors.append(f"Team 2 has more exploitable weaknesses ({len(team2.weaknesses)} vs {len(team1.weaknesses)})")
        
        # Playstyle matchups
        if team1.predicted_playstyle == "Hyper Offense" and team2.predicted_playstyle == "Stall/Bulky Offense":
            factors.append("Offense vs Stall matchup favors preparation and execution")
        
        return factors
    
    def _generate_battle_scenarios(
        self,
        team1: TeamAnalysis,
        team2: TeamAnalysis
    ) -> List[Dict[str, Any]]:
        """Generate possible battle scenarios."""
        
        scenarios = []
        
        # Scenario 1: Team 1 speed advantage
        if team1.speed_control > team2.speed_control:
            scenarios.append({
                "name": "Speed Control Victory",
                "description": "Team 1 outspeeds and applies immediate pressure",
                "probability": 0.3,
                "key_pokemon": [pkmn.name for pkmn in team1.pokemon if pkmn.effective_stats["speed"] > 100][:2]
            })
        
        # Scenario 2: Team 2 walls Team 1
        if team2.defensive_rating > team1.offensive_rating:
            scenarios.append({
                "name": "Defensive Wall Strategy", 
                "description": "Team 2 walls Team 1's attacks and wins through attrition",
                "probability": 0.25,
                "key_pokemon": [pkmn.name for pkmn in team2.pokemon if pkmn.role in ["wall", "support"]][:2]
            })
        
        # Scenario 3: Type advantage exploitation
        scenarios.append({
            "name": "Type Matchup Exploitation",
            "description": "Winner exploits favorable type matchups",
            "probability": 0.2,
            "key_pokemon": []
        })
        
        # Scenario 4: Setup sweep
        sweepers = [pkmn for pkmn in team1.pokemon + team2.pokemon if pkmn.role == "sweeper"]
        if sweepers:
            scenarios.append({
                "name": "Setup Sweep Victory",
                "description": "A sweeper sets up and cleans the opposing team",
                "probability": 0.15,
                "key_pokemon": [sweeper.name for sweeper in sweepers[:2]]
            })
        
        # Scenario 5: Close endgame
        scenarios.append({
            "name": "Close Endgame Battle",
            "description": "Battle comes down to final Pokemon matchup",
            "probability": 0.1,
            "key_pokemon": []
        })
        
        return scenarios
    
    def _predict_critical_matchups(
        self,
        team1: TeamAnalysis,
        team2: TeamAnalysis
    ) -> List[Tuple[str, str, float]]:
        """Predict critical 1v1 matchups."""
        
        critical_matchups = []
        
        # Test key Pokemon from each team against each other
        key_pokemon1 = sorted(team1.pokemon, key=lambda p: p.threat_level, reverse=True)[:3]
        key_pokemon2 = sorted(team2.pokemon, key=lambda p: p.threat_level, reverse=True)[:3]
        
        for pkmn1 in key_pokemon1:
            for pkmn2 in key_pokemon2:
                # Simplified matchup calculation
                advantage = self._calculate_1v1_advantage(pkmn1, pkmn2)
                if abs(advantage) > 0.2:  # Significant advantage
                    critical_matchups.append((pkmn1.name, pkmn2.name, advantage))
        
        # Sort by magnitude of advantage
        critical_matchups.sort(key=lambda x: abs(x[2]), reverse=True)
        
        return critical_matchups[:5]  # Top 5 critical matchups
    
    def _calculate_1v1_advantage(self, pokemon1: PokemonAnalysis, pokemon2: PokemonAnalysis) -> float:
        """Calculate 1v1 matchup advantage."""
        
        # Speed advantage
        speed_advantage = (pokemon1.effective_stats["speed"] - pokemon2.effective_stats["speed"]) / 200
        
        # Type advantage
        type_advantage = 0
        for move_name in pokemon1.moves:
            move = self.move_analyzer.move_database.get(move_name, {})
            if move.get("power", 0) > 0:
                effectiveness = self.move_analyzer.type_calculator.get_effectiveness(
                    move["type"], pokemon2.types
                )
                if effectiveness > 1.5:
                    type_advantage += 0.3
                elif effectiveness < 0.75:
                    type_advantage -= 0.3
        
        # Stat advantage (simplified)
        stat_advantage = (pokemon1.threat_level - pokemon2.threat_level) / 100
        
        return speed_advantage + type_advantage + stat_advantage
    
    def _predict_battle_length(self, team1: TeamAnalysis, team2: TeamAnalysis) -> int:
        """Predict battle length in turns."""
        
        # Base turn count
        base_turns = 15
        
        # Adjust based on team styles
        if team1.predicted_playstyle == "Hyper Offense" or team2.predicted_playstyle == "Hyper Offense":
            base_turns -= 5
        
        if team1.predicted_playstyle == "Stall/Bulky Offense" or team2.predicted_playstyle == "Stall/Bulky Offense":
            base_turns += 10
        
        # Adjust based on defensive ratings
        avg_defense = (team1.defensive_rating + team2.defensive_rating) / 2
        base_turns += int(avg_defense / 10)
        
        # Add randomness
        variation = random.randint(-5, 5)
        
        return max(5, base_turns + variation)
    
    def _predict_damage_distribution(
        self,
        team1: TeamAnalysis,
        team2: TeamAnalysis
    ) -> Dict[str, float]:
        """Predict damage distribution patterns."""
        
        predictions = {}
        
        # Average damage per turn
        avg_offense1 = team1.offensive_rating
        avg_offense2 = team2.offensive_rating
        
        predictions["team1_avg_damage"] = avg_offense1 * 0.3  # Scale factor
        predictions["team2_avg_damage"] = avg_offense2 * 0.3
        
        # KO predictions
        predictions["team1_potential_kos"] = min(6, len([p for p in team1.pokemon if p.threat_level > 70]))
        predictions["team2_potential_kos"] = min(6, len([p for p in team2.pokemon if p.threat_level > 70]))
        
        return predictions
    
    def _calculate_confidence_score(
        self,
        advantages: Dict[str, float],
        probabilities: Dict[str, float]
    ) -> float:
        """Calculate prediction confidence score."""
        
        # Higher advantage differences = higher confidence
        advantage_magnitude = sum(abs(adv) for adv in advantages.values())
        
        # More extreme probabilities = higher confidence
        prob_extremity = abs(probabilities["team1"] - 0.5) * 2
        
        # Combine factors
        confidence = (advantage_magnitude + prob_extremity) / 2
        
        return min(1.0, confidence)
    
    def run_monte_carlo_simulation(
        self,
        team1: List[Dict[str, Any]],
        team2: List[Dict[str, Any]], 
        num_simulations: int = 1000
    ) -> Dict[str, Any]:
        """Run Monte Carlo battle simulations."""
        
        results = {
            "team1_wins": 0,
            "team2_wins": 0,
            "avg_turns": 0,
            "simulation_details": []
        }
        
        for i in range(num_simulations):
            # Run individual simulation
            simulation = self._simulate_single_battle(team1, team2)
            
            if simulation.winner == "team1":
                results["team1_wins"] += 1
            else:
                results["team2_wins"] += 1
            
            results["avg_turns"] += simulation.turns
            
            if i < 10:  # Store first 10 for detailed analysis
                results["simulation_details"].append(asdict(simulation))
        
        results["avg_turns"] /= num_simulations
        results["team1_win_rate"] = results["team1_wins"] / num_simulations
        results["team2_win_rate"] = results["team2_wins"] / num_simulations
        
        return results
    
    def _simulate_single_battle(
        self,
        team1: List[Dict[str, Any]],
        team2: List[Dict[str, Any]]
    ) -> BattleSimulation:
        """Simulate a single battle."""
        
        # Simplified battle simulation
        simulation_id = str(uuid.uuid4())
        
        # Analyze teams
        team1_analysis = self.team_analyzer.analyze_team(team1)
        team2_analysis = self.team_analyzer.analyze_team(team2)
        
        # Simulate battle (very simplified)
        team1_pokemon_remaining = len(team1)
        team2_pokemon_remaining = len(team2)
        
        turns = 0
        key_moments = []
        
        while team1_pokemon_remaining > 0 and team2_pokemon_remaining > 0 and turns < 100:
            turns += 1
            
            # Simplified turn simulation
            if random.random() < 0.6:  # Team 1 action
                if random.random() < 0.3:  # KO chance
                    team2_pokemon_remaining -= 1
                    key_moments.append({
                        "turn": turns,
                        "event": "Team 1 scores a KO",
                        "remaining": {"team1": team1_pokemon_remaining, "team2": team2_pokemon_remaining}
                    })
            else:  # Team 2 action
                if random.random() < 0.3:  # KO chance
                    team1_pokemon_remaining -= 1
                    key_moments.append({
                        "turn": turns,
                        "event": "Team 2 scores a KO", 
                        "remaining": {"team1": team1_pokemon_remaining, "team2": team2_pokemon_remaining}
                    })
        
        winner = "team1" if team1_pokemon_remaining > 0 else "team2"
        
        return BattleSimulation(
            simulation_id=simulation_id,
            turns=turns,
            winner=winner,
            final_pokemon_counts={"team1": team1_pokemon_remaining, "team2": team2_pokemon_remaining},
            key_moments=key_moments,
            damage_dealt={"team1": 0, "team2": 0},  # Simplified
            status_effects={"team1": [], "team2": []},
            weather_changes=[],
            terrain_changes=[]
        )


# Demo function
def demonstrate_battle_predictor():
    """Demonstrate the battle prediction system."""
    print("⚔️ Advanced Battle Predictor Demo")
    print("=" * 60)
    
    # Initialize predictor
    predictor = BattlePredictor()
    
    # Sample teams
    team1 = [
        {
            "name": "Garchomp",
            "types": ["Dragon", "Ground"],
            "stats": {"hp": 108, "attack": 130, "defense": 95, "sp_attack": 80, "sp_defense": 85, "speed": 102},
            "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"],
            "ability": "Rough Skin",
            "item": "Life Orb",
            "level": 50,
            "nature": "Adamant"
        },
        {
            "name": "Rotom-Wash",
            "types": ["Electric", "Water"],
            "stats": {"hp": 50, "attack": 65, "defense": 107, "sp_attack": 105, "sp_defense": 107, "speed": 86},
            "moves": ["Hydro Pump", "Thunderbolt", "Will-O-Wisp", "Protect"],
            "ability": "Levitate",
            "item": "Leftovers",
            "level": 50,
            "nature": "Modest"
        }
    ]
    
    team2 = [
        {
            "name": "Clefable",
            "types": ["Fairy"],
            "stats": {"hp": 95, "attack": 70, "defense": 73, "sp_attack": 95, "sp_defense": 90, "speed": 60},
            "moves": ["Moonblast", "Soft-Boiled", "Stealth Rock", "Thunder Wave"],
            "ability": "Magic Guard", 
            "item": "Life Orb",
            "level": 50,
            "nature": "Bold"
        },
        {
            "name": "Landorus-T",
            "types": ["Ground", "Flying"],
            "stats": {"hp": 89, "attack": 145, "defense": 90, "sp_attack": 105, "sp_defense": 80, "speed": 91},
            "moves": ["Earthquake", "U-turn", "Stone Edge", "Stealth Rock"],
            "ability": "Intimidate",
            "item": "Choice Scarf",
            "level": 50,
            "nature": "Adamant"
        }
    ]
    
    print("🔍 Team Analysis:")
    print("-" * 40)
    
    # Analyze teams
    team1_analysis = predictor.team_analyzer.analyze_team(team1)
    team2_analysis = predictor.team_analyzer.analyze_team(team2)
    
    print(f"Team 1 ({team1_analysis.predicted_playstyle}):")
    print(f"  Offensive Rating: {team1_analysis.offensive_rating:.1f}")
    print(f"  Defensive Rating: {team1_analysis.defensive_rating:.1f}")
    print(f"  Synergy Score: {team1_analysis.synergy_score:.1f}")
    print(f"  Strengths: {', '.join(team1_analysis.strengths)}")
    
    print(f"\nTeam 2 ({team2_analysis.predicted_playstyle}):")
    print(f"  Offensive Rating: {team2_analysis.offensive_rating:.1f}")
    print(f"  Defensive Rating: {team2_analysis.defensive_rating:.1f}")
    print(f"  Synergy Score: {team2_analysis.synergy_score:.1f}")
    print(f"  Strengths: {', '.join(team2_analysis.strengths)}")
    
    # Make prediction
    print(f"\n🎯 Battle Prediction:")
    print("-" * 40)
    
    prediction = predictor.predict_battle(team1, team2)
    
    print(f"Predicted Winner: {prediction.predicted_winner}")
    print(f"Team 1 Win Chance: {prediction.team1_win_probability:.1%}")
    print(f"Team 2 Win Chance: {prediction.team2_win_probability:.1%}")
    print(f"Confidence Score: {prediction.confidence_score:.1%}")
    print(f"Predicted Battle Length: {prediction.turn_prediction} turns")
    
    print(f"\n🔑 Key Factors:")
    for factor in prediction.key_factors:
        print(f"  • {factor}")
    
    print(f"\n⚡ Critical Matchups:")
    for matchup in prediction.critical_matchups:
        pokemon1, pokemon2, advantage = matchup
        winner = pokemon1 if advantage > 0 else pokemon2
        print(f"  • {pokemon1} vs {pokemon2}: {winner} favored ({abs(advantage):.2f})")
    
    print(f"\n🎲 Battle Scenarios:")
    for scenario in prediction.potential_scenarios:
        print(f"  • {scenario['name']} ({scenario['probability']:.1%} chance)")
        print(f"    {scenario['description']}")
    
    # Run Monte Carlo simulation
    print(f"\n🧮 Monte Carlo Simulation (100 battles):")
    print("-" * 40)
    
    monte_carlo = predictor.run_monte_carlo_simulation(team1, team2, 100)
    
    print(f"Team 1 Wins: {monte_carlo['team1_wins']}/100 ({monte_carlo['team1_win_rate']:.1%})")
    print(f"Team 2 Wins: {monte_carlo['team2_wins']}/100 ({monte_carlo['team2_win_rate']:.1%})")
    print(f"Average Battle Length: {monte_carlo['avg_turns']:.1f} turns")

if __name__ == "__main__":
    import uuid  # Add missing import
    demonstrate_battle_predictor()