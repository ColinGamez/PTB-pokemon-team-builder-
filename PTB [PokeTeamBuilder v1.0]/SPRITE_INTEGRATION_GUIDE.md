# 🎨 Pokemon Sprite Integration Guide

## Overview
This guide explains how Pokemon sprites are integrated into the PokeTeamBuilder application, enabling visual representation of Pokemon across all GUI components.

## Sprite Directory Structure

### Location
```
C:\Users\Colin\Desktop\Pokemon\Sprites\pokemon\main-sprites\
```

### Available Generations
- `red-blue/` - Generation I (Red/Blue)
- `red-green/` - Generation I (Red/Green - Japanese)
- `yellow/` - Generation I (Yellow)
- `gold/` - Generation II (Gold)
- `silver/` - Generation II (Silver)
- `crystal/` - Generation II (Crystal)
- `ruby-sapphire/` - Generation III (Ruby/Sapphire)
- `emerald/` - Generation III (Emerald)
- `firered-leafgreen/` - Generation III (FireRed/LeafGreen)
- `diamond-pearl/` - Generation IV (Diamond/Pearl)
- `platinum/` - Generation IV (Platinum)
- `heartgold-soulsilver/` - Generation IV (HeartGold/SoulSilver)
- `black-white/` - Generation V (Black/White) **[DEFAULT]**

### Sprite Coverage (Black/White Generation)
- **Base Sprites**: Pokemon #0 - #649 (Complete Gen 1-5 coverage)
- **Form Variants**: 
  - Unown forms (201-a.png through 201-z.png)
  - Weather forms (Castform: 351-rainy/snowy/sunny.png)
  - Deoxys forms (386-attack/defense/normal/speed.png)
  - Regional forms (Shellos/Gastrodon: 422/423-east/west.png)
  - Rotom appliances (479-fan/frost/heat/mow/wash.png)
  - Giratina forms (487-altered/origin.png)
  - Shaymin forms (492-land/sky.png)
  - Arceus type plates (493-bug through 493-water.png - 17 variants)
  - Gen 5 forms (Darmanitan, Deerling, Sawsbuck, Forces of Nature, etc.)

### Special Sprite Types
- **Shiny Sprites**: `shiny/` subdirectory
- **Female Sprites**: `female/` subdirectory (for gender differences)
- **Back Sprites**: `back/` subdirectory (for battle back views)
- **Egg Sprites**: `egg.png`, `egg-manaphy.png`
- **Other**: `substitute.png`

## Sprite Manager Module

### Location
`src/utils/sprite_manager.py`

### Key Features

#### Initialization
```python
from src.utils.sprite_manager import get_sprite_manager

sprite_manager = get_sprite_manager()
```

#### Loading Pokemon Sprites
```python
# Basic usage - load Pokemon by ID
sprite = sprite_manager.get_sprite(pokemon_id=25)  # Pikachu

# With specific generation
sprite = sprite_manager.get_sprite(pokemon_id=25, generation='red-blue')

# Shiny variant
sprite = sprite_manager.get_sprite(pokemon_id=6, shiny=True)  # Shiny Charizard

# Female variant
sprite = sprite_manager.get_sprite(pokemon_id=3, female=True)  # Female Venusaur

# Form variant
sprite = sprite_manager.get_sprite(pokemon_id=351, variant='rainy')  # Rainy Castform

# Resized sprite
sprite = sprite_manager.get_sprite(pokemon_id=150, size=(100, 100))  # Mewtwo 100x100px
```

#### Convenience Functions
```python
from src.utils.sprite_manager import get_pokemon_sprite, get_egg_sprite, preload_sprites

# Quick sprite loading
pikachu = get_pokemon_sprite(25, shiny=False, size=(80, 80))

# Egg sprite
egg = get_egg_sprite()

# Preload sprites for faster initial display (Gen 1 example)
preload_sprites(generation='black-white', max_id=151)
```

#### Caching System
- Sprites are automatically cached after first load
- Reduces memory usage and improves performance
- Cache can be cleared with `sprite_manager.clear_cache()`

### Sprite Manager API Reference

#### `SpriteManager` Class

**Constructor**
```python
SpriteManager(sprites_base_path: Optional[str] = None)
```
- `sprites_base_path`: Custom path to sprites directory (defaults to `../../Sprites/pokemon/main-sprites`)

**Methods**

1. **`get_sprite()`**
   ```python
   get_sprite(
       pokemon_id: int,
       generation: Optional[str] = None,
       shiny: bool = False,
       female: bool = False,
       variant: Optional[str] = None,
       size: Optional[Tuple[int, int]] = None
   ) -> Optional[ImageTk.PhotoImage]
   ```
   - Returns: `ImageTk.PhotoImage` ready for Tkinter display, or `None` if not found
   - Automatically falls back to default generation if sprite not found

2. **`get_egg_sprite()`**
   ```python
   get_egg_sprite(generation: Optional[str] = None) -> Optional[ImageTk.PhotoImage]
   ```
   - Returns: Egg sprite image

3. **`get_substitute_sprite()`**
   ```python
   get_substitute_sprite(generation: Optional[str] = None) -> Optional[ImageTk.PhotoImage]
   ```
   - Returns: Substitute doll sprite

4. **`preload_generation()`**
   ```python
   preload_generation(generation: str, max_id: int = 151)
   ```
   - Preloads sprites into cache for faster display
   - Useful for initial app loading

