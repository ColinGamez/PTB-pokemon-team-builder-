"""
Battle Streaming Overlay System
Professional streaming overlay system for tournament broadcasting with real-time battle statistics,
player information displays, animated transitions, and customizable themes for content creators.
"""

import json
import time
import threading
import websocket
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import sqlite3
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
import cv2
import numpy as np
from collections import deque
import math

class OverlayTheme(Enum):
    """Predefined overlay themes."""
    MODERN_DARK = "modern_dark"
    NEON_GLOW = "neon_glow"
    RETRO_PIXEL = "retro_pixel"
    MINIMAL_CLEAN = "minimal_clean"
    TOURNAMENT_PRO = "tournament_pro"
    POKEMON_CLASSIC = "pokemon_classic"
    CYBERPUNK = "cyberpunk"
    NATURE_ORGANIC = "nature_organic"

class AnimationType(Enum):
    """Animation types for overlay elements."""
    FADE_IN = "fade_in"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ROTATE = "rotate"
    PULSE = "pulse"
    BOUNCE = "bounce"
    SHAKE = "shake"
    FLIP = "flip"

class OverlayPosition(Enum):
    """Overlay element positions."""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_CENTER = "middle_center"
    MIDDLE_RIGHT = "middle_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"
    CUSTOM = "custom"

class StreamingPlatform(Enum):
    """Supported streaming platforms."""
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    DISCORD = "discord"
    OBS = "obs"
    STREAMLABS = "streamlabs"

@dataclass
class PlayerInfo:
    """Player information for overlay display."""
    name: str
    team_name: str
    avatar_url: str
    rank: str
    rating: int
    wins: int
    losses: int
    current_pokemon: List[str]
    favorite_types: List[str]
    achievements: List[str]
    country: str = "Unknown"
    sponsor: str = ""
    social_media: Dict[str, str] = None
    
    def __post_init__(self):
        if self.social_media is None:
            self.social_media = {}

@dataclass
class BattleStats:
    """Real-time battle statistics."""
    turn_number: int
    time_elapsed: float
    damage_dealt: Dict[str, int]  # player -> total damage
    pokemon_ko_count: Dict[str, int]  # player -> KOs
    moves_used: Dict[str, List[str]]  # player -> move list
    type_effectiveness_hits: Dict[str, int]  # effectiveness -> count
    critical_hits: Dict[str, int]  # player -> crit count
    status_conditions: Dict[str, List[str]]  # player -> status list
    momentum_score: Dict[str, float]  # player -> momentum (-100 to 100)
    prediction_accuracy: float = 0.0

@dataclass
class OverlayElement:
    """Individual overlay element configuration."""
    element_id: str
    element_type: str  # "player_info", "battle_stats", "timer", "pokemon_status", etc.
    position: OverlayPosition
    custom_position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (200, 100)
    visible: bool = True
    opacity: float = 1.0
    animation: Optional[AnimationType] = None
    animation_duration: float = 1.0
    auto_hide: bool = False
    auto_hide_delay: float = 5.0
    z_index: int = 0
    custom_css: str = ""
    data_source: str = ""

@dataclass
class OverlayThemeConfig:
    """Complete overlay theme configuration."""
    theme_name: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    font_family: str
    font_size: int
    border_radius: int
    shadow_enabled: bool
    gradient_enabled: bool
    particle_effects: bool
    custom_css: str = ""

