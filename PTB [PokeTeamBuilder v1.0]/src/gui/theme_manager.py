"""
Theme management system for Pokemon Team Builder GUI.
Provides multiple color schemes and styling options.
"""

from typing import Dict, Any
from enum import Enum
import tkinter as tk
from tkinter import ttk


class ThemeType(Enum):
    """Available theme types."""
    LIGHT = "light"
    DARK = "dark"
    POKEMON = "pokemon"
    GAMECUBE = "gamecube"
    MODERN = "modern"
    RETRO = "retro"


class ThemeManager:
    """Manages GUI themes and styling."""
    
    def __init__(self):
        self.current_theme = ThemeType.POKEMON
        self.themes = self._initialize_themes()
    
    def _initialize_themes(self) -> Dict[ThemeType, Dict[str, Any]]:
        """Initialize all available themes."""
        themes = {}
        
        # Light Theme
        themes[ThemeType.LIGHT] = {
            'bg': '#ffffff',
            'fg': '#000000',
            'accent': '#007acc',
            'secondary': '#f0f0f0',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'border': '#cccccc',
            'highlight': '#e3f2fd'
        }
        
        # Dark Theme
        themes[ThemeType.DARK] = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'secondary': '#2d2d30',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'border': '#3e3e42',
            'highlight': '#264f78'
        }
        
        # Pokemon Theme (Inspired by Pokemon games)
        themes[ThemeType.POKEMON] = {
            'bg': '#f8f9fa',
            'fg': '#2c3e50',
            'accent': '#e74c3c',  # Pokemon red
            'secondary': '#ecf0f1',
            'success': '#27ae60',  # Pokemon green
            'warning': '#f39c12',  # Pokemon orange
            'error': '#e74c3c',   # Pokemon red
            'border': '#bdc3c7',
            'highlight': '#3498db', # Pokemon blue
            'grass': '#2ecc71',
            'fire': '#e74c3c',
            'water': '#3498db',
            'electric': '#f1c40f',
            'psychic': '#9b59b6',
            'ice': '#74b9ff',
            'fighting': '#e17055',
            'poison': '#a29bfe',
            'ground': '#d63031',
            'flying': '#81ecec',
            'bug': '#00b894',
            'rock': '#636e72',
            'ghost': '#6c5ce7',
            'dragon': '#fd79a8',
            'dark': '#2d3436',
            'steel': '#b2bec3',
            'fairy': '#fd79a8',
            'shadow': '#6c5ce7'
        }
        
        # GameCube Theme (Inspired by GameCube era)
        themes[ThemeType.GAMECUBE] = {
            'bg': '#2c1810',
            'fg': '#f4d03f',
            'accent': '#e67e22',
            'secondary': '#8b4513',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'border': '#a0522d',
            'highlight': '#d68910',
            'grass': '#2ecc71',
            'fire': '#e74c3c',
            'water': '#3498db',
            'electric': '#f1c40f',
            'psychic': '#9b59b6',
            'ice': '#74b9ff',
            'fighting': '#e17055',
            'poison': '#a29bfe',
            'ground': '#d63031',
            'flying': '#81ecec',
            'bug': '#00b894',
            'rock': '#636e72',
            'ghost': '#6c5ce7',
            'dragon': '#fd79a8',
            'dark': '#2d3436',
            'steel': '#b2bec3',
            'fairy': '#fd79a8',
            'shadow': '#8e44ad'
        }
        
        # Modern Theme
        themes[ThemeType.MODERN] = {
            'bg': '#fafafa',
            'fg': '#212121',
            'accent': '#2196f3',
            'secondary': '#f5f5f5',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'border': '#e0e0e0',
            'highlight': '#e3f2fd'
        }
        
        # Retro Theme
        themes[ThemeType.RETRO] = {
            'bg': '#000000',
            'fg': '#00ff00',
            'accent': '#ffff00',
            'secondary': '#008000',
            'success': '#00ff00',
            'warning': '#ffff00',
            'error': '#ff0000',
            'border': '#00ff00',
            'highlight': '#008000'
        }
        
        return themes
    
    def get_theme(self, theme_type: ThemeType = None) -> Dict[str, Any]:
        """Get a specific theme or the current theme."""
        if theme_type is None:
            theme_type = self.current_theme
        
        return self.themes.get(theme_type, self.themes[ThemeType.POKEMON])
    
    def set_theme(self, theme_type: ThemeType):
        """Set the current theme."""
        self.current_theme = theme_type
    
    def apply_theme(self, widget: tk.Widget, theme_type: ThemeType = None):
        """Apply a theme to a widget and its children."""
        theme = self.get_theme(theme_type)
        
        if isinstance(widget, tk.Tk) or isinstance(widget, tk.Toplevel):
            widget.configure(
                bg=theme['bg'],
                fg=theme['fg']
            )
        elif isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
            widget.configure(
                bg=theme['bg'],
                fg=theme['fg'],
                highlightbackground=theme['border'],
                highlightcolor=theme['accent']
            )
        elif isinstance(widget, tk.Label):
            widget.configure(
                bg=theme['bg'],
                fg=theme['fg']
            )
        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=theme['accent'],
                fg='white',
                activebackground=theme['highlight'],
                activeforeground='white',
                relief='flat',
                borderwidth=0,
                padx=10,
                pady=5
            )
        elif isinstance(widget, tk.Entry):
            widget.configure(
                bg=theme['secondary'],
                fg=theme['fg'],
                insertbackground=theme['fg'],
                relief='flat',
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=theme['border'],
                highlightcolor=theme['accent']
            )
        elif isinstance(widget, tk.Text):
            widget.configure(
                bg=theme['secondary'],
                fg=theme['fg'],
                insertbackground=theme['fg'],
                relief='flat',
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=theme['border'],
                highlightcolor=theme['accent']
            )
        elif isinstance(widget, ttk.Treeview):
            style = ttk.Style()
            style.theme_use('clam')
            style.configure(
                'Treeview',
                background=theme['secondary'],
                foreground=theme['fg'],
                fieldbackground=theme['secondary'],
                borderwidth=0
            )
            style.configure(
                'Treeview.Heading',
                background=theme['accent'],
                foreground='white',
                relief='flat'
            )
        
        # Apply theme to children
        for child in widget.winfo_children():
            self.apply_theme(child, theme_type)
    
    def get_type_color(self, pokemon_type: str) -> str:
        """Get the color for a specific Pokemon type."""
        theme = self.get_theme()
        type_lower = pokemon_type.lower()
        
        # Map Pokemon types to theme colors
        type_colors = {
            'grass': theme.get('grass', theme['accent']),
            'fire': theme.get('fire', theme['accent']),
            'water': theme.get('water', theme['accent']),
            'electric': theme.get('electric', theme['accent']),
            'psychic': theme.get('psychic', theme['accent']),
            'ice': theme.get('ice', theme['accent']),
            'fighting': theme.get('fighting', theme['accent']),
            'poison': theme.get('poison', theme['accent']),
            'ground': theme.get('ground', theme['accent']),
            'flying': theme.get('flying', theme['accent']),
            'bug': theme.get('bug', theme['accent']),
            'rock': theme.get('rock', theme['accent']),
            'ghost': theme.get('ghost', theme['accent']),
            'dragon': theme.get('dragon', theme['accent']),
            'dark': theme.get('dark', theme['accent']),
            'steel': theme.get('steel', theme['accent']),
            'fairy': theme.get('fairy', theme['accent']),
            'shadow': theme.get('shadow', theme['accent'])
        }
        
        return type_colors.get(type_lower, theme['accent'])
    
    def create_styled_button(
        self,
        parent: tk.Widget,
        text: str,
        command=None,
        theme_type: ThemeType = None
    ) -> tk.Button:
        """Create a styled button with the current theme."""
        theme = self.get_theme(theme_type)
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=theme['accent'],
            fg='white',
            activebackground=theme['highlight'],
            activeforeground='white',
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=8,
            font=('Arial', 10, 'bold'),
            cursor='hand2'
        )
        
        return button
    
    def create_styled_label(
        self,
        parent: tk.Widget,
        text: str,
        theme_type: ThemeType = None,
        **kwargs
    ) -> tk.Label:
        """Create a styled label with the current theme."""
        theme = self.get_theme(theme_type)
        
        label = tk.Label(
            parent,
            text=text,
            bg=theme['bg'],
            fg=theme['fg'],
            **kwargs
        )
        
        return label
    
    def create_styled_frame(
        self,
        parent: tk.Widget,
        theme_type: ThemeType = None,
        **kwargs
    ) -> tk.Frame:
        """Create a styled frame with the current theme."""
        theme = self.get_theme(theme_type)
        
        frame = tk.Frame(
            parent,
            bg=theme['bg'],
            **kwargs
        )
        
        return frame
    
    def get_available_themes(self) -> list:
        """Get list of available theme names."""
        return [theme.value for theme in ThemeType]
    
    def get_theme_preview(self, theme_type: ThemeType) -> str:
        """Get a preview description of a theme."""
        previews = {
            ThemeType.LIGHT: "Clean, bright interface with high contrast",
            ThemeType.DARK: "Modern dark theme for reduced eye strain",
            ThemeType.POKEMON: "Classic Pokemon-inspired color scheme",
            ThemeType.GAMECUBE: "Nostalgic GameCube era styling",
            ThemeType.MODERN: "Contemporary flat design aesthetic",
            ThemeType.RETRO: "Classic terminal-style green on black"
        }
        
        return previews.get(theme_type, "Custom theme")
