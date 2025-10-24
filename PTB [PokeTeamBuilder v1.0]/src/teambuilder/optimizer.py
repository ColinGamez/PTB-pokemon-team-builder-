"""
Team optimization system for Pokemon Team Builder.
Provides intelligent suggestions for improving team composition.
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import random

from .team import PokemonTeam, TeamSlot
from .analyzer import TeamAnalyzer
from .validator import TeamValidator
from ..core.pokemon import Pokemon, ShadowPokemon
from ..core.types import PokemonType, TypeEffectiveness
from ..core.pokemon import PokemonNature


class OptimizationType(Enum):
    """Types of team optimization."""
    TYPE_COVERAGE = "type_coverage"
    STAT_BALANCE = "stat_balance"
    MOVE_COVERAGE = "move_coverage"
    ERA_COMPATIBILITY = "era_compatibility"
    SYNERGY = "synergy"


class OptimizationSuggestion:
    """A suggestion for improving the team."""
    
    def __init__(
        self,
        optimization_type: OptimizationType,
        description: str,
        priority: float,
        pokemon_name: Optional[str] = None,
        slot_position: Optional[int] = None,
        suggested_changes: Optional[Dict[str, any]] = None
    ):
        self.optimization_type = optimization_type
        self.description = description
        self.priority = priority  # 0.0 to 1.0, higher = more important
        self.pokemon_name = pokemon_name
        self.slot_position = slot_position
        self.suggested_changes = suggested_changes or {}
    
    def __str__(self) -> str:
        return f"[{self.optimization_type.value.upper()}] {self.description} (Priority: {self.priority:.2f})"


class TeamOptimizer:
    """Intelligent team optimization system."""
    
    def __init__(self, team: PokemonTeam):
        self.team = team
        self.analyzer = TeamAnalyzer(team)
        self.validator = TeamValidator(team)
    
    def optimize_team(self, optimization_types: Optional[List[OptimizationType]] = None) -> List[OptimizationSuggestion]:
        """
        Optimize the team based on specified optimization types.
        
        Args:
            optimization_types: List of optimization types to apply. If None, applies all.
            
        Returns:
            List of optimization suggestions, sorted by priority
        """
        if optimization_types is None:
            optimization_types = list(OptimizationType)
        
        suggestions = []
        
        for opt_type in optimization_types:
            if opt_type == OptimizationType.TYPE_COVERAGE:
                suggestions.extend(self._optimize_type_coverage())
            elif opt_type == OptimizationType.STAT_BALANCE:
                suggestions.extend(self._optimize_stat_balance())
            elif opt_type == OptimizationType.MOVE_COVERAGE:
                suggestions.extend(self._optimize_move_coverage())
            elif opt_type == OptimizationType.ERA_COMPATIBILITY:
                suggestions.extend(self._optimize_era_compatibility())
            elif opt_type == OptimizationType.SYNERGY:
                suggestions.extend(self._optimize_synergy())
        
        # Sort by priority (highest first)
        suggestions.sort(key=lambda x: x.priority, reverse=True)
        return suggestions
    
    def _optimize_type_coverage(self) -> List[OptimizationSuggestion]:
        """Optimize type coverage by identifying missing types and suggesting additions."""
        suggestions = []
        
        # Get current type coverage
        analysis = self.analyzer.analyze_type_coverage()
        missing_types = analysis.missing_types
        
        if missing_types:
            # Calculate priority based on how many types are missing
            priority = min(0.9, 0.3 + len(missing_types) * 0.1)
            
            # Suggest adding Pokemon with missing types
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.TYPE_COVERAGE,
                description=f"Add Pokemon with missing types: {', '.join(missing_types)}",
                priority=priority,
                suggested_changes={
                    'missing_types': missing_types,
                    'recommended_types': self._get_recommended_types(missing_types)
                }
            ))
        
        # Check for type weaknesses
        weakness_analysis = self.analyzer.analyze_weaknesses()
        critical_weaknesses = weakness_analysis.critical_weaknesses
        
        if critical_weaknesses:
            priority = min(0.8, 0.4 + len(critical_weaknesses) * 0.1)
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.TYPE_COVERAGE,
                description=f"Address critical weaknesses: {', '.join(critical_weaknesses)}",
                priority=priority,
                suggested_changes={
                    'critical_weaknesses': critical_weaknesses,
                    'recommended_resistances': self._get_recommended_resistances(critical_weaknesses)
                }
            ))
        
        return suggestions
    
    def _optimize_stat_balance(self) -> List[OptimizationSuggestion]:
        """Optimize stat distribution across the team."""
        suggestions = []
        
        stat_analysis = self.analyzer.analyze_stats()
        stat_averages = stat_analysis.stat_averages
        
        # Check for stat imbalances
        if stat_averages:
            # Find stats that are significantly higher or lower than average
            total_stats = sum(stat_averages.values())
            avg_stat = total_stats / len(stat_averages)
            
            for stat_name, stat_value in stat_averages.items():
                if stat_value > avg_stat * 1.3:  # 30% above average
                    suggestions.append(OptimizationSuggestion(
                        optimization_type=OptimizationType.STAT_BALANCE,
                        description=f"Consider reducing {stat_name} focus (currently {stat_value:.1f})",
                        priority=0.6,
                        suggested_changes={
                            'stat_name': stat_name,
                            'current_value': stat_value,
                            'recommended_range': f"< {avg_stat * 1.2:.1f}"
                        }
                    ))
                elif stat_value < avg_stat * 0.7:  # 30% below average
                    suggestions.append(OptimizationSuggestion(
                        optimization_type=OptimizationType.STAT_BALANCE,
                        description=f"Consider increasing {stat_name} focus (currently {stat_value:.1f})",
                        priority=0.6,
                        suggested_changes={
                            'stat_name': stat_name,
                            'current_value': stat_value,
                            'recommended_range': f"> {avg_stat * 0.8:.1f}"
                        }
                    ))
        
        return suggestions
    
    def _optimize_move_coverage(self) -> List[OptimizationSuggestion]:
        """Optimize move type coverage."""
        suggestions = []
        
        move_analysis = self.analyzer.analyze_move_coverage()
        missing_move_types = move_analysis.missing_move_types
        
        if missing_move_types:
            priority = min(0.7, 0.3 + len(missing_move_types) * 0.1)
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.MOVE_COVERAGE,
                description=f"Add moves with missing types: {', '.join(missing_move_types)}",
                priority=priority,
                suggested_changes={
                    'missing_move_types': missing_move_types,
                    'recommended_moves': self._get_recommended_moves(missing_move_types)
                }
            ))
        
        return suggestions
    
    def _optimize_era_compatibility(self) -> List[OptimizationSuggestion]:
        """Optimize era compatibility."""
        suggestions = []
        
        era_analysis = self.analyzer.analyze_era_compatibility()
        
        if not era_analysis.is_compatible:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.ERA_COMPATIBILITY,
                description=f"Team has era compatibility issues: {era_analysis.compatibility_notes}",
                priority=0.8,
                suggested_changes={
                    'compatibility_issues': era_analysis.compatibility_notes,
                    'recommended_era': self.team.era.value
                }
            ))
        
        return suggestions
    
    def _optimize_synergy(self) -> List[OptimizationSuggestion]:
        """Optimize team synergies."""
        suggestions = []
        
        synergy_analysis = self.analyzer.analyze_synergies()
        
        if synergy_analysis.synergy_score < 0.5:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.SYNERGY,
                description="Team has poor synergy. Consider Pokemon that work well together.",
                priority=0.7,
                suggested_changes={
                    'current_synergy_score': synergy_analysis.synergy_score,
                    'recommended_synergy_score': '> 0.6'
                }
            ))
        
        return suggestions
    
    def _get_recommended_types(self, missing_types: List[str]) -> List[str]:
        """Get recommended types to add based on missing types."""
        # This would integrate with a Pokemon database in a real implementation
        type_recommendations = {
            'fire': ['Charizard', 'Arcanine', 'Infernape'],
            'water': ['Blastoise', 'Gyarados', 'Swampert'],
            'grass': ['Venusaur', 'Sceptile', 'Torterra'],
            'electric': ['Raichu', 'Luxray', 'Electivire'],
            'ice': ['Lapras', 'Weavile', 'Mamoswine'],
            'fighting': ['Machamp', 'Lucario', 'Conkeldurr'],
            'poison': ['Gengar', 'Crobat', 'Toxicroak'],
            'ground': ['Garchomp', 'Excadrill', 'Landorus'],
            'flying': ['Salamence', 'Staraptor', 'Talonflame'],
            'psychic': ['Alakazam', 'Metagross', 'Reuniclus'],
            'bug': ['Scizor', 'Volcarona', 'Genesect'],
            'rock': ['Tyranitar', 'Aerodactyl', 'Terrakion'],
            'ghost': ['Gengar', 'Chandelure', 'Aegislash'],
            'dragon': ['Salamence', 'Garchomp', 'Hydreigon'],
            'dark': ['Tyranitar', 'Weavile', 'Hydreigon'],
            'steel': ['Metagross', 'Scizor', 'Aegislash'],
            'fairy': ['Gardevoir', 'Togekiss', 'Azumarill'],
            'shadow': ['Shadow Lugia', 'Shadow Mewtwo', 'Shadow Ho-oh']
        }
        
        recommendations = []
        for missing_type in missing_types:
            if missing_type.lower() in type_recommendations:
                recommendations.extend(type_recommendations[missing_type.lower()])
        
        return list(set(recommendations))[:6]  # Return up to 6 unique recommendations
    
    def _get_recommended_resistances(self, critical_weaknesses: List[str]) -> List[str]:
        """Get recommended types to resist critical weaknesses."""
        # This would integrate with type effectiveness data in a real implementation
        resistance_mapping = {
            'fire': ['water', 'rock', 'dragon'],
            'water': ['grass', 'dragon'],
            'grass': ['fire', 'poison', 'bug', 'dragon', 'steel'],
            'electric': ['grass', 'dragon'],
            'ice': ['fire', 'water', 'steel'],
            'fighting': ['flying', 'psychic', 'fairy'],
            'poison': ['ground', 'psychic', 'rock', 'ghost'],
            'ground': ['grass', 'ice', 'bug'],
            'flying': ['electric', 'ice', 'rock'],
            'psychic': ['bug', 'ghost', 'dark'],
            'bug': ['fire', 'flying', 'rock'],
            'rock': ['water', 'grass', 'fighting', 'ground', 'steel'],
            'ghost': ['ghost', 'dark'],
            'dragon': ['dragon', 'steel', 'fairy'],
            'dark': ['fighting', 'bug', 'fairy'],
            'steel': ['fire', 'fighting', 'ground'],
            'fairy': ['poison', 'steel']
        }
        
        recommendations = []
        for weakness in critical_weaknesses:
            if weakness.lower() in resistance_mapping:
                recommendations.extend(resistance_mapping[weakness.lower()])
        
        return list(set(recommendations))[:4]  # Return up to 4 unique recommendations
    
    def _get_recommended_moves(self, missing_move_types: List[str]) -> List[str]:
        """Get recommended moves for missing move types."""
        # This would integrate with a move database in a real implementation
        move_recommendations = {
            'fire': ['Flamethrower', 'Fire Blast', 'Overheat'],
            'water': ['Surf', 'Hydro Pump', 'Aqua Jet'],
            'grass': ['Energy Ball', 'Leaf Blade', 'Giga Drain'],
            'electric': ['Thunderbolt', 'Thunder', 'Volt Switch'],
            'ice': ['Ice Beam', 'Blizzard', 'Ice Shard'],
            'fighting': ['Close Combat', 'Mach Punch', 'Drain Punch'],
            'poison': ['Sludge Bomb', 'Poison Jab', 'Gunk Shot'],
            'ground': ['Earthquake', 'Earth Power', 'Bulldoze'],
            'flying': ['Air Slash', 'Brave Bird', 'U-turn'],
            'psychic': ['Psychic', 'Psyshock', 'Zen Headbutt'],
            'bug': ['Bug Buzz', 'X-Scissor', 'U-turn'],
            'rock': ['Stone Edge', 'Rock Slide', 'Rock Tomb'],
            'ghost': ['Shadow Ball', 'Shadow Claw', 'Shadow Sneak'],
            'dragon': ['Dragon Claw', 'Dragon Pulse', 'Outrage'],
            'dark': ['Dark Pulse', 'Crunch', 'Sucker Punch'],
            'steel': ['Iron Head', 'Flash Cannon', 'Bullet Punch'],
            'fairy': ['Moonblast', 'Play Rough', 'Dazzling Gleam'],
            'shadow': ['Shadow Rush', 'Shadow Blast', 'Shadow Wave']
        }
        
        recommendations = []
        for move_type in missing_move_types:
            if move_type.lower() in move_recommendations:
                recommendations.extend(move_recommendations[move_type.lower()])
        
        return list(set(recommendations))[:6]  # Return up to 6 unique recommendations
    
    def get_optimization_summary(self, suggestions: List[OptimizationSuggestion]) -> str:
        """Get a human-readable summary of optimization suggestions."""
        if not suggestions:
            return "🎉 Your team is already well-optimized! No major improvements needed."
        
        summary_lines = ["🔧 Team Optimization Suggestions:"]
        
        # Group by optimization type
        by_type = {}
        for suggestion in suggestions:
            opt_type = suggestion.optimization_type.value
            if opt_type not in by_type:
                by_type[opt_type] = []
            by_type[opt_type].append(suggestion)
        
        for opt_type, type_suggestions in by_type.items():
            summary_lines.append(f"\n📊 {opt_type.replace('_', ' ').title()}:")
            for suggestion in type_suggestions:
                summary_lines.append(f"  • {suggestion.description}")
                if suggestion.suggested_changes:
                    for key, value in suggestion.suggested_changes.items():
                        if key.startswith('recommended_'):
                            summary_lines.append(f"    💡 {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(summary_lines)
