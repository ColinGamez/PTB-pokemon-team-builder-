"""
Sprite Manager for Pokemon Team Builder
Handles loading and caching Pokemon sprites from various generations.
"""

import os
from typing import Optional, Dict, Tuple
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk
import logging

logger = logging.getLogger(__name__)


class SpriteManager:
    """Manages Pokemon sprite loading and caching."""
    
    # Sprite generations available
    GENERATIONS = {
        'red-blue': 'Generation I (Red/Blue)',
        'red-green': 'Generation I (Red/Green)',
        'yellow': 'Generation I (Yellow)',
        'gold': 'Generation II (Gold)',
        'silver': 'Generation II (Silver)',
        'crystal': 'Generation II (Crystal)',
        'ruby-sapphire': 'Generation III (Ruby/Sapphire)',
        'emerald': 'Generation III (Emerald)',
        'firered-leafgreen': 'Generation III (FireRed/LeafGreen)',
        'diamond-pearl': 'Generation IV (Diamond/Pearl)',
        'platinum': 'Generation IV (Platinum)',
        'heartgold-soulsilver': 'Generation IV (HeartGold/SoulSilver)',
        'black-white': 'Generation V (Black/White)'
    }
    
    def __init__(self, sprites_base_path: Optional[str] = None):
        """
        Initialize the sprite manager.
        
        Args:
            sprites_base_path: Base path to sprites directory. 
                             Defaults to ../../Sprites/pokemon/main-sprites
        """
        if sprites_base_path is None:
            # Default path relative to this file
            project_root = Path(__file__).parent.parent.parent.parent
            sprites_base_path = project_root / "Sprites" / "pokemon" / "main-sprites"
        
        self.sprites_path = Path(sprites_base_path)
        self.cache: Dict[Tuple[int, str, bool, bool], ImageTk.PhotoImage] = {}
        self.default_generation = 'black-white'  # Modern looking sprites
        
        # Verify sprites directory exists
        if not self.sprites_path.exists():
            logger.warning(f"Sprites directory not found: {self.sprites_path}")
    
    def get_sprite(
        self, 
        pokemon_id: int, 
        generation: Optional[str] = None,
        shiny: bool = False,
        female: bool = False,
        variant: Optional[str] = None,
        size: Optional[Tuple[int, int]] = None
    ) -> Optional[ImageTk.PhotoImage]:
        """
        Get a Pokemon sprite.
        
        Args:
            pokemon_id: Pokemon National Dex number (1-649 for BW)
            generation: Generation folder name (e.g., 'black-white')
            shiny: Whether to load shiny variant
            female: Whether to load female variant
            variant: Specific variant (e.g., 'mega', 'alola', form names)
            size: Optional resize tuple (width, height)
            
        Returns:
            PIL ImageTk.PhotoImage or None if not found
        """
        if generation is None:
            generation = self.default_generation
        
        # Check cache
        cache_key = (pokemon_id, generation, shiny, female)
        if cache_key in self.cache and size is None:
            return self.cache[cache_key]
        
        # Build sprite path
        gen_path = self.sprites_path / generation
        
        # Determine subfolder based on variant type
        subfolder = ""
        if shiny and female:
            subfolder = "shiny/female"
        elif shiny:
            subfolder = "shiny"
        elif female:
            subfolder = "female"
        
        # Build filename
        if variant:
            filename = f"{pokemon_id}-{variant}.png"
        else:
            filename = f"{pokemon_id}.png"
        
        # Try to load sprite
        sprite_path = gen_path / subfolder / filename if subfolder else gen_path / filename
        
        if not sprite_path.exists():
            # Fallback: try without variant
            sprite_path = gen_path / subfolder / f"{pokemon_id}.png" if subfolder else gen_path / f"{pokemon_id}.png"
        
        if not sprite_path.exists():
            # Fallback: try default generation
            if generation != self.default_generation:
                return self.get_sprite(pokemon_id, self.default_generation, shiny, female, variant, size)
            logger.warning(f"Sprite not found: {sprite_path}")
            return None
        
        try:
            # Load and convert image
            img = Image.open(sprite_path)
            
            # Resize if requested
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Cache it
            if size is None:
                self.cache[cache_key] = photo
            
            return photo
            
        except Exception as e:
            logger.error(f"Error loading sprite {sprite_path}: {e}")
            return None
    
    def get_sprite_by_name(
        self,
        pokemon_name: str,
        generation: Optional[str] = None,
        shiny: bool = False,
        female: bool = False,
        size: Optional[Tuple[int, int]] = None
    ) -> Optional[ImageTk.PhotoImage]:
        """
        Get a Pokemon sprite by name (requires pokemon_id lookup).
        
        Args:
            pokemon_name: Pokemon name (e.g., 'Pikachu')
            generation: Generation folder name
            shiny: Whether to load shiny variant
            female: Whether to load female variant
            size: Optional resize tuple
            
        Returns:
            PIL ImageTk.PhotoImage or None if not found
        """
        # This would require a name->ID mapping
        # For now, return None and require ID-based lookup
        logger.warning("get_sprite_by_name not yet implemented - use get_sprite with ID")
        return None
    
    def get_egg_sprite(self, generation: Optional[str] = None) -> Optional[ImageTk.PhotoImage]:
        """Get the egg sprite."""
        if generation is None:
            generation = self.default_generation
        
        gen_path = self.sprites_path / generation
        egg_path = gen_path / "egg.png"
        
        if not egg_path.exists():
            return None
        
        try:
            img = Image.open(egg_path)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"Error loading egg sprite: {e}")
            return None
    
    def get_substitute_sprite(self, generation: Optional[str] = None) -> Optional[ImageTk.PhotoImage]:
        """Get the substitute sprite."""
        if generation is None:
            generation = self.default_generation
        
        gen_path = self.sprites_path / generation
        sub_path = gen_path / "substitute.png"
        
        if not sub_path.exists():
            return None
        
        try:
            img = Image.open(sub_path)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"Error loading substitute sprite: {e}")
            return None
    
    def preload_generation(self, generation: str, max_id: int = 151):
        """
        Preload sprites for a generation to speed up initial display.
        
        Args:
            generation: Generation to preload
            max_id: Maximum Pokemon ID to preload (default Gen 1)
        """
        logger.info(f"Preloading {max_id} sprites from {generation}...")
        
        for pokemon_id in range(1, max_id + 1):
            self.get_sprite(pokemon_id, generation)
        
        logger.info(f"Preloaded {len(self.cache)} sprites")
    
    def clear_cache(self):
        """Clear the sprite cache to free memory."""
        self.cache.clear()
        logger.info("Sprite cache cleared")
    
    def get_available_generations(self) -> Dict[str, str]:
        """Get dictionary of available generation folders."""
        available = {}
        for gen_folder, gen_name in self.GENERATIONS.items():
            gen_path = self.sprites_path / gen_folder
            if gen_path.exists():
                available[gen_folder] = gen_name
        return available
    
    def set_default_generation(self, generation: str):
        """Set the default generation for sprite loading."""
        if generation in self.GENERATIONS:
            self.default_generation = generation
            logger.info(f"Default sprite generation set to: {generation}")
        else:
            logger.warning(f"Unknown generation: {generation}")


