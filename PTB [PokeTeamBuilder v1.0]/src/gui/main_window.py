"""
Main window for Pokemon Team Builder GUI.
Provides the primary interface and navigation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.theme_manager import ThemeManager, ThemeType
from src.gui.team_builder_gui import TeamBuilderFrame
from src.gui.battle_simulator_gui import BattleSimulatorFrame
from src.gui.team_analysis_gui import TeamAnalysisFrame
from src.gui.team_optimization_gui import TeamOptimizationFrame
from src.gui.breeding_calculator_gui import BreedingCalculatorFrame
from src.gui.tournament_system_gui import TournamentSystemFrame
from src.gui.save_file_import_gui import SaveFileImportFrame
from src.gui.social_community_gui import SocialCommunityFrame
from src.gui.admin_panel_gui import AdminPanelFrame


class MainWindow:
    """Main application window for Pokemon Team Builder."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.theme_manager = ThemeManager()
        self.current_frame = None
        
        self._setup_window()
        self._create_menu()
        self._create_main_content()
        self._apply_theme()
        
        # Bind theme change event
        self.root.bind('<<ThemeChanged>>', self._on_theme_changed)
    
    def _setup_window(self):
        """Setup the main window properties."""
        self.root.title("Pokemon Team Builder v1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def _create_menu(self):
        """Create the main menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Team", command=self._new_team)
        file_menu.add_command(label="Open Team", command=self._open_team)
        file_menu.add_command(label="Save Team", command=self._save_team)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_app)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        for theme_type in ThemeType:
            theme_menu.add_command(
                label=theme_type.value.title(),
                command=lambda t=theme_type: self._change_theme(t)
            )
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Team Analysis", command=self._show_team_analysis)
        tools_menu.add_command(label="Team Optimization", command=self._show_team_optimization)
        tools_menu.add_command(label="Battle Simulator", command=self._show_battle_simulator)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
    
    def _create_main_content(self):
        """Create the main content area."""
        # Header
        header_frame = self.theme_manager.create_styled_frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo/Title
        title_label = self.theme_manager.create_styled_label(
            header_frame,
            text="🎮 Pokemon Team Builder",
            font=('Arial', 20, 'bold')
        )
        title_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Theme selector
        theme_frame = tk.Frame(header_frame)
        theme_frame.grid(row=0, column=1, sticky="e", padx=10)
        
        theme_label = self.theme_manager.create_styled_label(theme_frame, text="Theme:")
        theme_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.theme_var = tk.StringVar(value=self.theme_manager.current_theme.value)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=self.theme_manager.get_available_themes(),
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind('<<ComboboxSelected>>', self._on_theme_combo_changed)
        
        # Main content area
        self.content_frame = self.theme_manager.create_styled_frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Navigation buttons
        nav_frame = self.theme_manager.create_styled_frame(self.content_frame)
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Team Builder button
        self.team_builder_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="🏗️ Team Builder",
            command=self._show_team_builder
        )
        self.team_builder_btn.pack(side=tk.LEFT, padx=5)
        
        # Battle Simulator button
        self.battle_sim_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="⚔️ Battle Simulator",
            command=self._show_battle_simulator
        )
        self.battle_sim_btn.pack(side=tk.LEFT, padx=5)
        
        # Team Analysis button
        self.analysis_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="📊 Team Analysis",
            command=self._show_team_analysis
        )
        self.analysis_btn.pack(side=tk.LEFT, padx=5)
        
        # Team Optimization button
        self.optimization_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="🔧 Team Optimization",
            command=self._show_team_optimization
        )
        self.optimization_btn.pack(side=tk.LEFT, padx=5)
        
        # Breeding Calculator button
        self.breeding_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="🥚 Breeding Calculator",
            command=self._show_breeding_calculator
        )
        self.breeding_btn.pack(side=tk.LEFT, padx=5)
        
        # Tournament System button
        self.tournament_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="🏆 Tournament System",
            command=self._show_tournament_system
        )
        self.tournament_btn.pack(side=tk.LEFT, padx=5)
        
        # Save File Import button
        self.import_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="💾 Save File Import",
            command=self._show_save_file_import
        )
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        # Social Community button
        self.social_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="🌟 Social Hub",
            command=self._show_social_hub
        )
        self.social_btn.pack(side=tk.LEFT, padx=5)
        
        # Admin Panel button
        self.admin_btn = self.theme_manager.create_styled_button(
            nav_frame,
            text="🔒 Admin Panel",
            command=self._show_admin_panel
        )
        self.admin_btn.pack(side=tk.LEFT, padx=5)
        
        # Welcome message with enhanced layout
        self.welcome_frame = self.theme_manager.create_styled_frame(self.content_frame)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Hero section
        hero_frame = self.theme_manager.create_styled_frame(self.welcome_frame)
        hero_frame.pack(fill=tk.X, pady=(0, 30))
        
        welcome_label = self.theme_manager.create_styled_label(
            hero_frame,
            text="🎮 Pokemon Team Builder",
            font=('Arial', 28, 'bold')
        )
        welcome_label.pack(pady=(20, 10))
        
        subtitle_label = self.theme_manager.create_styled_label(
            hero_frame,
            text="Build, analyze, and optimize your Pokemon teams for competitive play!",
            font=('Arial', 16)
        )
        subtitle_label.pack(pady=(0, 10))
        
        version_label = self.theme_manager.create_styled_label(
            hero_frame,
            text="Version 1.0 • Multi-Platform Support • Enhanced Features",
            font=('Arial', 12, 'italic')
        )
        version_label.pack(pady=(0, 20))
        
        # Feature highlights with modern card layout
        features_title = self.theme_manager.create_styled_label(
            self.welcome_frame,
            text="✨ Key Features",
            font=('Arial', 18, 'bold')
        )
        features_title.pack(pady=(0, 15))
        
        # Create a grid of feature cards
        cards_frame = self.theme_manager.create_styled_frame(self.welcome_frame)
        cards_frame.pack(fill=tk.X, padx=20, pady=10)
        
        features = [
            {"icon": "�️", "title": "Team Builder", "desc": "Comprehensive team building with all Pokemon generations"},
            {"icon": "⚔️", "title": "Battle Simulator", "desc": "Advanced battle simulation with AI opponents"},
            {"icon": "📊", "title": "Team Analysis", "desc": "In-depth analysis of type coverage and weaknesses"},
            {"icon": "🔧", "title": "Optimization", "desc": "AI-powered team optimization and suggestions"},
            {"icon": "🥚", "title": "Breeding Calculator", "desc": "Calculate breeding chains and inheritance"},
            {"icon": "�", "title": "Tournament System", "desc": "Create and manage Pokemon tournaments"}
        ]
        
        # Create feature cards in 2 columns
        for i, feature in enumerate(features):
            row = i // 2
            col = i % 2
            
            card_frame = self.theme_manager.create_styled_frame(cards_frame)
            card_frame.grid(row=row, column=col, padx=10, pady=8, sticky="ew")
            cards_frame.grid_columnconfigure(col, weight=1)
            
            # Icon
            icon_label = self.theme_manager.create_styled_label(
                card_frame,
                text=feature["icon"],
                font=('Arial', 20)
            )
            icon_label.pack(side=tk.LEFT, padx=(15, 10), pady=15)
            
            # Text content
            text_frame = tk.Frame(card_frame)
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
            
            title_label = self.theme_manager.create_styled_label(
                text_frame,
                text=feature["title"],
                font=('Arial', 14, 'bold')
            )
            title_label.pack(anchor=tk.W)
            
            desc_label = self.theme_manager.create_styled_label(
                text_frame,
                text=feature["desc"],
                font=('Arial', 11),
                wraplength=250
            )
            desc_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Quick start section
        quick_start_frame = self.theme_manager.create_styled_frame(self.welcome_frame)
        quick_start_frame.pack(fill=tk.X, pady=(30, 10))
        
        quick_title = self.theme_manager.create_styled_label(
            quick_start_frame,
            text="🚀 Quick Start",
            font=('Arial', 16, 'bold')
        )
        quick_title.pack(pady=(0, 10))
        
        # Quick action buttons
        quick_buttons_frame = tk.Frame(quick_start_frame)
        quick_buttons_frame.pack()
        
        self.quick_team_btn = self.theme_manager.create_styled_button(
            quick_buttons_frame,
            text="🏗️ Start Building",
            command=self._show_team_builder,
            width=15
        )
        self.quick_team_btn.pack(side=tk.LEFT, padx=5)
        
        self.quick_battle_btn = self.theme_manager.create_styled_button(
            quick_buttons_frame,
            text="⚔️ Quick Battle",
            command=self._show_battle_simulator,
            width=15
        )
        self.quick_battle_btn.pack(side=tk.LEFT, padx=5)
        
        self.quick_analyze_btn = self.theme_manager.create_styled_button(
            quick_buttons_frame,
            text="📊 Analyze Team",
            command=self._show_team_analysis,
            width=15
        )
        self.quick_analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_bar = self.theme_manager.create_styled_label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=2)
    
    def _show_team_builder(self):
        """Show the team builder interface."""
        self._clear_content()
        self.current_frame = TeamBuilderFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Team Builder loaded")
    
    def _show_battle_simulator(self):
        """Show the battle simulator interface."""
        self._clear_content()
        self.current_frame = BattleSimulatorFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Battle Simulator loaded")
    
    def _show_team_analysis(self):
        """Show the team analysis interface."""
        self._clear_content()
        self.current_frame = TeamAnalysisFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Team Analysis loaded")
    
    def _show_team_optimization(self):
        """Show the team optimization interface."""
        self._clear_content()
        self.current_frame = TeamOptimizationFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Team Optimization loaded")
    
    def _show_breeding_calculator(self):
        """Show the breeding calculator interface."""
        self._clear_content()
        self.current_frame = BreedingCalculatorFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Breeding Calculator loaded")
    
    def _show_tournament_system(self):
        """Show the tournament system interface."""
        self._clear_content()
        self.current_frame = TournamentSystemFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Tournament System loaded")
    
    def _show_save_file_import(self):
        """Show the save file import interface."""
        self._clear_content()
        self.current_frame = SaveFileImportFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Save File Import loaded")
    
    def _show_social_hub(self):
        """Show the social community hub interface."""
        self._clear_content()
        self.current_frame = SocialCommunityFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Social Community Hub loaded")
    
    def _show_admin_panel(self):
        """Show the admin panel interface."""
        self._clear_content()
        self.current_frame = AdminPanelFrame(self.content_frame, self.theme_manager)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._update_status("Admin Panel loaded")
    
    def _clear_content(self):
        """Clear the current content frame."""
        # Destroy welcome frame if it exists
        if hasattr(self, 'welcome_frame') and self.welcome_frame and self.welcome_frame.winfo_exists():
            self.welcome_frame.destroy()
            self.welcome_frame = None
        
        # Destroy current frame if it exists
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
    
    def _change_theme(self, theme_type: ThemeType):
        """Change the application theme."""
        self.theme_manager.set_theme(theme_type)
        self.theme_var.set(theme_type.value)
        self._apply_theme()
        self._update_status(f"Theme changed to {theme_type.value.title()}")
    
    def _on_theme_combo_changed(self, event):
        """Handle theme combo box selection change."""
        theme_name = self.theme_var.get()
        for theme_type in ThemeType:
            if theme_type.value == theme_name:
                self._change_theme(theme_type)
                break
    
    def _apply_theme(self):
        """Apply the current theme to all widgets."""
        self.theme_manager.apply_theme(self.root)
    
    def _on_theme_changed(self, event):
        """Handle theme change events."""
        self._apply_theme()
    
    def _update_status(self, message: str):
        """Update the status bar message."""
        self.status_bar.config(text=message)
    
    def _new_team(self):
        """Create a new team."""
        self._update_status("New Team - Coming Soon!")
        messagebox.showinfo("Coming Soon", "New Team functionality will be available in the next update!")
    
    def _open_team(self):
        """Open an existing team."""
        self._update_status("Open Team - Coming Soon!")
        messagebox.showinfo("Coming Soon", "Open Team functionality will be available in the next update!")
    
    def _save_team(self):
        """Save the current team."""
        self._update_status("Save Team - Coming Soon!")
        messagebox.showinfo("Coming Soon", "Save Team functionality will be available in the next update!")
    
    def _exit_app(self):
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()
    
    def _show_about(self):
        """Show the about dialog."""
        about_text = """Pokemon Team Builder v1.0

A comprehensive Pokemon team building and trading platform.

Features:
• Support for all Pokemon games from GameCube to Switch
• Team building with Shadow Pokemon mechanics
• Advanced analysis and optimization
• Battle simulation
• Multiple themes and customization

Created with ❤️ for Pokemon fans everywhere!"""
        
        messagebox.showinfo("About Pokemon Team Builder", about_text)
    
    def _show_documentation(self):
        """Show the documentation."""
        self._update_status("Documentation - Coming Soon!")
        messagebox.showinfo("Coming Soon", "Documentation will be available in the next update!")
    
    def run(self):
        """Start the main application loop."""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.root.quit()


def main():
    """Main entry point for the GUI application."""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