class OverlayAnimationEngine:
    """Animation engine for overlay elements."""
    
    def __init__(self):
        self.active_animations = {}
        self.animation_queue = deque()
        self.running = False
        self.fps = 60
        self.frame_time = 1.0 / self.fps
    
    def start(self):
        """Start the animation engine."""
        self.running = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
    
    def stop(self):
        """Stop the animation engine."""
        self.running = False
    
    def _animation_loop(self):
        """Main animation loop."""
        while self.running:
            start_time = time.time()
            
            # Process active animations
            completed_animations = []
            for anim_id, animation in self.active_animations.items():
                if self._update_animation(animation):
                    completed_animations.append(anim_id)
            
            # Remove completed animations
            for anim_id in completed_animations:
                del self.active_animations[anim_id]
            
            # Process animation queue
            if self.animation_queue and len(self.active_animations) < 10:  # Limit concurrent animations
                new_animation = self.animation_queue.popleft()
                self.active_animations[new_animation['id']] = new_animation
            
            # Maintain FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, self.frame_time - elapsed)
            time.sleep(sleep_time)
    
    def _update_animation(self, animation: Dict[str, Any]) -> bool:
        """Update single animation frame."""
        current_time = time.time()
        elapsed = current_time - animation['start_time']
        progress = min(1.0, elapsed / animation['duration'])
        
        # Apply easing function
        eased_progress = self._apply_easing(progress, animation.get('easing', 'ease_out'))
        
        # Calculate current values
        element = animation['element']
        anim_type = animation['type']
        
        if anim_type == AnimationType.FADE_IN:
            element.opacity = animation['start_opacity'] + (animation['target_opacity'] - animation['start_opacity']) * eased_progress
        elif anim_type == AnimationType.SLIDE_LEFT:
            start_x, start_y = animation['start_position']
            target_x, target_y = animation['target_position']
            current_x = start_x + (target_x - start_x) * eased_progress
            element.custom_position = (int(current_x), start_y)
        elif anim_type == AnimationType.ZOOM_IN:
            start_size = animation['start_size']
            target_size = animation['target_size']
            current_width = start_size[0] + (target_size[0] - start_size[0]) * eased_progress
            current_height = start_size[1] + (target_size[1] - start_size[1]) * eased_progress
            element.size = (int(current_width), int(current_height))
        elif anim_type == AnimationType.PULSE:
            # Pulsing opacity animation
            pulse_value = 0.5 + 0.5 * math.sin(elapsed * 6.28)  # 1Hz pulse
            element.opacity = animation['base_opacity'] * pulse_value
        elif anim_type == AnimationType.BOUNCE:
            # Bouncing position animation
            bounce_height = animation.get('bounce_height', 20)
            bounce_value = abs(math.sin(elapsed * 6.28)) * bounce_height
            start_x, start_y = animation['start_position']
            element.custom_position = (start_x, int(start_y - bounce_value))
        
        # Update element in overlay system
        animation['update_callback'](element)
        
        return progress >= 1.0
    
    def _apply_easing(self, progress: float, easing: str) -> float:
        """Apply easing function to animation progress."""
        if easing == 'linear':
            return progress
        elif easing == 'ease_in':
            return progress * progress
        elif easing == 'ease_out':
            return 1 - (1 - progress) * (1 - progress)
        elif easing == 'ease_in_out':
            if progress < 0.5:
                return 2 * progress * progress
            else:
                return 1 - 2 * (1 - progress) * (1 - progress)
        elif easing == 'bounce':
            if progress < 0.36:
                return 7.5625 * progress * progress
            elif progress < 0.73:
                progress -= 0.54
                return 7.5625 * progress * progress + 0.75
            elif progress < 0.91:
                progress -= 0.82
                return 7.5625 * progress * progress + 0.9375
            else:
                progress -= 0.955
                return 7.5625 * progress * progress + 0.984375
        else:
            return progress
    
    def animate_element(
        self, 
        element: OverlayElement, 
        animation_type: AnimationType,
        duration: float = 1.0,
        easing: str = 'ease_out',
        update_callback: Callable = None,
        **kwargs
    ):
        """Queue an animation for an overlay element."""
        animation = {
            'id': f"{element.element_id}_{time.time()}",
            'element': element,
            'type': animation_type,
            'duration': duration,
            'easing': easing,
            'start_time': time.time(),
            'update_callback': update_callback or (lambda x: None),
            **kwargs
        }
        
        # Set animation-specific properties
        if animation_type == AnimationType.FADE_IN:
            animation['start_opacity'] = element.opacity
            animation['target_opacity'] = kwargs.get('target_opacity', 1.0)
        elif animation_type in [AnimationType.SLIDE_LEFT, AnimationType.SLIDE_RIGHT, 
                               AnimationType.SLIDE_UP, AnimationType.SLIDE_DOWN]:
            animation['start_position'] = element.custom_position
            animation['target_position'] = kwargs.get('target_position', element.custom_position)
        elif animation_type in [AnimationType.ZOOM_IN, AnimationType.ZOOM_OUT]:
            animation['start_size'] = element.size
            animation['target_size'] = kwargs.get('target_size', element.size)
        elif animation_type == AnimationType.PULSE:
            animation['base_opacity'] = element.opacity
        elif animation_type == AnimationType.BOUNCE:
            animation['start_position'] = element.custom_position
            animation['bounce_height'] = kwargs.get('bounce_height', 20)
        
        self.animation_queue.append(animation)

