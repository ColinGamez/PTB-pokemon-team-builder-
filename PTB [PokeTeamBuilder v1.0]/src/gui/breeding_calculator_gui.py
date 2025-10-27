"""
Breeding Calculator GUI for Pokemon Team Builder.
Provides interface for Pokemon breeding calculations and optimization.

NOTE: This GUI is temporarily disabled as it was designed for a different
breeding system API than the current GeneticBreedingCalculator.
Requires refactoring to work with the new system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
from enum import Enum
import logging

from src.gui.theme_manager import ThemeManager
# Temporarily disabled - API mismatch with GeneticBreedingCalculator
# from features.breeding_calculator import GeneticBreedingCalculator, BreedingPokemon, Gender, Nature, IVSet
from src.core.pokemon import Pokemon, PokemonNature
from src.core.stats import IV, EV, BaseStats

logger = logging.getLogger(__name__)

# Stub types to prevent import errors (for compatibility until refactored)
class EggGroup(Enum):
    """Stub for missing EggGroup enum."""
    DITTO = "ditto"
    MONSTER = "monster"
    DRAGON = "dragon"
    WATER_1 = "water1"
    GRASS = "grass"
    FIELD = "field"
    FAIRY = "fairy"
    UNDISCOVERED = "undiscovered"

class HeldItem(Enum):
    """Stub for missing HeldItem enum."""
    EVERSTONE = "everstone"
    DESTINY_KNOT = "destiny_knot"
    POWER_WEIGHT = "power_weight"

class BreedingPokemon:
    """Stub for compatibility."""
    pass

class BreedingCalculatorFrame(tk.Frame):
    """Breeding Calculator interface frame (currently disabled)."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.calculator = None  # Disabled
        self.parent1 = None
        self.parent2 = None
        self.breeding_result = None
        
        # Display disabled message
        msg = tk.Label(
            self,
            text="Breeding Calculator temporarily disabled.\nRequires refactoring for new breeding system.",
            font=("Arial", 14),
            fg="gray"
        )
        msg.pack(expand=True, pady=50)
        logger.warning("Breeding Calculator GUI loaded in disabled state")
        return  # Skip rest of initialization
        
        self._create_widgets()
        self._setup_layout()
        self._populate_sample_data()
    
    def _create_widgets(self):
        """Create all widgets for the breeding calculator."""
        # Header
        self.header_frame = self.theme_manager.create_styled_frame(self)
        self.title_label = self.theme_manager.create_styled_label(
            self.header_frame,
            text="🥚 Pokemon Breeding Calculator",
            font=('Arial', 18, 'bold')
        )
        
        # Main notebook for different sections
        self.main_notebook = ttk.Notebook(self)
        
        # Breeding Pair Setup Tab
        self.setup_frame = self.theme_manager.create_styled_frame(self.main_notebook)
        self.main_notebook.add(self.setup_frame, text="Breeding Setup")
        
        # Results Tab
        self.results_frame = self.theme_manager.create_styled_frame(self.main_notebook)
        self.main_notebook.add(self.results_frame, text="Breeding Results")
        
        # Optimization Tab
        self.optimization_frame = self.theme_manager.create_styled_frame(self.main_notebook)
        self.main_notebook.add(self.optimization_frame, text="Breeding Guide")
        
        # Create content for each tab
        self._create_setup_content()
        self._create_results_content()
        self._create_optimization_content()
    
    def _create_setup_content(self):
        """Create breeding setup tab content."""
        # Parent 1 Section
        parent1_frame = self.theme_manager.create_styled_frame(self.setup_frame)
        parent1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        parent1_label = self.theme_manager.create_styled_label(
            parent1_frame,
            text="Parent 1:",
            font=('Arial', 12, 'bold')
        )
        parent1_label.pack(anchor=tk.W, padx=5)
        
        # Parent 1 details
        p1_details_frame = self.theme_manager.create_styled_frame(parent1_frame)
        p1_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Pokemon selection
        tk.Label(p1_details_frame, text="Pokemon:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.p1_pokemon_var = tk.StringVar(value="Ditto")
        self.p1_pokemon_combo = ttk.Combobox(
            p1_details_frame,
            textvariable=self.p1_pokemon_var,
            values=["Ditto", "Charizard", "Blastoise", "Venusaur", "Pikachu", "Dragonite"],
            state="readonly"
        )
        self.p1_pokemon_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Gender
        tk.Label(p1_details_frame, text="Gender:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.p1_gender_var = tk.StringVar(value="genderless")
        self.p1_gender_combo = ttk.Combobox(
            p1_details_frame,
            textvariable=self.p1_gender_var,
            values=["male", "female", "genderless"],
            state="readonly"
        )
        self.p1_gender_combo.grid(row=0, column=3, padx=5, pady=2)
        
        # Nature
        tk.Label(p1_details_frame, text="Nature:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.p1_nature_var = tk.StringVar(value="Hardy")
        nature_values = [nature.value.title() for nature in PokemonNature]
        self.p1_nature_combo = ttk.Combobox(
            p1_details_frame,
            textvariable=self.p1_nature_var,
            values=nature_values,
            state="readonly"
        )
        self.p1_nature_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Held Item
        tk.Label(p1_details_frame, text="Held Item:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.p1_item_var = tk.StringVar(value="Destiny Knot")
        item_values = [item.value.replace('_', ' ').title() for item in HeldItem]
        self.p1_item_combo = ttk.Combobox(
            p1_details_frame,
            textvariable=self.p1_item_var,
            values=["None"] + item_values,
            state="readonly"
        )
        self.p1_item_combo.grid(row=1, column=3, padx=5, pady=2)
        
        # IVs for Parent 1
        tk.Label(p1_details_frame, text="IVs:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.p1_iv_frame = tk.Frame(p1_details_frame)
        self.p1_iv_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        self.p1_iv_vars = {}
        iv_stats = ["HP", "Att", "Def", "SpA", "SpD", "Spe"]
        for i, stat in enumerate(iv_stats):
            tk.Label(self.p1_iv_frame, text=f"{stat}:").grid(row=0, column=i*2, padx=2)
            var = tk.StringVar(value="31")
            self.p1_iv_vars[stat.lower()] = var
            entry = tk.Entry(self.p1_iv_frame, textvariable=var, width=4)
            entry.grid(row=0, column=i*2+1, padx=2)
        
        # Parent 2 Section (similar structure)
        parent2_frame = self.theme_manager.create_styled_frame(self.setup_frame)
        parent2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        parent2_label = self.theme_manager.create_styled_label(
            parent2_frame,
            text="Parent 2:",
            font=('Arial', 12, 'bold')
        )
        parent2_label.pack(anchor=tk.W, padx=5)
        
        # Parent 2 details
        p2_details_frame = self.theme_manager.create_styled_frame(parent2_frame)
        p2_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Pokemon selection
        tk.Label(p2_details_frame, text="Pokemon:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.p2_pokemon_var = tk.StringVar(value="Charizard")
        self.p2_pokemon_combo = ttk.Combobox(
            p2_details_frame,
            textvariable=self.p2_pokemon_var,
            values=["Ditto", "Charizard", "Blastoise", "Venusaur", "Pikachu", "Dragonite"],
            state="readonly"
        )
        self.p2_pokemon_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Gender
        tk.Label(p2_details_frame, text="Gender:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.p2_gender_var = tk.StringVar(value="male")
        self.p2_gender_combo = ttk.Combobox(
            p2_details_frame,
            textvariable=self.p2_gender_var,
            values=["male", "female", "genderless"],
            state="readonly"
        )
        self.p2_gender_combo.grid(row=0, column=3, padx=5, pady=2)
        
        # Nature
        tk.Label(p2_details_frame, text="Nature:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.p2_nature_var = tk.StringVar(value="Adamant")
        self.p2_nature_combo = ttk.Combobox(
            p2_details_frame,
            textvariable=self.p2_nature_var,
            values=nature_values,
            state="readonly"
        )
        self.p2_nature_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Held Item
        tk.Label(p2_details_frame, text="Held Item:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.p2_item_var = tk.StringVar(value="Everstone")
        self.p2_item_combo = ttk.Combobox(
            p2_details_frame,
            textvariable=self.p2_item_var,
            values=["None"] + item_values,
            state="readonly"
        )
        self.p2_item_combo.grid(row=1, column=3, padx=5, pady=2)
        
        # IVs for Parent 2
        tk.Label(p2_details_frame, text="IVs:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.p2_iv_frame = tk.Frame(p2_details_frame)
        self.p2_iv_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        self.p2_iv_vars = {}
        for i, stat in enumerate(iv_stats):
            tk.Label(self.p2_iv_frame, text=f"{stat}:").grid(row=0, column=i*2, padx=2)
            var = tk.StringVar(value="25" if stat != "Att" and stat != "Spe" else "31")
            self.p2_iv_vars[stat.lower()] = var
            entry = tk.Entry(self.p2_iv_frame, textvariable=var, width=4)
            entry.grid(row=0, column=i*2+1, padx=2)
        
        # Breeding Controls
        controls_frame = self.theme_manager.create_styled_frame(self.setup_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.breed_button = self.theme_manager.create_styled_button(
            controls_frame,
            text="🥚 Calculate Breeding",
            command=self._calculate_breeding
        )
        self.breed_button.pack(side=tk.LEFT, padx=5)
        
        self.compatibility_button = self.theme_manager.create_styled_button(
            controls_frame,
            text="💕 Check Compatibility",
            command=self._check_compatibility
        )
        self.compatibility_button.pack(side=tk.LEFT, padx=5)
        
        self.random_button = self.theme_manager.create_styled_button(
            controls_frame,
            text="🎲 Random Example",
            command=self._generate_random_example
        )
        self.random_button.pack(side=tk.RIGHT, padx=5)
    
    def _create_results_content(self):
        """Create breeding results tab content."""
        # Results display
        results_label = self.theme_manager.create_styled_label(
            self.results_frame,
            text="Breeding Results",
            font=('Arial', 14, 'bold')
        )
        results_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Results text area
        self.results_text = tk.Text(
            self.results_frame,
            height=25,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results scrollbar
        results_scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_optimization_content(self):
        """Create breeding optimization tab content."""
        # Target Pokemon section
        target_frame = self.theme_manager.create_styled_frame(self.optimization_frame)
        target_frame.pack(fill=tk.X, padx=10, pady=5)
        
        target_label = self.theme_manager.create_styled_label(
            target_frame,
            text="Target Pokemon Goals:",
            font=('Arial', 12, 'bold')
        )
        target_label.pack(anchor=tk.W, padx=5)
        
        # Target details
        target_details_frame = self.theme_manager.create_styled_frame(target_frame)
        target_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Target nature
        tk.Label(target_details_frame, text="Target Nature:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.target_nature_var = tk.StringVar(value="Adamant")
        nature_values = [nature.value.title() for nature in PokemonNature]
        target_nature_combo = ttk.Combobox(
            target_details_frame,
            textvariable=self.target_nature_var,
            values=nature_values,
            state="readonly"
        )
        target_nature_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Target IVs
        tk.Label(target_details_frame, text="Target IVs:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.target_iv_frame = tk.Frame(target_details_frame)
        self.target_iv_frame.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        self.target_iv_vars = {}
        iv_stats = ["HP", "Att", "Def", "SpA", "SpD", "Spe"]
        for i, stat in enumerate(iv_stats):
            tk.Label(self.target_iv_frame, text=f"{stat}:").grid(row=0, column=i*2, padx=2)
            var = tk.StringVar(value="31")
            self.target_iv_vars[stat.lower()] = var
            entry = tk.Entry(self.target_iv_frame, textvariable=var, width=4)
            entry.grid(row=0, column=i*2+1, padx=2)
        
        # Generate guide button
        guide_button = self.theme_manager.create_styled_button(
            target_frame,
            text="📋 Generate Breeding Guide",
            command=self._generate_breeding_guide
        )
        guide_button.pack(pady=10)
        
        # Guide display
        guide_label = self.theme_manager.create_styled_label(
            self.optimization_frame,
            text="Breeding Guide:",
            font=('Arial', 12, 'bold')
        )
        guide_label.pack(anchor=tk.W, padx=10, pady=5)
        
        self.guide_text = tk.Text(
            self.optimization_frame,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.guide_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _setup_layout(self):
        """Setup the layout of all widgets."""
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _populate_sample_data(self):
        """Populate with sample breeding data."""
        # Set some default values that make sense for breeding
        self.p1_iv_vars['hp'].set('31')
        self.p1_iv_vars['att'].set('31')
        self.p1_iv_vars['def'].set('31')
        self.p1_iv_vars['spa'].set('31')
        self.p1_iv_vars['spd'].set('31')
        self.p1_iv_vars['spe'].set('31')
        
        self.p2_iv_vars['hp'].set('25')
        self.p2_iv_vars['att'].set('31')
        self.p2_iv_vars['def'].set('20')
        self.p2_iv_vars['spa'].set('15')
        self.p2_iv_vars['spd'].set('25')
        self.p2_iv_vars['spe'].set('31')
    
    def _create_breeding_pokemon_from_inputs(self, prefix: str) -> Optional[BreedingPokemon]:
        """Create a BreedingPokemon from GUI inputs."""
        try:
            if prefix == 'p1':
                pokemon_name = self.p1_pokemon_var.get()
                nature_str = self.p1_nature_var.get().lower()
                gender = self.p1_gender_var.get()
                item_str = self.p1_item_var.get().lower().replace(' ', '_')
                iv_vars = self.p1_iv_vars
            else:
                pokemon_name = self.p2_pokemon_var.get()
                nature_str = self.p2_nature_var.get().lower()
                gender = self.p2_gender_var.get()
                item_str = self.p2_item_var.get().lower().replace(' ', '_')
                iv_vars = self.p2_iv_vars
            
            # Create IVs
            ivs = IV(
                hp=int(iv_vars['hp'].get()),
                attack=int(iv_vars['att'].get()),
                defense=int(iv_vars['def'].get()),
                special_attack=int(iv_vars['spa'].get()),
                special_defense=int(iv_vars['spd'].get()),
                speed=int(iv_vars['spe'].get())
            )
            
            # Get nature
            nature = PokemonNature(nature_str)
            
            # Get held item
            held_item = None
            if item_str != "none":
                try:
                    held_item = HeldItem(item_str)
                except ValueError:
                    held_item = None
            
            # Create Pokemon
            species_map = {
                "Ditto": 132,
                "Charizard": 6,
                "Blastoise": 9,
                "Venusaur": 3,
                "Pikachu": 25,
                "Dragonite": 149
            }
            
            pokemon = Pokemon(
                name=pokemon_name,
                species_id=species_map.get(pokemon_name, 1),
                level=50,
                nature=nature,
                ivs=ivs,
                evs=EV(),
                base_stats=BaseStats(hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50),
                moves=[],
                ability="Test Ability"
            )
            
            # Get egg groups
            egg_groups_map = {
                "Ditto": [EggGroup.DITTO],
                "Charizard": [EggGroup.MONSTER, EggGroup.DRAGON],
                "Blastoise": [EggGroup.MONSTER, EggGroup.WATER_1],
                "Venusaur": [EggGroup.MONSTER, EggGroup.GRASS],
                "Pikachu": [EggGroup.FIELD, EggGroup.FAIRY],
                "Dragonite": [EggGroup.WATER_1, EggGroup.DRAGON]
            }
            
            return BreedingPokemon(
                pokemon=pokemon,
                egg_groups=egg_groups_map.get(pokemon_name, [EggGroup.FIELD]),
                held_item=held_item,
                gender=gender
            )
        
        except Exception as e:
            logger.error(f"Error creating breeding Pokemon: {e}")
            return None
    
    def _check_compatibility(self):
        """Check if the two selected Pokemon can breed."""
        parent1 = self._create_breeding_pokemon_from_inputs('p1')
        parent2 = self._create_breeding_pokemon_from_inputs('p2')
        
        if not parent1 or not parent2:
            messagebox.showerror("Error", "Failed to create Pokemon from inputs")
            return
        
        can_breed = self.calculator.can_breed(parent1, parent2)
        
        if can_breed:
            messagebox.showinfo(
                "Compatibility Check",
                f"✅ {parent1.pokemon.name} and {parent2.pokemon.name} can breed together!\n\n"
                f"Shared egg groups: {set(parent1.egg_groups) & set(parent2.egg_groups)}\n"
                f"Gender compatibility: {parent1.gender} + {parent2.gender}"
            )
        else:
            reasons = []
            if set(parent1.egg_groups) & set(parent2.egg_groups) == set():
                reasons.append("No shared egg groups")
            if parent1.gender == parent2.gender and parent1.gender != "genderless":
                reasons.append("Same gender (not compatible)")
            if EggGroup.UNDISCOVERED in parent1.egg_groups or EggGroup.UNDISCOVERED in parent2.egg_groups:
                reasons.append("Undiscovered egg group cannot breed")
            
            messagebox.showwarning(
                "Compatibility Check",
                f"❌ {parent1.pokemon.name} and {parent2.pokemon.name} cannot breed.\n\n"
                f"Reasons: {', '.join(reasons)}"
            )
    
    def _calculate_breeding(self):
        """Calculate breeding results."""
        parent1 = self._create_breeding_pokemon_from_inputs('p1')
        parent2 = self._create_breeding_pokemon_from_inputs('p2')
        
        if not parent1 or not parent2:
            messagebox.showerror("Error", "Failed to create Pokemon from inputs")
            return
        
        # Calculate breeding result
        result = self.calculator.breed_pokemon(parent1, parent2)
        
        if not result:
            messagebox.showerror("Breeding Error", "These Pokemon cannot breed together")
            return
        
        self.breeding_result = result
        
        # Display results
        self._display_breeding_results(result, parent1, parent2)
        
        # Switch to results tab
        self.main_notebook.select(1)
    
    def _display_breeding_results(self, result, parent1, parent2):
        """Display breeding results in the results text area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        results_content = f"""🥚 BREEDING CALCULATION RESULTS
{'='*50}

PARENT INFORMATION:
Parent 1: {parent1.pokemon.name} ({parent1.gender})
- Nature: {parent1.pokemon.nature.value.title()}
- Held Item: {parent1.held_item.value.replace('_', ' ').title() if parent1.held_item else 'None'}
- IVs: HP:{parent1.pokemon.ivs.hp} Att:{parent1.pokemon.ivs.attack} Def:{parent1.pokemon.ivs.defense} SpA:{parent1.pokemon.ivs.special_attack} SpD:{parent1.pokemon.ivs.special_defense} Spe:{parent1.pokemon.ivs.speed}
- Egg Groups: {', '.join([group.value.title().replace('_', ' ') for group in parent1.egg_groups])}

Parent 2: {parent2.pokemon.name} ({parent2.gender})
- Nature: {parent2.pokemon.nature.value.title()}
- Held Item: {parent2.held_item.value.replace('_', ' ').title() if parent2.held_item else 'None'}
- IVs: HP:{parent2.pokemon.ivs.hp} Att:{parent2.pokemon.ivs.attack} Def:{parent2.pokemon.ivs.defense} SpA:{parent2.pokemon.ivs.special_attack} SpD:{parent2.pokemon.ivs.special_defense} Spe:{parent2.pokemon.ivs.speed}
- Egg Groups: {', '.join([group.value.title().replace('_', ' ') for group in parent2.egg_groups])}

OFFSPRING RESULT:
Species: {result.offspring.name}
Level: {result.offspring.level}
Nature: {result.offspring.nature.value.title()} (inherited from: {result.nature_inheritance})

FINAL IVs:
HP: {result.offspring.ivs.hp} (from: {result.iv_inheritance['hp']})
Attack: {result.offspring.ivs.attack} (from: {result.iv_inheritance['attack']})
Defense: {result.offspring.ivs.defense} (from: {result.iv_inheritance['defense']})
Sp. Attack: {result.offspring.ivs.special_attack} (from: {result.iv_inheritance['special_attack']})
Sp. Defense: {result.offspring.ivs.special_defense} (from: {result.iv_inheritance['special_defense']})
Speed: {result.offspring.ivs.speed} (from: {result.iv_inheritance['speed']})

BREEDING STATISTICS:
Success Rate: {result.success_rate:.6f} ({result.success_rate*100:.4f}%)
Estimated Generations: {result.generation_estimate}
Perfect IVs: {sum(1 for iv in [result.offspring.ivs.hp, result.offspring.ivs.attack, result.offspring.ivs.defense, result.offspring.ivs.special_attack, result.offspring.ivs.special_defense, result.offspring.ivs.speed] if iv == 31)}/6

BREEDING TIPS:
• Use Destiny Knot to inherit 5 IVs from parents
• Use Everstone to guarantee nature inheritance
• Use Power items to guarantee specific IV inheritance
• Keep the best offspring for next generation breeding
• Consider using different parent combinations for optimization

"""
        
        self.results_text.insert(1.0, results_content)
        self.results_text.config(state=tk.DISABLED)
    
    def _generate_breeding_guide(self):
        """Generate a comprehensive breeding guide."""
        try:
            # Create target Pokemon from inputs
            target_nature = PokemonNature(self.target_nature_var.get().lower())
            target_ivs = IV(
                hp=int(self.target_iv_vars['hp'].get()),
                attack=int(self.target_iv_vars['att'].get()),
                defense=int(self.target_iv_vars['def'].get()),
                special_attack=int(self.target_iv_vars['spa'].get()),
                special_defense=int(self.target_iv_vars['spd'].get()),
                speed=int(self.target_iv_vars['spe'].get())
            )
            
            target_pokemon = Pokemon(
                name="Target",
                species_id=1,
                level=50,
                nature=target_nature,
                ivs=target_ivs,
                evs=EV(),
                base_stats=BaseStats(hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50),
                moves=[],
                ability="Test"
            )
            
            # Create available Pokemon (using current inputs)
            parent1 = self._create_breeding_pokemon_from_inputs('p1')
            parent2 = self._create_breeding_pokemon_from_inputs('p2')
            
            if not parent1 or not parent2:
                messagebox.showerror("Error", "Failed to create Pokemon from inputs")
                return
            
            available_pokemon = [parent1, parent2]
            
            # Generate guide
            guide = self.calculator.generate_breeding_guide(target_pokemon, available_pokemon)
            
            # Display guide
            self._display_breeding_guide(guide)
            
        except Exception as e:
            logger.error(f"Error generating breeding guide: {e}")
            messagebox.showerror("Error", f"Failed to generate breeding guide: {e}")
    
    def _display_breeding_guide(self, guide):
        """Display the breeding guide."""
        self.guide_text.config(state=tk.NORMAL)
        self.guide_text.delete(1.0, tk.END)
        
        if not guide['success']:
            guide_content = f"""❌ BREEDING GUIDE - NO VIABLE PATH FOUND

{guide['message']}

RECOMMENDATIONS:
"""
            for rec in guide['recommendations']:
                guide_content += f"• {rec}\n"
        else:
            guide_content = f"""📋 BREEDING GUIDE - PATH TO SUCCESS

TARGET POKEMON:
Name: {guide['target']['name']}
Nature: {guide['target']['nature'].value.title()}
Target IVs: HP:{guide['target']['ivs'].hp} Att:{guide['target']['ivs'].attack} Def:{guide['target']['ivs'].defense} SpA:{guide['target']['ivs'].special_attack} SpD:{guide['target']['ivs'].special_defense} Spe:{guide['target']['ivs'].speed}

BEST BREEDING PAIR:
Parent 1: {guide['best_breeding_pair']['parent1'].pokemon.name}
Parent 2: {guide['best_breeding_pair']['parent2'].pokemon.name}
Optimization Score: {guide['best_breeding_pair']['score']:.1f}/100

BREEDING STEPS:
"""
            for step in guide['breeding_steps']:
                guide_content += f"""
Step {step['step']}: {step['action']}
Items Needed: {', '.join(step['items_needed'])}
Expected Outcome: {step['expected_outcome']}
Success Rate: {step['success_rate']}
"""
            
            guide_content += f"""
ESTIMATED GENERATIONS: {guide['estimated_generations']}

BREEDING TIPS:
"""
            for tip in guide['tips']:
                guide_content += f"• {tip}\n"
        
        self.guide_text.insert(1.0, guide_content)
        self.guide_text.config(state=tk.DISABLED)
    
    def _generate_random_example(self):
        """Generate a random breeding example."""
        import random
        
        # Random parent 1
        pokemon_options = ["Ditto", "Charizard", "Blastoise", "Venusaur", "Pikachu", "Dragonite"]
        self.p1_pokemon_var.set(random.choice(pokemon_options))
        self.p1_gender_var.set(random.choice(["male", "female", "genderless"]))
        self.p1_nature_var.set(random.choice([nature.value.title() for nature in PokemonNature]))
        self.p1_item_var.set(random.choice(["Destiny Knot", "Everstone", "None"]))
        
        # Random IVs for parent 1
        for stat in self.p1_iv_vars:
            self.p1_iv_vars[stat].set(str(random.randint(0, 31)))
        
        # Random parent 2
        self.p2_pokemon_var.set(random.choice(pokemon_options))
        self.p2_gender_var.set(random.choice(["male", "female", "genderless"]))
        self.p2_nature_var.set(random.choice([nature.value.title() for nature in PokemonNature]))
        self.p2_item_var.set(random.choice(["Destiny Knot", "Everstone", "None"]))
        
        # Random IVs for parent 2
        for stat in self.p2_iv_vars:
            self.p2_iv_vars[stat].set(str(random.randint(0, 31)))
        
        messagebox.showinfo("Random Example", "Generated random breeding example! Try calculating the results.")

if __name__ == "__main__":
    # Test the breeding calculator GUI
    root = tk.Tk()
    root.title("Pokemon Breeding Calculator")
    root.geometry("1000x700")
    
    theme_manager = ThemeManager()
    app = BreedingCalculatorFrame(root, theme_manager)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()