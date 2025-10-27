"""
Pokemon Save File Import System.
Supports importing Pokemon teams and data from various game save files.
"""

import struct
import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from src.core.pokemon import Pokemon
from src.core.types import PokemonType
from src.core.moves import Move, MoveCategory
from src.core.abilities import Ability
from src.teambuilder.team import PokemonTeam

logger = logging.getLogger(__name__)

class GameGeneration(Enum):
    """Pokemon game generations."""
    GEN_3 = "gen3"  # Ruby/Sapphire/Emerald, FireRed/LeafGreen
    GEN_4 = "gen4"  # Diamond/Pearl/Platinum, HeartGold/SoulSilver
    GEN_5 = "gen5"  # Black/White, Black2/White2
    GEN_6 = "gen6"  # X/Y, Omega Ruby/Alpha Sapphire
    GEN_7 = "gen7"  # Sun/Moon, Ultra Sun/Ultra Moon
    GEN_8 = "gen8"  # Sword/Shield
    GEN_9 = "gen9"  # Scarlet/Violet

class SaveFileFormat(Enum):
    """Save file formats."""
    SAV = "sav"      # Standard save file
    PKM = "pkm"      # Individual Pokemon file
    PK3 = "pk3"      # Gen 3 Pokemon
    PK4 = "pk4"      # Gen 4 Pokemon
    PK5 = "pk5"      # Gen 5 Pokemon
    PK6 = "pk6"      # Gen 6 Pokemon
    PK7 = "pk7"      # Gen 7 Pokemon
    PK8 = "pk8"      # Gen 8 Pokemon
    PK9 = "pk9"      # Gen 9 Pokemon

@dataclass
class SaveFileInfo:
    """Information about a save file."""
    file_path: str
    game_generation: GameGeneration
    file_format: SaveFileFormat
    game_version: str
    trainer_name: str
    trainer_id: int
    play_time: str
    pokemon_count: int
    is_valid: bool = True
    error_message: str = ""

@dataclass
class ImportedPokemon:
    """Pokemon data imported from save file."""
    species_id: int
    species_name: str
    nickname: str
    level: int
    experience: int
    nature: str
    ability: str
    held_item: str
    
    # Stats
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    
    # IVs
    hp_iv: int
    attack_iv: int
    defense_iv: int
    sp_attack_iv: int
    sp_defense_iv: int
    speed_iv: int
    
    # EVs
    hp_ev: int
    attack_ev: int
    defense_ev: int
    sp_attack_ev: int
    sp_defense_ev: int
    speed_ev: int
    
    # Moves
    moves: List[str]
    
    # Other data
    gender: str
    is_shiny: bool
    pokeball: str
    original_trainer: str
    trainer_id: int
    location_met: str
    level_met: int
    is_egg: bool = False
    
    def to_pokemon(self) -> Pokemon:
        """Convert to Pokemon object."""
        # Create basic Pokemon
        pokemon = Pokemon(
            name=self.species_name,
            types=[PokemonType.NORMAL],  # Will be updated with correct types
            stats={
                'hp': self.hp,
                'attack': self.attack,
                'defense': self.defense,
                'sp_attack': self.sp_attack,
                'sp_defense': self.sp_defense,
                'speed': self.speed
            }
        )
        
        # Set additional properties
        pokemon.level = self.level
        pokemon.nickname = self.nickname if self.nickname != self.species_name else ""
        pokemon.nature = self.nature
        pokemon.ability = self.ability
        pokemon.held_item = self.held_item
        pokemon.is_shiny = self.is_shiny
        
        # Set IVs
        pokemon.ivs = {
            'hp': self.hp_iv,
            'attack': self.attack_iv,
            'defense': self.defense_iv,
            'sp_attack': self.sp_attack_iv,
            'sp_defense': self.sp_defense_iv,
            'speed': self.speed_iv
        }
        
        # Set EVs
        pokemon.evs = {
            'hp': self.hp_ev,
            'attack': self.attack_ev,
            'defense': self.defense_ev,
            'sp_attack': self.sp_attack_ev,
            'sp_defense': self.sp_defense_ev,
            'speed': self.speed_ev
        }
        
        # Set moves (convert to Move objects)
        pokemon.moves = []
        for move_name in self.moves:
            if move_name and move_name != "---":
                move = Move(
                    name=move_name,
                    type=PokemonType.NORMAL,  # Will be updated
                    category=MoveCategory.PHYSICAL,  # Will be updated
                    power=50,  # Default values
                    accuracy=100,
                    pp=20
                )
                pokemon.moves.append(move)
        
        return pokemon

