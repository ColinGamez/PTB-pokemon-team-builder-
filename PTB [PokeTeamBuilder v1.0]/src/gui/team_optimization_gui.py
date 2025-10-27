"""
Team Optimization GUI component.
Provides team optimization suggestions and automated improvements.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TeamOptimizationFrame(tk.Frame):
    """Team optimization interface frame."""
    
    def __init__(self, parent, theme_manager, team=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_team = team
        self.optimization_results = None
        
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
    
    def _create_widgets(self):
        """Create all widgets for the optimization interface."""
        # Header
        self.header_frame = self.theme_manager.create_styled_frame(self)
        self.title_label = self.theme_manager.create_styled_label(
            self.header_frame,
            text="🔧 Team Optimization",
            font=('Arial', 18, 'bold')
        )
        
        # Control panel
        self.control_frame = self.theme_manager.create_styled_frame(self)
        
        self.optimize_btn = self.theme_manager.create_styled_button(
            self.control_frame,
            text="⚡ Optimize Team",
            command=self._optimize_team
        )
        
        self.apply_btn = self.theme_manager.create_styled_button(
            self.control_frame,
            text="✅ Apply Changes",
            command=self._apply_optimizations,
            state=tk.DISABLED
        )
        
        self.reset_btn = self.theme_manager.create_styled_button(
            self.control_frame,
            text="🔄 Reset",
            command=self._reset_optimizations
        )
        
        # Options frame
        self.options_frame = self.theme_manager.create_styled_frame(self)
        self.options_label = self.theme_manager.create_styled_label(
            self.options_frame,
            text="Optimization Options:",
            font=('Arial', 12, 'bold')
        )
        
        # Optimization checkboxes
        self.optimize_stats = tk.BooleanVar(value=True)
        self.optimize_moves = tk.BooleanVar(value=True)
        self.optimize_items = tk.BooleanVar(value=True)
        self.optimize_natures = tk.BooleanVar(value=False)
        
        self.stats_check = tk.Checkbutton(
            self.options_frame,
            text="Optimize EV/IV spreads",
            variable=self.optimize_stats
        )
        
        self.moves_check = tk.Checkbutton(
            self.options_frame,
            text="Suggest move improvements",
            variable=self.optimize_moves
        )
        
        self.items_check = tk.Checkbutton(
            self.options_frame,
            text="Recommend held items",
            variable=self.optimize_items
        )
        
        self.natures_check = tk.Checkbutton(
            self.options_frame,
            text="Suggest nature changes",
            variable=self.optimize_natures
        )
        
        # Results area
        self.results_frame = self.theme_manager.create_styled_frame(self)
        
        # Results notebook
        self.results_notebook = ttk.Notebook(self.results_frame)
        
        # Suggestions tab
        self.suggestions_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.suggestions_frame, text="Suggestions")
        
        # Pokemon-specific tab
        self.pokemon_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.pokemon_frame, text="Pokemon Changes")
        
        # Team composition tab
        self.composition_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.composition_frame, text="Team Composition")
        
        # Create content for tabs
        self._create_suggestions_content()
        self._create_pokemon_content()
        self._create_composition_content()
    
    def _setup_layout(self):
        """Setup the layout of all widgets."""
        # Header
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Control panel
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        self.optimize_btn.pack(side=tk.LEFT, padx=5)
        self.apply_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Options
        self.options_frame.pack(fill=tk.X, padx=10, pady=5)
        self.options_label.pack(anchor=tk.W, padx=5)
        self.stats_check.pack(anchor=tk.W, padx=20)
        self.moves_check.pack(anchor=tk.W, padx=20)
        self.items_check.pack(anchor=tk.W, padx=20)
        self.natures_check.pack(anchor=tk.W, padx=20)
        
        # Results
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
    
    def _bind_events(self):
        """Bind events for the optimization interface."""
        pass
    
    def _create_suggestions_content(self):
        """Create suggestions tab content."""
        self.suggestions_text = tk.Text(
            self.suggestions_frame,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        
        suggestions_scrollbar = ttk.Scrollbar(
            self.suggestions_frame,
            orient=tk.VERTICAL,
            command=self.suggestions_text.yview
        )
        self.suggestions_text.configure(yscrollcommand=suggestions_scrollbar.set)
        
        self.suggestions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        suggestions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_pokemon_content(self):
        """Create Pokemon-specific changes tab content."""
        # Pokemon selector
        self.pokemon_selector_frame = self.theme_manager.create_styled_frame(self.pokemon_frame)
        self.pokemon_selector_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.pokemon_label = self.theme_manager.create_styled_label(
            self.pokemon_selector_frame,
            text="Select Pokemon:"
        )
        self.pokemon_label.pack(side=tk.LEFT, padx=5)
        
        self.pokemon_var = tk.StringVar()
        self.pokemon_combo = ttk.Combobox(
            self.pokemon_selector_frame,
            textvariable=self.pokemon_var,
            state="readonly"
        )
        self.pokemon_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.pokemon_combo.bind('<<ComboboxSelected>>', self._on_pokemon_selected)
        
        # Pokemon details
        self.pokemon_details = tk.Text(
            self.pokemon_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=15
        )
        self.pokemon_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_composition_content(self):
        """Create team composition tab content."""
        self.composition_text = tk.Text(
            self.composition_frame,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        
        composition_scrollbar = ttk.Scrollbar(
            self.composition_frame,
            orient=tk.VERTICAL,
            command=self.composition_text.yview
        )
        self.composition_text.configure(yscrollcommand=composition_scrollbar.set)
        
        self.composition_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        composition_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def set_team(self, team):
        """Set the team to optimize."""
        self.current_team = team
        if team:
            self._update_pokemon_selector()
    
    def _update_pokemon_selector(self):
        """Update the Pokemon selector combo box."""
        if not self.current_team:
            return
        
        active_pokemon = self.current_team.get_active_pokemon()
        pokemon_names = [f"{i+1}. {pokemon.name}" for i, pokemon in enumerate(active_pokemon)]
        
        self.pokemon_combo['values'] = pokemon_names
        if pokemon_names:
            self.pokemon_combo.set(pokemon_names[0])
            self._on_pokemon_selected()
    
    def _on_pokemon_selected(self, event=None):
        """Handle Pokemon selection change."""
        if not self.current_team or not self.pokemon_var.get():
            return
        
        try:
            # Extract index from selection
            selection = self.pokemon_var.get()
            index = int(selection.split('.')[0]) - 1
            
            active_pokemon = self.current_team.get_active_pokemon()
            if 0 <= index < len(active_pokemon):
                selected_pokemon = active_pokemon[index]
                self._display_pokemon_details(selected_pokemon)
        except (ValueError, IndexError):
            pass
    
    def _display_pokemon_details(self, pokemon):
        """Display details for selected Pokemon."""
        self.pokemon_details.config(state=tk.NORMAL)
        self.pokemon_details.delete(1.0, tk.END)
        
        details = f"""POKEMON DETAILS
{'='*30}

