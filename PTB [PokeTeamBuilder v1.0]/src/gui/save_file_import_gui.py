"""
Save File Import GUI for Pokemon Team Builder.
Provides interface for importing Pokemon teams from game save files.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
from typing import Dict, List, Optional, Any

from src.gui.theme_manager import ThemeManager
from src.features.save_file_importer import (
    SaveFileImporter, SaveFileInfo, ImportedPokemon, 
    GameGeneration, SaveFileFormat
)
from src.teambuilder.team import PokemonTeam

class SaveFileImportFrame(tk.Frame):
    """Main save file import interface."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.importer = SaveFileImporter()
        self.current_save_info: Optional[SaveFileInfo] = None
        self.imported_pokemon: List[ImportedPokemon] = []
        self.imported_teams: List[PokemonTeam] = []
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container with notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # File Import Tab
        self.import_frame = tk.Frame(self.notebook)
        self.notebook.add(self.import_frame, text="Import Save File")
        self.setup_import_tab()
        
        # Pokemon View Tab
        self.pokemon_frame = tk.Frame(self.notebook)
        self.notebook.add(self.pokemon_frame, text="Imported Pokemon")
        self.setup_pokemon_tab()
        
        # Team Management Tab
        self.team_frame = tk.Frame(self.notebook)
        self.notebook.add(self.team_frame, text="Team Management")
        self.setup_team_tab()
        
        # Import History Tab
        self.history_frame = tk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Import History")
        self.setup_history_tab()
    
    def setup_import_tab(self):
        """Set up the file import interface."""
        # File Selection Section
        selection_frame = tk.LabelFrame(self.import_frame, text="Select Save File")
        selection_frame.pack(fill='x', padx=10, pady=5)
        
        # File path entry
        path_frame = tk.Frame(selection_frame)
        path_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(path_frame, text="Save File:").pack(side='left', padx=5)
        
        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(path_frame, textvariable=self.file_path_var, width=50)
        self.file_path_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        self.browse_btn = tk.Button(path_frame, text="Browse...", command=self.browse_file)
        self.browse_btn.pack(side='right', padx=5)
        
        # File analysis section
        analysis_frame = tk.LabelFrame(self.import_frame, text="Save File Analysis")
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        self.analyze_btn = tk.Button(analysis_frame, text="Analyze Save File", 
                                   command=self.analyze_file)
        self.analyze_btn.pack(pady=5)
        
        # Analysis results
        self.analysis_text = tk.Text(analysis_frame, height=8, width=60)
        analysis_scroll = tk.Scrollbar(analysis_frame, orient='vertical', command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scroll.set)
        
        self.analysis_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        analysis_scroll.pack(side='right', fill='y', pady=5)
        
        # Import controls
        import_frame = tk.LabelFrame(self.import_frame, text="Import Options")
        import_frame.pack(fill='x', padx=10, pady=5)
        
        # Import settings
        settings_frame = tk.Frame(import_frame)
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(settings_frame, text="Team Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.team_name_var = tk.StringVar(value="Imported Team")
        team_name_entry = tk.Entry(settings_frame, textvariable=self.team_name_var, width=30)
        team_name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        self.import_party_var = tk.BooleanVar(value=True)
        party_check = tk.Checkbutton(settings_frame, text="Import Party Pokemon", 
                                   variable=self.import_party_var)
        party_check.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=2)
        
        self.import_pc_var = tk.BooleanVar(value=False)
        pc_check = tk.Checkbutton(settings_frame, text="Import PC Pokemon (Coming Soon)", 
                                variable=self.import_pc_var, state='disabled')
        pc_check.grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=2)
        
        # Import button
        self.import_btn = tk.Button(import_frame, text="Import Pokemon", 
                                  command=self.import_pokemon, state='disabled')
        self.import_btn.pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(import_frame, variable=self.progress_var, 
                                          maximum=100, length=300)
        self.progress_bar.pack(pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to import save files")
        self.status_label = tk.Label(import_frame, textvariable=self.status_var, 
                                   font=('Arial', 10))
        self.status_label.pack(pady=5)
    
    def setup_pokemon_tab(self):
        """Set up the Pokemon viewing interface."""
        # Pokemon list
        list_frame = tk.Frame(self.pokemon_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Pokemon tree view
        columns = ('Species', 'Nickname', 'Level', 'Nature', 'Ability', 'HP', 'ATK', 'DEF', 'SPA', 'SPD', 'SPE')
        self.pokemon_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = {'Species': 100, 'Nickname': 100, 'Level': 50, 'Nature': 80, 'Ability': 100,
                        'HP': 50, 'ATK': 50, 'DEF': 50, 'SPA': 50, 'SPD': 50, 'SPE': 50}
        
        for col in columns:
            self.pokemon_tree.heading(col, text=col)
            self.pokemon_tree.column(col, width=column_widths.get(col, 80))
        
        # Scrollbars
        tree_v_scroll = tk.Scrollbar(list_frame, orient='vertical', command=self.pokemon_tree.yview)
        tree_h_scroll = tk.Scrollbar(list_frame, orient='horizontal', command=self.pokemon_tree.xview)
        self.pokemon_tree.configure(yscrollcommand=tree_v_scroll.set, xscrollcommand=tree_h_scroll.set)
        
        self.pokemon_tree.pack(side='left', fill='both', expand=True)
        tree_v_scroll.pack(side='right', fill='y')
        tree_h_scroll.pack(side='bottom', fill='x')
        
        # Pokemon details
        details_frame = tk.LabelFrame(self.pokemon_frame, text="Pokemon Details")
        details_frame.pack(fill='x', padx=10, pady=5)
        
        self.details_text = tk.Text(details_frame, height=8, width=60)
        details_scroll = tk.Scrollbar(details_frame, orient='vertical', command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        details_scroll.pack(side='right', fill='y', pady=5)
        
        # Bind selection
        self.pokemon_tree.bind('<<TreeviewSelect>>', self.on_pokemon_select)
        
        # Control buttons
        control_frame = tk.Frame(self.pokemon_frame)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        self.refresh_pokemon_btn = tk.Button(control_frame, text="Refresh List", 
                                           command=self.refresh_pokemon_list)
        self.refresh_pokemon_btn.pack(side='left', padx=5)
        
        self.export_pokemon_btn = tk.Button(control_frame, text="Export Pokemon Data", 
                                          command=self.export_pokemon_data)
        self.export_pokemon_btn.pack(side='left', padx=5)
    
    def setup_team_tab(self):
        """Set up the team management interface."""
        # Team creation section
        creation_frame = tk.LabelFrame(self.team_frame, text="Create Team from Imported Pokemon")
        creation_frame.pack(fill='x', padx=10, pady=5)
        
        # Team selection
        selection_frame = tk.Frame(creation_frame)
        selection_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(selection_frame, text="Select Pokemon for Team:").pack(anchor='w')
        
        # Pokemon selection listbox
        self.team_pokemon_listbox = tk.Listbox(selection_frame, selectmode='multiple', height=6)
        team_scroll = tk.Scrollbar(selection_frame, orient='vertical', command=self.team_pokemon_listbox.yview)
        self.team_pokemon_listbox.configure(yscrollcommand=team_scroll.set)
        
        self.team_pokemon_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        team_scroll.pack(side='right', fill='y', pady=5)
        
        # Team creation controls
        team_controls = tk.Frame(creation_frame)
        team_controls.pack(fill='x', padx=5, pady=5)
        
        tk.Label(team_controls, text="New Team Name:").pack(side='left', padx=5)
        
        self.new_team_name_var = tk.StringVar(value="Custom Team")
        new_team_entry = tk.Entry(team_controls, textvariable=self.new_team_name_var, width=25)
        new_team_entry.pack(side='left', padx=5)
        
        self.create_team_btn = tk.Button(team_controls, text="Create Team", 
                                       command=self.create_custom_team)
        self.create_team_btn.pack(side='left', padx=10)
        
        # Imported teams list
        teams_frame = tk.LabelFrame(self.team_frame, text="Imported Teams")
        teams_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Teams tree view
        team_columns = ('Team Name', 'Pokemon Count', 'Average Level', 'Import Date')
        self.teams_tree = ttk.Treeview(teams_frame, columns=team_columns, show='headings')
        
        for col in team_columns:
            self.teams_tree.heading(col, text=col)
            if col == 'Team Name':
                self.teams_tree.column(col, width=200)
            else:
                self.teams_tree.column(col, width=120)
        
        teams_tree_scroll = tk.Scrollbar(teams_frame, orient='vertical', command=self.teams_tree.yview)
        self.teams_tree.configure(yscrollcommand=teams_tree_scroll.set)
        
        self.teams_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        teams_tree_scroll.pack(side='right', fill='y', pady=5)
        
        # Team management buttons
        team_mgmt_frame = tk.Frame(self.team_frame)
        team_mgmt_frame.pack(fill='x', padx=10, pady=5)
        
        self.use_team_btn = tk.Button(team_mgmt_frame, text="Use in Team Builder", 
                                    command=self.use_team_in_builder)
        self.use_team_btn.pack(side='left', padx=5)
        
        self.export_team_btn = tk.Button(team_mgmt_frame, text="Export Team", 
                                       command=self.export_team)
        self.export_team_btn.pack(side='left', padx=5)
        
        self.delete_team_btn = tk.Button(team_mgmt_frame, text="Delete Team", 
                                       command=self.delete_team)
        self.delete_team_btn.pack(side='left', padx=5)
    
    def setup_history_tab(self):
        """Set up the import history interface."""
        # History list
        history_frame = tk.LabelFrame(self.history_frame, text="Import History")
        history_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # History tree view
        history_columns = ('Date', 'File Name', 'Game Version', 'Pokemon Imported', 'Status')
        self.history_tree = ttk.Treeview(history_frame, columns=history_columns, show='headings')
        
        column_widths = {'Date': 120, 'File Name': 200, 'Game Version': 150, 
                        'Pokemon Imported': 120, 'Status': 100}
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths.get(col, 100))
        
        history_scroll = tk.Scrollbar(history_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        history_scroll.pack(side='right', fill='y', pady=5)
        
        # History controls
        history_controls = tk.Frame(self.history_frame)
        history_controls.pack(fill='x', padx=10, pady=5)
        
        self.clear_history_btn = tk.Button(history_controls, text="Clear History", 
                                         command=self.clear_history)
        self.clear_history_btn.pack(side='left', padx=5)
        
        self.export_history_btn = tk.Button(history_controls, text="Export History", 
                                          command=self.export_history)
        self.export_history_btn.pack(side='left', padx=5)
    
    def apply_theme(self):
        """Apply the current theme."""
        if hasattr(self.theme_manager, 'apply_to_widget'):
            self.theme_manager.apply_to_widget(self)
    
    def browse_file(self):
        """Browse for a save file."""
        file_types = [
            ("All Save Files", "*.sav;*.pk3;*.pk4;*.pk5;*.pk6;*.pk7;*.pk8;*.pk9;*.pkm"),
            ("Save Files", "*.sav"),
            ("Pokemon Files", "*.pk3;*.pk4;*.pk5;*.pk6;*.pk7;*.pk8;*.pk9;*.pkm"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Pokemon Save File",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set("File selected - click Analyze to examine")
    
    def analyze_file(self):
        """Analyze the selected save file."""
        file_path = self.file_path_var.get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a save file first")
            return
        
        self.status_var.set("Analyzing save file...")
        self.progress_var.set(25)
        
        # Run analysis in a separate thread to prevent UI freezing
        def analyze_thread():
            try:
                save_info = self.importer.analyze_save_file(file_path)
                
                # Update UI in main thread
                self.after(0, lambda: self.display_analysis_results(save_info))
                
            except Exception as e:
                self.after(0, lambda: self.handle_analysis_error(str(e)))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def display_analysis_results(self, save_info: Optional[SaveFileInfo]):
        """Display the analysis results."""
        self.progress_var.set(100)
        
        if not save_info:
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, "Error: Could not analyze save file")
            self.status_var.set("Analysis failed")
            return
        
        self.current_save_info = save_info
        
        # Display analysis results
        self.analysis_text.delete(1.0, tk.END)
        
        if save_info.is_valid:
            analysis = f"SAVE FILE ANALYSIS\n"
            analysis += f"{'='*50}\n\n"
            analysis += f"File Path: {save_info.file_path}\n"
            analysis += f"Game Generation: {save_info.game_generation.value.upper()}\n"
            analysis += f"Game Version: {save_info.game_version}\n"
            analysis += f"File Format: {save_info.file_format.value.upper()}\n\n"
            analysis += f"Trainer Information:\n"
            analysis += f"  Name: {save_info.trainer_name}\n"
            analysis += f"  ID: {save_info.trainer_id}\n"
            analysis += f"  Play Time: {save_info.play_time}\n\n"
            analysis += f"Pokemon Count: {save_info.pokemon_count}\n\n"
            analysis += f"Status: ✅ Valid save file - ready for import\n"
            
            self.import_btn.config(state='normal')
            self.status_var.set("Analysis complete - ready to import")
        else:
            analysis = f"SAVE FILE ANALYSIS - ERROR\n"
            analysis += f"{'='*50}\n\n"
            analysis += f"File Path: {save_info.file_path}\n"
            analysis += f"Error: {save_info.error_message}\n\n"
            analysis += f"Status: ❌ Invalid or unsupported save file\n"
            
            self.import_btn.config(state='disabled')
            self.status_var.set("Analysis failed - unsupported file")
        
        self.analysis_text.insert(tk.END, analysis)
        self.progress_var.set(0)
    
    def handle_analysis_error(self, error_message: str):
        """Handle analysis errors."""
        self.progress_var.set(0)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, f"Analysis Error: {error_message}")
        self.status_var.set("Analysis error occurred")
        messagebox.showerror("Analysis Error", f"Failed to analyze save file:\n{error_message}")
    
    def import_pokemon(self):
        """Import Pokemon from the analyzed save file."""
        if not self.current_save_info or not self.current_save_info.is_valid:
            messagebox.showerror("Error", "No valid save file analyzed")
            return
        
        team_name = self.team_name_var.get().strip()
        if not team_name:
            team_name = "Imported Team"
        
        self.status_var.set("Importing Pokemon...")
        self.progress_var.set(50)
        
        # Run import in separate thread
        def import_thread():
            try:
                pokemon_list, save_info = self.importer.import_pokemon_from_save(
                    self.current_save_info.file_path
                )
                
                # Update UI in main thread
                self.after(0, lambda: self.handle_import_results(pokemon_list, save_info, team_name))
                
            except Exception as e:
                self.after(0, lambda: self.handle_import_error(str(e)))
        
        threading.Thread(target=import_thread, daemon=True).start()
    
    def handle_import_results(self, pokemon_list: List[ImportedPokemon], 
                            save_info: SaveFileInfo, team_name: str):
        """Handle successful import results."""
        self.progress_var.set(100)
        
        if not pokemon_list:
            messagebox.showwarning("Import Warning", "No Pokemon were found in the save file")
            self.status_var.set("Import completed - no Pokemon found")
            self.progress_var.set(0)
            return
        
        # Store imported Pokemon
        self.imported_pokemon = pokemon_list
        
        # Create team
        team = self.importer.create_team_from_imported(pokemon_list, team_name)
        self.imported_teams.append(team)
        
        # Update UI
        self.refresh_pokemon_list()
        self.refresh_teams_list()
        self.update_team_pokemon_list()
        
        # Add to history
        self.add_to_history(save_info, len(pokemon_list), "Success")
        
        # Show success message
        message = f"Successfully imported {len(pokemon_list)} Pokemon!\n\n"
        message += f"Team '{team_name}' created with {len(team.pokemon)} Pokemon.\n"
        message_box = messagebox.showinfo("Import Successful", message)
        
        self.status_var.set(f"Import completed - {len(pokemon_list)} Pokemon imported")
        self.progress_var.set(0)
        
        # Switch to Pokemon tab to show results
        self.notebook.select(self.pokemon_frame)
    
    def handle_import_error(self, error_message: str):
        """Handle import errors."""
        self.progress_var.set(0)
        self.status_var.set("Import error occurred")
        messagebox.showerror("Import Error", f"Failed to import Pokemon:\n{error_message}")
        
        if self.current_save_info:
            self.add_to_history(self.current_save_info, 0, "Failed")
    
    def refresh_pokemon_list(self):
        """Refresh the Pokemon list display."""
        # Clear existing items
        for item in self.pokemon_tree.get_children():
            self.pokemon_tree.delete(item)
        
        # Add imported Pokemon
        for pokemon in self.imported_pokemon:
            values = (
                pokemon.species_name,
                pokemon.nickname if pokemon.nickname != pokemon.species_name else "",
                pokemon.level,
                pokemon.nature,
                pokemon.ability,
                pokemon.hp,
                pokemon.attack,
                pokemon.defense,
                pokemon.sp_attack,
                pokemon.sp_defense,
                pokemon.speed
            )
            self.pokemon_tree.insert('', 'end', values=values)
    
    def on_pokemon_select(self, event):
        """Handle Pokemon selection in the tree."""
        selection = self.pokemon_tree.selection()
        if not selection:
            return
        
        # Get selected index
        selected_item = selection[0]
        index = self.pokemon_tree.index(selected_item)
        
        if 0 <= index < len(self.imported_pokemon):
            pokemon = self.imported_pokemon[index]
            self.display_pokemon_details(pokemon)
    
    def display_pokemon_details(self, pokemon: ImportedPokemon):
        """Display detailed Pokemon information."""
        self.details_text.delete(1.0, tk.END)
        
        details = f"POKEMON DETAILS\n"
        details += f"{'='*40}\n\n"
        details += f"Species: {pokemon.species_name} (#{pokemon.species_id})\n"
        details += f"Nickname: {pokemon.nickname}\n"
        details += f"Level: {pokemon.level}\n"
        details += f"Nature: {pokemon.nature}\n"
        details += f"Ability: {pokemon.ability}\n"
        details += f"Held Item: {pokemon.held_item or 'None'}\n"
        details += f"Gender: {pokemon.gender}\n"
        details += f"Shiny: {'Yes' if pokemon.is_shiny else 'No'}\n\n"
        
        details += f"STATS:\n"
        details += f"  HP: {pokemon.hp}\n"
        details += f"  Attack: {pokemon.attack}\n"
        details += f"  Defense: {pokemon.defense}\n"
        details += f"  Sp. Attack: {pokemon.sp_attack}\n"
        details += f"  Sp. Defense: {pokemon.sp_defense}\n"
        details += f"  Speed: {pokemon.speed}\n\n"
        
        details += f"IVs:\n"
        details += f"  HP: {pokemon.hp_iv}\n"
        details += f"  Attack: {pokemon.attack_iv}\n"
        details += f"  Defense: {pokemon.defense_iv}\n"
        details += f"  Sp. Attack: {pokemon.sp_attack_iv}\n"
        details += f"  Sp. Defense: {pokemon.sp_defense_iv}\n"
        details += f"  Speed: {pokemon.speed_iv}\n\n"
        
        details += f"EVs:\n"
        details += f"  HP: {pokemon.hp_ev}\n"
        details += f"  Attack: {pokemon.attack_ev}\n"
        details += f"  Defense: {pokemon.defense_ev}\n"
        details += f"  Sp. Attack: {pokemon.sp_attack_ev}\n"
        details += f"  Sp. Defense: {pokemon.sp_defense_ev}\n"
        details += f"  Speed: {pokemon.speed_ev}\n\n"
        
        details += f"MOVES:\n"
        for i, move in enumerate(pokemon.moves, 1):
            if move and move != "---":
                details += f"  {i}. {move}\n"
        
        details += f"\nORIGINAL TRAINER INFO:\n"
        details += f"  Trainer: {pokemon.original_trainer}\n"
        details += f"  ID: {pokemon.trainer_id}\n"
        details += f"  Location Met: {pokemon.location_met}\n"
        details += f"  Level Met: {pokemon.level_met}\n"
        details += f"  Pokeball: {pokemon.pokeball}\n"
        
        self.details_text.insert(tk.END, details)
    
    def update_team_pokemon_list(self):
        """Update the team Pokemon selection list."""
        self.team_pokemon_listbox.delete(0, tk.END)
        
        for i, pokemon in enumerate(self.imported_pokemon):
            display_text = f"{pokemon.species_name} (Lv.{pokemon.level}) - {pokemon.nature}"
            if pokemon.nickname != pokemon.species_name:
                display_text = f"{pokemon.nickname} ({pokemon.species_name}, Lv.{pokemon.level})"
            self.team_pokemon_listbox.insert(tk.END, display_text)
    
    def create_custom_team(self):
        """Create a custom team from selected Pokemon."""
        selected_indices = self.team_pokemon_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select Pokemon for the team")
            return
        
        if len(selected_indices) > 6:
            messagebox.showwarning("Too Many Pokemon", "A team can have maximum 6 Pokemon")
            return
        
        team_name = self.new_team_name_var.get().strip()
        if not team_name:
            team_name = "Custom Team"
        
        # Create team from selected Pokemon
        selected_pokemon = [self.imported_pokemon[i] for i in selected_indices]
        team = self.importer.create_team_from_imported(selected_pokemon, team_name)
        
        self.imported_teams.append(team)
        self.refresh_teams_list()
        
        messagebox.showinfo("Team Created", f"Team '{team_name}' created with {len(selected_pokemon)} Pokemon!")
    
    def refresh_teams_list(self):
        """Refresh the teams list display."""
        # Clear existing items
        for item in self.teams_tree.get_children():
            self.teams_tree.delete(item)
        
        # Add imported teams
        for team in self.imported_teams:
            avg_level = sum(p.level for p in team.pokemon) / len(team.pokemon) if team.pokemon else 0
            values = (
                team.name,
                len(team.pokemon),
                f"{avg_level:.1f}",
                "2025-10-25"  # Current date
            )
            self.teams_tree.insert('', 'end', values=values)
    
    def use_team_in_builder(self):
        """Use selected team in team builder."""
        messagebox.showinfo("Coming Soon", "Team Builder integration coming soon!")
    
    def export_team(self):
        """Export selected team."""
        messagebox.showinfo("Coming Soon", "Team export functionality coming soon!")
    
    def delete_team(self):
        """Delete selected team."""
        selection = self.teams_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a team to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this team?"):
            # Get selected index and remove team
            selected_item = selection[0]
            index = self.teams_tree.index(selected_item)
            
            if 0 <= index < len(self.imported_teams):
                del self.imported_teams[index]
                self.refresh_teams_list()
                messagebox.showinfo("Team Deleted", "Team deleted successfully!")
    
    def add_to_history(self, save_info: SaveFileInfo, pokemon_count: int, status: str):
        """Add import to history."""
        values = (
            "2025-10-25",  # Current date
            save_info.file_path.split('/')[-1].split('\\')[-1],  # File name only
            save_info.game_version,
            pokemon_count,
            status
        )
        self.history_tree.insert('', 'end', values=values)
    
    def clear_history(self):
        """Clear import history."""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the import history?"):
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            messagebox.showinfo("History Cleared", "Import history cleared!")
    
    def export_history(self):
        """Export import history."""
        messagebox.showinfo("Coming Soon", "History export functionality coming soon!")
    
    def export_pokemon_data(self):
        """Export Pokemon data to JSON."""
        if not self.imported_pokemon:
            messagebox.showwarning("No Data", "No imported Pokemon to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Pokemon Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                export_data = []
                for pokemon in self.imported_pokemon:
                    export_data.append({
                        'species': pokemon.species_name,
                        'nickname': pokemon.nickname,
                        'level': pokemon.level,
                        'nature': pokemon.nature,
                        'ability': pokemon.ability,
                        'stats': {
                            'hp': pokemon.hp,
                            'attack': pokemon.attack,
                            'defense': pokemon.defense,
                            'sp_attack': pokemon.sp_attack,
                            'sp_defense': pokemon.sp_defense,
                            'speed': pokemon.speed
                        },
                        'ivs': {
                            'hp': pokemon.hp_iv,
                            'attack': pokemon.attack_iv,
                            'defense': pokemon.defense_iv,
                            'sp_attack': pokemon.sp_attack_iv,
                            'sp_defense': pokemon.sp_defense_iv,
                            'speed': pokemon.speed_iv
                        },
                        'evs': {
                            'hp': pokemon.hp_ev,
                            'attack': pokemon.attack_ev,
                            'defense': pokemon.defense_ev,
                            'sp_attack': pokemon.sp_attack_ev,
                            'sp_defense': pokemon.sp_defense_ev,
                            'speed': pokemon.speed_ev
                        },
                        'moves': pokemon.moves,
                        'is_shiny': pokemon.is_shiny,
                        'held_item': pokemon.held_item
                    })
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Export Successful", f"Pokemon data exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Save File Import Test")
    root.geometry("1200x800")
    
    # Create a mock theme manager
    class MockThemeManager:
        def apply_to_widget(self, widget):
            pass
    
    theme_manager = MockThemeManager()
    import_frame = SaveFileImportFrame(root, theme_manager)
    import_frame.pack(fill='both', expand=True)
    
    root.mainloop()