"""
AI Team Recommendation Engine
Intelligent system that analyzes battle meta and suggests optimal team compositions
"""

import json
import random
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3
from datetime import datetime, timedelta

class BattleFormat(Enum):
    """Battle format types."""
    SINGLES = "singles"
    DOUBLES = "doubles"
    VGC = "vgc"
    OU = "ou"
    UU = "uu"
    RU = "ru"
    NU = "nu"
    LITTLE_CUP = "little_cup"

class MetaTier(Enum):
    """Pokemon meta tier rankings."""
    S_TIER = "S"
    A_TIER = "A"
    B_TIER = "B"
    C_TIER = "C"
    D_TIER = "D"
    UNRANKED = "U"

@dataclass
class PokemonAnalysis:
    """Analysis data for a Pokemon."""
    name: str
    types: List[str]
    stats: Dict[str, int]
    tier: MetaTier
    usage_rate: float
    win_rate: float
    common_movesets: List[Dict[str, Any]]
    common_items: List[str]
    common_abilities: List[str]
    counters: List[str]
    checks: List[str]
    synergies: List[str]
    roles: List[str]  # sweeper, wall, support, etc.

@dataclass
class TeamRecommendation:
    """AI team recommendation with analysis."""
    pokemon_list: List[str]
    confidence_score: float
    analysis: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    meta_score: float
    type_coverage: Dict[str, float]
    role_balance: Dict[str, int]

