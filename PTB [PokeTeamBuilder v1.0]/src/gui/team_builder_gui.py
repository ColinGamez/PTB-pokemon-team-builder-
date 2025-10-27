"""
Team Builder GUI frame for Pokemon Team Builder.
Provides interface for building and managing Pokemon teams.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.theme_manager import ThemeManager
from src.teambuilder.team import PokemonTeam, TeamFormat, TeamEra
from src.teambuilder.analyzer import TeamAnalyzer
from src.teambuilder.validator import TeamValidator
from src.teambuilder.optimizer import TeamOptimizer
from src.core.pokemon import Pokemon, ShadowPokemon
from src.core.pokemon import PokemonNature
from src.utils.sprite_manager import get_sprite_manager


class TeamBuilderFrame(tk.Frame):
    """Team Builder interface frame."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.team = None
        self.analyzer = None
        self.validator = None
        self.optimizer = None
        self.sprite_manager = get_sprite_manager()
        
        self._create_widgets()
        self._create_sample_team()
    
    def _create_widgets(self):
        """Create the team builder interface widgets."""
        # Enhanced header section
        header_frame = self.theme_manager.create_styled_frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title_label = self.theme_manager.create_styled_label(
            header_frame,
            text="🏗️ Pokemon Team Builder",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = self.theme_manager.create_styled_label(
            header_frame,
            text="Build competitive teams with advanced analysis and optimization",
            font=('Arial', 12, 'italic')
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Team configuration section with enhanced layout
        config_frame = self.theme_manager.create_styled_frame(self)
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        config_title = self.theme_manager.create_styled_label(
            config_frame,
            text="⚙️ Team Configuration",
            font=('Arial', 14, 'bold')
        )
        config_title.pack(pady=(10, 15))
        
        # Team settings in a grid layout
        settings_frame = tk.Frame(config_frame)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Team name row
        name_row = tk.Frame(settings_frame)
        name_row.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        settings_frame.grid_columnconfigure(1, weight=1)
        
        name_label = self.theme_manager.create_styled_label(name_row, text="Team Name:")
        name_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.team_name_var = tk.StringVar(value="My Competitive Team")
        name_entry = tk.Entry(name_row, textvariable=self.team_name_var, width=30, font=('Arial', 11))
        name_entry.grid(row=0, column=1, padx=(0, 20), sticky="ew")
        
        # Format and era row
        format_row = tk.Frame(settings_frame)
        format_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        format_row.grid_columnconfigure(1, weight=1)
        format_row.grid_columnconfigure(3, weight=1)
        
        # Team format selection
        format_label = self.theme_manager.create_styled_label(format_row, text="Battle Format:")
        format_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.format_var = tk.StringVar(value="singles")
        format_combo = ttk.Combobox(
            format_row,
            textvariable=self.format_var,
            values=["singles", "doubles", "triple", "rotation", "multi", "vgc"],
            state="readonly",
            width=15
        )
        format_combo.grid(row=0, column=1, padx=(0, 30), sticky="w")
        
        # Team era selection
        era_label = self.theme_manager.create_styled_label(format_row, text="Game Era:")
        era_label.grid(row=0, column=2, padx=(0, 10), sticky="w")
        
        self.era_var = tk.StringVar(value="switch")
        era_combo = ttk.Combobox(
            format_row,
            textvariable=self.era_var,
            values=["gamecube", "wii", "ds", "3ds", "switch", "modern"],
            state="readonly",
            width=15
        )
        era_combo.grid(row=0, column=3, sticky="w")
        
        # Action buttons row
        buttons_frame = tk.Frame(config_frame)
        buttons_frame.pack(pady=15)
        
        create_btn = self.theme_manager.create_styled_button(
            buttons_frame,
            text="🏗️ Create New Team",
            command=self._create_team,
            style="primary",
            width=15
        )
        create_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = self.theme_manager.create_styled_button(
            buttons_frame,
            text="📁 Load Team",
            command=self._load_team,
            style="secondary",
            width=12
        )
        load_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = self.theme_manager.create_styled_button(
            buttons_frame,
            text="📥 Import Team",
            command=self._import_team,
            style="secondary",
            width=12
        )
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # Team display section
        self.team_display_frame = self.theme_manager.create_styled_frame(self)
        self.team_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Team info
        self.team_info_label = self.theme_manager.create_styled_label(
            self.team_display_frame,
            text="No team created yet. Create a team to get started!",
            font=('Arial', 12)
        )
        self.team_info_label.pack(pady=20)
        
        # Pokemon slots
        self.slots_frame = tk.Frame(self.team_display_frame)
        self.slots_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create 6 Pokemon slots
        self.pokemon_slots = []
        for i in range(6):
            slot_frame = self._create_pokemon_slot(i)
            slot_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
            self.pokemon_slots.append(slot_frame)
        
        # Add Pokemon section
        add_pokemon_frame = self.theme_manager.create_styled_frame(self)
        add_pokemon_frame.pack(fill=tk.X, padx=20, pady=10)
        
        add_label = self.theme_manager.create_styled_label(
            add_pokemon_frame,
            text="Add Pokemon:",
            font=('Arial', 12, 'bold')
        )
        add_label.pack(pady=5)
        
        # Pokemon input fields
        input_frame = tk.Frame(add_pokemon_frame)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Row 1
        row1 = tk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=2)
        
        tk.Label(row1, text="Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.name_var, width=15).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(row1, text="Species ID:").pack(side=tk.LEFT, padx=(0, 5))
        self.species_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.species_var, width=8).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(row1, text="Level:").pack(side=tk.LEFT, padx=(0, 5))
        self.level_var = tk.StringVar(value="50")
        tk.Entry(row1, textvariable=self.level_var, width=8).pack(side=tk.LEFT)
        
        # Row 2
        row2 = tk.Frame(input_frame)
        row2.pack(fill=tk.X, pady=2)
        
        tk.Label(row2, text="Nature:").pack(side=tk.LEFT, padx=(0, 5))
        self.nature_var = tk.StringVar(value="hardy")
        nature_combo = ttk.Combobox(
            row2,
            textvariable=self.nature_var,
            values=["hardy", "lonely", "brave", "adamant", "naughty", "bold", "docile", "relaxed", "impish", "lax", "timid", "hasty", "serious", "jolly", "naive", "modest", "mild", "quiet", "bashful", "rash", "calm", "gentle", "sassy", "careful", "quirky"],
            state="readonly",
            width=10
        )
        nature_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(row2, text="Shadow Pokemon:").pack(side=tk.LEFT, padx=(0, 5))
        self.shadow_var = tk.BooleanVar()
        tk.Checkbutton(row2, variable=self.shadow_var).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(row2, text="Position:").pack(side=tk.LEFT, padx=(0, 5))
        self.position_var = tk.StringVar()
        position_combo = ttk.Combobox(
            row2,
            textvariable=self.position_var,
            values=["1", "2", "3", "4", "5", "6"],
            state="readonly",
            width=5
        )
        position_combo.pack(side=tk.LEFT)
        
        # Add Pokemon button
        add_btn = self.theme_manager.create_styled_button(
            add_pokemon_frame,
            text="Add Pokemon",
            command=self._add_pokemon
        )
        add_btn.pack(pady=10)
        
        # Analysis and optimization section
        analysis_frame = self.theme_manager.create_styled_frame(self)
        analysis_frame.pack(fill=tk.X, padx=20, pady=10)
        
        analysis_label = self.theme_manager.create_styled_label(
            analysis_frame,
            text="Team Analysis & Optimization:",
            font=('Arial', 12, 'bold')
        )
        analysis_label.pack(pady=5)
        
        # Analysis buttons
        button_frame = tk.Frame(analysis_frame)
        button_frame.pack(pady=10)
        
        analyze_btn = self.theme_manager.create_styled_button(
            button_frame,
            text="📊 Analyze Team",
            command=self._analyze_team
        )
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        validate_btn = self.theme_manager.create_styled_button(
            button_frame,
            text="✅ Validate Team",
            command=self._validate_team
        )
        validate_btn.pack(side=tk.LEFT, padx=5)
        
        optimize_btn = self.theme_manager.create_styled_button(
            button_frame,
            text="🔧 Optimize Team",
            command=self._optimize_team
        )
        optimize_btn.pack(side=tk.LEFT, padx=5)
        
        # Results display
        self.results_text = tk.Text(
            analysis_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.results_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    def _create_pokemon_slot(self, slot_number: int) -> tk.Frame:
        """Create a Pokemon slot display frame."""
        slot_frame = tk.Frame(self.slots_frame, relief=tk.RAISED, borderwidth=2)
        
        # Slot number
        slot_label = tk.Label(slot_frame, text=f"Slot {slot_number + 1}", font=('Arial', 10, 'bold'))
        slot_label.pack(pady=2)
        
        # Pokemon sprite (placeholder)
        sprite_label = tk.Label(slot_frame, text="?", font=('Arial', 32))
        sprite_label.pack(pady=5)
        
        # Pokemon name
        name_label = tk.Label(slot_frame, text="Empty", font=('Arial', 9))
        name_label.pack(pady=2)
        
        # Pokemon level
        level_label = tk.Label(slot_frame, text="", font=('Arial', 8))
        level_label.pack(pady=1)
        
        # Pokemon types
        types_label = tk.Label(slot_frame, text="", font=('Arial', 8))
        types_label.pack(pady=1)
        
        # Store references
        slot_frame.sprite_label = sprite_label
        slot_frame.name_label = name_label
        slot_frame.level_label = level_label
        slot_frame.types_label = types_label
        
        return slot_frame
    
    def _create_sample_team(self):
        """Create a sample team for demonstration."""
        self._create_team()
        
        # Add some sample Pokemon
        sample_pokemon = [
            ("Shadow Bulbasaur", 1, 50, "hardy", True, 1),
            ("Shadow Charmander", 4, 50, "adamant", True, 2),
            ("Squirtle", 7, 50, "modest", False, 3)
        ]
        
        for name, species_id, level, nature, is_shadow, position in sample_pokemon:
            self.name_var.set(name)
            self.species_var.set(str(species_id))
            self.level_var.set(str(level))
            self.nature_var.set(nature)
            self.shadow_var.set(is_shadow)
            self.position_var.set(str(position))
            self._add_pokemon()
    
    def _create_team(self):
        """Create a new Pokemon team."""
        try:
            team_name = self.team_name_var.get()
            if not team_name.strip():
                messagebox.showerror("Error", "Team name cannot be empty!")
                return
            
            format_value = TeamFormat(self.format_var.get())
            era_value = TeamEra(self.era_var.get())
            
            self.team = PokemonTeam(
                name=team_name,
                format=format_value,
                era=era_value,
                max_size=6
            )
            
            self.analyzer = TeamAnalyzer(self.team)
            self.validator = TeamValidator(self.team)
            self.optimizer = TeamOptimizer(self.team)
            
            self._update_team_display()
            self._update_results("✅ Team created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create team: {str(e)}")
    
    def _add_pokemon(self):
        """Add a Pokemon to the team."""
        if not self.team:
            messagebox.showerror("Error", "Please create a team first!")
            return
        
        try:
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Pokemon name cannot be empty!")
                return
            
            species_id = int(self.species_var.get())
            level = int(self.level_var.get())
            nature = PokemonNature(self.nature_var.get())
            is_shadow = self.shadow_var.get()
            position = int(self.position_var.get()) - 1
            
            if position < 0 or position >= 6:
                messagebox.showerror("Error", "Position must be between 1 and 6!")
                return
            
            # Create Pokemon
            if is_shadow:
                pokemon = ShadowPokemon(
                    name=name,
                    species_id=species_id,
                    level=level,
                    nature=nature,
                    moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                )
            else:
                pokemon = Pokemon(
                    name=name,
                    species_id=species_id,
                    level=level,
                    nature=nature,
                    moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                )
            
            # Add to team
            self.team.add_pokemon(pokemon, position)
            
            # Update display
            self._update_team_display()
            self._update_results(f"✅ Added {name} to slot {position + 1}")
            
            # Clear input fields
            self.name_var.set("")
            self.species_var.set("")
            self.level_var.set("50")
            self.nature_var.set("hardy")
            self.shadow_var.set(False)
            self.position_var.set("")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add Pokemon: {str(e)}")
    
    def _update_team_display(self):
        """Update the team display."""
        if not self.team:
            return
        
        # Update team info
        team_info = f"Team: {self.team.name} ({self.team.format.value}, {self.team.era.value})\n"
        team_info += f"Size: {self.team.get_team_size()}/6"
        self.team_info_label.config(text=team_info)
        
        # Update Pokemon slots
        active_pokemon = self.team.get_active_pokemon()
        
        for i, slot in enumerate(self.pokemon_slots):
            if i < len(active_pokemon):
                pokemon = active_pokemon[i]
                slot.name_label.config(text=pokemon.name)
                slot.level_label.config(text=f"Lv.{pokemon.level}")
                
                # Get types
                types = [t.value for t in pokemon.types]
                types_text = "/".join(types) if types else "Unknown"
                slot.types_label.config(text=types_text)
                
                # Color code types
                if len(types) > 0:
                    type_color = self.theme_manager.get_type_color(types[0])
                    slot.types_label.config(fg=type_color)
                
                # Load and display sprite
                try:
                    # Try to get sprite by species ID
                    sprite_image = self.sprite_manager.get_sprite(
                        pokemon.species_id,
                        shiny=getattr(pokemon, 'is_shiny', False),
                        size=(80, 80)
                    )
                    
                    if sprite_image:
                        slot.sprite_label.config(image=sprite_image, text="")
                        # Keep reference to prevent garbage collection
                        slot.sprite_label.image = sprite_image
                    else:
                        # Fallback to text if sprite not found
                        slot.sprite_label.config(image="", text="?")
                except Exception as e:
                    # If sprite loading fails, show text
                    slot.sprite_label.config(image="", text="?")
            else:
                slot.name_label.config(text="Empty")
                slot.level_label.config(text="")
                slot.types_label.config(text="")
                slot.types_label.config(fg="black")
                slot.sprite_label.config(image="", text="?")
    
    def _analyze_team(self):
        """Analyze the current team."""
        if not self.team or not self.analyzer:
            messagebox.showerror("Error", "Please create a team first!")
            return
        
        try:
            # Perform analysis
            type_analysis = self.analyzer.analyze_type_coverage()
            weakness_analysis = self.analyzer.analyze_weaknesses()
            synergy_analysis = self.analyzer.analyze_synergies()
            stat_analysis = self.analyzer.analyze_stats()
            move_analysis = self.analyzer.analyze_move_coverage()
            era_analysis = self.analyzer.analyze_era_compatibility()
            
            # Generate report
            report = "📊 TEAM ANALYSIS REPORT\n"
            report += "=" * 50 + "\n\n"
            
            report += f"Team: {self.team.name}\n"
            report += f"Format: {self.team.format.value.title()}\n"
            report += f"Era: {self.team.era.value.title()}\n"
            report += f"Size: {self.team.get_team_size()}/6\n\n"
            
            report += "🎯 TYPE COVERAGE\n"
            report += f"Score: {type_analysis.coverage_score:.2f}\n"
            report += f"Covered Types: {', '.join(type_analysis.covered_types)}\n"
            report += f"Missing Types: {', '.join(type_analysis.missing_types)}\n\n"
            
            report += "🛡️ DEFENSE ANALYSIS\n"
            report += f"Overall Defense Score: {weakness_analysis.overall_defense_score:.2f}\n"
            report += f"Critical Weaknesses: {', '.join(weakness_analysis.critical_weaknesses)}\n\n"
            
            report += "🤝 SYNERGY ANALYSIS\n"
            report += f"Synergy Score: {synergy_analysis.synergy_score:.2f}\n"
            report += f"Core Synergies: {len(synergy_analysis.core_synergies)}\n"
            report += f"Anti-Synergies: {len(synergy_analysis.anti_synergies)}\n\n"
            
            report += "📈 STAT ANALYSIS\n"
            report += f"Balance Score: {stat_analysis.balance_score:.2f}\n"
            report += f"Total Stats: {sum(stat_analysis.stat_totals.values())}\n\n"
            
            report += "⚔️ MOVE COVERAGE\n"
            report += f"Total Moves: {move_analysis.total_moves}\n"
            report += f"Move Types: {', '.join(move_analysis.move_types)}\n\n"
            
            report += "🎮 ERA COMPATIBILITY\n"
            report += f"Compatible: {'Yes' if era_analysis.is_compatible else 'No'}\n"
            if not era_analysis.is_compatible:
                report += f"Issues: {era_analysis.compatibility_notes}\n"
            
            self._update_results(report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    def _validate_team(self):
        """Validate the current team."""
        if not self.team or not self.validator:
            messagebox.showerror("Error", "Please create a team first!")
            return
        
        try:
            # Perform validation
            validation_result = self.validator.validate_team()
            
            # Generate report
            report = "✅ TEAM VALIDATION REPORT\n"
            report += "=" * 50 + "\n\n"
            
            report += f"Team Valid: {'Yes' if validation_result.is_valid else 'No'}\n"
            report += f"Overall Score: {validation_result.overall_score:.2f}\n\n"
            
            report += "📋 VALIDATION SUMMARY\n"
            report += validation_result.get_validation_summary() + "\n\n"
            
            if validation_result.issues:
                report += "🔍 DETAILED ISSUES\n"
                for i, issue in enumerate(validation_result.issues, 1):
                    report += f"{i}. [{issue.level.value.upper()}] {issue.category}: {issue.message}\n"
                    if issue.suggestion:
                        report += f"   💡 Suggestion: {issue.suggestion}\n"
                    if issue.pokemon_name:
                        report += f"   🎯 Pokemon: {issue.pokemon_name}\n"
                    report += "\n"
            
            self._update_results(report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {str(e)}")
    
    def _optimize_team(self):
        """Optimize the current team."""
        if not self.team or not self.optimizer:
            messagebox.showerror("Error", "Please create a team first!")
            return
        
        try:
            # Perform optimization
            suggestions = self.optimizer.optimize_team()
            
            # Generate report
            report = "🔧 TEAM OPTIMIZATION REPORT\n"
            report += "=" * 50 + "\n\n"
            
            if suggestions:
                report += self.optimizer.get_optimization_summary(suggestions)
            else:
                report += "🎉 Your team is already well-optimized! No major improvements needed."
            
            self._update_results(report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")
    
    def _update_results(self, text: str):
        """Update the results display."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        self.results_text.config(state=tk.DISABLED)
    
    def _load_team(self):
        """Load a team from file."""
        try:
            from tkinter import filedialog
            
            filetypes = [
                ("JSON files", "*.json"),
                ("Pokemon Showdown", "*.txt"),
                ("All files", "*.*")
            ]
            
            file_path = filedialog.askopenfilename(
                title="Load Team",
                filetypes=filetypes
            )
            
            if file_path:
                # TODO: Implement actual team loading logic
                messagebox.showinfo("Success", f"Team loaded from {file_path}")
                self._update_results(f"📁 Team loaded from: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load team: {str(e)}")
    
    def _import_team(self):
        """Import a team from various formats."""
        try:
            # Create import dialog
            import_window = tk.Toplevel(self)
            import_window.title("Import Team")
            import_window.geometry("600x400")
            import_window.transient(self)
            import_window.grab_set()
            
            # Center the window
            import_window.update_idletasks()
            x = (import_window.winfo_screenwidth() // 2) - (600 // 2)
            y = (import_window.winfo_screenheight() // 2) - (400 // 2)
            import_window.geometry(f"600x400+{x}+{y}")
            
            # Import format selection
            format_frame = self.theme_manager.create_styled_frame(import_window)
            format_frame.pack(fill=tk.X, padx=20, pady=10)
            
            format_label = self.theme_manager.create_styled_label(
                format_frame,
                text="Import Format:",
                font=('Arial', 12, 'bold')
            )
            format_label.pack(anchor=tk.W, pady=(0, 5))
            
            format_var = tk.StringVar(value="showdown")
            formats = [
                ("Pokemon Showdown", "showdown"),
                ("PKHeX", "pkhex"),
                ("Save File", "save"),
                ("JSON", "json")
            ]
            
            for text, value in formats:
                rb = tk.Radiobutton(
                    format_frame,
                    text=text,
                    variable=format_var,
                    value=value,
                    font=('Arial', 10)
                )
                rb.pack(anchor=tk.W, pady=2)
            
            # Import text area
            text_frame = self.theme_manager.create_styled_frame(import_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            text_label = self.theme_manager.create_styled_label(
                text_frame,
                text="Paste team data:",
                font=('Arial', 12, 'bold')
            )
            text_label.pack(anchor=tk.W, pady=(0, 5))
            
            import_text = tk.Text(
                text_frame,
                height=15,
                font=('Consolas', 10)
            )
            import_text.pack(fill=tk.BOTH, expand=True)
            
            # Buttons
            button_frame = tk.Frame(import_window)
            button_frame.pack(fill=tk.X, padx=20, pady=10)
            
            def do_import():
                try:
                    content = import_text.get(1.0, tk.END).strip()
                    selected_format = format_var.get()
                    
                    if not content:
                        messagebox.showwarning("Warning", "Please paste team data first!")
                        return
                    
                    # TODO: Implement actual import logic based on format
                    messagebox.showinfo("Success", f"Team imported from {selected_format} format!")
                    self._update_results(f"📥 Team imported from {selected_format} format")
                    import_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Import failed: {str(e)}")
            
            import_btn = self.theme_manager.create_styled_button(
                button_frame,
                text="Import Team",
                command=do_import,
                style="primary"
            )
            import_btn.pack(side=tk.RIGHT, padx=(5, 0))
            
            cancel_btn = self.theme_manager.create_styled_button(
                button_frame,
                text="Cancel",
                command=import_window.destroy,
                style="secondary"
            )
            cancel_btn.pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open import dialog: {str(e)}")