class StreamingOverlaySystem:
    """Main streaming overlay system."""
    
    def __init__(self):
        self.elements = {}
        self.theme_config = self._load_default_theme()
        self.animation_engine = OverlayAnimationEngine()
        self.websocket_server = None
        self.battle_stats = BattleStats(0, 0.0, {}, {}, {}, {}, {}, {}, {})
        self.player_info = {}
        self.tournament_info = {}
        self.observers = []
        self.recording = False
        self.stream_key = ""
        self.platform_configs = {}
        
        # Start animation engine
        self.animation_engine.start()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize overlay database."""
        self.db_connection = sqlite3.connect("overlay_data.db", check_same_thread=False)
        cursor = self.db_connection.cursor()
        
        # Overlay elements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overlay_elements (
                element_id TEXT PRIMARY KEY,
                element_type TEXT NOT NULL,
                position TEXT NOT NULL,
                custom_position_x INTEGER DEFAULT 0,
                custom_position_y INTEGER DEFAULT 0,
                width INTEGER DEFAULT 200,
                height INTEGER DEFAULT 100,
                visible BOOLEAN DEFAULT 1,
                opacity REAL DEFAULT 1.0,
                z_index INTEGER DEFAULT 0,
                custom_css TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Themes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overlay_themes (
                theme_name TEXT PRIMARY KEY,
                primary_color TEXT NOT NULL,
                secondary_color TEXT NOT NULL,
                accent_color TEXT NOT NULL,
                background_color TEXT NOT NULL,
                text_color TEXT NOT NULL,
                font_family TEXT DEFAULT 'Arial',
                font_size INTEGER DEFAULT 14,
                border_radius INTEGER DEFAULT 5,
                shadow_enabled BOOLEAN DEFAULT 1,
                gradient_enabled BOOLEAN DEFAULT 0,
                particle_effects BOOLEAN DEFAULT 0,
                custom_css TEXT DEFAULT ''
            )
        """)
        
        # Stream sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stream_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                platform TEXT NOT NULL,
                stream_title TEXT,
                viewer_count INTEGER DEFAULT 0,
                battle_count INTEGER DEFAULT 0,
                highlights_count INTEGER DEFAULT 0,
                duration_seconds INTEGER DEFAULT 0
            )
        """)
        
        self.db_connection.commit()
        
        # Insert default themes
        self._create_default_themes()
    
    def _create_default_themes(self):
        """Create default overlay themes."""
        default_themes = [
            OverlayThemeConfig(
                theme_name="Modern Dark",
                primary_color="#1a1a2e",
                secondary_color="#16213e",
                accent_color="#0f3460",
                background_color="#000000aa",
                text_color="#e94560",
                font_family="Roboto",
                font_size=16,
                border_radius=8,
                shadow_enabled=True,
                gradient_enabled=True,
                particle_effects=False
            ),
            OverlayThemeConfig(
                theme_name="Neon Glow",
                primary_color="#0f0f0f",
                secondary_color="#1a1a1a",
                accent_color="#00ff41",
                background_color="#000000cc",
                text_color="#00ff41",
                font_family="Orbitron",
                font_size=18,
                border_radius=0,
                shadow_enabled=True,
                gradient_enabled=False,
                particle_effects=True
            ),
            OverlayThemeConfig(
                theme_name="Tournament Pro",
                primary_color="#ffffff",
                secondary_color="#f8f9fa",
                accent_color="#007bff",
                background_color="#ffffffee",
                text_color="#212529",
                font_family="Inter",
                font_size=15,
                border_radius=6,
                shadow_enabled=True,
                gradient_enabled=False,
                particle_effects=False
            ),
            OverlayThemeConfig(
                theme_name="Pokemon Classic",
                primary_color="#ffcb05",
                secondary_color="#3d7dca",
                accent_color="#ff0000",
                background_color="#ffffff99",
                text_color="#2a75bb",
                font_family="Pokemon",
                font_size=14,
                border_radius=12,
                shadow_enabled=True,
                gradient_enabled=True,
                particle_effects=True
            )
        ]
        
        cursor = self.db_connection.cursor()
        for theme in default_themes:
            cursor.execute("""
                INSERT OR IGNORE INTO overlay_themes 
                (theme_name, primary_color, secondary_color, accent_color, background_color,
                 text_color, font_family, font_size, border_radius, shadow_enabled,
                 gradient_enabled, particle_effects, custom_css)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                theme.theme_name, theme.primary_color, theme.secondary_color,
                theme.accent_color, theme.background_color, theme.text_color,
                theme.font_family, theme.font_size, theme.border_radius,
                theme.shadow_enabled, theme.gradient_enabled, theme.particle_effects,
                theme.custom_css
            ))
        
        self.db_connection.commit()
    
    def _load_default_theme(self) -> OverlayThemeConfig:
        """Load default theme configuration."""
        return OverlayThemeConfig(
            theme_name="Modern Dark",
            primary_color="#1a1a2e",
            secondary_color="#16213e",
            accent_color="#0f3460",
            background_color="#000000aa",
            text_color="#e94560",
            font_family="Roboto",
            font_size=16,
            border_radius=8,
            shadow_enabled=True,
            gradient_enabled=True,
            particle_effects=False
        )
    
    def add_element(self, element: OverlayElement) -> bool:
        """Add overlay element to the system."""
        try:
            self.elements[element.element_id] = element
            
            # Save to database
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO overlay_elements
                (element_id, element_type, position, custom_position_x, custom_position_y,
                 width, height, visible, opacity, z_index, custom_css)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                element.element_id, element.element_type, element.position.value,
                element.custom_position[0], element.custom_position[1],
                element.size[0], element.size[1], element.visible,
                element.opacity, element.z_index, element.custom_css
            ))
            
            self.db_connection.commit()
            
            # Notify observers
            self._notify_observers('element_added', element)
            
            return True
        except Exception as e:
            print(f"Error adding overlay element: {e}")
            return False
    
    def remove_element(self, element_id: str) -> bool:
        """Remove overlay element."""
        try:
            if element_id in self.elements:
                element = self.elements[element_id]
                del self.elements[element_id]
                
                # Remove from database
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM overlay_elements WHERE element_id = ?", (element_id,))
                self.db_connection.commit()
                
                # Notify observers
                self._notify_observers('element_removed', element)
                
                return True
            return False
        except Exception as e:
            print(f"Error removing overlay element: {e}")
            return False
    
    def update_element(self, element_id: str, **kwargs) -> bool:
        """Update overlay element properties."""
        try:
            if element_id in self.elements:
                element = self.elements[element_id]
                
                # Update properties
                for key, value in kwargs.items():
                    if hasattr(element, key):
                        setattr(element, key, value)
                
                # Update database
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE overlay_elements SET
                    position = ?, custom_position_x = ?, custom_position_y = ?,
                    width = ?, height = ?, visible = ?, opacity = ?, z_index = ?, custom_css = ?
                    WHERE element_id = ?
                """, (
                    element.position.value, element.custom_position[0], element.custom_position[1],
                    element.size[0], element.size[1], element.visible,
                    element.opacity, element.z_index, element.custom_css, element_id
                ))
                
                self.db_connection.commit()
                
                # Notify observers
                self._notify_observers('element_updated', element)
                
                return True
            return False
        except Exception as e:
            print(f"Error updating overlay element: {e}")
            return False
    
    def animate_element(
        self, 
        element_id: str, 
        animation: AnimationType,
        duration: float = 1.0,
        **kwargs
    ) -> bool:
        """Animate overlay element."""
        try:
            if element_id in self.elements:
                element = self.elements[element_id]
                
                def update_callback(updated_element):
                    self._notify_observers('element_animated', updated_element)
                
                self.animation_engine.animate_element(
                    element, animation, duration, update_callback=update_callback, **kwargs
                )
                
                return True
            return False
        except Exception as e:
            print(f"Error animating overlay element: {e}")
            return False
    
    def set_theme(self, theme_name: str) -> bool:
        """Set overlay theme."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM overlay_themes WHERE theme_name = ?", (theme_name,))
            theme_row = cursor.fetchone()
            
            if theme_row:
                self.theme_config = OverlayThemeConfig(
                    theme_name=theme_row[0],
                    primary_color=theme_row[1],
                    secondary_color=theme_row[2],
                    accent_color=theme_row[3],
                    background_color=theme_row[4],
                    text_color=theme_row[5],
                    font_family=theme_row[6],
                    font_size=theme_row[7],
                    border_radius=theme_row[8],
                    shadow_enabled=bool(theme_row[9]),
                    gradient_enabled=bool(theme_row[10]),
                    particle_effects=bool(theme_row[11]),
                    custom_css=theme_row[12]
                )
                
                # Notify observers
                self._notify_observers('theme_changed', self.theme_config)
                
                return True
            return False
        except Exception as e:
            print(f"Error setting overlay theme: {e}")
            return False
    
    def update_battle_stats(self, stats: BattleStats):
        """Update battle statistics."""
        self.battle_stats = stats
        self._notify_observers('battle_stats_updated', stats)
    
    def update_player_info(self, player_id: str, info: PlayerInfo):
        """Update player information."""
        self.player_info[player_id] = info
        self._notify_observers('player_info_updated', {'player_id': player_id, 'info': info})
    
    def start_tournament_mode(self, tournament_info: Dict[str, Any]):
        """Start tournament overlay mode."""
        self.tournament_info = tournament_info
        
        # Show tournament-specific elements
        tournament_elements = [
            OverlayElement(
                element_id="tournament_banner",
                element_type="tournament_info",
                position=OverlayPosition.TOP_CENTER,
                size=(600, 80),
                z_index=10
            ),
            OverlayElement(
                element_id="match_info",
                element_type="match_details",
                position=OverlayPosition.TOP_LEFT,
                size=(300, 60),
                z_index=5
            ),
            OverlayElement(
                element_id="bracket_display",
                element_type="bracket_preview",
                position=OverlayPosition.BOTTOM_RIGHT,
                size=(200, 150),
                z_index=3
            )
        ]
        
        for element in tournament_elements:
            self.add_element(element)
            # Animate in
            self.animate_element(element.element_id, AnimationType.SLIDE_DOWN, 1.5)
        
        self._notify_observers('tournament_mode_started', tournament_info)
    
    def create_highlight_clip(self, duration: float = 30.0) -> str:
        """Create highlight clip from recent battle moments."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clip_id = f"highlight_{timestamp}"
            
            # In a real implementation, this would capture video/screenshots
            highlight_data = {
                'clip_id': clip_id,
                'timestamp': timestamp,
                'duration': duration,
                'battle_context': asdict(self.battle_stats),
                'players': self.player_info.copy(),
                'memorable_moments': [
                    "Critical hit landed!",
                    "Unexpected type advantage!",
                    "Comeback victory!"
                ]
            }
            
            # Save highlight data
            with open(f"highlights/{clip_id}.json", 'w') as f:
                json.dump(highlight_data, f, indent=2)
            
            self._notify_observers('highlight_created', highlight_data)
            
            return clip_id
        except Exception as e:
            print(f"Error creating highlight clip: {e}")
            return ""
    
    def start_stream_session(self, platform: StreamingPlatform, stream_title: str) -> str:
        """Start streaming session."""
        try:
            session_id = f"session_{int(time.time())}"
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO stream_sessions 
                (session_id, start_time, platform, stream_title)
                VALUES (?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                platform.value,
                stream_title
            ))
            
            self.db_connection.commit()
            
            # Configure platform-specific settings
            self._configure_platform(platform)
            
            self._notify_observers('stream_started', {
                'session_id': session_id,
                'platform': platform.value,
                'title': stream_title
            })
            
            return session_id
        except Exception as e:
            print(f"Error starting stream session: {e}")
            return ""
    
    def _configure_platform(self, platform: StreamingPlatform):
        """Configure platform-specific overlay settings."""
        if platform == StreamingPlatform.TWITCH:
            # Twitch-specific configurations
            self.platform_configs[platform.value] = {
                'max_resolution': (1920, 1080),
                'safe_area_margins': (20, 20, 20, 20),  # top, right, bottom, left
                'chat_integration': True,
                'bits_alerts': True,
                'subscriber_alerts': True
            }
        elif platform == StreamingPlatform.YOUTUBE:
            # YouTube-specific configurations
            self.platform_configs[platform.value] = {
                'max_resolution': (1920, 1080),
                'safe_area_margins': (10, 10, 10, 10),
                'super_chat_integration': True,
                'member_alerts': True,
                'live_chat_display': True
            }
        elif platform == StreamingPlatform.OBS:
            # OBS-specific configurations
            self.platform_configs[platform.value] = {
                'websocket_port': 4444,
                'scene_switching': True,
                'source_management': True,
                'filter_control': True
            }
    
    def add_observer(self, observer: Callable):
        """Add observer for overlay events."""
        self.observers.append(observer)
    
    def remove_observer(self, observer: Callable):
        """Remove observer."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, event_type: str, data: Any):
        """Notify all observers of overlay events."""
        for observer in self.observers:
            try:
                observer(event_type, data)
            except Exception as e:
                print(f"Error notifying observer: {e}")
    
    def export_overlay_config(self, filename: str) -> bool:
        """Export overlay configuration to file."""
        try:
            config = {
                'theme': asdict(self.theme_config),
                'elements': {eid: asdict(element) for eid, element in self.elements.items()},
                'tournament_info': self.tournament_info,
                'platform_configs': self.platform_configs,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error exporting overlay config: {e}")
            return False
    
    def import_overlay_config(self, filename: str) -> bool:
        """Import overlay configuration from file."""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            # Import theme
            if 'theme' in config:
                theme_data = config['theme']
                self.theme_config = OverlayThemeConfig(**theme_data)
            
            # Import elements
            if 'elements' in config:
                self.elements.clear()
                for element_id, element_data in config['elements'].items():
                    # Convert position back to enum
                    element_data['position'] = OverlayPosition(element_data['position'])
                    if element_data.get('animation'):
                        element_data['animation'] = AnimationType(element_data['animation'])
                    
                    element = OverlayElement(**element_data)
                    self.elements[element_id] = element
            
            # Import other settings
            if 'tournament_info' in config:
                self.tournament_info = config['tournament_info']
            
            if 'platform_configs' in config:
                self.platform_configs = config['platform_configs']
            
            self._notify_observers('config_imported', config)
            
            return True
        except Exception as e:
            print(f"Error importing overlay config: {e}")
            return False
    
    def get_overlay_statistics(self) -> Dict[str, Any]:
        """Get overlay usage statistics."""
        cursor = self.db_connection.cursor()
        
        # Stream session stats
        cursor.execute("""
            SELECT platform, COUNT(*) as session_count, 
                   AVG(duration_seconds) as avg_duration,
                   SUM(viewer_count) as total_viewers
            FROM stream_sessions 
            GROUP BY platform
        """)
        
        session_stats = {}
        for row in cursor.fetchall():
            session_stats[row[0]] = {
                'session_count': row[1],
                'avg_duration': row[2] or 0,
                'total_viewers': row[3] or 0
            }
        
        # Element usage stats
        cursor.execute("""
            SELECT element_type, COUNT(*) as usage_count
            FROM overlay_elements
            GROUP BY element_type
        """)
        
        element_stats = {}
        for row in cursor.fetchall():
            element_stats[row[0]] = row[1]
        
        return {
            'session_statistics': session_stats,
            'element_usage': element_stats,
            'active_elements': len(self.elements),
            'current_theme': self.theme_config.theme_name,
            'total_themes': len(self._get_available_themes()),
            'animation_engine_active': self.animation_engine.running
        }
    
    def _get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT theme_name FROM overlay_themes")
        return [row[0] for row in cursor.fetchall()]

class OverlayGUI:
    """GUI for overlay system configuration."""
    
    def __init__(self, overlay_system: StreamingOverlaySystem):
        self.overlay_system = overlay_system
        self.root = tk.Tk()
        self.root.title("Battle Streaming Overlay System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")
        
        self.setup_gui()
        self.overlay_system.add_observer(self.on_overlay_event)
    
    def setup_gui(self):
        """Setup GUI components."""
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Elements tab
        self.elements_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.elements_frame, text="Elements")
        self.setup_elements_tab()
        
        # Themes tab
        self.themes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.themes_frame, text="Themes")
        self.setup_themes_tab()
        
        # Animation tab
        self.animation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.animation_frame, text="Animations")
        self.setup_animation_tab()
        
        # Streaming tab
        self.streaming_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.streaming_frame, text="Streaming")
        self.setup_streaming_tab()
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.setup_statistics_tab()
    
    def setup_elements_tab(self):
        """Setup elements configuration tab."""
        # Elements list
        ttk.Label(self.elements_frame, text="Overlay Elements", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.elements_listbox = tk.Listbox(self.elements_frame, height=10)
        self.elements_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Element controls
        controls_frame = ttk.Frame(self.elements_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Add Element", command=self.add_element_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Edit Element", command=self.edit_element_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Remove Element", command=self.remove_element).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Preview", command=self.preview_overlay).pack(side=tk.RIGHT, padx=5)
        
        self.refresh_elements_list()
    
    def setup_themes_tab(self):
        """Setup themes configuration tab."""
        ttk.Label(self.themes_frame, text="Overlay Themes", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Theme selection
        theme_select_frame = ttk.Frame(self.themes_frame)
        theme_select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(theme_select_frame, text="Current Theme:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.overlay_system.theme_config.theme_name)
        self.theme_combo = ttk.Combobox(theme_select_frame, textvariable=self.theme_var, 
                                       values=self.overlay_system._get_available_themes())
        self.theme_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(theme_select_frame, text="Apply", command=self.apply_theme).pack(side=tk.RIGHT, padx=5)
        
        # Theme preview
        self.theme_preview_frame = ttk.LabelFrame(self.themes_frame, text="Theme Preview")
        self.theme_preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Theme customization would go here
        ttk.Label(self.theme_preview_frame, text="Theme customization controls coming soon...").pack(pady=20)
    
    def setup_animation_tab(self):
        """Setup animation configuration tab."""
        ttk.Label(self.animation_frame, text="Animation Controls", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Animation controls
        anim_controls_frame = ttk.Frame(self.animation_frame)
        anim_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(anim_controls_frame, text="Element:").grid(row=0, column=0, sticky=tk.W)
        self.anim_element_var = tk.StringVar()
        anim_element_combo = ttk.Combobox(anim_controls_frame, textvariable=self.anim_element_var)
        anim_element_combo.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        ttk.Label(anim_controls_frame, text="Animation:").grid(row=1, column=0, sticky=tk.W)
        self.anim_type_var = tk.StringVar()
        anim_type_combo = ttk.Combobox(anim_controls_frame, textvariable=self.anim_type_var,
                                      values=[anim.value for anim in AnimationType])
        anim_type_combo.grid(row=1, column=1, padx=5, sticky=tk.EW)
        
        ttk.Label(anim_controls_frame, text="Duration:").grid(row=2, column=0, sticky=tk.W)
        self.anim_duration_var = tk.DoubleVar(value=1.0)
        anim_duration_spin = ttk.Spinbox(anim_controls_frame, from_=0.1, to=10.0, increment=0.1,
                                        textvariable=self.anim_duration_var)
        anim_duration_spin.grid(row=2, column=1, padx=5, sticky=tk.EW)
        
        ttk.Button(anim_controls_frame, text="Animate", command=self.animate_element).grid(row=3, column=1, pady=10)
        
        anim_controls_frame.columnconfigure(1, weight=1)
    
    def setup_streaming_tab(self):
        """Setup streaming configuration tab."""
        ttk.Label(self.streaming_frame, text="Streaming Configuration", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Platform selection
        platform_frame = ttk.LabelFrame(self.streaming_frame, text="Streaming Platform")
        platform_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.platform_var = tk.StringVar(value="twitch")
        for platform in StreamingPlatform:
            ttk.Radiobutton(platform_frame, text=platform.value.title(), 
                           variable=self.platform_var, value=platform.value).pack(anchor=tk.W)
        
        # Stream controls
        stream_controls_frame = ttk.Frame(self.streaming_frame)
        stream_controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stream_controls_frame, text="Stream Title:").pack(anchor=tk.W)
        self.stream_title_var = tk.StringVar(value="Pokemon Battle Tournament")
        ttk.Entry(stream_controls_frame, textvariable=self.stream_title_var).pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(stream_controls_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Start Stream", command=self.start_stream).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create Highlight", command=self.create_highlight).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Tournament Mode", command=self.start_tournament_mode).pack(side=tk.LEFT, padx=5)
    
    def setup_statistics_tab(self):
        """Setup statistics display tab."""
        ttk.Label(self.stats_frame, text="Overlay Statistics", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.stats_text = tk.Text(self.stats_frame, height=20, width=80)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Button(self.stats_frame, text="Refresh Statistics", command=self.refresh_statistics).pack(pady=10)
        
        self.refresh_statistics()
    
    def refresh_elements_list(self):
        """Refresh the elements list."""
        self.elements_listbox.delete(0, tk.END)
        for element_id, element in self.overlay_system.elements.items():
            self.elements_listbox.insert(tk.END, f"{element_id} ({element.element_type})")
    
    def add_element_dialog(self):
        """Open dialog to add new element."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Overlay Element")
        dialog.geometry("400x300")
        
        # Element configuration form would go here
        ttk.Label(dialog, text="Add element dialog coming soon...").pack(pady=20)
    
    def edit_element_dialog(self):
        """Open dialog to edit selected element."""
        selection = self.elements_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an element to edit.")
            return
        
        # Edit dialog would go here
        messagebox.showinfo("Edit Element", "Edit element dialog coming soon...")
    
    def remove_element(self):
        """Remove selected element."""
        selection = self.elements_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an element to remove.")
            return
        
        element_text = self.elements_listbox.get(selection[0])
        element_id = element_text.split(' (')[0]
        
        if messagebox.askyesno("Confirm Removal", f"Remove element '{element_id}'?"):
            self.overlay_system.remove_element(element_id)
            self.refresh_elements_list()
    
    def preview_overlay(self):
        """Preview overlay configuration."""
        messagebox.showinfo("Preview", "Overlay preview coming soon...")
    
    def apply_theme(self):
        """Apply selected theme."""
        theme_name = self.theme_var.get()
        if self.overlay_system.set_theme(theme_name):
            messagebox.showinfo("Theme Applied", f"Theme '{theme_name}' applied successfully!")
        else:
            messagebox.showerror("Error", f"Failed to apply theme '{theme_name}'")
    
    def animate_element(self):
        """Animate selected element."""
        element_id = self.anim_element_var.get()
        animation_type = AnimationType(self.anim_type_var.get())
        duration = self.anim_duration_var.get()
        
        if element_id and animation_type:
            if self.overlay_system.animate_element(element_id, animation_type, duration):
                messagebox.showinfo("Animation", f"Animation started for '{element_id}'")
            else:
                messagebox.showerror("Error", f"Failed to animate element '{element_id}'")
    
    def start_stream(self):
        """Start streaming session."""
        platform = StreamingPlatform(self.platform_var.get())
        title = self.stream_title_var.get()
        
        session_id = self.overlay_system.start_stream_session(platform, title)
        if session_id:
            messagebox.showinfo("Stream Started", f"Stream session '{session_id}' started!")
        else:
            messagebox.showerror("Error", "Failed to start stream session")
    
    def create_highlight(self):
        """Create highlight clip."""
        clip_id = self.overlay_system.create_highlight_clip()
        if clip_id:
            messagebox.showinfo("Highlight Created", f"Highlight clip '{clip_id}' created!")
        else:
            messagebox.showerror("Error", "Failed to create highlight clip")
    
    def start_tournament_mode(self):
        """Start tournament mode."""
        tournament_info = {
            'name': 'Pokemon Battle Championship',
            'round': 'Semifinals',
            'match': '1 of 2',
            'format': 'OU Singles'
        }
        
        self.overlay_system.start_tournament_mode(tournament_info)
        messagebox.showinfo("Tournament Mode", "Tournament mode activated!")
    
    def refresh_statistics(self):
        """Refresh overlay statistics."""
        stats = self.overlay_system.get_overlay_statistics()
        
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = "📊 OVERLAY STATISTICS\n"
        stats_text += "=" * 50 + "\n\n"
        
        stats_text += f"Active Elements: {stats['active_elements']}\n"
        stats_text += f"Current Theme: {stats['current_theme']}\n"
        stats_text += f"Total Themes: {stats['total_themes']}\n"
        stats_text += f"Animation Engine: {'Running' if stats['animation_engine_active'] else 'Stopped'}\n\n"
        
        stats_text += "Stream Sessions by Platform:\n"
        for platform, data in stats['session_statistics'].items():
            stats_text += f"  {platform.title()}: {data['session_count']} sessions\n"
            stats_text += f"    Avg Duration: {data['avg_duration']:.1f}s\n"
            stats_text += f"    Total Viewers: {data['total_viewers']}\n"
        
        stats_text += "\nElement Usage:\n"
        for element_type, count in stats['element_usage'].items():
            stats_text += f"  {element_type}: {count} times\n"
        
        self.stats_text.insert(1.0, stats_text)
    
    def on_overlay_event(self, event_type: str, data: Any):
        """Handle overlay system events."""
        if event_type == 'element_added' or event_type == 'element_removed':
            self.refresh_elements_list()
        elif event_type == 'theme_changed':
            self.theme_var.set(data.theme_name)
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

# Demo function
def demonstrate_streaming_overlay_system():
    """Demonstrate the streaming overlay system."""
    print("🎥 Battle Streaming Overlay System Demo")
    print("=" * 60)
    
    # Create overlay system
    overlay_system = StreamingOverlaySystem()
    
    # Add sample elements
    player1_info = OverlayElement(
        element_id="player1_info",
        element_type="player_info",
        position=OverlayPosition.TOP_LEFT,
        size=(300, 120),
        z_index=5
    )
    
    battle_timer = OverlayElement(
        element_id="battle_timer",
        element_type="timer",
        position=OverlayPosition.TOP_CENTER,
        size=(150, 50),
        z_index=10
    )
    
    pokemon_status = OverlayElement(
        element_id="pokemon_status",
        element_type="pokemon_health",
        position=OverlayPosition.BOTTOM_CENTER,
        size=(400, 100),
        z_index=8
    )
    
    overlay_system.add_element(player1_info)
    overlay_system.add_element(battle_timer)
    overlay_system.add_element(pokemon_status)
    
    print(f"\n📱 Added Overlay Elements:")
    print(f"• Player Info Panel (Top Left)")
    print(f"• Battle Timer (Top Center)")
    print(f"• Pokemon Status (Bottom Center)")
    
    # Set theme
    overlay_system.set_theme("Neon Glow")
    print(f"\n🎨 Applied Theme: Neon Glow")
    
    # Update battle stats
    battle_stats = BattleStats(
        turn_number=15,
        time_elapsed=180.5,
        damage_dealt={"player1": 2450, "player2": 1890},
        pokemon_ko_count={"player1": 2, "player2": 1},
        moves_used={"player1": ["Earthquake", "Stone Edge"], "player2": ["Hydro Pump", "Ice Beam"]},
        type_effectiveness_hits={"super_effective": 3, "not_very_effective": 1},
        critical_hits={"player1": 1, "player2": 2},
        status_conditions={"player1": ["burn"], "player2": []},
        momentum_score={"player1": 25.5, "player2": -25.5}
    )
    
    overlay_system.update_battle_stats(battle_stats)
    
    # Add player information
    player_info = PlayerInfo(
        name="AshKetchum99",
        team_name="Pallet Town Champions",
        avatar_url="https://example.com/avatar.png",
        rank="Master Ball",
        rating=1847,
        wins=234,
        losses=89,
        current_pokemon=["Pikachu", "Charizard", "Blastoise"],
        favorite_types=["Electric", "Fire"],
        achievements=["Regional Champion", "Elite Four Defeated"],
        country="Kanto",
        sponsor="Pokemon Center"
    )
    
    overlay_system.update_player_info("player1", player_info)
    
    print(f"\n⚡ Updated Battle Statistics:")
    print(f"• Turn: {battle_stats.turn_number}")
    print(f"• Time: {battle_stats.time_elapsed}s")
    print(f"• Damage: P1: {battle_stats.damage_dealt['player1']}, P2: {battle_stats.damage_dealt['player2']}")
    print(f"• KOs: P1: {battle_stats.pokemon_ko_count['player1']}, P2: {battle_stats.pokemon_ko_count['player2']}")
    
    # Start tournament mode
    tournament_info = {
        'name': 'Pokemon World Championship 2024',
        'round': 'Grand Finals',
        'match': 'Game 3 of 5',
        'format': 'VGC 2024',
        'prize_pool': '$50,000'
    }
    
    overlay_system.start_tournament_mode(tournament_info)
    print(f"\n🏆 Tournament Mode Started:")
    print(f"• {tournament_info['name']}")
    print(f"• {tournament_info['round']} - {tournament_info['match']}")
    print(f"• Format: {tournament_info['format']}")
    
    # Animate elements
    overlay_system.animate_element("player1_info", AnimationType.SLIDE_LEFT, 2.0)
    overlay_system.animate_element("battle_timer", AnimationType.PULSE, 1.5)
    overlay_system.animate_element("pokemon_status", AnimationType.BOUNCE, 1.0)
    
    print(f"\n🎬 Started Animations:")
    print(f"• Player Info: Slide Left (2.0s)")
    print(f"• Battle Timer: Pulse (1.5s)")
    print(f"• Pokemon Status: Bounce (1.0s)")
    
    # Start streaming session
    session_id = overlay_system.start_stream_session(StreamingPlatform.TWITCH, "Pokemon Championship Live")
    print(f"\n📺 Started Stream Session: {session_id}")
    
    # Create highlight clip
    clip_id = overlay_system.create_highlight_clip(45.0)
    print(f"📹 Created Highlight Clip: {clip_id}")
    
    # Get statistics
    stats = overlay_system.get_overlay_statistics()
    print(f"\n📊 Overlay Statistics:")
    print(f"• Active Elements: {stats['active_elements']}")
    print(f"• Current Theme: {stats['current_theme']}")
    print(f"• Animation Engine: {'Running' if stats['animation_engine_active'] else 'Stopped'}")
    
    # Export configuration
    config_exported = overlay_system.export_overlay_config("tournament_overlay_config.json")
    if config_exported:
        print(f"💾 Configuration exported to tournament_overlay_config.json")
    
    print(f"\n🎥 Battle Streaming Overlay System Ready!")
    print("Features: Real-time Stats, Animated Elements, Tournament Mode, Multi-Platform")
    
    return overlay_system

if __name__ == "__main__":
    # Run demonstration
    overlay_system = demonstrate_streaming_overlay_system()
    
    # Launch GUI
    print(f"\n🚀 Launching Overlay Control Panel...")
    gui = OverlayGUI(overlay_system)
    gui.run()