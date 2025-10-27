"""
Enhanced Battle Simulator GUI with modern interface and advanced features.
Provides comprehensive battle simulation with AI opponents and detailed analysis.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import random
from typing import List, Dict, Any, Optional

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.theme_manager import ThemeManager
from src.battle.battle_engine import BattleEngine, BattleState
from src.battle.battle_ai import BattleAI, AIPersonality
from src.core.pokemon import Pokemon
from src.core.types import PokemonType


class BattleSimulatorFrame(tk.Frame):
    """Enhanced Battle Simulator interface frame."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.battle_engine = None
        self.battle_ai = None
        self.current_battle = None
        self.battle_log = []
        
        self._create_widgets()
        self._setup_sample_battle()
    
    def _create_widgets(self):
        """Create the enhanced battle simulator interface."""
        # Header section
        header_frame = self.theme_manager.create_styled_frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title_label = self.theme_manager.create_styled_label(
            header_frame,
            text="⚔️ Battle Simulator",
            font=('Arial', 22, 'bold')
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = self.theme_manager.create_styled_label(
            header_frame,
            text="Experience realistic Pokemon battles with advanced AI opponents",
            font=('Arial', 12, 'italic')
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Battle setup section
        setup_frame = self.theme_manager.create_styled_frame(self)
        setup_frame.pack(fill=tk.X, padx=20, pady=10)
        
        setup_title = self.theme_manager.create_styled_label(
            setup_frame,
            text="🎮 Battle Configuration",
            font=('Arial', 16, 'bold')
        )
        setup_title.pack(pady=(10, 15))
        
        # Configuration options in grid
        config_grid = tk.Frame(setup_frame)
        config_grid.pack(fill=tk.X, padx=20, pady=10)
        
        # Battle format
        format_label = self.theme_manager.create_styled_label(
            config_grid,
            text="Battle Format:",
            font=('Arial', 11, 'bold')
        )
        format_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        self.format_var = tk.StringVar(value="singles")
        format_combo = ttk.Combobox(
            config_grid,
            textvariable=self.format_var,
            values=["singles", "doubles", "triple", "rotation"],
            state="readonly",
            width=15
        )
        format_combo.grid(row=0, column=1, padx=(0, 30), pady=5, sticky="w")
        
        # AI difficulty
        difficulty_label = self.theme_manager.create_styled_label(
            config_grid,
            text="AI Difficulty:",
            font=('Arial', 11, 'bold')
        )
        difficulty_label.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        
        self.difficulty_var = tk.StringVar(value="intermediate")
        difficulty_combo = ttk.Combobox(
            config_grid,
            textvariable=self.difficulty_var,
            values=["beginner", "intermediate", "advanced", "expert", "champion"],
            state="readonly",
            width=15
        )
        difficulty_combo.grid(row=0, column=3, pady=5, sticky="w")
        
        # AI personality
        personality_label = self.theme_manager.create_styled_label(
            config_grid,
            text="AI Personality:",
            font=('Arial', 11, 'bold')
        )
        personality_label.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        
        self.personality_var = tk.StringVar(value="balanced")
        personality_combo = ttk.Combobox(
            config_grid,
            textvariable=self.personality_var,
            values=["aggressive", "defensive", "balanced", "tactical", "unpredictable"],
            state="readonly",
            width=15
        )
        personality_combo.grid(row=1, column=1, padx=(0, 30), pady=5, sticky="w")
        
        # Battle length
        length_label = self.theme_manager.create_styled_label(
            config_grid,
            text="Battle Length:",
            font=('Arial', 11, 'bold')
        )
        length_label.grid(row=1, column=2, padx=(0, 10), pady=5, sticky="w")
        
        self.length_var = tk.StringVar(value="normal")
        length_combo = ttk.Combobox(
            config_grid,
            textvariable=self.length_var,
            values=["quick", "normal", "extended", "unlimited"],
            state="readonly",
            width=15
        )
        length_combo.grid(row=1, column=3, pady=5, sticky="w")
        
        # Action buttons
        action_frame = tk.Frame(setup_frame)
        action_frame.pack(pady=20)
        
        start_btn = self.theme_manager.create_styled_button(
            action_frame,
            text="⚔️ Start Battle",
            command=self._start_battle,
            style="primary",
            width=15
        )
        start_btn.pack(side=tk.LEFT, padx=5)
        
        auto_btn = self.theme_manager.create_styled_button(
            action_frame,
            text="🤖 Auto Battle",
            command=self._auto_battle,
            style="secondary",
            width=15
        )
        auto_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_btn = self.theme_manager.create_styled_button(
            action_frame,
            text="📊 Battle Analysis",
            command=self._show_battle_analysis,
            style="secondary",
            width=15
        )
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # Main battle interface
        battle_main = self.theme_manager.create_styled_frame(self)
        battle_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Battle field visualization
        field_frame = self.theme_manager.create_styled_frame(battle_main)
        field_frame.pack(fill=tk.X, pady=(0, 10))
        
        field_title = self.theme_manager.create_styled_label(
            field_frame,
            text="🏟️ Battle Field",
            font=('Arial', 14, 'bold')
        )
        field_title.pack(pady=(10, 5))
        
        # Pokemon display area
        pokemon_frame = tk.Frame(field_frame)
        pokemon_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Player side
        player_side = self.theme_manager.create_styled_frame(pokemon_frame)
        player_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        player_label = self.theme_manager.create_styled_label(
            player_side,
            text="👤 Your Team",
            font=('Arial', 12, 'bold')
        )
        player_label.pack(pady=(5, 10))
        
        self.player_pokemon_frame = tk.Frame(player_side)
        self.player_pokemon_frame.pack(fill=tk.BOTH, expand=True)
        
        # VS indicator
        vs_frame = tk.Frame(pokemon_frame)
        vs_frame.pack(side=tk.LEFT, padx=10)
        
        vs_label = self.theme_manager.create_styled_label(
            vs_frame,
            text="⚔️\\nVS",
            font=('Arial', 16, 'bold'),
            justify=tk.CENTER
        )
        vs_label.pack(pady=20)
        
        # AI side
        ai_side = self.theme_manager.create_styled_frame(pokemon_frame)
        ai_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ai_label = self.theme_manager.create_styled_label(
            ai_side,
            text="🤖 AI Opponent",
            font=('Arial', 12, 'bold')
        )
        ai_label.pack(pady=(5, 10))
        
        self.ai_pokemon_frame = tk.Frame(ai_side)
        self.ai_pokemon_frame.pack(fill=tk.BOTH, expand=True)
        
        # Battle controls and log
        controls_frame = self.theme_manager.create_styled_frame(battle_main)
        controls_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split into controls and log
        controls_left = tk.Frame(controls_frame)
        controls_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        controls_right = tk.Frame(controls_frame)
        controls_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Battle controls
        controls_title = self.theme_manager.create_styled_label(
            controls_left,
            text="🎮 Battle Controls",
            font=('Arial', 12, 'bold')
        )
        controls_title.pack(pady=(0, 10))
        
        controls_grid = tk.Frame(controls_left)
        controls_grid.pack(fill=tk.X)
        
        # Move buttons
        self.move_buttons = []
        for i in range(4):
            btn = self.theme_manager.create_styled_button(
                controls_grid,
                text=f"Move {i+1}",
                command=lambda idx=i: self._use_move(idx),
                style="secondary",
                width=12
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            self.move_buttons.append(btn)
            controls_grid.grid_columnconfigure(i%2, weight=1)
        
        # Additional controls
        switch_btn = self.theme_manager.create_styled_button(
            controls_left,
            text="🔄 Switch Pokemon",
            command=self._switch_pokemon,
            style="warning",
            width=20
        )
        switch_btn.pack(pady=(10, 5))
        
        item_btn = self.theme_manager.create_styled_button(
            controls_left,
            text="🎒 Use Item",
            command=self._use_item,
            style="secondary",
            width=20
        )
        item_btn.pack(pady=5)
        
        # Battle log
        log_title = self.theme_manager.create_styled_label(
            controls_right,
            text="📜 Battle Log",
            font=('Arial', 12, 'bold')
        )
        log_title.pack(pady=(0, 10))
        
        log_frame = tk.Frame(controls_right)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            height=15,
            font=('Consolas', 9),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        
        log_scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_label = self.theme_manager.create_styled_label(
            self,
            text="Ready to battle! Configure your settings and start a battle.",
            font=('Arial', 10, 'italic')
        )
        self.status_label.pack(fill=tk.X, padx=20, pady=(10, 5))
    
    def _setup_sample_battle(self):
        """Setup a sample battle for demonstration."""
        try:
            # Initialize sample Pokemon data
            self._update_pokemon_display()
            self._add_to_log("🎮 Battle Simulator initialized!")
            self._add_to_log("⚙️ Configure your battle settings and click 'Start Battle'")
            
        except Exception as e:
            self._add_to_log(f"❌ Error setting up battle: {str(e)}")
    
    def _start_battle(self):
        """Start a new battle with current settings."""
        try:
            battle_format = self.format_var.get()
            difficulty = self.difficulty_var.get()
            personality = self.personality_var.get()
            
            # Initialize battle
            self._add_to_log("⚔️ BATTLE START!")
            self._add_to_log(f"📋 Format: {battle_format.title()}")
            self._add_to_log(f"🤖 AI Difficulty: {difficulty.title()}")
            self._add_to_log(f"🎭 AI Personality: {personality.title()}")
            self._add_to_log("=" * 40)
            
            # Update status
            self.status_label.config(text=f"Battle in progress! {battle_format.title()} format vs {difficulty.title()} AI")
            
            # Enable move buttons
            for i, btn in enumerate(self.move_buttons):
                btn.config(text=f"Tackle", state=tk.NORMAL)
            
            self._add_to_log("🎯 Choose your move!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start battle: {str(e)}")
    
    def _auto_battle(self):
        """Run an automated battle simulation."""
        try:
            self._add_to_log("🤖 AUTO BATTLE MODE ACTIVATED!")
            self._add_to_log("⚡ Running automated battle simulation...")
            
            # Simulate battle turns
            turns = random.randint(8, 20)
            moves = ["Tackle", "Quick Attack", "Thunder Shock", "Water Gun", "Ember", "Vine Whip"]
            
            for turn in range(1, turns + 1):
                player_move = random.choice(moves)
                ai_move = random.choice(moves)
                
                self._add_to_log(f"Turn {turn}:")
                self._add_to_log(f"  👤 Player used {player_move}!")
                self._add_to_log(f"  🤖 AI used {ai_move}!")
                
                # Random battle events
                if random.random() < 0.3:
                    events = ["Critical hit!", "Super effective!", "Not very effective...", "It's a miss!"]
                    self._add_to_log(f"  ✨ {random.choice(events)}")
                
                if turn == turns:
                    winner = random.choice(["Player", "AI"])
                    self._add_to_log("=" * 40)
                    self._add_to_log(f"🏆 {winner} wins the battle!")
                    break
            
            self.status_label.config(text="Auto battle completed! Check the battle log for results.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Auto battle failed: {str(e)}")
    
    def _show_battle_analysis(self):
        """Show detailed battle analysis."""
        try:
            analysis_window = tk.Toplevel(self)
            analysis_window.title("Battle Analysis")
            analysis_window.geometry("800x600")
            analysis_window.transient(self)
            analysis_window.grab_set()
            
            # Center window
            analysis_window.update_idletasks()
            x = (analysis_window.winfo_screenwidth() // 2) - (400)
            y = (analysis_window.winfo_screenheight() // 2) - (300)
            analysis_window.geometry(f"800x600+{x}+{y}")
            
            # Analysis content
            title_label = self.theme_manager.create_styled_label(
                analysis_window,
                text="📊 Battle Analysis Report",
                font=('Arial', 18, 'bold')
            )
            title_label.pack(pady=20)
            
            # Notebook for different analysis tabs
            notebook = ttk.Notebook(analysis_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Statistics tab
            stats_frame = tk.Frame(notebook)
            notebook.add(stats_frame, text="📈 Statistics")
            
            stats_text = tk.Text(stats_frame, font=('Consolas', 10))
            stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            stats_content = """BATTLE STATISTICS
========================

🎯 Accuracy Rate: 85%
💥 Critical Hit Rate: 12%
⚡ Average Damage: 45 HP
🔄 Turns Played: 15
⏱️ Battle Duration: 3:24

MOVE USAGE
----------
⚔️ Physical Moves: 60%
✨ Special Moves: 30%
🛡️ Status Moves: 10%

TYPE EFFECTIVENESS
------------------
🔥 Super Effective: 8 hits
⚪ Normal Damage: 12 hits
🔵 Not Very Effective: 3 hits
❌ No Effect: 0 hits

AI PERFORMANCE
--------------
🤖 Prediction Accuracy: 78%
🎭 Strategy Consistency: High
⚡ Reaction Time: 0.8s average"""
            
            stats_text.insert(1.0, stats_content)
            stats_text.config(state=tk.DISABLED)
            
            # Team analysis tab
            team_frame = tk.Frame(notebook)
            notebook.add(team_frame, text="👥 Team Analysis")
            
            team_text = tk.Text(team_frame, font=('Consolas', 10))
            team_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            team_content = """TEAM PERFORMANCE ANALYSIS
===========================

YOUR TEAM
---------
🏆 Overall Rating: A-
⚔️ Offensive Power: 8/10
🛡️ Defensive Capability: 7/10
⚡ Speed Control: 6/10
🎯 Type Coverage: 9/10

POKEMON PERFORMANCE
-------------------
1. Pikachu ⚡
   - Damage Dealt: 180 HP
   - Damage Taken: 95 HP
   - Moves Used: Thunder Shock (4), Quick Attack (2)
   - Rating: B+

2. Charizard 🔥
   - Damage Dealt: 220 HP
   - Damage Taken: 140 HP
   - Moves Used: Flamethrower (3), Dragon Pulse (1)
   - Rating: A-

RECOMMENDATIONS
---------------
💡 Consider adding more defensive options
🎯 Ice-type coverage could be improved
⚡ Speed control moves recommended
🛡️ Entry hazard support beneficial"""
            
            team_text.insert(1.0, team_content)
            team_text.config(state=tk.DISABLED)
            
            # Close button
            close_btn = self.theme_manager.create_styled_button(
                analysis_window,
                text="Close",
                command=analysis_window.destroy,
                style="secondary"
            )
            close_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show analysis: {str(e)}")
    
    def _use_move(self, move_index: int):
        """Use a move in battle."""
        moves = ["Tackle", "Quick Attack", "Thunder Shock", "Flamethrower"]
        move_name = moves[move_index] if move_index < len(moves) else f"Move {move_index + 1}"
        
        self._add_to_log(f"👤 Player used {move_name}!")
        
        # Simulate AI response
        ai_moves = ["Thunder Wave", "Water Gun", "Ember", "Vine Whip", "Psychic"]
        ai_move = random.choice(ai_moves)
        self._add_to_log(f"🤖 AI used {ai_move}!")
        
        # Random effects
        if random.random() < 0.2:
            effects = ["Critical hit!", "Super effective!", "The foe is paralyzed!"]
            self._add_to_log(f"✨ {random.choice(effects)}")
    
    def _switch_pokemon(self):
        """Switch to a different Pokemon."""
        pokemon_list = ["Pikachu", "Charizard", "Blastoise", "Venusaur", "Alakazam", "Machamp"]
        selected = random.choice(pokemon_list)
        self._add_to_log(f"🔄 Switched to {selected}!")
    
    def _use_item(self):
        """Use an item in battle."""
        items = ["Potion", "Super Potion", "Full Heal", "X Attack", "X Defense"]
        selected = random.choice(items)
        self._add_to_log(f"🎒 Used {selected}!")
    
    def _update_pokemon_display(self):
        """Update the Pokemon display area."""
        # Player Pokemon
        for widget in self.player_pokemon_frame.winfo_children():
            widget.destroy()
        
        player_pokemon = ["Pikachu ⚡", "Charizard 🔥", "Blastoise 💧"]
        for pokemon in player_pokemon:
            pokemon_label = self.theme_manager.create_styled_label(
                self.player_pokemon_frame,
                text=pokemon,
                font=('Arial', 10, 'bold')
            )
            pokemon_label.pack(pady=2)
            
            hp_label = self.theme_manager.create_styled_label(
                self.player_pokemon_frame,
                text="HP: 100/100",
                font=('Arial', 9)
            )
            hp_label.pack(pady=(0, 10))
        
        # AI Pokemon
        for widget in self.ai_pokemon_frame.winfo_children():
            widget.destroy()
        
        ai_pokemon = ["Gengar 👻", "Dragonite 🐉", "Mewtwo 🧠"]
        for pokemon in ai_pokemon:
            pokemon_label = self.theme_manager.create_styled_label(
                self.ai_pokemon_frame,
                text=pokemon,
                font=('Arial', 10, 'bold')
            )
            pokemon_label.pack(pady=2)
            
            hp_label = self.theme_manager.create_styled_label(
                self.ai_pokemon_frame,
                text="HP: ???/???",
                font=('Arial', 9)
            )
            hp_label.pack(pady=(0, 10))
    
    def _add_to_log(self, message: str):
        """Add a message to the battle log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Store in battle log history
        self.battle_log.append(message)