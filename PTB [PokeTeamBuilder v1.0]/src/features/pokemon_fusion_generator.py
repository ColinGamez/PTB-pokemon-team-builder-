"""
Pokemon Fusion Generator
Create unique hybrid Pokemon by combining two species with balanced stats,
merged types, and combined movesets.
"""

import random
import json
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import colorsys

class FusionMethod(Enum):
    """Methods for fusing Pokemon."""
    BALANCED = "balanced"  # Average stats evenly
    DOMINANT = "dominant"  # First Pokemon is dominant
    HYBRID = "hybrid"     # Complex weighted fusion
    RANDOM = "random"     # Random fusion elements

@dataclass
class FusedPokemon:
    """A fused Pokemon with combined characteristics."""
    name: str
    base_pokemon1: str
    base_pokemon2: str
    types: List[str]
    stats: Dict[str, int]
    abilities: List[str]
    moves: List[str]
    description: str
    fusion_method: FusionMethod
    rarity_tier: str
    color_scheme: Dict[str, str]
    sprite_data: Optional[Dict[str, Any]] = None

class PokemonFusionGenerator:
    """Advanced Pokemon fusion system."""
    
    def __init__(self):
        self.pokemon_database = {}
        self.fusion_history = []
        self.name_patterns = []
        self.color_palettes = {}
        
        self._initialize_pokemon_data()
        self._initialize_fusion_patterns()
        self._initialize_color_system()
    
    def _initialize_pokemon_data(self):
        """Initialize comprehensive Pokemon database for fusion."""
        self.pokemon_database = {
            "Pikachu": {
                "types": ["Electric"],
                "stats": {"hp": 35, "attack": 55, "defense": 40, "sp_attack": 50, "sp_defense": 50, "speed": 90},
                "abilities": ["Static", "Lightning Rod"],
                "signature_moves": ["Thunderbolt", "Quick Attack", "Thunder Wave", "Agility"],
                "color_primary": "#FFD700",  # Gold
                "color_secondary": "#FF6B6B",  # Red
                "personality_traits": ["energetic", "loyal", "quick"],
                "habitat": "forest",
                "rarity": "common"
            },
            "Charizard": {
                "types": ["Fire", "Flying"],
                "stats": {"hp": 78, "attack": 84, "defense": 78, "sp_attack": 109, "sp_defense": 85, "speed": 100},
                "abilities": ["Blaze", "Solar Power"],
                "signature_moves": ["Flamethrower", "Dragon Pulse", "Air Slash", "Heat Wave"],
                "color_primary": "#FF4500",  # Orange Red
                "color_secondary": "#FFA500",  # Orange
                "personality_traits": ["fierce", "proud", "powerful"],
                "habitat": "mountain",
                "rarity": "rare"
            },
            "Blastoise": {
                "types": ["Water"],
                "stats": {"hp": 79, "attack": 83, "defense": 100, "sp_attack": 85, "sp_defense": 105, "speed": 78},
                "abilities": ["Torrent", "Rain Dish"],
                "signature_moves": ["Hydro Pump", "Ice Beam", "Rapid Spin", "Shell Smash"],
                "color_primary": "#4169E1",  # Royal Blue
                "color_secondary": "#87CEEB",  # Sky Blue
                "personality_traits": ["calm", "defensive", "steady"],
                "habitat": "ocean",
                "rarity": "rare"
            },
            "Venusaur": {
                "types": ["Grass", "Poison"],
                "stats": {"hp": 80, "attack": 82, "defense": 83, "sp_attack": 100, "sp_defense": 100, "speed": 80},
                "abilities": ["Overgrow", "Chlorophyll"],
                "signature_moves": ["Solar Beam", "Sludge Bomb", "Sleep Powder", "Synthesis"],
                "color_primary": "#228B22",  # Forest Green
                "color_secondary": "#9932CC",  # Dark Orchid
                "personality_traits": ["wise", "nurturing", "patient"],
                "habitat": "forest",
                "rarity": "rare"
            },
            "Alakazam": {
                "types": ["Psychic"],
                "stats": {"hp": 55, "attack": 50, "defense": 45, "sp_attack": 135, "sp_defense": 95, "speed": 120},
                "abilities": ["Synchronize", "Inner Focus", "Magic Guard"],
                "signature_moves": ["Psychic", "Teleport", "Future Sight", "Calm Mind"],
                "color_primary": "#DAA520",  # Goldenrod
                "color_secondary": "#8A2BE2",  # Blue Violet
                "personality_traits": ["intelligent", "mystical", "analytical"],
                "habitat": "urban",
                "rarity": "rare"
            },
            "Machamp": {
                "types": ["Fighting"],
                "stats": {"hp": 90, "attack": 130, "defense": 80, "sp_attack": 65, "sp_defense": 85, "speed": 55},
                "abilities": ["Guts", "No Guard"],
                "signature_moves": ["Dynamic Punch", "Cross Chop", "Bulk Up", "Seismic Toss"],
                "color_primary": "#8B4513",  # Saddle Brown
                "color_secondary": "#D2691E",  # Chocolate
                "personality_traits": ["strong", "determined", "hardworking"],
                "habitat": "mountain",
                "rarity": "uncommon"
            },
            "Gengar": {
                "types": ["Ghost", "Poison"],
                "stats": {"hp": 60, "attack": 65, "defense": 60, "sp_attack": 130, "sp_defense": 75, "speed": 110},
                "abilities": ["Levitate", "Cursed Body"],
                "signature_moves": ["Shadow Ball", "Hypnosis", "Dream Eater", "Destiny Bond"],
                "color_primary": "#4B0082",  # Indigo
                "color_secondary": "#8B008B",  # Dark Magenta
                "personality_traits": ["mischievous", "sneaky", "playful"],
                "habitat": "haunted",
                "rarity": "rare"
            },
            "Dragonite": {
                "types": ["Dragon", "Flying"],
                "stats": {"hp": 91, "attack": 134, "defense": 95, "sp_attack": 100, "sp_defense": 100, "speed": 80},
                "abilities": ["Inner Focus", "Multiscale"],
                "signature_moves": ["Dragon Rush", "Hurricane", "Extreme Speed", "Dragon Dance"],
                "color_primary": "#FFB347",  # Peach
                "color_secondary": "#FF8C00",  # Dark Orange
                "personality_traits": ["gentle", "powerful", "protective"],
                "habitat": "ocean",
                "rarity": "legendary"
            }
        }
    
    def _initialize_fusion_patterns(self):
        """Initialize name fusion patterns and methods."""
        self.name_patterns = [
            # Simple concatenation patterns
            lambda name1, name2: name1[:len(name1)//2] + name2[len(name2)//2:],
            lambda name1, name2: name1[:3] + name2[3:],
            lambda name1, name2: name1[:-2] + name2[-3:],
            
            # Complex patterns
            lambda name1, name2: name1[:2] + name2[1:4] + name1[-2:],
            lambda name1, name2: name2[:3] + name1[2:-1] + name2[-1:],
            
            # Syllable-based patterns
            lambda name1, name2: self._syllable_fusion(name1, name2),
            lambda name1, name2: self._reverse_syllable_fusion(name1, name2),
        ]
    
    def _initialize_color_system(self):
        """Initialize color mixing and palette system."""
        self.color_palettes = {
            "fire": ["#FF4500", "#FF6347", "#DC143C", "#B22222"],
            "water": ["#0000FF", "#1E90FF", "#00CED1", "#4682B4"],
            "grass": ["#228B22", "#32CD32", "#9ACD32", "#6B8E23"],
            "electric": ["#FFD700", "#FFFF00", "#F0E68C", "#DAA520"],
            "psychic": ["#FF1493", "#DA70D6", "#BA55D3", "#9370DB"],
            "dark": ["#2F4F4F", "#36454F", "#696969", "#778899"],
            "dragon": ["#4B0082", "#8A2BE2", "#9400D3", "#8B008B"],
            "steel": ["#C0C0C0", "#A9A9A9", "#696969", "#2F4F4F"]
        }
    
    def create_fusion(
        self, 
        pokemon1: str, 
        pokemon2: str, 
        fusion_method: FusionMethod = FusionMethod.BALANCED,
        custom_parameters: Dict[str, Any] = None
    ) -> FusedPokemon:
        """Create a fusion of two Pokemon."""
        
        if pokemon1 not in self.pokemon_database or pokemon2 not in self.pokemon_database:
            raise ValueError(f"Pokemon not found in database: {pokemon1} or {pokemon2}")
        
        base1 = self.pokemon_database[pokemon1]
        base2 = self.pokemon_database[pokemon2]
        
        # Generate fusion name
        fusion_name = self._generate_fusion_name(pokemon1, pokemon2)
        
        # Fuse types
        fusion_types = self._fuse_types(base1["types"], base2["types"])
        
        # Fuse stats
        fusion_stats = self._fuse_stats(base1["stats"], base2["stats"], fusion_method)
        
        # Fuse abilities
        fusion_abilities = self._fuse_abilities(base1["abilities"], base2["abilities"])
        
        # Create moveset
        fusion_moves = self._create_fusion_moveset(base1["signature_moves"], base2["signature_moves"])
        
        # Generate description
        description = self._generate_fusion_description(pokemon1, pokemon2, base1, base2)
        
        # Determine rarity
        rarity = self._calculate_fusion_rarity(base1, base2, fusion_method)
        
        # Create color scheme
        color_scheme = self._create_color_scheme(
            base1["color_primary"], base1["color_secondary"],
            base2["color_primary"], base2["color_secondary"]
        )
        
        # Create the fused Pokemon
        fusion = FusedPokemon(
            name=fusion_name,
            base_pokemon1=pokemon1,
            base_pokemon2=pokemon2,
            types=fusion_types,
            stats=fusion_stats,
            abilities=fusion_abilities,
            moves=fusion_moves,
            description=description,
            fusion_method=fusion_method,
            rarity_tier=rarity,
            color_scheme=color_scheme
        )
        
        # Store in history
        self.fusion_history.append(fusion)
        
        return fusion
    
    def _generate_fusion_name(self, name1: str, name2: str) -> str:
        """Generate a creative fusion name."""
        # Try different patterns and pick the best sounding one
        candidates = []
        
        for pattern in self.name_patterns:
            try:
                candidate = pattern(name1, name2)
                if len(candidate) >= 4 and len(candidate) <= 12:
                    candidates.append(candidate)
            except:
                continue
        
        if not candidates:
            # Fallback to simple concatenation
            return name1[:4] + name2[4:] if len(name2) > 4 else name1[:3] + name2
        
        # Score candidates based on pronounceability and uniqueness
        scored_candidates = []
        for candidate in candidates:
            score = self._score_name_quality(candidate)
            scored_candidates.append((candidate, score))
        
        # Return the highest scored name
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0].capitalize()
    
    def _syllable_fusion(self, name1: str, name2: str) -> str:
        """Fuse names based on syllable patterns."""
        # Simple syllable detection (this could be more sophisticated)
        vowels = "aeiouAEIOU"
        
        def get_syllables(name):
            syllables = []
            current = ""
            for char in name:
                current += char
                if char in vowels and len(current) >= 2:
                    syllables.append(current)
                    current = ""
            if current:
                syllables.append(current)
            return syllables
        
        syl1 = get_syllables(name1)
        syl2 = get_syllables(name2)
        
        if len(syl1) >= 2 and len(syl2) >= 2:
            return syl1[0] + syl2[-1]
        else:
            return name1[:3] + name2[-3:]
    
    def _reverse_syllable_fusion(self, name1: str, name2: str) -> str:
        """Reverse syllable fusion pattern."""
        return self._syllable_fusion(name2, name1)
    
    def _score_name_quality(self, name: str) -> float:
        """Score a fusion name for quality and pronounceability."""
        score = 0
        
        # Length bonus (6-9 characters is ideal)
        if 6 <= len(name) <= 9:
            score += 20
        elif 4 <= len(name) <= 11:
            score += 10
        
        # Vowel-consonant balance
        vowels = sum(1 for c in name.lower() if c in "aeiou")
        consonants = len(name) - vowels
        if vowels > 0 and consonants > 0:
            balance = min(vowels, consonants) / max(vowels, consonants)
            score += balance * 30
        
        # Avoid repeated characters
        repeated = sum(1 for i, c in enumerate(name[1:], 1) if c == name[i-1])
        score -= repeated * 5
        
        # Prefer certain letter combinations
        good_combinations = ["ch", "th", "sh", "ph", "st", "cr", "br", "dr"]
        for combo in good_combinations:
            if combo in name.lower():
                score += 5
        
        return score
    
    def _fuse_types(self, types1: List[str], types2: List[str]) -> List[str]:
        """Fuse type combinations intelligently."""
        all_types = types1 + types2
        unique_types = list(dict.fromkeys(all_types))  # Preserve order, remove duplicates
        
        # Pokemon can have at most 2 types
        if len(unique_types) <= 2:
            return unique_types
        
        # If more than 2 types, use intelligent selection
        type_priority = {
            "Dragon": 10, "Steel": 9, "Fairy": 8, "Ghost": 7, "Dark": 6,
            "Psychic": 5, "Electric": 4, "Fire": 3, "Water": 3, "Grass": 3,
            "Fighting": 2, "Flying": 2, "Ground": 2, "Rock": 2,
            "Bug": 1, "Poison": 1, "Ice": 1, "Normal": 0
        }
        
        # Sort by priority and take top 2
        sorted_types = sorted(unique_types, key=lambda t: type_priority.get(t, 0), reverse=True)
        return sorted_types[:2]
    
    def _fuse_stats(
        self, 
        stats1: Dict[str, int], 
        stats2: Dict[str, int], 
        method: FusionMethod
    ) -> Dict[str, int]:
        """Fuse stats based on the chosen method."""
        
        if method == FusionMethod.BALANCED:
            # Simple average
            return {stat: (stats1[stat] + stats2[stat]) // 2 for stat in stats1}
        
        elif method == FusionMethod.DOMINANT:
            # First Pokemon is dominant (70-30 split)
            return {
                stat: int(stats1[stat] * 0.7 + stats2[stat] * 0.3) 
                for stat in stats1
            }
        
        elif method == FusionMethod.HYBRID:
            # Complex weighted fusion based on stat roles
            fused_stats = {}
            
            # Identify stat strengths
            total1 = sum(stats1.values())
            total2 = sum(stats2.values())
            
            for stat in stats1:
                # Weight based on relative strength in each Pokemon
                weight1 = stats1[stat] / total1
                weight2 = stats2[stat] / total2
                
                # Boost the higher weighted stat
                if weight1 > weight2:
                    fused_stats[stat] = int(stats1[stat] * 0.6 + stats2[stat] * 0.4)
                else:
                    fused_stats[stat] = int(stats1[stat] * 0.4 + stats2[stat] * 0.6)
            
            return fused_stats
        
        elif method == FusionMethod.RANDOM:
            # Random fusion with controlled chaos
            fused_stats = {}
            for stat in stats1:
                # Random weight between 0.2 and 0.8
                weight = random.uniform(0.2, 0.8)
                fused_stats[stat] = int(stats1[stat] * weight + stats2[stat] * (1 - weight))
            
            return fused_stats
        
        # Fallback to balanced
        return {stat: (stats1[stat] + stats2[stat]) // 2 for stat in stats1}
    
    def _fuse_abilities(self, abilities1: List[str], abilities2: List[str]) -> List[str]:
        """Combine abilities from both Pokemon."""
        all_abilities = abilities1 + abilities2
        unique_abilities = list(dict.fromkeys(all_abilities))
        
        # Pokemon typically have 1-3 abilities
        if len(unique_abilities) <= 3:
            return unique_abilities
        
        # If too many, prioritize more unique/powerful abilities
        ability_priority = {
            "Wonder Guard": 100, "Pure Power": 95, "Huge Power": 95,
            "Magic Guard": 90, "Levitate": 85, "Multiscale": 80,
            "Speed Boost": 75, "Regenerator": 70, "Intimidate": 65,
            "Drought": 60, "Drizzle": 60, "Sand Stream": 60,
            "Chlorophyll": 55, "Swift Swim": 55, "Solar Power": 50
        }
        
        scored_abilities = sorted(
            unique_abilities, 
            key=lambda a: ability_priority.get(a, 25), 
            reverse=True
        )
        
        return scored_abilities[:3]
    
    def _create_fusion_moveset(self, moves1: List[str], moves2: List[str]) -> List[str]:
        """Create a fusion moveset combining signature moves."""
        # Combine signature moves
        all_moves = moves1 + moves2
        unique_moves = list(dict.fromkeys(all_moves))
        
        # Add some fusion-specific moves based on type combinations
        fusion_moves = []
        
        # Type-based fusion moves
        type_fusion_moves = {
            ("Fire", "Electric"): ["Thunder Punch", "Flame Charge"],
            ("Water", "Grass"): ["Giga Drain", "Scald"],
            ("Fire", "Flying"): ["Heat Wave", "Aerial Ace"],
            ("Water", "Ice"): ["Ice Beam", "Surf"],
            ("Electric", "Steel"): ["Magnet Rise", "Thunder Wave"],
            ("Ghost", "Dark"): ["Shadow Sneak", "Sucker Punch"],
            ("Dragon", "Flying"): ["Air Slash", "Dragon Rush"],
            ("Psychic", "Fighting"): ["Zen Headbutt", "Focus Blast"]
        }
        
        # Add fusion moves (this would need type information)
        # For now, just return the combined unique moves
        return unique_moves[:8]  # Limit to 8 moves
    
    def _generate_fusion_description(
        self, 
        name1: str, 
        name2: str, 
        data1: Dict, 
        data2: Dict
    ) -> str:
        """Generate a descriptive text for the fusion."""
        
        # Combine personality traits
        traits1 = data1.get("personality_traits", [])
        traits2 = data2.get("personality_traits", [])
        combined_traits = list(set(traits1 + traits2))
        
        # Select 2-3 traits
        selected_traits = random.sample(combined_traits, min(3, len(combined_traits)))
        traits_text = ", ".join(selected_traits)
        
        # Generate description templates
        templates = [
            f"A remarkable fusion combining the best qualities of {name1} and {name2}. This Pokemon is known for being {traits_text}.",
            f"Born from the mystical union of {name1} and {name2}, this creature embodies {traits_text} characteristics.",
            f"This unique hybrid Pokemon merges {name1}'s abilities with {name2}'s strengths, resulting in a {traits_text} companion.",
            f"A legendary fusion of {name1} and {name2}, displaying {traits_text} behavior in battle and friendship.",
        ]
        
        return random.choice(templates)
    
    def _calculate_fusion_rarity(self, data1: Dict, data2: Dict, method: FusionMethod) -> str:
        """Calculate the rarity tier of the fusion."""
        rarity_scores = {
            "common": 1, "uncommon": 2, "rare": 3, "legendary": 4, "mythical": 5
        }
        
        score1 = rarity_scores.get(data1.get("rarity", "common"), 1)
        score2 = rarity_scores.get(data2.get("rarity", "common"), 1)
        
        # Average the rarity scores
        avg_score = (score1 + score2) / 2
        
        # Method bonus
        method_bonus = {
            FusionMethod.BALANCED: 0.5,
            FusionMethod.DOMINANT: 0.3,
            FusionMethod.HYBRID: 1.0,
            FusionMethod.RANDOM: 0.8
        }.get(method, 0.5)
        
        final_score = avg_score + method_bonus
        
        if final_score >= 4.5:
            return "Mythical Fusion"
        elif final_score >= 3.5:
            return "Legendary Fusion"
        elif final_score >= 2.5:
            return "Rare Fusion"
        elif final_score >= 1.5:
            return "Uncommon Fusion"
        else:
            return "Common Fusion"
    
    def _create_color_scheme(
        self, 
        primary1: str, secondary1: str, 
        primary2: str, secondary2: str
    ) -> Dict[str, str]:
        """Create a fusion color scheme."""
        
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        def blend_colors(color1, color2, ratio=0.5):
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            blended = tuple(
                rgb1[i] * ratio + rgb2[i] * (1 - ratio) 
                for i in range(3)
            )
            
            return rgb_to_hex(blended)
        
        # Create blended colors
        fusion_primary = blend_colors(primary1, primary2)
        fusion_secondary = blend_colors(secondary1, secondary2)
        
        # Create additional accent colors
        accent1 = blend_colors(primary1, secondary2)
        accent2 = blend_colors(primary2, secondary1)
        
        return {
            "primary": fusion_primary,
            "secondary": fusion_secondary,
            "accent1": accent1,
            "accent2": accent2,
            "base1_primary": primary1,
            "base1_secondary": secondary1,
            "base2_primary": primary2,
            "base2_secondary": secondary2
        }
    
    def generate_random_fusion(self) -> FusedPokemon:
        """Generate a completely random fusion."""
        pokemon_names = list(self.pokemon_database.keys())
        
        # Select two different Pokemon
        selected = random.sample(pokemon_names, 2)
        method = random.choice(list(FusionMethod))
        
        return self.create_fusion(selected[0], selected[1], method)
    
    def get_fusion_recommendations(self, base_pokemon: str) -> List[Tuple[str, float]]:
        """Get fusion recommendations for a base Pokemon."""
        if base_pokemon not in self.pokemon_database:
            return []
        
        base_data = self.pokemon_database[base_pokemon]
        recommendations = []
        
        for other_pokemon, other_data in self.pokemon_database.items():
            if other_pokemon == base_pokemon:
                continue
            
            # Calculate compatibility score
            compatibility = self._calculate_fusion_compatibility(base_data, other_data)
            recommendations.append((other_pokemon, compatibility))
        
        # Sort by compatibility score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _calculate_fusion_compatibility(self, data1: Dict, data2: Dict) -> float:
        """Calculate how well two Pokemon would fuse together."""
        score = 0
        
        # Type synergy
        types1 = set(data1["types"])
        types2 = set(data2["types"])
        
        # Bonus for complementary types
        complementary_pairs = [
            ("Fire", "Water"), ("Electric", "Water"), ("Grass", "Fire"),
            ("Ice", "Fire"), ("Dragon", "Steel"), ("Ghost", "Fighting"),
            ("Psychic", "Dark"), ("Flying", "Ground")
        ]
        
        for type1 in types1:
            for type2 in types2:
                if (type1, type2) in complementary_pairs or (type2, type1) in complementary_pairs:
                    score += 20
        
        # Stat complementarity
        stats1 = data1["stats"]
        stats2 = data2["stats"]
        
        # Reward combinations where one Pokemon's weak stats are covered by the other's strong stats
        for stat in stats1:
            if stats1[stat] < 60 and stats2[stat] > 100:
                score += 10
            elif stats1[stat] > 100 and stats2[stat] < 60:
                score += 10
        
        # Habitat diversity
        if data1.get("habitat") != data2.get("habitat"):
            score += 5
        
        # Rarity combination bonus
        rarity_bonus = {
            ("common", "rare"): 8,
            ("common", "legendary"): 15,
            ("rare", "legendary"): 12,
            ("rare", "rare"): 10
        }
        
        rarity_pair = (data1.get("rarity", "common"), data2.get("rarity", "common"))
        score += rarity_bonus.get(rarity_pair, 0)
        score += rarity_bonus.get((rarity_pair[1], rarity_pair[0]), 0)
        
        return min(100, score)
    
    def export_fusion_data(self, fusion: FusedPokemon) -> Dict[str, Any]:
        """Export fusion data for sharing or storage."""
        return {
            "name": fusion.name,
            "base_pokemon": [fusion.base_pokemon1, fusion.base_pokemon2],
            "types": fusion.types,
            "stats": fusion.stats,
            "abilities": fusion.abilities,
            "moves": fusion.moves,
            "description": fusion.description,
            "fusion_method": fusion.fusion_method.value,
            "rarity_tier": fusion.rarity_tier,
            "color_scheme": fusion.color_scheme,
            "total_stats": sum(fusion.stats.values()),
            "created_date": "2025-10-25"  # Could be dynamic
        }
    
    def get_fusion_stats(self) -> Dict[str, Any]:
        """Get statistics about created fusions."""
        if not self.fusion_history:
            return {"total_fusions": 0}
        
        total_fusions = len(self.fusion_history)
        
        # Method distribution
        method_counts = {}
        for fusion in self.fusion_history:
            method = fusion.fusion_method.value
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # Rarity distribution
        rarity_counts = {}
        for fusion in self.fusion_history:
            rarity = fusion.rarity_tier
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        # Most used Pokemon
        pokemon_usage = {}
        for fusion in self.fusion_history:
            for pokemon in [fusion.base_pokemon1, fusion.base_pokemon2]:
                pokemon_usage[pokemon] = pokemon_usage.get(pokemon, 0) + 1
        
        most_used = sorted(pokemon_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_fusions": total_fusions,
            "method_distribution": method_counts,
            "rarity_distribution": rarity_counts,
            "most_used_pokemon": most_used,
            "average_total_stats": sum(sum(f.stats.values()) for f in self.fusion_history) / total_fusions
        }


# Example usage and demonstration
def demonstrate_fusion_system():
    """Demonstrate the Pokemon Fusion Generator."""
    print("🧬 Pokemon Fusion Generator Demo")
    print("=" * 50)
    
    # Initialize the fusion generator
    generator = PokemonFusionGenerator()
    
    # Create some example fusions
    fusions = [
        generator.create_fusion("Pikachu", "Charizard", FusionMethod.BALANCED),
        generator.create_fusion("Blastoise", "Venusaur", FusionMethod.HYBRID),
        generator.create_fusion("Alakazam", "Machamp", FusionMethod.DOMINANT),
        generator.generate_random_fusion()
    ]
    
    # Display the fusions
    for i, fusion in enumerate(fusions, 1):
        print(f"\n🔥 FUSION #{i}: {fusion.name}")
        print("-" * 40)
        print(f"Base Pokemon: {fusion.base_pokemon1} + {fusion.base_pokemon2}")
        print(f"Types: {' / '.join(fusion.types)}")
        print(f"Method: {fusion.fusion_method.value.title()}")
        print(f"Rarity: {fusion.rarity_tier}")
        
        print(f"\n📊 Stats:")
        for stat, value in fusion.stats.items():
            print(f"  {stat.replace('_', ' ').title()}: {value}")
        print(f"  Total: {sum(fusion.stats.values())}")
        
        print(f"\n⚡ Abilities: {', '.join(fusion.abilities)}")
        print(f"🎯 Signature Moves: {', '.join(fusion.moves[:4])}")
        
        print(f"\n🎨 Color Scheme:")
        print(f"  Primary: {fusion.color_scheme['primary']}")
        print(f"  Secondary: {fusion.color_scheme['secondary']}")
        
        print(f"\n📖 Description:")
        print(f"  {fusion.description}")
    
    # Show fusion statistics
    print(f"\n📊 FUSION STATISTICS")
    print("-" * 40)
    stats = generator.get_fusion_stats()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Show recommendations
    print(f"\n💡 FUSION RECOMMENDATIONS FOR PIKACHU")
    print("-" * 40)
    recommendations = generator.get_fusion_recommendations("Pikachu")
    for pokemon, score in recommendations:
        print(f"  {pokemon}: {score:.1f}% compatibility")

if __name__ == "__main__":
    demonstrate_fusion_system()