# Global sprite manager instance
_sprite_manager: Optional[SpriteManager] = None


def get_sprite_manager() -> SpriteManager:
    """Get or create the global sprite manager instance."""
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
    return _sprite_manager


# Convenience functions
def get_pokemon_sprite(
    pokemon_id: int,
    generation: Optional[str] = None,
    shiny: bool = False,
    female: bool = False,
    variant: Optional[str] = None,
    size: Optional[Tuple[int, int]] = None
) -> Optional[ImageTk.PhotoImage]:
    """Convenience function to get a Pokemon sprite."""
    manager = get_sprite_manager()
    return manager.get_sprite(pokemon_id, generation, shiny, female, variant, size)


def get_egg_sprite(generation: Optional[str] = None) -> Optional[ImageTk.PhotoImage]:
    """Convenience function to get egg sprite."""
    manager = get_sprite_manager()
    return manager.get_egg_sprite(generation)


def preload_sprites(generation: str = 'black-white', max_id: int = 151):
    """Convenience function to preload sprites."""
    manager = get_sprite_manager()
    manager.preload_generation(generation, max_id)


if __name__ == "__main__":
    # Test the sprite manager
    import tkinter as tk
    
    root = tk.Tk()
    root.title("Sprite Manager Test")
    
    manager = SpriteManager()
    
    # Test loading Pikachu
    pikachu_sprite = manager.get_sprite(25, 'black-white')
    if pikachu_sprite:
        label = tk.Label(root, image=pikachu_sprite)
        label.pack()
        label.image = pikachu_sprite  # Keep reference
        
        tk.Label(root, text="Pikachu (#25) - Black/White").pack()
    
    # Test loading shiny Charizard
    charizard_shiny = manager.get_sprite(6, 'black-white', shiny=True)
    if charizard_shiny:
        label2 = tk.Label(root, image=charizard_shiny)
        label2.pack()
        label2.image = charizard_shiny
        
        tk.Label(root, text="Charizard (#6) - Shiny").pack()
    
    root.mainloop()
