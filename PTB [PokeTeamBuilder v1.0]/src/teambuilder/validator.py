"""
Team validation and legality checking system.
Ensures teams meet game rules and compatibility requirements.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from ..core import Pokemon, ShadowPokemon, Move, Ability, PokemonType
from .team import PokemonTeam, TeamFormat, TeamEra


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"           # Informational
    WARNING = "warning"      # Warning (may cause issues)
    ERROR = "error"          # Error (will cause problems)
    CRITICAL = "critical"    # Critical (team cannot function)


@dataclass
class ValidationIssue:
    """A single validation issue found."""
    level: ValidationLevel
    category: str
    message: str
    pokemon_name: Optional[str] = None
    slot_position: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation results."""
    is_valid: bool
    issues: List[ValidationIssue]
    warnings_count: int
    errors_count: int
    critical_count: int
    overall_score: float  # 0.0 to 1.0


class TeamValidator:
    """Comprehensive team validation and legality checking system."""
    
    def __init__(self, team: PokemonTeam):
        """
        Initialize team validator.
        
        Args:
            team: Pokemon team to validate
        """
        self.team = team
        self.active_pokemon = team.get_active_pokemon()
        self.issues: List[ValidationIssue] = []
    
    def validate_team(self) -> ValidationResult:
        """
        Perform comprehensive team validation.
        
        Returns:
            ValidationResult with all issues and overall status
        """
        self.issues.clear()
        
        # Run all validation checks
        self._validate_team_structure()
        self._validate_pokemon_legality()
        self._validate_move_legality()
        self._validate_ability_legality()
        self._validate_era_compatibility()
        self._validate_team_balance()
        self._validate_format_specific_rules()
        
        # Calculate results
        warnings_count = len([i for i in self.issues if i.level == ValidationLevel.WARNING])
        errors_count = len([i for i in self.issues if i.level == ValidationLevel.ERROR])
        critical_count = len([i for i in self.issues if i.level == ValidationLevel.CRITICAL])
        
        # Team is valid if no critical or error issues
        is_valid = critical_count == 0 and errors_count == 0
        
        # Calculate overall score
        overall_score = self._calculate_validation_score()
        
        return ValidationResult(
            is_valid=is_valid,
            issues=self.issues,
            warnings_count=warnings_count,
            errors_count=errors_count,
            critical_count=critical_count,
            overall_score=overall_score
        )
    
    def _validate_team_structure(self):
        """Validate basic team structure."""
        # Check team size
        if self.team.is_empty():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                category="Team Structure",
                message="Team is empty",
                suggestion="Add Pokemon to your team"
            ))
            return
        
        # Check minimum team size for format
        min_size = self._get_minimum_team_size()
        if self.team.get_team_size() < min_size:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category="Team Structure",
                message=f"Team has {self.team.get_team_size()} Pokemon, minimum required is {min_size}",
                suggestion=f"Add {min_size - self.team.get_team_size()} more Pokemon"
            ))
        
        # Check for duplicate Pokemon
        pokemon_names = [p.name for p in self.active_pokemon]
        duplicates = [name for name in set(pokemon_names) if pokemon_names.count(name) > 1]
        if duplicates:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="Team Structure",
                message=f"Duplicate Pokemon found: {', '.join(duplicates)}",
                suggestion="Consider using different Pokemon for better type coverage"
            ))
    
    def _validate_pokemon_legality(self):
        """Validate individual Pokemon legality."""
        for i, pokemon in enumerate(self.active_pokemon):
            # Check Pokemon level
            if pokemon.level < 1 or pokemon.level > 100:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="Pokemon Legality",
                    message=f"{pokemon.name} has invalid level: {pokemon.level}",
                    pokemon_name=pokemon.name,
                    slot_position=i,
                    suggestion="Pokemon level must be between 1 and 100"
                ))
            
            # Check Pokemon stats
            if not pokemon.is_legal():
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="Pokemon Legality",
                    message=f"{pokemon.name} has invalid stats",
                    pokemon_name=pokemon.name,
                    slot_position=i,
                    suggestion="Check EV/IV distribution and base stats"
                ))
            
            # Check Shadow Pokemon specifics
            if hasattr(pokemon, 'shadow_level'):
                if pokemon.shadow_level < 0 or pokemon.shadow_level > 5:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        category="Pokemon Legality",
                        message=f"{pokemon.name} has invalid shadow level: {pokemon.shadow_level}",
                        pokemon_name=pokemon.name,
                        slot_position=i,
                        suggestion="Shadow level must be between 0 and 5"
                    ))
                
                if pokemon.shadow_level > 0 and pokemon.purification_progress < 0:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        category="Pokemon Legality",
                        message=f"{pokemon.name} has invalid purification progress: {pokemon.purification_progress}",
                        pokemon_name=pokemon.name,
                        slot_position=i,
                        suggestion="Purification progress must be between 0.0 and 1.0"
                    ))
    
    def _validate_move_legality(self):
        """Validate move legality and compatibility."""
        for i, pokemon in enumerate(self.active_pokemon):
            # Check move count
            if len(pokemon.moves) < 1:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="Move Legality",
                    message=f"{pokemon.name} has no moves",
                    pokemon_name=pokemon.name,
                    slot_position=i,
                    suggestion="Pokemon must have at least 1 move"
                ))
            
            if len(pokemon.moves) > 4:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="Move Legality",
                    message=f"{pokemon.name} has {len(pokemon.moves)} moves (maximum 4)",
                    pokemon_name=pokemon.name,
                    slot_position=i,
                    suggestion="Remove excess moves"
                ))
            
            # Check individual moves
            for move in pokemon.moves:
                # Handle both Move objects and string move names
                if hasattr(move, 'is_legal_for_era'):
                    # Move object
                    move_name = move.name
                    is_shadow_move = move.is_shadow_move
                    move_pp = move.pp
                    
                    # Check move era compatibility
                    if not move.is_legal_for_era(self.team.era.value):
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            category="Move Legality",
                            message=f"{pokemon.name} has move {move_name} not legal for {self.team.era.value} era",
                            pokemon_name=pokemon.name,
                            slot_position=i,
                            suggestion=f"Replace {move_name} with a move legal for {self.team.era.value} era"
                        ))
                    
                    # Check Shadow move restrictions
                    if is_shadow_move and self.team.era != TeamEra.GAMECUBE:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            category="Move Legality",
                            message=f"{pokemon.name} has Shadow move {move_name} (GameCube era only)",
                            pokemon_name=pokemon.name,
                            slot_position=i,
                            suggestion="Shadow moves are only available in GameCube era games"
                        ))
                    
                    # Check move PP
                    if move_pp < 1 or move_pp > 40:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            category="Move Legality",
                            message=f"{pokemon.name} has move {move_name} with invalid PP: {move_pp}",
                            pokemon_name=pokemon.name,
                            slot_position=i,
                            suggestion="Move PP must be between 1 and 40"
                        ))
                else:
                    # String move name - simplified validation
                    move_name = move
                    is_shadow_move = 'shadow' in move_name.lower()
                    
                    # Check Shadow move restrictions for string moves
                    if is_shadow_move and self.team.era != TeamEra.GAMECUBE:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            category="Move Legality",
                            message=f"{pokemon.name} has Shadow move {move_name} (GameCube era only)",
                            pokemon_name=pokemon.name,
                            slot_position=i,
                            suggestion="Shadow moves are only available in GameCube era games"
                        ))
    
    def _validate_ability_legality(self):
        """Validate ability legality and compatibility."""
        for i, pokemon in enumerate(self.active_pokemon):
            if pokemon.ability:
                # Check if ability exists in registry
                from ..core.abilities import get_ability
                ability_obj = get_ability(pokemon.ability)
                
                if not ability_obj:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category="Ability Legality",
                        message=f"{pokemon.name} has unknown ability: {pokemon.ability}",
                        pokemon_name=pokemon.name,
                        slot_position=i,
                        suggestion="Verify ability name or use a standard ability"
                    ))
                else:
                    # Check era compatibility
                    if not ability_obj.is_legal_for_era(self.team.era.value):
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            category="Ability Legality",
                            message=f"{pokemon.name} has ability {pokemon.ability} not legal for {self.team.era.value} era",
                            pokemon_name=pokemon.name,
                            slot_position=i,
                            suggestion=f"Replace {pokemon.ability} with an ability legal for {self.team.era.value} era"
                        ))
    
    def _validate_era_compatibility(self):
        """Validate era-specific compatibility rules."""
        if self.team.era == TeamEra.GAMECUBE:
            # GameCube era specific rules
            shadow_pokemon_count = sum(1 for p in self.active_pokemon if hasattr(p, 'shadow_level') and p.shadow_level > 0)
            
            if shadow_pokemon_count == 0:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    category="Era Compatibility",
                    message="No Shadow Pokemon in team (GameCube era)",
                    suggestion="Consider adding Shadow Pokemon for authentic GameCube experience"
                ))
            
            # Check for non-GameCube Pokemon
            for i, pokemon in enumerate(self.active_pokemon):
                if not hasattr(pokemon, 'shadow_level'):
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category="Era Compatibility",
                        message=f"{pokemon.name} is not a Shadow Pokemon (GameCube era)",
                        pokemon_name=pokemon.name,
                        slot_position=i,
                        suggestion="Consider using Shadow Pokemon for authentic GameCube experience"
                    ))
        
        elif self.team.era == TeamEra.SWITCH:
            # Switch era specific rules
            # Check for modern mechanics
            for i, pokemon in enumerate(self.active_pokemon):
                if hasattr(pokemon, 'shadow_level') and pokemon.shadow_level > 0:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category="Era Compatibility",
                        message=f"{pokemon.name} uses Shadow mechanics (not available in Switch era)",
                        pokemon_name=pokemon.name,
                        slot_position=i,
                        suggestion="Shadow Pokemon are not available in modern games"
                    ))
    
    def _validate_team_balance(self):
        """Validate team balance and competitive viability."""
        # Check type diversity
        type_counts = {}
        for pokemon in self.active_pokemon:
            for pokemon_type in pokemon.types:
                type_name = pokemon_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Check for over-represented types
        over_represented = [t for t, count in type_counts.items() if count > 2]
        if over_represented:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="Team Balance",
                message=f"Over-represented types: {', '.join(over_represented)}",
                suggestion="Consider diversifying your team's type coverage"
            ))
        
        # Check for critical weaknesses
        critical_weaknesses = self._find_critical_weaknesses()
        if critical_weaknesses:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="Team Balance",
                message=f"Critical weaknesses: {', '.join(critical_weaknesses)}",
                suggestion="Add Pokemon that resist these types"
            ))
    
    def _validate_format_specific_rules(self):
        """Validate format-specific rules."""
        if self.team.format == TeamFormat.DOUBLE:
            # Double battle specific rules
            if self.team.get_team_size() < 2:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="Format Rules",
                    message="Double battles require at least 2 Pokemon",
                    suggestion="Add more Pokemon to your team"
                ))
            
            # Check for moves that don't work in double battles
            for i, pokemon in enumerate(self.active_pokemon):
                for move in pokemon.moves:
                    # Handle string moves (simplified validation)
                    if isinstance(move, str):
                        # Skip string-based move validation for now
                        continue
                    
                    if move.target.value in ['single_ally', 'all_allies'] and self.team.format != TeamFormat.DOUBLE:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            category="Format Rules",
                            message=f"{pokemon.name} has move {move.name} designed for double battles",
                            pokemon_name=pokemon.name,
                            slot_position=i,
                            suggestion="Consider replacing with single-target moves"
                        ))
        
        elif self.team.format == TeamFormat.SINGLE:
            # Single battle specific rules
            for i, pokemon in enumerate(self.active_pokemon):
                for move in pokemon.moves:
                    # Handle string moves (simplified validation)
                    if isinstance(move, str):
                        # Skip string-based move validation for now
                        continue
                    
                    if move.target.value in ['single_ally', 'all_allies']:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            category="Format Rules",
                            message=f"{pokemon.name} has move {move.name} designed for double battles",
                            pokemon_name=pokemon.name,
                            slot_position=i,
                            suggestion="This move will have no effect in single battles"
                        ))
    
    def _get_minimum_team_size(self) -> int:
        """Get minimum team size for the current format."""
        format_min_sizes = {
            TeamFormat.SINGLE: 1,
            TeamFormat.DOUBLE: 2,
            TeamFormat.TRIPLE: 3,
            TeamFormat.ROTATION: 3,
            TeamFormat.MULTI: 2
        }
        return format_min_sizes.get(self.team.format, 1)
    
    def _find_critical_weaknesses(self) -> List[str]:
        """Find types that hit multiple Pokemon super effectively."""
        team_weaknesses = {}
        
        for pokemon in self.active_pokemon:
            pokemon_types = [t.value for t in pokemon.types]
            
            # Check against all types
            for attack_type in PokemonType:
                effectiveness = pokemon.get_type_effectiveness(attack_type)
                if effectiveness > 1.0:  # Super effective
                    type_name = attack_type.value
                    if type_name not in team_weaknesses:
                        team_weaknesses[type_name] = []
                    team_weaknesses[type_name].append(pokemon.name)
        
        # Return types that hit multiple Pokemon
        return [t for t, pokemon_list in team_weaknesses.items() if len(pokemon_list) >= 2]
    
    def _calculate_validation_score(self) -> float:
        """Calculate overall validation score."""
        if not self.issues:
            return 1.0
        
        # Weight issues by severity
        issue_scores = {
            ValidationLevel.INFO: 0.0,      # Info doesn't affect score
            ValidationLevel.WARNING: 0.1,   # Warning reduces score slightly
            ValidationLevel.ERROR: 0.3,     # Error reduces score more
            ValidationLevel.CRITICAL: 0.5   # Critical reduces score significantly
        }
        
        total_penalty = sum(issue_scores[issue.level] for issue in self.issues)
        score = max(0.0, 1.0 - total_penalty)
        
        return round(score, 3)
    
    def get_validation_summary(self) -> str:
        """Get human-readable validation summary."""
        if not self.issues:
            return "✅ Team validation passed! No issues found."
        
        summary_lines = []
        
        # Count issues by level
        info_count = len([i for i in self.issues if i.level == ValidationLevel.INFO])
        warning_count = len([i for i in self.issues if i.level == ValidationLevel.WARNING])
        error_count = len([i for i in self.issues if i.level == ValidationLevel.ERROR])
        critical_count = len([i for i in self.issues if i.level == ValidationLevel.CRITICAL])
        
        # Summary header
        if critical_count > 0:
            summary_lines.append("❌ CRITICAL ISSUES FOUND - Team cannot function properly")
        elif error_count > 0:
            summary_lines.append("⚠️ ERRORS FOUND - Team has serious problems")
        elif warning_count > 0:
            summary_lines.append("⚠️ WARNINGS FOUND - Team may have issues")
        else:
            summary_lines.append("ℹ️ INFO - Team has minor considerations")
        
        # Issue counts
        summary_lines.append(f"Critical: {critical_count}, Errors: {error_count}, Warnings: {warning_count}, Info: {info_count}")
        
        # Most important issues
        critical_issues = [i for i in self.issues if i.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR]]
        if critical_issues:
            summary_lines.append("\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues[:3]:  # Show first 3
                summary_lines.append(f"• {issue.message}")
                if issue.suggestion:
                    summary_lines.append(f"  💡 {issue.suggestion}")
        
        return "\n".join(summary_lines)