5. **`clear_cache()`**
   ```python
   clear_cache()
   ```
   - Clears the sprite cache to free memory

6. **`get_available_generations()`**
   ```python
   get_available_generations() -> Dict[str, str]
   ```
   - Returns: Dictionary of available generation folders with descriptions

7. **`set_default_generation()`**
   ```python
   set_default_generation(generation: str)
   ```
   - Changes the default generation for sprite loading

## GUI Integration

### Team Builder Integration
**File**: `src/gui/team_builder_gui.py`

Sprites are displayed in the team slots showing:
- Pokemon front sprite (80x80px)
- Shiny indicator (if applicable)
- Species name
- Level
- Types

**Usage in Code**:
```python
# In __init__
self.sprite_manager = get_sprite_manager()

# In _update_team_display
sprite_image = self.sprite_manager.get_sprite(
    pokemon.species_id,
    shiny=getattr(pokemon, 'is_shiny', False),
    size=(80, 80)
)

if sprite_image:
    slot.sprite_label.config(image=sprite_image, text="")
    slot.sprite_label.image = sprite_image  # Prevent garbage collection
```

### Battle Simulator Integration
**File**: `src/gui/battle_simulator_gui.py`

Sprites shown during battle:
- Player Pokemon (front view)
- Opponent Pokemon (back view for realism)
- Real-time sprite updates during battle
- Shiny animations

**Planned Features**:
- HP bar overlay on sprites
- Status condition indicators
- Battle animations using sprite frames

### Social Community Hub
**File**: `src/gui/social_community_gui.py`

Sprites displayed in:
- Team sharing posts
- User profiles (favorite Pokemon)
- Tournament brackets
- Battle history

## Performance Optimization

### Sprite Caching
```python
# Sprites are cached by (pokemon_id, generation, shiny, female)
cache_key = (25, 'black-white', False, False)  # Pikachu cached
```

### Preloading Strategy
```python
# On app startup, preload common Pokemon
sprite_manager.preload_generation('black-white', max_id=151)  # Gen 1
```

### Memory Management
```python
# Clear cache when switching teams/battles to free memory
sprite_manager.clear_cache()
```

## Testing the Sprite System

### Command Line Test
```powershell
cd "C:\Users\Colin\Desktop\Pokemon\PTB [PokeTeamBuilder v1.0]"
python src/utils/sprite_manager.py
```

This will open a test window showing:
- Pikachu sprite (ID 25)
- Shiny Charizard sprite (ID 6)

### Integration Test in App
1. Launch the app: `python run_gui.py`
2. Navigate to **Team Builder**
3. Create a new team
4. Add Pokemon to team
5. Sprites should appear in team slots

## Troubleshooting

### Sprite Not Loading
**Problem**: Pokemon sprite shows "?" instead of image

**Solutions**:
1. Verify sprite path exists:
   ```python
   sprite_manager.sprites_path  # Should point to sprites directory
   ```

2. Check if Pokemon ID is valid:
   ```python
   # IDs 1-649 supported in black-white generation
   ```

3. Check console for error messages:
   ```
   ERROR: Sprite not found: C:\...\main-sprites\black-white\999.png
   ```

### Missing Pillow (PIL)
**Problem**: `ImportError: No module named 'PIL'`

**Solution**:
```powershell
pip install Pillow
```

### Performance Issues
**Problem**: Slow sprite loading

**Solutions**:
1. Preload sprites on startup
2. Reduce sprite size parameter
3. Clear cache periodically
4. Use lower resolution generation (e.g., 'red-blue')

## Sprite Naming Convention Reference

### Base Pokemon
- Format: `{pokedex_id}.png`
- Examples: `1.png` (Bulbasaur), `25.png` (Pikachu), `150.png` (Mewtwo)

### Form Variants
- Format: `{pokedex_id}-{form_name}.png`
- Examples:
  - `201-a.png` (Unown A)
  - `351-rainy.png` (Rainy Castform)
  - `386-attack.png` (Attack Deoxys)
  - `479-wash.png` (Wash Rotom)
  - `493-fire.png` (Fire Arceus)

### Special Variants
- Shiny: `shiny/{pokedex_id}.png`
- Female: `female/{pokedex_id}.png`
- Back: `back/{pokedex_id}.png`
- Shiny Female: `shiny/female/{pokedex_id}.png`

## Future Enhancements

### Planned Features
1. **Animated Sprites**
   - Support for GIF sprites from later generations
   - Battle animations

2. **Custom Sprite Sets**
   - User-uploaded custom sprites
   - Sprite pack manager

3. **Sprite Editor**
   - In-app sprite customization
   - Shiny color palette editor

4. **Advanced Battle Sprites**
   - HP/status overlays
   - Attack animations
   - Weather effect overlays

5. **Mobile Sprite Optimization**
   - Compressed sprite formats
   - Lazy loading for mobile app
   - WebP conversion for React Native

## Related Files
- `src/utils/sprite_manager.py` - Core sprite management system
- `src/gui/team_builder_gui.py` - Team builder sprite integration
- `src/gui/battle_simulator_gui.py` - Battle sprite display
- `src/gui/social_community_gui.py` - Social features sprites
- `data/pokemon.json` - Pokemon database with species IDs

## Support
For sprite-related issues or questions, check:
1. Console error messages
2. Sprite path configuration
3. Pokemon ID mapping
4. PIL/Pillow installation

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Sprite Collection**: Black/White (Gen 5) - 649+ Pokemon
