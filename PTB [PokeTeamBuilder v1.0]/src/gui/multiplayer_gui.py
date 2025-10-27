"""
GUI components for Online Multiplayer Battle System.
Provides user interface for matchmaking, battle management, and spectating.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from teambuilder.team import PokemonTeam
try:
    from .online_multiplayer import (
        OnlineBattleManager, BattlePlayer, BattleMode, BattleFormat,
        PlayerStatus, BattlePhase, BattleMessage
    )
except ImportError:
    # Mock classes if online_multiplayer is not available
    class OnlineBattleManager:
        def __init__(self):
            pass
    class BattlePlayer:
        def __init__(self, name):
            self.name = name
    class BattleMode:
        SINGLES = "singles"
    class BattleFormat:
        CASUAL = "casual"
    class PlayerStatus:
        ONLINE = "online"
    class BattlePhase:
        LOBBY = "lobby"
    class BattleMessage:
        def __init__(self, message):
            self.message = message

class MultiplayerLobbyGUI:
    """Main lobby interface for online multiplayer."""
    
    def __init__(self, parent, battle_manager: OnlineBattleManager):
        self.parent = parent
        self.battle_manager = battle_manager
        self.current_user = None
        self.current_battle_id = None
        
        # Create lobby window
        self.window = tk.Toplevel(parent)
        self.window.title("Online Multiplayer Lobby")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        self.setup_ui()
        self.update_thread_running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        """Setup the lobby user interface."""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Quick Match tab
        self.quick_match_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quick_match_frame, text="Quick Match")
        self.setup_quick_match_tab()
        
        # Private Battle tab
        self.private_battle_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.private_battle_frame, text="Private Battle")
        self.setup_private_battle_tab()
        
        # Battle List tab
        self.battle_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.battle_list_frame, text="Active Battles")
        self.setup_battle_list_tab()
        
        # Profile tab
        self.profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_frame, text="Profile")
        self.setup_profile_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.window, textvariable=self.status_var, relief='sunken')
        self.status_bar.pack(side='bottom', fill='x')
    
    def setup_quick_match_tab(self):
        """Setup quick match interface."""
        # User login section
        login_frame = ttk.LabelFrame(self.quick_match_frame, text="Login", padding=10)
        login_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky='w')
        self.username_var = tk.StringVar(value="Player1")
        self.username_entry = ttk.Entry(login_frame, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        self.login_btn.grid(row=0, column=2, padx=5)
        
        login_frame.columnconfigure(1, weight=1)
        
        # Team selection
        team_frame = ttk.LabelFrame(self.quick_match_frame, text="Team Selection", padding=10)
        team_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(team_frame, text="Team:").grid(row=0, column=0, sticky='w')
        self.team_var = tk.StringVar()
        self.team_combo = ttk.Combobox(team_frame, textvariable=self.team_var, state='readonly')
        self.team_combo.grid(row=0, column=1, padx=5, sticky='ew')
        self.load_teams()
        
        team_frame.columnconfigure(1, weight=1)
        
        # Battle settings
        settings_frame = ttk.LabelFrame(self.quick_match_frame, text="Battle Settings", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(settings_frame, text="Mode:").grid(row=0, column=0, sticky='w')
        self.mode_var = tk.StringVar(value=BattleMode.SINGLES.value)
        self.mode_combo = ttk.Combobox(settings_frame, textvariable=self.mode_var, 
                                      values=[mode.value for mode in BattleMode], state='readonly')
        self.mode_combo.grid(row=0, column=1, padx=5, sticky='ew')
        
        ttk.Label(settings_frame, text="Format:").grid(row=1, column=0, sticky='w')
        self.format_var = tk.StringVar(value=BattleFormat.CASUAL.value)
        self.format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var,
                                        values=[fmt.value for fmt in BattleFormat], state='readonly')
        self.format_combo.grid(row=1, column=1, padx=5, sticky='ew')
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Queue controls
        queue_frame = ttk.Frame(self.quick_match_frame)
        queue_frame.pack(fill='x', padx=10, pady=10)
        
        self.queue_btn = ttk.Button(queue_frame, text="Find Match", command=self.queue_for_match)
        self.queue_btn.pack(side='left', padx=5)
        
        self.cancel_queue_btn = ttk.Button(queue_frame, text="Cancel Queue", 
                                          command=self.cancel_queue, state='disabled')
        self.cancel_queue_btn.pack(side='left', padx=5)
        
        # Queue status
        self.queue_status_var = tk.StringVar(value="Not in queue")
        self.queue_status_label = ttk.Label(queue_frame, textvariable=self.queue_status_var)
        self.queue_status_label.pack(side='right', padx=5)
    
    def setup_private_battle_tab(self):
        """Setup private battle interface."""
        # Create private battle
        create_frame = ttk.LabelFrame(self.private_battle_frame, text="Create Private Battle", padding=10)
        create_frame.pack(fill='x', padx=10, pady=5)
        
        # Battle settings
        ttk.Label(create_frame, text="Mode:").grid(row=0, column=0, sticky='w')
        self.private_mode_var = tk.StringVar(value=BattleMode.SINGLES.value)
        self.private_mode_combo = ttk.Combobox(create_frame, textvariable=self.private_mode_var,
                                              values=[mode.value for mode in BattleMode], state='readonly')
        self.private_mode_combo.grid(row=0, column=1, padx=5, sticky='ew')
        
        ttk.Label(create_frame, text="Format:").grid(row=1, column=0, sticky='w')
        self.private_format_var = tk.StringVar(value=BattleFormat.CUSTOM.value)
        self.private_format_combo = ttk.Combobox(create_frame, textvariable=self.private_format_var,
                                                values=[fmt.value for fmt in BattleFormat], state='readonly')
        self.private_format_combo.grid(row=1, column=1, padx=5, sticky='ew')
        
        # Advanced settings
        self.timer_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(create_frame, text="Enable Timer", 
                       variable=self.timer_enabled_var).grid(row=2, column=0, columnspan=2, sticky='w')
        
        self.allow_spectators_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(create_frame, text="Allow Spectators",
                       variable=self.allow_spectators_var).grid(row=3, column=0, columnspan=2, sticky='w')
        
        ttk.Label(create_frame, text="Move Time Limit (sec):").grid(row=4, column=0, sticky='w')
        self.move_time_var = tk.StringVar(value="60")
        self.move_time_entry = ttk.Entry(create_frame, textvariable=self.move_time_var, width=10)
        self.move_time_entry.grid(row=4, column=1, padx=5, sticky='w')
        
        self.create_private_btn = ttk.Button(create_frame, text="Create Battle",
                                           command=self.create_private_battle)
        self.create_private_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        create_frame.columnconfigure(1, weight=1)
        
        # Join private battle
        join_frame = ttk.LabelFrame(self.private_battle_frame, text="Join Private Battle", padding=10)
        join_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(join_frame, text="Battle ID:").grid(row=0, column=0, sticky='w')
        self.battle_id_var = tk.StringVar()
        self.battle_id_entry = ttk.Entry(join_frame, textvariable=self.battle_id_var)
        self.battle_id_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.join_private_btn = ttk.Button(join_frame, text="Join Battle",
                                         command=self.join_private_battle)
        self.join_private_btn.grid(row=0, column=2, padx=5)
        
        join_frame.columnconfigure(1, weight=1)
    
    def setup_battle_list_tab(self):
        """Setup battle list interface."""
        # Battle list
        list_frame = ttk.LabelFrame(self.battle_list_frame, text="Active Battles", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for battles
        columns = ('ID', 'Mode', 'Format', 'Players', 'Phase', 'Created')
        self.battle_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.battle_tree.heading(col, text=col)
            self.battle_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.battle_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.battle_tree.xview)
        self.battle_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.battle_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Battle controls
        controls_frame = ttk.Frame(list_frame)
        controls_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew')
        
        self.spectate_btn = ttk.Button(controls_frame, text="Spectate", command=self.spectate_battle)
        self.spectate_btn.pack(side='left', padx=5)
        
        self.refresh_btn = ttk.Button(controls_frame, text="Refresh", command=self.refresh_battle_list)
        self.refresh_btn.pack(side='left', padx=5)
    
    def setup_profile_tab(self):
        """Setup profile interface."""
        profile_frame = ttk.LabelFrame(self.profile_frame, text="Player Profile", padding=10)
        profile_frame.pack(fill='x', padx=10, pady=5)
        
        # Profile info
        self.profile_info = tk.Text(profile_frame, height=10, width=50)
        self.profile_info.pack(fill='both', expand=True)
        
        # Update profile display
        self.update_profile_display()
    
    def load_teams(self):
        """Load available teams for selection."""
        # In a real implementation, this would load from saved teams
        teams = ["Sample Team 1", "Sample Team 2", "Random Team"]
        self.team_combo['values'] = teams
        if teams:
            self.team_combo.set(teams[0])
    
    def login(self):
        """Handle user login."""
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        # Create player
        self.current_user = BattlePlayer(
            id=f"player_{int(time.time())}",
            username=username,
            rating=1200,  # Default rating
            team=None  # Would load selected team
        )
        
        # Register with battle manager
        self.battle_manager.register_connection(self.current_user.id, "gui_connection")
        
        # Update UI
        self.username_entry.config(state='disabled')
        self.login_btn.config(state='disabled')
        self.queue_btn.config(state='normal')
        
        self.status_var.set(f"Logged in as {username}")
        messagebox.showinfo("Success", f"Logged in as {username}")
    
    def queue_for_match(self):
        """Queue for a match."""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        if not self.team_var.get():
            messagebox.showerror("Error", "Please select a team")
            return
        
        # Get battle settings
        mode = BattleMode(self.mode_var.get())
        format = BattleFormat(self.format_var.get())
        
        # Queue for battle
        if self.battle_manager.queue_for_battle(self.current_user, mode, format):
            self.queue_btn.config(state='disabled')
            self.cancel_queue_btn.config(state='normal')
            self.queue_status_var.set("In queue - searching for opponent...")
            self.status_var.set("Searching for match...")
        else:
            messagebox.showerror("Error", "Failed to join queue")
    
    def cancel_queue(self):
        """Cancel matchmaking queue."""
        if not self.current_user:
            return
        
        if self.battle_manager.cancel_queue(self.current_user.id):
            self.queue_btn.config(state='normal')
            self.cancel_queue_btn.config(state='disabled')
            self.queue_status_var.set("Not in queue")
            self.status_var.set("Ready")
    
    def create_private_battle(self):
        """Create a private battle."""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        if not self.team_var.get():
            messagebox.showerror("Error", "Please select a team")
            return
        
        # Get settings
        mode = BattleMode(self.private_mode_var.get())
        format = BattleFormat(self.private_format_var.get())
        
        settings = {
            'timer_enabled': self.timer_enabled_var.get(),
            'move_time_limit': int(self.move_time_var.get()),
            'allow_spectators': self.allow_spectators_var.get(),
            'private_battle': True
        }
        
        # Create battle
        battle_id = self.battle_manager.create_private_battle(
            self.current_user, mode, format, settings
        )
        
        self.current_battle_id = battle_id
        messagebox.showinfo("Battle Created", f"Battle ID: {battle_id}")
        self.status_var.set(f"Hosting private battle: {battle_id}")
        
        # Open battle window
        self.open_battle_window(battle_id)
    
    def join_private_battle(self):
        """Join a private battle."""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        battle_id = self.battle_id_var.get().strip()
        if not battle_id:
            messagebox.showerror("Error", "Please enter a battle ID")
            return
        
        # Join battle
        if self.battle_manager.join_battle(battle_id, self.current_user):
            self.current_battle_id = battle_id
            messagebox.showinfo("Success", f"Joined battle {battle_id}")
            self.status_var.set(f"Joined battle: {battle_id}")
            
            # Open battle window
            self.open_battle_window(battle_id)
        else:
            messagebox.showerror("Error", "Failed to join battle")
    
    def spectate_battle(self):
        """Spectate selected battle."""
        selection = self.battle_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a battle to spectate")
            return
        
        item = self.battle_tree.item(selection[0])
        battle_id = item['values'][0]
        
        # Open battle window in spectator mode
        self.open_battle_window(battle_id, spectator=True)
    
    def refresh_battle_list(self):
        """Refresh the battle list."""
        # Clear current items
        for item in self.battle_tree.get_children():
            self.battle_tree.delete(item)
        
        # Get battle list
        battles = self.battle_manager.get_battle_list()
        
        # Add battles to tree
        for battle in battles:
            created_time = datetime.fromisoformat(battle['created_at']).strftime("%H:%M:%S")
            self.battle_tree.insert('', 'end', values=(
                battle['battle_id'][:8],  # Shortened ID
                battle['mode'].title(),
                battle['format'].title(),
                f"{battle['players']}/2",
                battle['phase'].replace('_', ' ').title(),
                created_time
            ))
    
    def open_battle_window(self, battle_id: str, spectator: bool = False):
        """Open battle window."""
        BattleGUI(self.window, self.battle_manager, battle_id, 
                 self.current_user, spectator)
    
    def update_profile_display(self):
        """Update profile display."""
        if self.current_user:
            profile_text = f"""Username: {self.current_user.username}