class SaveFileParser:
    """Base class for save file parsers."""
    
    def __init__(self):
        self.species_names = self._load_species_names()
        self.move_names = self._load_move_names()
        self.ability_names = self._load_ability_names()
        self.item_names = self._load_item_names()
        self.nature_names = [
            "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
            "Bold", "Docile", "Relaxed", "Impish", "Lax",
            "Timid", "Hasty", "Serious", "Jolly", "Naive",
            "Modest", "Mild", "Quiet", "Bashful", "Rash",
            "Calm", "Gentle", "Sassy", "Careful", "Quirky"
        ]
    
    def _load_species_names(self) -> Dict[int, str]:
        """Load Pokemon species names."""
        # Simplified species list - in a real implementation, 
        # this would load from comprehensive data files
        return {
            1: "Bulbasaur", 2: "Ivysaur", 3: "Venusaur",
            4: "Charmander", 5: "Charmeleon", 6: "Charizard",
            7: "Squirtle", 8: "Wartortle", 9: "Blastoise",
            25: "Pikachu", 26: "Raichu", 150: "Mewtwo",
            151: "Mew", 249: "Lugia", 250: "Ho-Oh"
            # ... would include all Pokemon
        }
    
    def _load_move_names(self) -> Dict[int, str]:
        """Load move names."""
        return {
            1: "Pound", 2: "Karate Chop", 3: "Double Slap",
            4: "Comet Punch", 5: "Mega Punch", 6: "Pay Day",
            7: "Fire Punch", 8: "Ice Punch", 9: "Thunder Punch",
            10: "Scratch", 33: "Tackle", 52: "Ember",
            55: "Water Gun", 71: "Absorb", 85: "Thunderbolt"
            # ... would include all moves
        }
    
    def _load_ability_names(self) -> Dict[int, str]:
        """Load ability names."""
        return {
            1: "Stench", 2: "Drizzle", 3: "Speed Boost",
            4: "Battle Armor", 5: "Sturdy", 6: "Damp",
            7: "Limber", 8: "Sand Veil", 9: "Static",
            10: "Volt Absorb", 11: "Water Absorb", 12: "Oblivious"
            # ... would include all abilities
        }
    
    def _load_item_names(self) -> Dict[int, str]:
        """Load item names."""
        return {
            1: "Master Ball", 2: "Ultra Ball", 3: "Great Ball",
            4: "Poke Ball", 5: "Safari Ball", 12: "Super Potion",
            13: "Hyper Potion", 17: "Full Heal", 45: "Leftovers",
            114: "Life Orb", 135: "Choice Scarf", 136: "Choice Specs"
            # ... would include all items
        }
    
    def detect_save_format(self, file_path: str) -> Optional[SaveFileInfo]:
        """Detect save file format and game version."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            file_size = len(data)
            file_ext = Path(file_path).suffix.lower()
            
            # Detect based on file size and extension
            if file_ext == '.sav':
                return self._detect_sav_format(file_path, data, file_size)
            elif file_ext in ['.pkm', '.pk3', '.pk4', '.pk5', '.pk6', '.pk7', '.pk8', '.pk9']:
                return self._detect_pkm_format(file_path, data, file_ext)
            else:
                return SaveFileInfo(
                    file_path=file_path,
                    game_generation=GameGeneration.GEN_3,
                    file_format=SaveFileFormat.SAV,
                    game_version="Unknown",
                    trainer_name="Unknown",
                    trainer_id=0,
                    play_time="00:00",
                    pokemon_count=0,
                    is_valid=False,
                    error_message="Unsupported file format"
                )
                
        except Exception as e:
            logger.error(f"Error detecting save format: {e}")
            return None
    
    def _detect_sav_format(self, file_path: str, data: bytes, file_size: int) -> SaveFileInfo:
        """Detect SAV file format based on size."""
        size_to_gen = {
            # Gen 3
            128 * 1024: (GameGeneration.GEN_3, "Ruby/Sapphire/Emerald"),
            128 * 1024: (GameGeneration.GEN_3, "FireRed/LeafGreen"),
            
            # Gen 4  
            524288: (GameGeneration.GEN_4, "Diamond/Pearl/Platinum"),
            524288: (GameGeneration.GEN_4, "HeartGold/SoulSilver"),
            
            # Gen 5
            524288: (GameGeneration.GEN_5, "Black/White"),
            524288: (GameGeneration.GEN_5, "Black2/White2"),
            
            # Gen 6+
            415232: (GameGeneration.GEN_6, "X/Y"),
            441856: (GameGeneration.GEN_6, "Omega Ruby/Alpha Sapphire"),
            441856: (GameGeneration.GEN_7, "Sun/Moon"),
            441856: (GameGeneration.GEN_7, "Ultra Sun/Ultra Moon")
        }
        
        if file_size in size_to_gen:
            generation, game_version = size_to_gen[file_size]
        else:
            # Default to Gen 3 for unknown sizes
            generation = GameGeneration.GEN_3
            game_version = "Unknown"
        
        # Extract basic info (simplified)
        trainer_name = "Trainer"  # Would extract from save data
        trainer_id = 12345  # Would extract from save data
        play_time = "999:59"  # Would extract from save data
        pokemon_count = 6  # Would count actual Pokemon
        
        return SaveFileInfo(
            file_path=file_path,
            game_generation=generation,
            file_format=SaveFileFormat.SAV,
            game_version=game_version,
            trainer_name=trainer_name,
            trainer_id=trainer_id,
            play_time=play_time,
            pokemon_count=pokemon_count
        )
    
    def _detect_pkm_format(self, file_path: str, data: bytes, file_ext: str) -> SaveFileInfo:
        """Detect PKM file format."""
        ext_to_gen = {
            '.pk3': (GameGeneration.GEN_3, SaveFileFormat.PK3),
            '.pk4': (GameGeneration.GEN_4, SaveFileFormat.PK4),
            '.pk5': (GameGeneration.GEN_5, SaveFileFormat.PK5),
            '.pk6': (GameGeneration.GEN_6, SaveFileFormat.PK6),
            '.pk7': (GameGeneration.GEN_7, SaveFileFormat.PK7),
            '.pk8': (GameGeneration.GEN_8, SaveFileFormat.PK8),
            '.pk9': (GameGeneration.GEN_9, SaveFileFormat.PK9),
            '.pkm': (GameGeneration.GEN_3, SaveFileFormat.PKM)  # Default
        }
        
        generation, format_type = ext_to_gen.get(file_ext, (GameGeneration.GEN_3, SaveFileFormat.PKM))
        
        return SaveFileInfo(
            file_path=file_path,
            game_generation=generation,
            file_format=format_type,
            game_version=f"Generation {generation.value.replace('gen', '')}",
            trainer_name="Individual Pokemon",
            trainer_id=0,
            play_time="N/A",
            pokemon_count=1
        )

class Gen3Parser(SaveFileParser):
    """Parser for Generation 3 save files."""
    
    def parse_save_file(self, file_path: str) -> List[ImportedPokemon]:
        """Parse Generation 3 save file."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            pokemon_list = []
            
            # Gen 3 party Pokemon start at different offsets
            # This is a simplified implementation
            party_offset = 0x234  # Example offset for party Pokemon
            
            for i in range(6):  # Party has max 6 Pokemon
                pokemon_offset = party_offset + (i * 100)  # 100 bytes per Pokemon
                
                if pokemon_offset + 100 <= len(data):
                    pokemon_data = data[pokemon_offset:pokemon_offset + 100]
                    pokemon = self._parse_gen3_pokemon(pokemon_data)
                    
                    if pokemon and pokemon.species_id > 0:
                        pokemon_list.append(pokemon)
            
            return pokemon_list
            
        except Exception as e:
            logger.error(f"Error parsing Gen 3 save file: {e}")
            return []
    
    def _parse_gen3_pokemon(self, data: bytes) -> Optional[ImportedPokemon]:
        """Parse individual Gen 3 Pokemon data."""
        if len(data) < 100:
            return None
        
        try:
            # Gen 3 Pokemon structure (simplified)
            # This would need to be implemented according to actual save format
            
            # Species ID (bytes 0-1)
            species_id = struct.unpack('<H', data[0:2])[0]
            
            if species_id == 0 or species_id > 386:  # Gen 3 has Pokemon 1-386
                return None
            
            # Basic data extraction (example offsets)
            level = data[84] if len(data) > 84 else 1
            
            # Stats (example calculation)
            hp = struct.unpack('<H', data[86:88])[0] if len(data) >= 88 else 100
            attack = struct.unpack('<H', data[88:90])[0] if len(data) >= 90 else 100
            defense = struct.unpack('<H', data[90:92])[0] if len(data) >= 92 else 100
            sp_attack = struct.unpack('<H', data[92:94])[0] if len(data) >= 94 else 100
            sp_defense = struct.unpack('<H', data[94:96])[0] if len(data) >= 96 else 100
            speed = struct.unpack('<H', data[96:98])[0] if len(data) >= 98 else 100
            
            # IVs and EVs (would be calculated from actual data)
            # For now, using example values
            ivs = [15, 15, 15, 15, 15, 15]  # Example IVs
            evs = [0, 0, 0, 0, 0, 0]  # Example EVs
            
            # Other data
            species_name = self.species_names.get(species_id, f"Unknown #{species_id}")
            nickname = species_name  # Would decode actual nickname
            nature = self.nature_names[0]  # Would calculate from personality value
            ability = "Unknown"  # Would determine from species and personality
            held_item = ""  # Would extract from item ID
            
            moves = ["Tackle", "---", "---", "---"]  # Would extract actual moves
            
            return ImportedPokemon(
                species_id=species_id,
                species_name=species_name,
                nickname=nickname,
                level=level,
                experience=0,  # Would calculate
                nature=nature,
                ability=ability,
                held_item=held_item,
                hp=hp,
                attack=attack,
                defense=defense,
                sp_attack=sp_attack,
                sp_defense=sp_defense,
                speed=speed,
                hp_iv=ivs[0],
                attack_iv=ivs[1],
                defense_iv=ivs[2],
                sp_attack_iv=ivs[3],
                sp_defense_iv=ivs[4],
                speed_iv=ivs[5],
                hp_ev=evs[0],
                attack_ev=evs[1],
                defense_ev=evs[2],
                sp_attack_ev=evs[3],
                sp_defense_ev=evs[4],
                speed_ev=evs[5],
                moves=moves,
                gender="Unknown",
                is_shiny=False,
                pokeball="Poke Ball",
                original_trainer="Trainer",
                trainer_id=12345,
                location_met="Unknown",
                level_met=5
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gen 3 Pokemon: {e}")
            return None

class SaveFileImporter:
    """Main save file import manager."""
    
    def __init__(self):
        self.parsers = {
            GameGeneration.GEN_3: Gen3Parser(),
            GameGeneration.GEN_4: Gen3Parser(),  # Placeholder - would implement Gen4Parser
            GameGeneration.GEN_5: Gen3Parser(),  # Placeholder - would implement Gen5Parser
            GameGeneration.GEN_6: Gen3Parser(),  # Placeholder - would implement Gen6Parser
            GameGeneration.GEN_7: Gen3Parser(),  # Placeholder - would implement Gen7Parser
            GameGeneration.GEN_8: Gen3Parser(),  # Placeholder - would implement Gen8Parser
            GameGeneration.GEN_9: Gen3Parser(),  # Placeholder - would implement Gen9Parser
        }
    
    def analyze_save_file(self, file_path: str) -> Optional[SaveFileInfo]:
        """Analyze a save file and return information about it."""
        if not os.path.exists(file_path):
            return None
        
        parser = SaveFileParser()
        return parser.detect_save_format(file_path)
    
    def import_pokemon_from_save(self, file_path: str) -> Tuple[List[ImportedPokemon], SaveFileInfo]:
        """Import Pokemon from a save file."""
        # Analyze the save file first
        save_info = self.analyze_save_file(file_path)
        
        if not save_info or not save_info.is_valid:
            return [], save_info or SaveFileInfo(
                file_path=file_path,
                game_generation=GameGeneration.GEN_3,
                file_format=SaveFileFormat.SAV,
                game_version="Unknown",
                trainer_name="Unknown",
                trainer_id=0,
                play_time="00:00",
                pokemon_count=0,
                is_valid=False,
                error_message="Invalid save file"
            )
        
        # Get appropriate parser
        parser = self.parsers.get(save_info.game_generation)
        if not parser:
            save_info.is_valid = False
            save_info.error_message = f"No parser available for {save_info.game_generation.value}"
            return [], save_info
        
        # Parse Pokemon data
        try:
            if save_info.file_format == SaveFileFormat.SAV:
                pokemon_list = parser.parse_save_file(file_path)
            else:
                # Individual Pokemon file
                pokemon_list = parser.parse_save_file(file_path)
            
            logger.info(f"Imported {len(pokemon_list)} Pokemon from {file_path}")
            return pokemon_list, save_info
            
        except Exception as e:
            logger.error(f"Error importing Pokemon: {e}")
            save_info.is_valid = False
            save_info.error_message = str(e)
            return [], save_info
    
    def create_team_from_imported(self, imported_pokemon: List[ImportedPokemon], 
                                 team_name: str = "Imported Team") -> PokemonTeam:
        """Create a PokemonTeam from imported Pokemon."""
        team = PokemonTeam(name=team_name)
        
        for imported in imported_pokemon[:6]:  # Max 6 Pokemon per team
            pokemon = imported.to_pokemon()
            team.add_pokemon(pokemon)
        
        return team
    
    def export_import_summary(self, imported_pokemon: List[ImportedPokemon], 
                            save_info: SaveFileInfo) -> Dict[str, Any]:
        """Create a summary of the import process."""
        return {
            'save_file_info': {
                'file_path': save_info.file_path,
                'game_generation': save_info.game_generation.value,
                'game_version': save_info.game_version,
                'trainer_name': save_info.trainer_name,
                'trainer_id': save_info.trainer_id,
                'play_time': save_info.play_time,
                'is_valid': save_info.is_valid,
                'error_message': save_info.error_message
            },
            'import_results': {
                'pokemon_imported': len(imported_pokemon),
                'import_successful': save_info.is_valid,
                'pokemon_list': [
                    {
                        'species': pokemon.species_name,
                        'nickname': pokemon.nickname,
                        'level': pokemon.level,
                        'nature': pokemon.nature,
                        'ability': pokemon.ability,
                        'is_shiny': pokemon.is_shiny,
                        'moves': pokemon.moves
                    }
                    for pokemon in imported_pokemon
                ]
            },
            'timestamp': 'October 25, 2025'
        }

# Example usage and testing
if __name__ == "__main__":
    # Create importer
    importer = SaveFileImporter()
    
    # Example: Analyze a save file (this would be a real file path)
    example_save_path = "pokemon_ruby.sav"
    
    # This would work with a real save file:
    # save_info = importer.analyze_save_file(example_save_path)
    # if save_info and save_info.is_valid:
    #     pokemon_list, save_info = importer.import_pokemon_from_save(example_save_path)
    #     
    #     if pokemon_list:
    #         team = importer.create_team_from_imported(pokemon_list, "My Ruby Team")
    #         summary = importer.export_import_summary(pokemon_list, save_info)
    #         
    #         print(f"Imported team '{team.name}' with {len(team.pokemon)} Pokemon")
    #         print(f"Summary: {json.dumps(summary, indent=2)}")
    
    print("Save file importer system ready!")
    print("Supported formats:")
    for gen in GameGeneration:
        print(f"  - {gen.value.upper()}: Generation {gen.value.replace('gen', '')}")
    
    print("\nSupported file types:")
    for fmt in SaveFileFormat:
        print(f"  - .{fmt.value}: {fmt.value.upper()} files")