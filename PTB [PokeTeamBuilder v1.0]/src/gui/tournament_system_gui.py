"""
Tournament System GUI for Pokemon Team Builder.
Provides interface for creating tournaments, managing brackets, and viewing results.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.gui.theme_manager import ThemeManager
from src.features.tournament_system import (
    TournamentManager, Tournament, TournamentFormat, TournamentStatus,
    MatchStatus, Player
)

class TournamentSystemFrame(tk.Frame):
    """Main tournament system interface."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.tournament_manager = TournamentManager()
        self.current_tournament: Optional[Tournament] = None
        
        self.setup_ui()
        self.apply_theme()
        self.refresh_tournaments()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container with notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tournament Management Tab
        self.management_frame = tk.Frame(self.notebook)
        self.notebook.add(self.management_frame, text="Tournament Management")
        self.setup_management_tab()
        
        # Bracket View Tab
        self.bracket_frame = tk.Frame(self.notebook)
        self.notebook.add(self.bracket_frame, text="Bracket View")
        self.setup_bracket_tab()
        
        # Leaderboard Tab
        self.leaderboard_frame = tk.Frame(self.notebook)
        self.notebook.add(self.leaderboard_frame, text="Leaderboard")
        self.setup_leaderboard_tab()
        
        # Results Tab
        self.results_frame = tk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        self.setup_results_tab()
    
    def setup_management_tab(self):
        """Set up tournament management interface."""
        # Tournament Creation Section
        creation_frame = tk.LabelFrame(self.management_frame, text="Create New Tournament")
        creation_frame.pack(fill='x', padx=10, pady=5)
        
        # Tournament name
        tk.Label(creation_frame, text="Tournament Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.name_entry = tk.Entry(creation_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Tournament format
        tk.Label(creation_frame, text="Format:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.format_var = tk.StringVar(value="single_elimination")
        format_combo = ttk.Combobox(creation_frame, textvariable=self.format_var, state="readonly")
        format_combo['values'] = ["single_elimination", "double_elimination", "round_robin", "swiss"]
        format_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Max players
        tk.Label(creation_frame, text="Max Players:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.max_players_var = tk.IntVar(value=16)
        max_players_spin = tk.Spinbox(creation_frame, from_=4, to=64, textvariable=self.max_players_var, width=10)
        max_players_spin.grid(row=2, column=1, padx=5, pady=2)
        
        # Create button
        create_btn = tk.Button(creation_frame, text="Create Tournament", 
                              command=self.create_tournament)
        create_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Tournament List Section
        list_frame = tk.LabelFrame(self.management_frame, text="Active Tournaments")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tournament listbox with scrollbar
        list_container = tk.Frame(list_frame)
        list_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.tournament_listbox = tk.Listbox(list_container)
        list_scrollbar = tk.Scrollbar(list_container, orient='vertical', command=self.tournament_listbox.yview)
        self.tournament_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.tournament_listbox.pack(side='left', fill='both', expand=True)
        list_scrollbar.pack(side='right', fill='y')
        
        self.tournament_listbox.bind('<<ListboxSelect>>', self.on_tournament_select)
        
        # Tournament actions
        actions_frame = tk.Frame(list_frame)
        actions_frame.pack(fill='x', padx=5, pady=5)
        
        self.select_btn = tk.Button(actions_frame, text="Select Tournament", 
                                   command=self.select_tournament, state='disabled')
        self.select_btn.pack(side='left', padx=5)
        
        self.start_btn = tk.Button(actions_frame, text="Start Tournament", 
                                  command=self.start_tournament, state='disabled')
        self.start_btn.pack(side='left', padx=5)
        
        self.delete_btn = tk.Button(actions_frame, text="Delete Tournament", 
                                   command=self.delete_tournament, state='disabled')
        self.delete_btn.pack(side='left', padx=5)
        
        # Player Registration Section
        player_frame = tk.LabelFrame(self.management_frame, text="Player Management")
        player_frame.pack(fill='x', padx=10, pady=5)
        
        # Player name entry
        tk.Label(player_frame, text="Player Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.player_name_entry = tk.Entry(player_frame, width=20)
        self.player_name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Register button
        self.register_btn = tk.Button(player_frame, text="Register Player", 
                                     command=self.register_player, state='disabled')
        self.register_btn.grid(row=0, column=2, padx=5, pady=2)
        
        # Registered players list
        tk.Label(player_frame, text="Registered Players:").grid(row=1, column=0, sticky='nw', padx=5, pady=2)
        self.players_listbox = tk.Listbox(player_frame, height=6)
        self.players_listbox.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        player_frame.grid_columnconfigure(1, weight=1)
    
    def setup_bracket_tab(self):
        """Set up bracket visualization interface."""
        # Tournament info
        info_frame = tk.Frame(self.bracket_frame)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        self.tournament_info_label = tk.Label(info_frame, text="No tournament selected", 
                                            font=('Arial', 12, 'bold'))
        self.tournament_info_label.pack()
        
        # Bracket container with scrolling
        bracket_container = tk.Frame(self.bracket_frame)
        bracket_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Canvas for bracket visualization
        self.bracket_canvas = tk.Canvas(bracket_container, bg='white')
        bracket_h_scroll = tk.Scrollbar(bracket_container, orient='horizontal', command=self.bracket_canvas.xview)
        bracket_v_scroll = tk.Scrollbar(bracket_container, orient='vertical', command=self.bracket_canvas.yview)
        
        self.bracket_canvas.configure(xscrollcommand=bracket_h_scroll.set, yscrollcommand=bracket_v_scroll.set)
        
        self.bracket_canvas.pack(side='left', fill='both', expand=True)
        bracket_v_scroll.pack(side='right', fill='y')
        bracket_h_scroll.pack(side='bottom', fill='x')
        
        # Match completion controls
        controls_frame = tk.Frame(self.bracket_frame)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(controls_frame, text="Complete Match:").pack(side='left', padx=5)
        
        self.match_var = tk.StringVar()
        self.match_combo = ttk.Combobox(controls_frame, textvariable=self.match_var, 
                                       state="readonly", width=20)
        self.match_combo.pack(side='left', padx=5)
        
        tk.Label(controls_frame, text="Winner:").pack(side='left', padx=5)
        
        self.winner_var = tk.StringVar()
        self.winner_combo = ttk.Combobox(controls_frame, textvariable=self.winner_var, 
                                        state="readonly", width=15)
        self.winner_combo.pack(side='left', padx=5)
        
        self.complete_match_btn = tk.Button(controls_frame, text="Complete Match", 
                                           command=self.complete_match, state='disabled')
        self.complete_match_btn.pack(side='left', padx=5)
        
        self.refresh_bracket_btn = tk.Button(controls_frame, text="Refresh Bracket", 
                                           command=self.refresh_bracket)
        self.refresh_bracket_btn.pack(side='left', padx=5)
    
    def setup_leaderboard_tab(self):
        """Set up leaderboard interface."""
        # Leaderboard tree
        columns = ('Rank', 'Player', 'Rating', 'Wins', 'Losses', 'Tournaments', 'Win Rate')
        self.leaderboard_tree = ttk.Treeview(self.leaderboard_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.leaderboard_tree.heading(col, text=col)
            if col == 'Player':
                self.leaderboard_tree.column(col, width=150)
            else:
                self.leaderboard_tree.column(col, width=80)
        
        # Scrollbar for leaderboard
        leaderboard_scroll = tk.Scrollbar(self.leaderboard_frame, orient='vertical', 
                                        command=self.leaderboard_tree.yview)
        self.leaderboard_tree.configure(yscrollcommand=leaderboard_scroll.set)
        
        self.leaderboard_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        leaderboard_scroll.pack(side='right', fill='y', pady=10)
        
        # Refresh button
        refresh_leaderboard_btn = tk.Button(self.leaderboard_frame, text="Refresh Leaderboard", 
                                          command=self.refresh_leaderboard)
        refresh_leaderboard_btn.pack(pady=5)
    
    def setup_results_tab(self):
        """Set up results and statistics interface."""
        # Tournament selection for results
        selection_frame = tk.Frame(self.results_frame)
        selection_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(selection_frame, text="Select Tournament:").pack(side='left', padx=5)
        
        self.results_tournament_var = tk.StringVar()
        self.results_tournament_combo = ttk.Combobox(selection_frame, textvariable=self.results_tournament_var, 
                                                   state="readonly", width=30)
        self.results_tournament_combo.pack(side='left', padx=5)
        self.results_tournament_combo.bind('<<ComboboxSelected>>', self.on_results_tournament_select)
        
        # Results display
        results_container = tk.Frame(self.results_frame)
        results_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tournament info
        self.results_info_text = tk.Text(results_container, height=8, width=60)
        results_info_scroll = tk.Scrollbar(results_container, orient='vertical', command=self.results_info_text.yview)
        self.results_info_text.configure(yscrollcommand=results_info_scroll.set)
        
        self.results_info_text.pack(side='left', fill='both', expand=True)
        results_info_scroll.pack(side='right', fill='y')
        
        # Export buttons
        export_frame = tk.Frame(self.results_frame)
        export_frame.pack(fill='x', padx=10, pady=5)
        
        export_json_btn = tk.Button(export_frame, text="Export Results (JSON)", 
                                   command=self.export_results_json)
        export_json_btn.pack(side='left', padx=5)
        
        export_bracket_btn = tk.Button(export_frame, text="Export Bracket", 
                                      command=self.export_bracket)
        export_bracket_btn.pack(side='left', padx=5)
    
    def apply_theme(self):
        """Apply the current theme."""
        if hasattr(self.theme_manager, 'apply_to_widget'):
            self.theme_manager.apply_to_widget(self)
    
    def create_tournament(self):
        """Create a new tournament."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a tournament name")
            return
        
        try:
            format_type = TournamentFormat(self.format_var.get())
            max_players = self.max_players_var.get()
            
            tournament = self.tournament_manager.create_tournament(name, format_type, max_players)
            
            self.name_entry.delete(0, tk.END)
            self.refresh_tournaments()
            
            messagebox.showinfo("Success", f"Tournament '{name}' created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create tournament: {str(e)}")
    
    def refresh_tournaments(self):
        """Refresh the tournament list."""
        self.tournament_listbox.delete(0, tk.END)
        
        active_tournaments = self.tournament_manager.get_active_tournaments()
        for tournament in active_tournaments:
            status_text = tournament.status.value.replace('_', ' ').title()
            display_text = f"{tournament.name} ({status_text}, {len(tournament.players)} players)"
            self.tournament_listbox.insert(tk.END, display_text)
        
        # Update results tournament combo
        all_tournaments = list(self.tournament_manager.tournaments.values())
        tournament_names = [f"{t.name} ({t.id[:8]})" for t in all_tournaments]
        self.results_tournament_combo['values'] = tournament_names
        
        self.update_ui_state()
    
    def on_tournament_select(self, event):
        """Handle tournament selection."""
        self.update_ui_state()
    
    def update_ui_state(self):
        """Update UI button states."""
        has_selection = bool(self.tournament_listbox.curselection())
        
        self.select_btn.config(state='normal' if has_selection else 'disabled')
        self.delete_btn.config(state='normal' if has_selection else 'disabled')
        
        # Start button only for registration tournaments
        if has_selection and self.current_tournament:
            can_start = (self.current_tournament.status == TournamentStatus.REGISTRATION and 
                        len(self.current_tournament.players) >= 2)
            self.start_btn.config(state='normal' if can_start else 'disabled')
        else:
            self.start_btn.config(state='disabled')
        
        # Register button only for registration tournaments
        has_tournament = self.current_tournament is not None
        can_register = (has_tournament and 
                       self.current_tournament.status == TournamentStatus.REGISTRATION)
        self.register_btn.config(state='normal' if can_register else 'disabled')
        
        # Match completion controls
        has_active_tournament = (self.current_tournament and 
                               self.current_tournament.status == TournamentStatus.IN_PROGRESS)
        self.complete_match_btn.config(state='normal' if has_active_tournament else 'disabled')
    
    def select_tournament(self):
        """Select the current tournament."""
        selection = self.tournament_listbox.curselection()
        if not selection:
            return
        
        active_tournaments = self.tournament_manager.get_active_tournaments()
        tournament = active_tournaments[selection[0]]
        self.current_tournament = tournament
        
        self.refresh_players_list()
        self.refresh_bracket()
        self.update_match_combos()
        self.update_ui_state()
        
        messagebox.showinfo("Tournament Selected", f"Selected: {tournament.name}")
    
    def start_tournament(self):
        """Start the selected tournament."""
        if not self.current_tournament:
            messagebox.showerror("Error", "No tournament selected")
            return
        
        if len(self.current_tournament.players) < 2:
            messagebox.showerror("Error", "Need at least 2 players to start tournament")
            return
        
        if self.current_tournament.start_tournament():
            self.refresh_tournaments()
            self.refresh_bracket()
            self.update_match_combos()
            messagebox.showinfo("Success", f"Tournament '{self.current_tournament.name}' started!")
        else:
            messagebox.showerror("Error", "Failed to start tournament")
    
    def delete_tournament(self):
        """Delete the selected tournament."""
        selection = self.tournament_listbox.curselection()
        if not selection:
            return
        
        active_tournaments = self.tournament_manager.get_active_tournaments()
        tournament = active_tournaments[selection[0]]
        
        if messagebox.askyesno("Confirm Delete", f"Delete tournament '{tournament.name}'?"):
            del self.tournament_manager.tournaments[tournament.id]
            if self.current_tournament == tournament:
                self.current_tournament = None
            self.refresh_tournaments()
            self.refresh_players_list()
            self.refresh_bracket()
    
    def register_player(self):
        """Register a new player."""
        if not self.current_tournament:
            messagebox.showerror("Error", "No tournament selected")
            return
        
        player_name = self.player_name_entry.get().strip()
        if not player_name:
            messagebox.showerror("Error", "Please enter a player name")
            return
        
        if self.tournament_manager.register_player(self.current_tournament.id, player_name):
            self.player_name_entry.delete(0, tk.END)
            self.refresh_players_list()
            self.refresh_tournaments()
            messagebox.showinfo("Success", f"Player '{player_name}' registered!")
        else:
            messagebox.showerror("Error", "Failed to register player")
    
    def refresh_players_list(self):
        """Refresh the registered players list."""
        self.players_listbox.delete(0, tk.END)
        
        if self.current_tournament:
            for player in self.current_tournament.players:
                self.players_listbox.insert(tk.END, f"{player.name} (Seed: {player.seed or 'TBD'})")
    
    def refresh_bracket(self):
        """Refresh the bracket visualization."""
        self.bracket_canvas.delete('all')
        
        if not self.current_tournament:
            self.tournament_info_label.config(text="No tournament selected")
            return
        
        tournament = self.current_tournament
        status_text = tournament.status.value.replace('_', ' ').title()
        info_text = f"{tournament.name} - {status_text} - {len(tournament.players)} Players"
        self.tournament_info_label.config(text=info_text)
        
        if not tournament.rounds:
            self.bracket_canvas.create_text(200, 100, text="Tournament not started", 
                                          font=('Arial', 14), fill='gray')
            return
        
        # Draw bracket
        self.draw_bracket(tournament)
    
    def draw_bracket(self, tournament: Tournament):
        """Draw the tournament bracket."""
        canvas = self.bracket_canvas
        
        # Calculate layout
        max_round = len(tournament.rounds)
        if max_round == 0:
            return
        
        round_width = 200
        match_height = 60
        canvas_width = max_round * round_width + 100
        
        # Set canvas size
        canvas.configure(scrollregion=(0, 0, canvas_width, 800))
        
        y_offset = 50
        
        for round_idx, tournament_round in enumerate(tournament.rounds):
            x = round_idx * round_width + 50
            
            # Round title
            canvas.create_text(x + round_width // 2, y_offset - 20, 
                             text=tournament_round.name, 
                             font=('Arial', 12, 'bold'))
            
            # Draw matches
            for match_idx, match in enumerate(tournament_round.matches):
                y = y_offset + match_idx * (match_height + 20)
                
                # Match box
                box_color = 'lightgreen' if match.status == MatchStatus.COMPLETED else 'lightblue'
                canvas.create_rectangle(x, y, x + round_width - 20, y + match_height, 
                                      fill=box_color, outline='black')
                
                # Player names
                player1_name = match.player1.name if match.player1 else "BYE"
                player2_name = match.player2.name if match.player2 else "BYE"
                
                canvas.create_text(x + 10, y + 15, text=player1_name, 
                                 anchor='w', font=('Arial', 10))
                canvas.create_text(x + 10, y + 35, text=player2_name, 
                                 anchor='w', font=('Arial', 10))
                
                # Winner indicator
                if match.winner:
                    winner_text = f"Winner: {match.winner.name}"
                    canvas.create_text(x + 10, y + 50, text=winner_text, 
                                     anchor='w', font=('Arial', 8, 'bold'), 
                                     fill='darkgreen')
                
                # Match score
                if match.score != "0-0":
                    canvas.create_text(x + round_width - 30, y + 30, text=match.score, 
                                     anchor='e', font=('Arial', 10))
    
    def update_match_combos(self):
        """Update match and winner combo boxes."""
        if not self.current_tournament or not self.current_tournament.rounds:
            self.match_combo['values'] = []
            self.winner_combo['values'] = []
            return
        
        # Get current round matches
        current_round = None
        for tournament_round in reversed(self.current_tournament.rounds):
            if not tournament_round.completed:
                current_round = tournament_round
                break
        
        if not current_round:
            self.match_combo['values'] = []
            self.winner_combo['values'] = []
            return
        
        # Populate match combo
        scheduled_matches = [match for match in current_round.matches 
                           if match.status == MatchStatus.SCHEDULED and not match.is_bye()]
        
        match_options = []
        for match in scheduled_matches:
            match_text = f"{match.player1.name} vs {match.player2.name}"
            match_options.append((match_text, match.id))
        
        self.match_combo['values'] = [option[0] for option in match_options]
        self._match_lookup = {option[0]: option[1] for option in match_options}
        
        # Update winner combo when match selected
        self.match_combo.bind('<<ComboboxSelected>>', self.on_match_select)
    
    def on_match_select(self, event):
        """Handle match selection for completion."""
        match_text = self.match_var.get()
        if not match_text or not self.current_tournament:
            return
        
        match_id = self._match_lookup.get(match_text)
        if not match_id:
            return
        
        # Find the match
        match = None
        for tournament_round in self.current_tournament.rounds:
            for m in tournament_round.matches:
                if m.id == match_id:
                    match = m
                    break
        
        if match and match.player1 and match.player2:
            self.winner_combo['values'] = [match.player1.name, match.player2.name]
    
    def complete_match(self):
        """Complete the selected match."""
        match_text = self.match_var.get()
        winner_name = self.winner_var.get()
        
        if not match_text or not winner_name:
            messagebox.showerror("Error", "Please select match and winner")
            return
        
        match_id = self._match_lookup.get(match_text)
        if not match_id:
            return
        
        # Find winner ID
        winner_id = None
        for tournament_round in self.current_tournament.rounds:
            for match in tournament_round.matches:
                if match.id == match_id:
                    if match.player1 and match.player1.name == winner_name:
                        winner_id = match.player1.id
                    elif match.player2 and match.player2.name == winner_name:
                        winner_id = match.player2.id
                    break
        
        if not winner_id:
            messagebox.showerror("Error", "Winner not found")
            return
        
        # Get score from user
        score = simpledialog.askstring("Match Score", "Enter match score (e.g., '2-1'):", 
                                     initialvalue="1-0")
        if not score:
            score = "1-0"
        
        # Complete the match
        if self.current_tournament.complete_match(match_id, winner_id, score):
            self.refresh_bracket()
            self.update_match_combos()
            messagebox.showinfo("Success", f"Match completed! Winner: {winner_name}")
        else:
            messagebox.showerror("Error", "Failed to complete match")
    
    def refresh_leaderboard(self):
        """Refresh the global leaderboard."""
        # Clear existing items
        for item in self.leaderboard_tree.get_children():
            self.leaderboard_tree.delete(item)
        
        # Get leaderboard data
        leaderboard = self.tournament_manager.get_leaderboard(50)
        
        # Populate tree
        for entry in leaderboard:
            values = (
                entry['rank'],
                entry['name'],
                entry['rating'],
                entry['wins'],
                entry['losses'],
                entry['tournaments'],
                f"{entry['win_rate']:.1%}"
            )
            self.leaderboard_tree.insert('', 'end', values=values)
    
    def on_results_tournament_select(self, event):
        """Handle tournament selection for results."""
        selection = self.results_tournament_var.get()
        if not selection:
            return
        
        # Extract tournament ID from selection
        tournament_id = None
        for tid, tournament in self.tournament_manager.tournaments.items():
            if selection.startswith(tournament.name):
                tournament_id = tid
                break
        
        if not tournament_id:
            return
        
        tournament = self.tournament_manager.get_tournament(tournament_id)
        if not tournament:
            return
        
        # Display tournament results
        self.display_tournament_results(tournament)
    
    def display_tournament_results(self, tournament: Tournament):
        """Display detailed tournament results."""
        self.results_info_text.delete(1.0, tk.END)
        
        # Tournament info
        info = f"Tournament: {tournament.name}\n"
        info += f"Format: {tournament.format.value.replace('_', ' ').title()}\n"
        info += f"Status: {tournament.status.value.replace('_', ' ').title()}\n"
        info += f"Players: {len(tournament.players)}\n"
        info += f"Created: {tournament.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        
        if tournament.started_at:
            info += f"Started: {tournament.started_at.strftime('%Y-%m-%d %H:%M')}\n"
        
        if tournament.completed_at:
            info += f"Completed: {tournament.completed_at.strftime('%Y-%m-%d %H:%M')}\n"
        
        info += "\n" + "="*50 + "\n\n"
        
        # Standings
        info += "FINAL STANDINGS:\n\n"
        standings = tournament.get_standings()
        
        for standing in standings:
            info += f"{standing['position']:2d}. {standing['player']:20s} "
            info += f"({standing['wins']}-{standing['losses']}, "
            info += f"Rating: {standing['rating']}, "
            info += f"Win Rate: {standing['win_rate']:.1%})\n"
        
        info += "\n" + "="*50 + "\n\n"
        
        # Round results
        if tournament.rounds:
            info += "ROUND RESULTS:\n\n"
            
            for tournament_round in tournament.rounds:
                info += f"{tournament_round.name}:\n"
                
                for match in tournament_round.matches:
                    if match.is_bye():
                        info += f"  {match.player1.name} - BYE\n"
                    else:
                        player1 = match.player1.name
                        player2 = match.player2.name if match.player2 else "BYE"
                        
                        if match.winner:
                            winner_marker1 = " ✓" if match.winner == match.player1 else ""
                            winner_marker2 = " ✓" if match.winner == match.player2 else ""
                            info += f"  {player1}{winner_marker1} vs {player2}{winner_marker2}"
                            info += f" ({match.score})\n"
                        else:
                            info += f"  {player1} vs {player2} - Not played\n"
                
                info += "\n"
        
        self.results_info_text.insert(1.0, info)
    
    def export_results_json(self):
        """Export tournament results as JSON."""
        selection = self.results_tournament_var.get()
        if not selection:
            messagebox.showerror("Error", "Please select a tournament")
            return
        
        # Find tournament
        tournament = None
        for t in self.tournament_manager.tournaments.values():
            if selection.startswith(t.name):
                tournament = t
                break
        
        if not tournament:
            return
        
        try:
            results = tournament.export_results()
            
            # Save to file
            filename = f"tournament_results_{tournament.id}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            messagebox.showinfo("Success", f"Results exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def export_bracket(self):
        """Export tournament bracket visualization."""
        messagebox.showinfo("Info", "Bracket export feature coming soon!")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tournament System Test")
    root.geometry("1200x800")
    
    # Create a mock theme manager
    class MockThemeManager:
        def apply_to_widget(self, widget):
            pass
    
    theme_manager = MockThemeManager()
    tournament_frame = TournamentSystemFrame(root, theme_manager)
    tournament_frame.pack(fill='both', expand=True)
    
    root.mainloop()