class AITeamRecommendationEngine:
    """Advanced AI system for team recommendations."""
    
    def __init__(self, db_path: str = "team_meta.db"):
        self.db_path = db_path
        self.pokemon_data = {}
        self.meta_trends = {}
        self.user_preferences = {}
        self.battle_history = []
        
        self._initialize_database()
        self._load_pokemon_data()
        self._initialize_meta_analysis()
    
    def _initialize_database(self):
        """Initialize the meta analysis database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for meta analysis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pokemon_meta (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    format TEXT,
                    tier TEXT,
                    usage_rate REAL,
                    win_rate REAL,
                    avg_rating REAL,
                    last_updated TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS battle_results (
                    id INTEGER PRIMARY KEY,
                    team_composition TEXT,
                    opponent_team TEXT,
                    format TEXT,
                    result TEXT,
                    rating_change INTEGER,
                    battle_date TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    preferred_playstyle TEXT,
                    favorite_types TEXT,
                    avoided_pokemon TEXT,
                    skill_level TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_synergies (
                    id INTEGER PRIMARY KEY,
                    pokemon1 TEXT,
                    pokemon2 TEXT,
                    synergy_score REAL,
                    synergy_type TEXT,
                    description TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def _load_pokemon_data(self):
        """Load Pokemon data for analysis."""
        # Sample Pokemon data with meta information
        sample_pokemon = {
            "Pikachu": {
                "types": ["Electric"],
                "stats": {"hp": 35, "attack": 55, "defense": 40, "sp_attack": 50, "sp_defense": 50, "speed": 90},
                "tier": MetaTier.C_TIER,
                "usage_rate": 0.12,
                "win_rate": 0.45,
                "roles": ["sweeper", "support"],
                "common_items": ["Light Ball", "Focus Sash"],
                "common_abilities": ["Static", "Lightning Rod"]
            },
            "Charizard": {
                "types": ["Fire", "Flying"],
                "stats": {"hp": 78, "attack": 84, "defense": 78, "sp_attack": 109, "sp_defense": 85, "speed": 100},
                "tier": MetaTier.B_TIER,
                "usage_rate": 0.25,
                "win_rate": 0.58,
                "roles": ["sweeper", "wall_breaker"],
                "common_items": ["Heavy-Duty Boots", "Life Orb"],
                "common_abilities": ["Blaze", "Solar Power"]
            },
            "Garchomp": {
                "types": ["Dragon", "Ground"],
                "stats": {"hp": 108, "attack": 130, "defense": 95, "sp_attack": 80, "sp_defense": 85, "speed": 102},
                "tier": MetaTier.A_TIER,
                "usage_rate": 0.45,
                "win_rate": 0.72,
                "roles": ["sweeper", "wallbreaker"],
                "common_items": ["Rocky Helmet", "Leftovers"],
                "common_abilities": ["Sand Veil", "Rough Skin"]
            },
            "Toxapex": {
                "types": ["Poison", "Water"],
                "stats": {"hp": 50, "attack": 63, "defense": 152, "sp_attack": 53, "sp_defense": 142, "speed": 35},
                "tier": MetaTier.S_TIER,
                "usage_rate": 0.68,
                "win_rate": 0.85,
                "roles": ["wall", "support"],
                "common_items": ["Black Sludge", "Rocky Helmet"],
                "common_abilities": ["Regenerator", "Limber"]
            },
            "Dragapult": {
                "types": ["Dragon", "Ghost"],
                "stats": {"hp": 88, "attack": 120, "defense": 75, "sp_attack": 100, "sp_defense": 75, "speed": 142},
                "tier": MetaTier.S_TIER,
                "usage_rate": 0.72,
                "win_rate": 0.78,
                "roles": ["sweeper", "revenge_killer"],
                "common_items": ["Choice Specs", "Life Orb"],
                "common_abilities": ["Clear Body", "Infiltrator"]
            },
            "Ferrothorn": {
                "types": ["Grass", "Steel"],
                "stats": {"hp": 74, "attack": 94, "defense": 131, "sp_attack": 54, "sp_defense": 116, "speed": 20},
                "tier": MetaTier.A_TIER,
                "usage_rate": 0.52,
                "win_rate": 0.69,
                "roles": ["wall", "support", "hazard_setter"],
                "common_items": ["Leftovers", "Rocky Helmet"],
                "common_abilities": ["Iron Barbs", "Anticipation"]
            }
        }
        
        self.pokemon_data = sample_pokemon
    
    def _initialize_meta_analysis(self):
        """Initialize meta trend analysis."""
        self.meta_trends = {
            "rising_pokemon": ["Dragapult", "Toxapex", "Garchomp"],
            "falling_pokemon": ["Pikachu", "Charizard"],
            "trending_strategies": ["hyper_offense", "balance", "stall"],
            "popular_types": ["Dragon", "Steel", "Water", "Ground"],
            "effective_cores": [
                ["Dragapult", "Toxapex", "Ferrothorn"],
                ["Garchomp", "Toxapex", "Charizard"],
                ["Ferrothorn", "Dragapult", "Garchomp"]
            ]
        }
    
    def analyze_team_composition(self, team: List[str], battle_format: BattleFormat) -> Dict[str, Any]:
        """Analyze a team composition for strengths and weaknesses."""
        analysis = {
            "type_coverage": self._calculate_type_coverage(team),
            "role_balance": self._analyze_role_balance(team),
            "stat_distribution": self._analyze_stat_distribution(team),
            "meta_score": self._calculate_meta_score(team, battle_format),
            "synergy_score": self._calculate_team_synergy(team),
            "weaknesses": self._identify_weaknesses(team),
            "threats": self._identify_major_threats(team, battle_format)
        }
        
        return analysis
    
    def _calculate_type_coverage(self, team: List[str]) -> Dict[str, float]:
        """Calculate offensive and defensive type coverage."""
        offensive_coverage = {}
        defensive_coverage = {}
        
        all_types = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", 
                    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
                    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
        
        for defending_type in all_types:
            offensive_effectiveness = 0
            defensive_resistance = 0
            
            for pokemon_name in team:
                if pokemon_name in self.pokemon_data:
                    pokemon = self.pokemon_data[pokemon_name]
                    
                    # Calculate offensive coverage
                    for attacking_type in pokemon["types"]:
                        effectiveness = self._get_type_effectiveness(attacking_type, defending_type)
                        offensive_effectiveness = max(offensive_effectiveness, effectiveness)
                    
                    # Calculate defensive coverage
                    for pokemon_type in pokemon["types"]:
                        resistance = self._get_type_effectiveness(defending_type, pokemon_type)
                        defensive_resistance += resistance
            
            offensive_coverage[defending_type] = offensive_effectiveness
            defensive_coverage[defending_type] = defensive_resistance / len(team)
        
        return {
            "offensive": offensive_coverage,
            "defensive": defensive_coverage,
            "overall_coverage": sum(offensive_coverage.values()) / len(all_types)
        }
    
    def _get_type_effectiveness(self, attacking_type: str, defending_type: str) -> float:
        """Get type effectiveness multiplier."""
        # Simplified type chart (in reality, this would be much more comprehensive)
        effectiveness_chart = {
            "Fire": {"Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Steel": 2.0, "Water": 0.5, "Fire": 0.5, "Rock": 0.5, "Dragon": 0.5},
            "Water": {"Fire": 2.0, "Ground": 2.0, "Rock": 2.0, "Water": 0.5, "Grass": 0.5, "Dragon": 0.5},
            "Electric": {"Water": 2.0, "Flying": 2.0, "Electric": 0.5, "Grass": 0.5, "Dragon": 0.5, "Ground": 0.0},
            "Grass": {"Water": 2.0, "Ground": 2.0, "Rock": 2.0, "Fire": 0.5, "Grass": 0.5, "Poison": 0.5, "Flying": 0.5, "Bug": 0.5, "Dragon": 0.5, "Steel": 0.5},
            "Dragon": {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
            "Steel": {"Ice": 2.0, "Rock": 2.0, "Fairy": 2.0, "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Steel": 0.5},
        }
        
        if attacking_type in effectiveness_chart:
            return effectiveness_chart[attacking_type].get(defending_type, 1.0)
        return 1.0
    
    def _analyze_role_balance(self, team: List[str]) -> Dict[str, int]:
        """Analyze team role balance."""
        role_counts = {
            "sweeper": 0,
            "wall": 0,
            "support": 0,
            "wall_breaker": 0,
            "revenge_killer": 0,
            "hazard_setter": 0
        }
        
        for pokemon_name in team:
            if pokemon_name in self.pokemon_data:
                pokemon = self.pokemon_data[pokemon_name]
                for role in pokemon.get("roles", []):
                    if role in role_counts:
                        role_counts[role] += 1
        
        return role_counts
    
    def _analyze_stat_distribution(self, team: List[str]) -> Dict[str, float]:
        """Analyze team stat distribution."""
        total_stats = {"hp": 0, "attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0}
        
        for pokemon_name in team:
            if pokemon_name in self.pokemon_data:
                pokemon = self.pokemon_data[pokemon_name]
                for stat, value in pokemon["stats"].items():
                    total_stats[stat] += value
        
        team_size = len(team)
        avg_stats = {stat: total / team_size for stat, total in total_stats.items()}
        
        return {
            "average_stats": avg_stats,
            "total_bst": sum(total_stats.values()),
            "speed_tier": self._calculate_speed_tier(avg_stats["speed"]),
            "bulk_rating": (avg_stats["hp"] + avg_stats["defense"] + avg_stats["sp_defense"]) / 3
        }
    
    def _calculate_speed_tier(self, avg_speed: float) -> str:
        """Calculate speed tier classification."""
        if avg_speed >= 110:
            return "Very Fast"
        elif avg_speed >= 90:
            return "Fast"
        elif avg_speed >= 70:
            return "Medium"
        elif avg_speed >= 50:
            return "Slow"
        else:
            return "Very Slow"
    
    def _calculate_meta_score(self, team: List[str], battle_format: BattleFormat) -> float:
        """Calculate team meta relevance score."""
        total_score = 0
        
        for pokemon_name in team:
            if pokemon_name in self.pokemon_data:
                pokemon = self.pokemon_data[pokemon_name]
                
                # Base score from usage and win rate
                usage_score = pokemon["usage_rate"] * 100
                win_rate_score = pokemon["win_rate"] * 100
                
                # Tier bonus
                tier_bonus = {
                    MetaTier.S_TIER: 20,
                    MetaTier.A_TIER: 15,
                    MetaTier.B_TIER: 10,
                    MetaTier.C_TIER: 5,
                    MetaTier.D_TIER: 0,
                    MetaTier.UNRANKED: -5
                }.get(pokemon["tier"], 0)
                
                # Meta trend bonus
                trend_bonus = 0
                if pokemon_name in self.meta_trends["rising_pokemon"]:
                    trend_bonus = 10
                elif pokemon_name in self.meta_trends["falling_pokemon"]:
                    trend_bonus = -5
                
                pokemon_score = usage_score + win_rate_score + tier_bonus + trend_bonus
                total_score += pokemon_score
        
        return min(100, total_score / len(team))
    
    def _calculate_team_synergy(self, team: List[str]) -> float:
        """Calculate team synergy score."""
        synergy_score = 0
        team_size = len(team)
        
        # Check for effective cores
        for core in self.meta_trends["effective_cores"]:
            core_pokemon_in_team = sum(1 for pokemon in core if pokemon in team)
            if core_pokemon_in_team >= 2:
                synergy_score += core_pokemon_in_team * 10
        
        # Type synergy analysis
        type_synergy = self._analyze_type_synergy(team)
        synergy_score += type_synergy
        
        # Role synergy analysis
        role_balance = self._analyze_role_balance(team)
        if role_balance["wall"] >= 1 and role_balance["sweeper"] >= 1:
            synergy_score += 15  # Good balance bonus
        
        return min(100, synergy_score / team_size)
    
    def _analyze_type_synergy(self, team: List[str]) -> float:
        """Analyze type synergy within the team."""
        synergy_score = 0
        team_types = []
        
        for pokemon_name in team:
            if pokemon_name in self.pokemon_data:
                team_types.extend(self.pokemon_data[pokemon_name]["types"])
        
        # Bonus for type diversity
        unique_types = len(set(team_types))
        synergy_score += unique_types * 2
        
        # Bonus for complementary types
        if "Fire" in team_types and "Water" in team_types:
            synergy_score += 5
        if "Dragon" in team_types and "Steel" in team_types:
            synergy_score += 8
        
        return synergy_score
    
    def _identify_weaknesses(self, team: List[str]) -> List[str]:
        """Identify team weaknesses."""
        weaknesses = []
        type_coverage = self._calculate_type_coverage(team)
        role_balance = self._analyze_role_balance(team)
        
        # Type coverage weaknesses
        for type_name, coverage in type_coverage["offensive"].items():
            if coverage < 1.0:
                weaknesses.append(f"Poor coverage against {type_name} types")
        
        # Role balance issues
        if role_balance["wall"] == 0:
            weaknesses.append("No defensive presence")
        if role_balance["sweeper"] == 0:
            weaknesses.append("Lacks offensive threats")
        if role_balance["support"] == 0:
            weaknesses.append("No utility/support options")
        
        return weaknesses[:5]  # Top 5 weaknesses
    
    def _identify_major_threats(self, team: List[str], battle_format: BattleFormat) -> List[str]:
        """Identify major threats to the team."""
        threats = []
        
        # Common meta threats
        meta_threats = {
            BattleFormat.SINGLES: ["Dragapult", "Toxapex", "Garchomp", "Ferrothorn"],
            BattleFormat.DOUBLES: ["Incineroar", "Rillaboom", "Dragapult", "Regieleki"],
            BattleFormat.VGC: ["Calyrex-Shadow", "Kyogre", "Groudon", "Zacian"]
        }
        
        format_threats = meta_threats.get(battle_format, meta_threats[BattleFormat.SINGLES])
        
        for threat in format_threats:
            if threat not in team:  # Don't list threats we already have
                threat_coverage = self._calculate_threat_coverage(team, threat)
                if threat_coverage < 0.5:
                    threats.append(threat)
        
        return threats[:3]  # Top 3 threats
    
    def _calculate_threat_coverage(self, team: List[str], threat: str) -> float:
        """Calculate how well the team covers a specific threat."""
        if threat not in self.pokemon_data:
            return 0.5  # Unknown threat
        
        threat_data = self.pokemon_data[threat]
        coverage_score = 0
        
        for pokemon_name in team:
            if pokemon_name in self.pokemon_data:
                pokemon = self.pokemon_data[pokemon_name]
                
                # Type effectiveness against threat
                for pokemon_type in pokemon["types"]:
                    for threat_type in threat_data["types"]:
                        effectiveness = self._get_type_effectiveness(pokemon_type, threat_type)
                        if effectiveness > 1.0:
                            coverage_score += effectiveness * 0.3
                
                # Speed advantage
                if pokemon["stats"]["speed"] > threat_data["stats"]["speed"]:
                    coverage_score += 0.2
                
                # Defensive capability
                threat_attack = max(threat_data["stats"]["attack"], threat_data["stats"]["sp_attack"])
                pokemon_defense = max(pokemon["stats"]["defense"], pokemon["stats"]["sp_defense"])
                if pokemon_defense > threat_attack:
                    coverage_score += 0.3
        
        return min(1.0, coverage_score / len(team))
    
    def generate_team_recommendations(
        self, 
        battle_format: BattleFormat,
        user_preferences: Dict[str, Any] = None,
        num_recommendations: int = 3
    ) -> List[TeamRecommendation]:
        """Generate AI-powered team recommendations."""
        
        recommendations = []
        
        for i in range(num_recommendations):
            # Generate team based on different strategies
            strategies = ["balanced", "hyper_offense", "stall", "meta_core"]
            strategy = strategies[i % len(strategies)]
            
            team = self._generate_team_by_strategy(strategy, battle_format, user_preferences)
            analysis = self.analyze_team_composition(team, battle_format)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(team, analysis, strategy)
            
            recommendation = TeamRecommendation(
                pokemon_list=team,
                confidence_score=confidence,
                analysis=analysis,
                strengths=self._identify_team_strengths(team, analysis),
                weaknesses=analysis["weaknesses"],
                suggestions=self._generate_improvement_suggestions(team, analysis),
                meta_score=analysis["meta_score"],
                type_coverage=analysis["type_coverage"],
                role_balance=analysis["role_balance"]
            )
            
            recommendations.append(recommendation)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations
    
    def _generate_team_by_strategy(
        self, 
        strategy: str, 
        battle_format: BattleFormat,
        user_preferences: Dict[str, Any] = None
    ) -> List[str]:
        """Generate a team based on a specific strategy."""
        
        available_pokemon = list(self.pokemon_data.keys())
        team = []
        
        if strategy == "balanced":
            # Build a balanced team
            team.append(self._select_pokemon_by_role("sweeper", available_pokemon))
            team.append(self._select_pokemon_by_role("wall", available_pokemon))
            team.append(self._select_pokemon_by_role("support", available_pokemon))
            
            # Fill remaining slots with high-tier Pokemon
            remaining_slots = 6 - len(team)
            high_tier_pokemon = [p for p in available_pokemon 
                               if p not in team and 
                               self.pokemon_data[p]["tier"] in [MetaTier.S_TIER, MetaTier.A_TIER]]
            team.extend(random.sample(high_tier_pokemon, min(remaining_slots, len(high_tier_pokemon))))
        
        elif strategy == "hyper_offense":
            # Build an offensive team
            sweepers = [p for p in available_pokemon 
                       if "sweeper" in self.pokemon_data[p].get("roles", [])]
            team.extend(random.sample(sweepers, min(5, len(sweepers))))
            
            # Add one support for utility
            support_pokemon = [p for p in available_pokemon 
                             if p not in team and "support" in self.pokemon_data[p].get("roles", [])]
            if support_pokemon:
                team.append(random.choice(support_pokemon))
        
        elif strategy == "stall":
            # Build a defensive team
            walls = [p for p in available_pokemon 
                    if "wall" in self.pokemon_data[p].get("roles", [])]
            team.extend(random.sample(walls, min(4, len(walls))))
            
            # Add support and one win condition
            support_pokemon = [p for p in available_pokemon 
                             if p not in team and "support" in self.pokemon_data[p].get("roles", [])]
            if support_pokemon:
                team.append(random.choice(support_pokemon))
            
            sweepers = [p for p in available_pokemon 
                       if p not in team and "sweeper" in self.pokemon_data[p].get("roles", [])]
            if sweepers:
                team.append(random.choice(sweepers))
        
        elif strategy == "meta_core":
            # Use proven meta cores
            if self.meta_trends["effective_cores"]:
                core = random.choice(self.meta_trends["effective_cores"])
                team.extend(core)
                
                # Fill remaining slots
                remaining_slots = 6 - len(team)
                remaining_pokemon = [p for p in available_pokemon if p not in team]
                team.extend(random.sample(remaining_pokemon, min(remaining_slots, len(remaining_pokemon))))
        
        # Apply user preferences if provided
        if user_preferences:
            team = self._apply_user_preferences(team, user_preferences, available_pokemon)
        
        # Ensure team has exactly 6 Pokemon
        while len(team) < 6:
            remaining = [p for p in available_pokemon if p not in team]
            if remaining:
                team.append(random.choice(remaining))
            else:
                break
        
        return team[:6]
    
    def _select_pokemon_by_role(self, role: str, available_pokemon: List[str]) -> str:
        """Select the best Pokemon for a specific role."""
        candidates = [p for p in available_pokemon 
                     if role in self.pokemon_data[p].get("roles", [])]
        
        if not candidates:
            return random.choice(available_pokemon)
        
        # Sort by tier and usage rate
        candidates.sort(key=lambda p: (
            list(MetaTier).index(self.pokemon_data[p]["tier"]),
            -self.pokemon_data[p]["usage_rate"]
        ))
        
        return candidates[0]
    
    def _apply_user_preferences(
        self, 
        team: List[str], 
        preferences: Dict[str, Any], 
        available_pokemon: List[str]
    ) -> List[str]:
        """Apply user preferences to team selection."""
        modified_team = team.copy()
        
        # Replace Pokemon based on preferences
        if "favorite_types" in preferences:
            favorite_types = preferences["favorite_types"]
            for i, pokemon_name in enumerate(modified_team):
                if pokemon_name in self.pokemon_data:
                    pokemon_types = self.pokemon_data[pokemon_name]["types"]
                    if not any(t in favorite_types for t in pokemon_types):
                        # Try to replace with preferred type
                        replacements = [p for p in available_pokemon 
                                      if p not in modified_team and 
                                      any(t in favorite_types for t in self.pokemon_data[p]["types"])]
                        if replacements:
                            modified_team[i] = random.choice(replacements)
        
        return modified_team
    
    def _calculate_confidence_score(
        self, 
        team: List[str], 
        analysis: Dict[str, Any], 
        strategy: str
    ) -> float:
        """Calculate confidence score for a team recommendation."""
        score = 0
        
        # Meta score weight (40%)
        score += analysis["meta_score"] * 0.4
        
        # Synergy score weight (30%)
        score += analysis["synergy_score"] * 0.3
        
        # Type coverage weight (20%)
        score += analysis["type_coverage"]["overall_coverage"] * 100 * 0.2
        
        # Strategy coherence weight (10%)
        strategy_bonus = self._calculate_strategy_coherence(team, strategy)
        score += strategy_bonus * 0.1
        
        return min(100, max(0, score))
    
    def _calculate_strategy_coherence(self, team: List[str], strategy: str) -> float:
        """Calculate how well the team follows the intended strategy."""
        role_balance = self._analyze_role_balance(team)
        
        if strategy == "hyper_offense":
            return min(100, role_balance["sweeper"] * 20)
        elif strategy == "stall":
            return min(100, role_balance["wall"] * 25)
        elif strategy == "balanced":
            balance_score = 0
            if role_balance["sweeper"] >= 1:
                balance_score += 33
            if role_balance["wall"] >= 1:
                balance_score += 33
            if role_balance["support"] >= 1:
                balance_score += 34
            return balance_score
        
        return 50  # Default for unknown strategies
    
    def _identify_team_strengths(self, team: List[str], analysis: Dict[str, Any]) -> List[str]:
        """Identify team strengths."""
        strengths = []
        
        # High meta score
        if analysis["meta_score"] >= 70:
            strengths.append("Strong meta relevance")
        
        # Good type coverage
        if analysis["type_coverage"]["overall_coverage"] >= 1.5:
            strengths.append("Excellent type coverage")
        
        # High synergy
        if analysis["synergy_score"] >= 60:
            strengths.append("Great team synergy")
        
        # Role analysis
        role_balance = analysis["role_balance"]
        if role_balance["sweeper"] >= 2:
            strengths.append("Strong offensive presence")
        if role_balance["wall"] >= 2:
            strengths.append("Solid defensive core")
        if role_balance["support"] >= 1:
            strengths.append("Good utility options")
        
        return strengths[:4]  # Top 4 strengths
    
    def _generate_improvement_suggestions(self, team: List[str], analysis: Dict[str, Any]) -> List[str]:
        """Generate suggestions for team improvement."""
        suggestions = []
        
        # Based on weaknesses
        for weakness in analysis["weaknesses"]:
            if "coverage" in weakness.lower():
                suggestions.append("Consider adding Pokemon with better type coverage")
            elif "defensive" in weakness.lower():
                suggestions.append("Add a defensive wall or pivot")
            elif "offensive" in weakness.lower():
                suggestions.append("Include more offensive threats")
        
        # Based on threats
        for threat in analysis["threats"]:
            suggestions.append(f"Consider adding a {threat} counter")
        
        # Meta suggestions
        if analysis["meta_score"] < 50:
            suggestions.append("Consider using more meta-relevant Pokemon")
        
        return suggestions[:3]  # Top 3 suggestions

# Example usage and testing
def demonstrate_ai_recommendations():
    """Demonstrate the AI team recommendation system."""
    print("🤖 AI Team Recommendation Engine Demo")
    print("=" * 50)
    
    # Initialize the engine
    engine = AITeamRecommendationEngine()
    
    # Generate recommendations
    recommendations = engine.generate_team_recommendations(
        battle_format=BattleFormat.SINGLES,
        user_preferences={
            "favorite_types": ["Dragon", "Steel"],
            "preferred_playstyle": "balanced"
        },
        num_recommendations=3
    )
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"\n🏆 RECOMMENDATION #{i} (Confidence: {rec.confidence_score:.1f}%)")
        print("-" * 40)
        print(f"Team: {', '.join(rec.pokemon_list)}")
        print(f"Meta Score: {rec.meta_score:.1f}/100")
        print(f"Synergy Score: {rec.analysis['synergy_score']:.1f}/100")
        
        print(f"\n✅ Strengths:")
        for strength in rec.strengths:
            print(f"  • {strength}")
        
        print(f"\n⚠️ Weaknesses:")
        for weakness in rec.weaknesses:
            print(f"  • {weakness}")
        
        print(f"\n💡 Suggestions:")
        for suggestion in rec.suggestions:
            print(f"  • {suggestion}")

if __name__ == "__main__":
    demonstrate_ai_recommendations()