Player ID: {self.current_user.id}
Rating: {self.current_user.rating}
Status: {self.current_user.status.value}

Battle Statistics:
- Battles Played: 0
- Wins: 0
- Losses: 0
- Win Rate: 0%

Current Activity:
- In Battle: {"Yes" if self.current_battle_id else "No"}
- Battle ID: {self.current_battle_id or "None"}
"""
        else:
            profile_text = "Not logged in"
        
        self.profile_info.delete(1.0, tk.END)
        self.profile_info.insert(1.0, profile_text)
    
    def update_loop(self):
        """Background update loop."""
        while self.update_thread_running:
            try:
                # Update battle list
                if self.notebook.index('current') == 2:  # Battle list tab
                    self.refresh_battle_list()
                
                # Update profile
                if self.notebook.index('current') == 3:  # Profile tab
                    self.update_profile_display()
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Update loop error: {e}")
                time.sleep(5)
    
    def on_close(self):
        """Handle window close."""
        self.update_thread_running = False
        
        # Disconnect user
        if self.current_user:
            self.battle_manager.handle_disconnect("gui_connection")
        
        self.window.destroy()

class BattleGUI:
    """GUI for participating in or spectating battles."""
    
    def __init__(self, parent, battle_manager: OnlineBattleManager, 
                 battle_id: str, player: Optional[BattlePlayer], spectator: bool = False):
        self.parent = parent
        self.battle_manager = battle_manager
        self.battle_id = battle_id
        self.player = player
        self.spectator = spectator
        
        # Create battle window
        self.window = tk.Toplevel(parent)
        title = f"Battle {battle_id[:8]}" + (" (Spectator)" if spectator else "")
        self.window.title(title)
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        self.setup_ui()
        
        # Update thread
        self.update_thread_running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        """Setup battle user interface."""
        # Main paned window
        self.paned = ttk.PanedWindow(self.window, orient='horizontal')
        self.paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Battle field
        self.left_frame = ttk.Frame(self.paned)
        self.paned.add(self.left_frame, weight=3)
        
        # Battle status
        status_frame = ttk.LabelFrame(self.left_frame, text="Battle Status", padding=5)
        status_frame.pack(fill='x', padx=5, pady=5)
        
        self.phase_var = tk.StringVar(value="Loading...")
        ttk.Label(status_frame, text="Phase:").grid(row=0, column=0, sticky='w')
        ttk.Label(status_frame, textvariable=self.phase_var).grid(row=0, column=1, sticky='w')
        
        self.turn_var = tk.StringVar(value="0")
        ttk.Label(status_frame, text="Turn:").grid(row=0, column=2, sticky='w', padx=(20,0))
        ttk.Label(status_frame, textvariable=self.turn_var).grid(row=0, column=3, sticky='w')
        
        self.timer_var = tk.StringVar(value="--")
        ttk.Label(status_frame, text="Timer:").grid(row=0, column=4, sticky='w', padx=(20,0))
        ttk.Label(status_frame, textvariable=self.timer_var).grid(row=0, column=5, sticky='w')
        
        # Battle field visualization
        field_frame = ttk.LabelFrame(self.left_frame, text="Battle Field", padding=5)
        field_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Simple text display for battle state
        self.battle_display = scrolledtext.ScrolledText(field_frame, height=20, state='disabled')
        self.battle_display.pack(fill='both', expand=True)
        
        # Move selection (if not spectator)
        if not self.spectator:
            moves_frame = ttk.LabelFrame(self.left_frame, text="Move Selection", padding=5)
            moves_frame.pack(fill='x', padx=5, pady=5)
            
            # Move buttons
            self.move_buttons = []
            for i in range(4):
                btn = ttk.Button(moves_frame, text=f"Move {i+1}", 
                               command=lambda i=i: self.select_move(i))
                btn.grid(row=0, column=i, padx=2, pady=2, sticky='ew')
                self.move_buttons.append(btn)
                moves_frame.columnconfigure(i, weight=1)
            
            # Submit moves button
            self.submit_btn = ttk.Button(moves_frame, text="Submit Moves", 
                                       command=self.submit_moves, state='disabled')
            self.submit_btn.grid(row=1, column=0, columnspan=4, pady=5, sticky='ew')
        
        # Right panel - Battle log and info
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=1)
        
        # Players info
        players_frame = ttk.LabelFrame(self.right_frame, text="Players", padding=5)
        players_frame.pack(fill='x', padx=5, pady=5)
        
        self.players_info = tk.Text(players_frame, height=6, state='disabled')
        self.players_info.pack(fill='both', expand=True)
        
        # Battle log
        log_frame = ttk.LabelFrame(self.right_frame, text="Battle Log", padding=5)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.battle_log = scrolledtext.ScrolledText(log_frame, height=15, state='disabled')
        self.battle_log.pack(fill='both', expand=True)
        
        # Chat (for spectators or after battle)
        chat_frame = ttk.LabelFrame(self.right_frame, text="Chat", padding=5)
        chat_frame.pack(fill='x', padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=6, state='disabled')
        self.chat_display.pack(fill='both', expand=True)
        
        self.chat_entry = ttk.Entry(chat_frame)
        self.chat_entry.pack(fill='x', pady=(5,0))
        self.chat_entry.bind('<Return>', self.send_chat)
        
        # Initialize display
        self.selected_move = None
        self.update_display()
    
    def select_move(self, move_index: int):
        """Select a move."""
        self.selected_move = move_index
        
        # Update button states
        for i, btn in enumerate(self.move_buttons):
            if i == move_index:
                btn.config(relief='sunken')
            else:
                btn.config(relief='raised')
        
        # Enable submit button
        self.submit_btn.config(state='normal')
    
    def submit_moves(self):
        """Submit selected moves."""
        if self.selected_move is None or not self.player:
            return
        
        # In a real implementation, this would get the actual move name
        moves = [f"Move_{self.selected_move}"]
        
        if self.battle_manager.submit_moves(self.battle_id, self.player.id, moves):
            self.submit_btn.config(state='disabled')
            for btn in self.move_buttons:
                btn.config(state='disabled')
            
            self.add_to_log("Moves submitted. Waiting for opponent...")
        else:
            messagebox.showerror("Error", "Failed to submit moves")
    
    def send_chat(self, event):
        """Send chat message."""
        message = self.chat_entry.get().strip()
        if message:
            # Add to chat display
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"You: {message}\n")
            self.chat_display.config(state='disabled')
            self.chat_display.see(tk.END)
            
            self.chat_entry.delete(0, tk.END)
    
    def add_to_log(self, message: str):
        """Add message to battle log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.battle_log.config(state='normal')
        self.battle_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.battle_log.config(state='disabled')
        self.battle_log.see(tk.END)
    
    def update_display(self):
        """Update the battle display."""
        # Get battle state
        battle_state = self.battle_manager.get_battle_state(self.battle_id)
        
        if battle_state:
            # Update status
            self.phase_var.set(battle_state['phase'].replace('_', ' ').title())
            self.turn_var.set(str(battle_state['turn_number']))
            
            # Update timer
            if battle_state['timer']['enabled']:
                remaining = int(battle_state['timer']['remaining'])
                self.timer_var.set(f"{remaining}s")
            else:
                self.timer_var.set("--")
            
            # Update players info
            self.players_info.config(state='normal')
            self.players_info.delete(1.0, tk.END)
            
            players_text = ""
            for player_id, player_info in battle_state['players'].items():
                status_emoji = "🟢" if player_info['ready'] else "🔴"
                players_text += f"{status_emoji} {player_info['username']}\n"
                players_text += f"   Status: {player_info['status'].title()}\n\n"
            
            self.players_info.insert(1.0, players_text)
            self.players_info.config(state='disabled')
            
            # Update battle field display
            self.battle_display.config(state='normal')
            self.battle_display.delete(1.0, tk.END)
            
            field_text = f"""Battle ID: {self.battle_id}
Phase: {battle_state['phase'].replace('_', ' ').title()}
Turn: {battle_state['turn_number']}

Players:
{chr(10).join(f"- {info['username']} ({info['status']})" for info in battle_state['players'].values())}

Status: {"Spectating" if self.spectator else "Participating"}
"""
            
            self.battle_display.insert(1.0, field_text)
            self.battle_display.config(state='disabled')
            
            # Update move buttons based on phase
            if not self.spectator and hasattr(self, 'move_buttons'):
                if battle_state['phase'] == 'move_selection':
                    for btn in self.move_buttons:
                        btn.config(state='normal')
                else:
                    for btn in self.move_buttons:
                        btn.config(state='disabled')
        else:
            self.add_to_log("Failed to get battle state")
    
    def update_loop(self):
        """Background update loop."""
        while self.update_thread_running:
            try:
                self.update_display()
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Battle update error: {e}")
                time.sleep(5)
    
    def on_close(self):
        """Handle window close."""
        self.update_thread_running = False
        self.window.destroy()

# Integration with main GUI
def add_multiplayer_menu(parent_menu, main_window):
    """Add multiplayer menu to main application."""
    multiplayer_menu = tk.Menu(parent_menu, tearoff=0)
    parent_menu.add_cascade(label="Multiplayer", menu=multiplayer_menu)
    
    def open_multiplayer_lobby():
        battle_manager = OnlineBattleManager()
        MultiplayerLobbyGUI(main_window, battle_manager)
    
    multiplayer_menu.add_command(label="Open Lobby", command=open_multiplayer_lobby)
    multiplayer_menu.add_separator()
    multiplayer_menu.add_command(label="Quick Match", command=lambda: messagebox.showinfo("Info", "Use lobby for quick match"))
    multiplayer_menu.add_command(label="Private Battle", command=lambda: messagebox.showinfo("Info", "Use lobby for private battle"))

if __name__ == "__main__":
    # Test the GUI
    root = tk.Tk()
    root.title("Pokemon Team Builder")
    root.geometry("400x300")
    
    # Create menu
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # Add multiplayer menu
    add_multiplayer_menu(menubar, root)
    
    root.mainloop()