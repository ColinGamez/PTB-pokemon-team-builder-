"""
Battle Simulator GUI frame for Pokemon Team Builder.
Provides interface for simulating Pokemon battles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from gui.theme_manager import ThemeManager
from teambuilder.team import PokemonTeam, TeamFormat, TeamEra
from battle.simulator import BattleSimulator
from core.pokemon import Pokemon, ShadowPokemon
from core.stats import PokemonNature


class BattleSimulatorFrame(tk.Frame):
    """Battle Simulator interface frame."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.player_team = None
        self.opponent_team = None
        self.battle_simulator = BattleSimulator()
        self.battle_result = None
        self.ai_manager = None
        
        self._initialize_ai_system()
        self._create_widgets()
        self._create_sample_teams()
    
    def _initialize_ai_system(self):
        """Initialize the AI battle system."""
        try:
            from battle.battle_ai import AIOpponentManager
            self.ai_manager = AIOpponentManager()
            print("✅ AI battle system initialized")
        except ImportError as e:
            print(f"❌ Failed to initialize AI system: {e}")
            self.ai_manager = None
    
    def _create_widgets(self):
        """Create the battle simulator interface widgets."""
        # Title
        title_label = self.theme_manager.create_styled_label(
            self,
            text="⚔️ Battle Simulator",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=10)
        
        # Team setup section
        teams_frame = self.theme_manager.create_styled_frame(self)
        teams_frame.pack(fill=tk.X, padx=20, pady=10)
        
        teams_label = self.theme_manager.create_styled_label(
            teams_frame,
            text="Team Setup:",
            font=('Arial', 12, 'bold')
        )
        teams_label.pack(pady=5)
        
        # Team creation controls
        controls_frame = tk.Frame(teams_frame)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Player team controls
        player_frame = tk.LabelFrame(controls_frame, text="Player Team", padx=10, pady=5)
        player_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Player team name
        tk.Label(player_frame, text="Team Name:").pack(anchor=tk.W)
        self.player_team_name = tk.StringVar(value="My Team")
        tk.Entry(player_frame, textvariable=self.player_team_name, width=20).pack(fill=tk.X, pady=2)
        
        # Player team format
        tk.Label(player_frame, text="Format:").pack(anchor=tk.W)
        self.player_format = tk.StringVar(value="single")
        ttk.Combobox(
            player_frame,
            textvariable=self.player_format,
            values=["single", "double", "triple", "rotation", "multi"],
            state="readonly",
            width=15
        ).pack(fill=tk.X, pady=2)
        
        # Player team era
        tk.Label(player_frame, text="Era:").pack(anchor=tk.W)
        self.player_era = tk.StringVar(value="modern")
        ttk.Combobox(
            player_frame,
            textvariable=self.player_era,
            values=["gamecube", "wii", "ds", "3ds", "switch", "modern"],
            state="readonly",
            width=15
        ).pack(fill=tk.X, pady=2)
        
        # Create player team button
        create_player_btn = self.theme_manager.create_styled_button(
            player_frame,
            text="Create Player Team",
            command=self._create_player_team
        )
        create_player_btn.pack(pady=10)
        
        # Opponent team controls
        opponent_frame = tk.LabelFrame(controls_frame, text="Opponent Team", padx=10, pady=5)
        opponent_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Opponent team name
        tk.Label(opponent_frame, text="Team Name:").pack(anchor=tk.W)
        self.opponent_team_name = tk.StringVar(value="AI Opponent")
        tk.Entry(opponent_frame, textvariable=self.opponent_team_name, width=20).pack(fill=tk.X, pady=2)
        
        # Opponent team format
        tk.Label(opponent_frame, text="Format:").pack(anchor=tk.W)
        self.opponent_format = tk.StringVar(value="single")
        ttk.Combobox(
            opponent_frame,
            textvariable=self.opponent_format,
            values=["single", "double", "triple", "rotation", "multi"],
            state="readonly",
            width=15
        ).pack(fill=tk.X, pady=2)
        
        # Opponent team era
        tk.Label(opponent_frame, text="Era:").pack(anchor=tk.W)
        self.opponent_era = tk.StringVar(value="modern")
        ttk.Combobox(
            opponent_frame,
            textvariable=self.opponent_era,
            values=["gamecube", "wii", "ds", "3ds", "switch", "modern"],
            state="readonly",
            width=15
        ).pack(fill=tk.X, pady=2)
        
        # Create opponent team button
        create_opponent_btn = self.theme_manager.create_styled_button(
            opponent_frame,
            text="Create Opponent Team",
            command=self._create_opponent_team
        )
        create_opponent_btn.pack(pady=5)
        
        # AI opponent button
        ai_opponent_btn = self.theme_manager.create_styled_button(
            opponent_frame,
            text="🤖 Use AI Opponent",
            command=self._create_ai_opponent
        )
        ai_opponent_btn.pack(pady=5)
        
        # Battle settings section
        battle_settings_frame = self.theme_manager.create_styled_frame(self)
        battle_settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        settings_label = self.theme_manager.create_styled_label(
            battle_settings_frame,
            text="Battle Settings:",
            font=('Arial', 12, 'bold')
        )
        settings_label.pack(pady=5)
        
        # Settings controls
        settings_controls = tk.Frame(battle_settings_frame)
        settings_controls.pack(fill=tk.X, padx=20, pady=10)
        
        # AI difficulty
        tk.Label(settings_controls, text="AI Difficulty:").pack(side=tk.LEFT, padx=(0, 10))
        self.ai_difficulty = tk.StringVar(value="medium")
        difficulty_combo = ttk.Combobox(
            settings_controls,
            textvariable=self.ai_difficulty,
            values=["easy", "medium", "hard"],
            state="readonly",
            width=10
        )
        difficulty_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Max turns
        tk.Label(settings_controls, text="Max Turns:").pack(side=tk.LEFT, padx=(0, 10))
        self.max_turns = tk.StringVar(value="50")
        turns_entry = tk.Entry(settings_controls, textvariable=self.max_turns, width=8)
        turns_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Start battle button
        start_battle_btn = self.theme_manager.create_styled_button(
            battle_settings_frame,
            text="⚔️ Start Battle!",
            command=self._start_battle
        )
        start_battle_btn.pack(pady=10)
        
        # Team display section
        teams_display_frame = self.theme_manager.create_styled_frame(self)
        teams_display_frame.pack(fill=tk.X, padx=20, pady=10)
        
        display_label = self.theme_manager.create_styled_label(
            teams_display_frame,
            text="Team Status:",
            font=('Arial', 12, 'bold')
        )
        display_label.pack(pady=5)
        
        # Team status display
        status_frame = tk.Frame(teams_display_frame)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Player team status
        self.player_status_label = tk.Label(
            status_frame,
            text="Player Team: Not created",
            font=('Arial', 10),
            anchor=tk.W
        )
        self.player_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Opponent team status
        self.opponent_status_label = tk.Label(
            status_frame,
            text="Opponent Team: Not created",
            font=('Arial', 10),
            anchor=tk.W
        )
        self.opponent_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Battle results section
        results_frame = self.theme_manager.create_styled_frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        results_label = self.theme_manager.create_styled_label(
            results_frame,
            text="Battle Results:",
            font=('Arial', 12, 'bold')
        )
        results_label.pack(pady=5)
        
        # Results display
        self.results_text = tk.Text(
            results_frame,
            height=20,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.results_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Battle log section
        log_frame = self.theme_manager.create_styled_frame(self)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        log_label = self.theme_manager.create_styled_label(
            log_frame,
            text="Battle Log:",
            font=('Arial', 12, 'bold')
        )
        log_label.pack(pady=5)
        
        # Battle log display
        self.battle_log_text = tk.Text(
            log_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.battle_log_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    def _create_sample_teams(self):
        """Create sample teams for demonstration."""
        self._create_player_team()
        self._create_opponent_team()
    
    def _create_player_team(self):
        """Create the player team."""
        try:
            team_name = self.player_team_name.get()
            if not team_name.strip():
                messagebox.showerror("Error", "Player team name cannot be empty!")
                return
            
            format_value = TeamFormat(self.player_format.get())
            era_value = TeamEra(self.player_era.get())
            
            self.player_team = PokemonTeam(
                name=team_name,
                format=format_value,
                era=era_value,
                max_size=6
            )
            
            # Add some sample Pokemon
            sample_pokemon = [
                ("Shadow Bulbasaur", 1, 50, "hardy", True),
                ("Shadow Charmander", 4, 50, "adamant", True),
                ("Squirtle", 7, 50, "modest", False),
                ("Pikachu", 25, 50, "timid", False),
                ("Eevee", 133, 50, "jolly", False),
                ("Mewtwo", 150, 50, "modest", False)
            ]
            
            for name, species_id, level, nature, is_shadow in sample_pokemon:
                if is_shadow:
                    pokemon = ShadowPokemon(
                        name=name,
                        species_id=species_id,
                        level=level,
                        nature=PokemonNature(nature),
                        moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                    )
                else:
                    pokemon = Pokemon(
                        name=name,
                        species_id=species_id,
                        level=level,
                        nature=PokemonNature(nature),
                        moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                    )
                
                self.player_team.add_pokemon(pokemon)
            
            self._update_team_status()
            self._update_results("✅ Player team created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create player team: {str(e)}")
    
    def _create_opponent_team(self):
        """Create the opponent team."""
        try:
            team_name = self.opponent_team_name.get()
            if not team_name.strip():
                messagebox.showerror("Error", "Opponent team name cannot be empty!")
                return
            
            format_value = TeamFormat(self.opponent_format.get())
            era_value = TeamEra(self.opponent_era.get())
            
            self.opponent_team = PokemonTeam(
                name=team_name,
                format=format_value,
                era=era_value,
                max_size=6
            )
            
            # Add some sample Pokemon
            sample_pokemon = [
                ("Pikachu", 25, 50, "timid"),
                ("Charmander", 4, 50, "adamant"),
                ("Bulbasaur", 1, 50, "modest"),
                ("Squirtle", 7, 50, "bold"),
                ("Rattata", 19, 50, "jolly"),
                ("Pidgey", 16, 50, "timid")
            ]
            
            for name, species_id, level, nature in sample_pokemon:
                pokemon = Pokemon(
                    name=name,
                    species_id=species_id,
                    level=level,
                    nature=PokemonNature(nature),
                    moves=[f"{name} Move 1", f"{name} Move 2", f"{name} Move 3", f"{name} Move 4"]
                )
                
                self.opponent_team.add_pokemon(pokemon)
            
            self._update_team_status()
            self._update_results("✅ Opponent team created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create opponent team: {str(e)}")
    
    def _update_team_status(self):
        """Update the team status display."""
        if self.player_team:
            player_text = f"Player Team: {self.player_team.name} ({self.player_team.get_team_size()}/6 Pokemon)"
            self.player_status_label.config(text=player_text)
        else:
            self.player_status_label.config(text="Player Team: Not created")
        
        if self.opponent_team:
            opponent_text = f"Opponent Team: {self.opponent_team.name} ({self.opponent_team.get_team_size()}/6 Pokemon)"
            self.opponent_status_label.config(text=opponent_text)
        else:
            self.opponent_status_label.config(text="Opponent Team: Not created")
    
    def _start_battle(self):
        """Start the battle simulation."""
        if not self.player_team or not self.opponent_team:
            messagebox.showerror("Error", "Please create both teams before starting a battle!")
            return
        
        try:
            # Get battle settings
            ai_difficulty = self.ai_difficulty.get()
            max_turns = int(self.max_turns.get())
            
            if max_turns <= 0:
                messagebox.showerror("Error", "Max turns must be greater than 0!")
                return
            
            # Clear previous results
            self._clear_results()
            
            # Start battle simulation
            self._update_results("⚔️ Battle starting...\n")
            self._update_results(f"Player Team: {self.player_team.name}\n")
            self._update_results(f"Opponent Team: {self.opponent_team.name}\n")
            self._update_results(f"AI Difficulty: {ai_difficulty.title()}\n")
            self._update_results(f"Max Turns: {max_turns}\n")
            self._update_results("=" * 50 + "\n\n")
            
            # Simulate battle
            self.battle_result = self.battle_simulator.simulate_battle(
                player_team=self.player_team,
                opponent_team=self.opponent_team,
                max_turns=max_turns,
                ai_difficulty=ai_difficulty
            )
            
            # Display battle results
            self._display_battle_results()
            
            # Display battle log
            self._display_battle_log()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Battle simulation failed: {str(e)}")
    
    def _display_battle_results(self):
        """Display the battle results."""
        if not self.battle_result:
            return
        
        # Battle outcome
        self._update_results("🎯 BATTLE RESULTS\n")
        self._update_results("=" * 30 + "\n")
        self._update_results(self.battle_result.get_result_text() + "\n\n")
        
        # Battle statistics
        stats = self.battle_simulator.get_battle_statistics(self.battle_result)
        self._update_results("📊 BATTLE STATISTICS\n")
        self._update_results("=" * 30 + "\n")
        self._update_results(f"Turns Taken: {stats['turns_taken']}\n")
        self._update_results(f"Player Pokemon Fainted: {stats['player_pokemon_fainted']}\n")
        self._update_results(f"Opponent Pokemon Fainted: {stats['opponent_pokemon_fainted']}\n")
        self._update_results(f"Total Events: {stats['total_events']}\n")
        self._update_results(f"Move Events: {stats['move_events']}\n")
        self._update_results(f"Damage Events: {stats['damage_events']}\n")
        self._update_results(f"Faint Events: {stats['faint_events']}\n\n")
        
        # Team final states
        self._update_results("🏁 FINAL TEAM STATES\n")
        self._update_results("=" * 30 + "\n")
        self._update_results(self.battle_result.get_team_summary(True) + "\n\n")
        self._update_results(self.battle_result.get_team_summary(False) + "\n\n")
    
    def _display_battle_log(self):
        """Display the battle log."""
        if not self.battle_result:
            return
        
        # Clear previous log
        self.battle_log_text.config(state=tk.NORMAL)
        self.battle_log_text.delete(1.0, tk.END)
        
        # Display battle log
        log_text = self.battle_result.battle_log.get_summary()
        self.battle_log_text.insert(1.0, log_text)
        
        self.battle_log_text.config(state=tk.DISABLED)
    
    def _clear_results(self):
        """Clear the results display."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        self.battle_log_text.config(state=tk.NORMAL)
        self.battle_log_text.delete(1.0, tk.END)
        self.battle_log_text.config(state=tk.DISABLED)
    
    def _update_results(self, text: str):
        """Update the results display."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        self.results_text.see(tk.END)
    
    def _create_ai_opponent(self):
        """Create an AI opponent team."""
        if not self.ai_manager:
            messagebox.showerror("Error", "AI system is not available!")
            return
        
        try:
            # Get available AI opponents
            opponents = self.ai_manager.get_available_opponents()
            if not opponents:
                messagebox.showerror("Error", "No AI opponents available!")
                return
            
            # Create selection dialog
            ai_dialog = tk.Toplevel(self)
            ai_dialog.title("Select AI Opponent")
            ai_dialog.geometry("400x500")
            ai_dialog.transient(self)
            ai_dialog.grab_set()
            
            # Center the dialog
            ai_dialog.update_idletasks()
            x = (ai_dialog.winfo_screenwidth() // 2) - (ai_dialog.winfo_width() // 2)
            y = (ai_dialog.winfo_screenheight() // 2) - (ai_dialog.winfo_height() // 2)
            ai_dialog.geometry(f"+{x}+{y}")
            
            # Dialog content
            tk.Label(ai_dialog, text="Select AI Opponent:", font=('Arial', 12, 'bold')).pack(pady=10)
            
            # Listbox for opponents
            listbox_frame = tk.Frame(ai_dialog)
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            opponent_listbox = tk.Listbox(listbox_frame, height=15)
            opponent_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=opponent_listbox.yview)
            opponent_listbox.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Populate listbox
            for opponent in opponents:
                display_text = f"{opponent['name']} ({opponent['difficulty'].title()}) - {opponent['personality'].title()}"
                opponent_listbox.insert(tk.END, display_text)
            
            # Details text
            details_text = tk.Text(ai_dialog, height=8, wrap=tk.WORD, state=tk.DISABLED)
            details_text.pack(fill=tk.X, padx=20, pady=10)
            
            def on_opponent_select(event):
                selection = opponent_listbox.curselection()
                if selection:
                    index = selection[0]
                    opponent_data = opponents[index]
                    
                    details_text.config(state=tk.NORMAL)
                    details_text.delete(1.0, tk.END)
                    
                    details = f"""Name: {opponent_data['name']}
Difficulty: {opponent_data['difficulty'].title()}
Personality: {opponent_data['personality'].title()}
Team Size: {opponent_data['team_size']}/6 Pokemon

Description: {opponent_data['description']}"""
                    
                    details_text.insert(1.0, details)
                    details_text.config(state=tk.DISABLED)
            
            opponent_listbox.bind('<<ListboxSelect>>', on_opponent_select)
            
            # Buttons
            button_frame = tk.Frame(ai_dialog)
            button_frame.pack(fill=tk.X, padx=20, pady=10)
            
            selected_opponent = [None]  # Use list to modify from inner function
            
            def select_opponent():
                selection = opponent_listbox.curselection()
                if selection:
                    index = selection[0]
                    selected_opponent[0] = opponents[index]['name']
                    ai_dialog.destroy()
                else:
                    messagebox.showwarning("No Selection", "Please select an AI opponent.")
            
            def cancel_selection():
                ai_dialog.destroy()
            
            tk.Button(button_frame, text="Select", command=select_opponent, bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Cancel", command=cancel_selection, bg='#f44336', fg='white').pack(side=tk.RIGHT, padx=5)
            
            # Wait for dialog to close
            ai_dialog.wait_window()
            
            # Create AI opponent team if one was selected
            if selected_opponent[0]:
                ai_opponent = self.ai_manager.get_opponent(selected_opponent[0])
                if ai_opponent:
                    self.opponent_team = ai_opponent.team
                    self.opponent_team_name.set(f"{ai_opponent.name} (AI)")
                    self._update_team_status()
                    self._update_results(f"✅ AI opponent '{ai_opponent.name}' selected successfully!")
                    messagebox.showinfo("Success", f"AI opponent '{ai_opponent.name}' has been loaded!")
                else:
                    messagebox.showerror("Error", "Failed to load selected AI opponent.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create AI opponent: {str(e)}")