Name: {pokemon.name}
Level: {pokemon.level}
Nature: {pokemon.nature.value.title()}
Types: {', '.join([t.value.title() for t in pokemon.types])}

Base Stats:
  HP: {pokemon.base_stats.hp}
  Attack: {pokemon.base_stats.attack}
  Defense: {pokemon.base_stats.defense}
  Sp. Attack: {pokemon.base_stats.special_attack}
  Sp. Defense: {pokemon.base_stats.special_defense}
  Speed: {pokemon.base_stats.speed}

Current EVs:
  HP: {pokemon.evs.hp}
  Attack: {pokemon.evs.attack}
  Defense: {pokemon.evs.defense}
  Sp. Attack: {pokemon.evs.special_attack}
  Sp. Defense: {pokemon.evs.special_defense}
  Speed: {pokemon.evs.speed}
  Total: {sum(pokemon.evs.__dict__.values())}/510

Current IVs:
  HP: {pokemon.ivs.hp}
  Attack: {pokemon.ivs.attack}
  Defense: {pokemon.ivs.defense}
  Sp. Attack: {pokemon.ivs.special_attack}
  Sp. Defense: {pokemon.ivs.special_defense}
  Speed: {pokemon.ivs.speed}

Moves:
"""
        
        for i, move in enumerate(pokemon.moves, 1):
            details += f"  {i}. {move}\n"
        
        if hasattr(pokemon, 'ability') and pokemon.ability:
            details += f"\nAbility: {pokemon.ability}"
        
        self.pokemon_details.insert(1.0, details)
        self.pokemon_details.config(state=tk.DISABLED)
    
    def _optimize_team(self):
        """Perform team optimization."""
        if not self.current_team:
            messagebox.showwarning("No Team", "Please load a team first.")
            return
        
        try:
            # Perform optimization based on selected options
            self.optimization_results = self._perform_optimization()
            
            # Update displays
            self._update_suggestions()
            self._update_composition_suggestions()
            
            # Enable apply button
            self.apply_btn.config(state=tk.NORMAL)
            
            logger.info(f"Team optimization completed for {self.current_team.name}")
            messagebox.showinfo("Optimization Complete", "Team optimization analysis complete!")
            
        except Exception as e:
            logger.error(f"Team optimization failed: {e}")
            messagebox.showerror("Optimization Error", f"Failed to optimize team: {str(e)}")
    
    def _perform_optimization(self):
        """Perform the actual optimization analysis."""
        if not self.current_team:
            return {
                'suggestions': ['No team loaded'],
                'pokemon_changes': {},
                'composition_changes': []
            }
            
        active_pokemon = self.current_team.get_active_pokemon()
        
        optimization_results = {
            'suggestions': [],
            'pokemon_changes': {},
            'composition_changes': []
        }
        
        # General suggestions
        if len(active_pokemon) < 6:
            optimization_results['suggestions'].append(
                f"Add {6 - len(active_pokemon)} more Pokemon to complete your team"
            )
        
        if self.optimize_stats.get():
            optimization_results['suggestions'].append(
                "Consider optimizing EV spreads for better stat distribution"
            )
        
        if self.optimize_moves.get():
            optimization_results['suggestions'].append(
                "Review move sets for better coverage and synergy"
            )
        
        if self.optimize_items.get():
            optimization_results['suggestions'].append(
                "Add held items to maximize Pokemon potential"
            )
        
        if self.optimize_natures.get():
            optimization_results['suggestions'].append(
                "Consider nature changes for better stat optimization"
            )
        
        # Pokemon-specific analysis
        for pokemon in active_pokemon:
            pokemon_suggestions = []
            
            # Check EV optimization
            if self.optimize_stats.get():
                ev_total = sum(pokemon.evs.__dict__.values())
                if ev_total < 500:
                    pokemon_suggestions.append(f"Could use {510 - ev_total} more EVs")
                
                # Check for perfect IVs
                perfect_ivs = sum(1 for iv in pokemon.ivs.__dict__.values() if iv == 31)
                if perfect_ivs < 6:
                    pokemon_suggestions.append(f"Could improve {6 - perfect_ivs} IVs to 31")
            
            # Check moves
            if self.optimize_moves.get() and len(pokemon.moves) < 4:
                pokemon_suggestions.append(f"Could learn {4 - len(pokemon.moves)} more moves")
            
            if pokemon_suggestions:
                optimization_results['pokemon_changes'][pokemon.name] = pokemon_suggestions
        
        # Team composition suggestions
        type_counts = {}
        for pokemon in active_pokemon:
            for ptype in pokemon.types:
                type_counts[ptype.value] = type_counts.get(ptype.value, 0) + 1
        
        if len(type_counts) < 4:
            optimization_results['composition_changes'].append(
                "Consider adding more type diversity to your team"
            )
        
        # Check for common weaknesses
        if 'fire' not in type_counts:
            optimization_results['composition_changes'].append(
                "Consider adding a Fire-type for better offensive coverage"
            )
        
        if 'water' not in type_counts:
            optimization_results['composition_changes'].append(
                "Consider adding a Water-type for defensive utility"
            )
        
        return optimization_results
    
    def _update_suggestions(self):
        """Update the suggestions display."""
        self.suggestions_text.config(state=tk.NORMAL)
        self.suggestions_text.delete(1.0, tk.END)
        
        if not self.optimization_results:
            self.suggestions_text.insert(1.0, "No optimization results available.")
            self.suggestions_text.config(state=tk.DISABLED)
            return
        
        suggestions_content = "TEAM OPTIMIZATION SUGGESTIONS\n"
        suggestions_content += "="*40 + "\n\n"
        
        general_suggestions = self.optimization_results.get('suggestions', [])
        if general_suggestions:
            suggestions_content += "General Improvements:\n"
            for i, suggestion in enumerate(general_suggestions, 1):
                suggestions_content += f"{i}. {suggestion}\n"
        
        # Pokemon-specific suggestions
        pokemon_changes = self.optimization_results.get('pokemon_changes', {})
        if pokemon_changes:
            suggestions_content += "\nPokemon-Specific Improvements:\n"
            for pokemon_name, changes in pokemon_changes.items():
                suggestions_content += f"\n{pokemon_name}:\n"
                for change in changes:
                    suggestions_content += f"  • {change}\n"
        
        # Add general optimization tips
        suggestions_content += "\n" + "="*40
        suggestions_content += "\nOptimization Tips:\n"
        suggestions_content += "• Maximize EV investment (510 total)\n"
        suggestions_content += "• Aim for perfect IVs (31) in key stats\n"
        suggestions_content += "• Choose natures that boost important stats\n"
        suggestions_content += "• Ensure move coverage against common threats\n"
        suggestions_content += "• Consider held items for additional benefits\n"
        suggestions_content += "• Balance offensive and defensive capabilities\n"
        
        self.suggestions_text.insert(1.0, suggestions_content)
        self.suggestions_text.config(state=tk.DISABLED)
    
    def _update_composition_suggestions(self):
        """Update the team composition suggestions."""
        self.composition_text.config(state=tk.NORMAL)
        self.composition_text.delete(1.0, tk.END)
        
        if not self.optimization_results:
            self.composition_text.insert(1.0, "No composition analysis available.")
            self.composition_text.config(state=tk.DISABLED)
            return
        
        composition_content = "TEAM COMPOSITION ANALYSIS\n"
        composition_content += "="*40 + "\n\n"
        
        composition_changes = self.optimization_results.get('composition_changes', [])
        if composition_changes:
            composition_content += "Recommended Changes:\n"
            for i, change in enumerate(composition_changes, 1):
                composition_content += f"{i}. {change}\n"
        else:
            composition_content += "Your team composition looks balanced!\n"
        
        # Add current team analysis
        if self.current_team:
            active_pokemon = self.current_team.get_active_pokemon()
            
            composition_content += f"\nCurrent Team ({len(active_pokemon)}/6):\n"
            for i, pokemon in enumerate(active_pokemon, 1):
                types_str = '/'.join([t.value.title() for t in pokemon.types])
                composition_content += f"{i}. {pokemon.name} ({types_str}) - Lv.{pokemon.level}\n"
            
            # Type coverage analysis
            type_counts = {}
            for pokemon in active_pokemon:
                for ptype in pokemon.types:
                    type_counts[ptype.value] = type_counts.get(ptype.value, 0) + 1
            
            composition_content += f"\nType Coverage ({len(type_counts)} unique types):\n"
            for type_name, count in sorted(type_counts.items()):
                composition_content += f"  {type_name.title()}: {count} Pokemon\n"
        
        composition_content += "\n" + "="*40
        composition_content += "\nComposition Guidelines:\n"
        composition_content += "• Aim for 4-6 different types\n"
        composition_content += "• Include both offensive and defensive Pokemon\n"
        composition_content += "• Consider type synergies and resistances\n"
        composition_content += "• Plan for different battle scenarios\n"
        composition_content += "• Ensure good move coverage across the team\n"
        
        self.composition_text.insert(1.0, composition_content)
        self.composition_text.config(state=tk.DISABLED)
    
    def _apply_optimizations(self):
        """Apply the optimization suggestions."""
        if not self.optimization_results:
            messagebox.showwarning("No Optimizations", "Please run optimization first.")
            return
        
        # In a full implementation, this would apply actual changes
        # For now, just show a confirmation
        result = messagebox.askyesno(
            "Apply Optimizations",
            "This will apply the suggested optimizations to your team. Continue?"
        )
        
        if result:
            messagebox.showinfo(
                "Optimizations Applied",
                "Optimization suggestions have been noted. In a full implementation, "
                "this would automatically apply the changes to your team."
            )
            team_name = self.current_team.name if self.current_team else "Unknown"
            logger.info(f"Optimizations applied to team {team_name}")
    
    def _reset_optimizations(self):
        """Reset all optimization results."""
        self.optimization_results = None
        
        # Clear all displays
        self.suggestions_text.config(state=tk.NORMAL)
        self.suggestions_text.delete(1.0, tk.END)
        self.suggestions_text.insert(1.0, "Run optimization to see suggestions here.")
        self.suggestions_text.config(state=tk.DISABLED)
        
        self.composition_text.config(state=tk.NORMAL)
        self.composition_text.delete(1.0, tk.END)
        self.composition_text.insert(1.0, "Run optimization to see composition analysis here.")
        self.composition_text.config(state=tk.DISABLED)
        
        self.pokemon_details.config(state=tk.NORMAL)
        self.pokemon_details.delete(1.0, tk.END)
        self.pokemon_details.insert(1.0, "Select a Pokemon to see details here.")
        self.pokemon_details.config(state=tk.DISABLED)
        
        # Disable apply button
        self.apply_btn.config(state=tk.DISABLED)
        
        logger.info("Optimization results reset")