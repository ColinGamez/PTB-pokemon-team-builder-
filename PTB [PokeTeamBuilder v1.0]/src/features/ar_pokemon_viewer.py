"""
Augmented Reality Pokemon Viewer
Advanced AR system for visualizing Pokemon in real-world environments
with 3D models, stat overlays, and interactive features.
"""

import cv2
import numpy as np
import json
import math
import threading
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pygame
from pygame import gfxdraw

class ARTrackingMode(Enum):
    """AR tracking modes for Pokemon placement."""
    MARKER_BASED = "marker"      # QR/ArUco marker tracking
    FACE_TRACKING = "face"       # Face detection tracking
    HAND_TRACKING = "hand"       # Hand gesture tracking
    SURFACE_PLANE = "surface"    # Plane detection tracking
    FREE_PLACEMENT = "free"      # Manual placement mode

class PokemonARState(Enum):
    """States for AR Pokemon display."""
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    DEFENDING = "defending"
    CELEBRATING = "celebrating"
    FAINTING = "fainting"

@dataclass
class ARPokemon:
    """3D Pokemon model data for AR rendering."""
    name: str
    model_path: str
    texture_path: str
    position: Tuple[float, float, float]  # 3D world coordinates
    rotation: Tuple[float, float, float]  # Euler angles
    scale: float
    animation_state: PokemonARState
    stats: Dict[str, int]
    types: List[str]
    level: int
    is_shiny: bool = False
    transparency: float = 1.0

@dataclass
class ARVisualization:
    """AR visualization configuration."""
    show_stats: bool = True
    show_type_chart: bool = True
    show_moves: bool = True
    show_battle_effects: bool = True
    particle_effects: bool = True
    sound_effects: bool = True
    interaction_mode: str = "gesture"

class AR3DRenderer:
    """3D rendering engine for AR Pokemon."""
    
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.camera_matrix = None
        self.distortion_coeffs = None
        
        # Initialize 3D graphics
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pokemon AR Viewer")
        
        # 3D rendering matrices
        self.projection_matrix = self._create_projection_matrix()
        self.view_matrix = np.eye(4)
        
        # Lighting system
        self.light_position = np.array([0, 10, 5])
        self.ambient_light = 0.3
        self.diffuse_light = 0.7
        
        # Shader programs (simplified)
        self.vertex_shader = self._create_vertex_shader()
        self.fragment_shader = self._create_fragment_shader()
    
    def _create_projection_matrix(self) -> np.ndarray:
        """Create perspective projection matrix."""
        fov = 60.0  # Field of view in degrees
        aspect_ratio = self.width / self.height
        near_plane = 0.1
        far_plane = 100.0
        
        fov_rad = math.radians(fov)
        f = 1.0 / math.tan(fov_rad / 2.0)
        
        projection = np.array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far_plane + near_plane) / (near_plane - far_plane), 
             (2 * far_plane * near_plane) / (near_plane - far_plane)],
            [0, 0, -1, 0]
        ])
        
        return projection
    
    def _create_vertex_shader(self) -> str:
        """Create vertex shader code."""
        return """
        #version 330 core
        layout (location = 0) in vec3 position;
        layout (location = 1) in vec3 normal;
        layout (location = 2) in vec2 texCoord;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        uniform vec3 lightPos;
        
        out vec3 FragPos;
        out vec3 Normal;
        out vec2 TexCoord;
        out vec3 LightPos;
        
        void main() {
            FragPos = vec3(model * vec4(position, 1.0));
            Normal = mat3(transpose(inverse(model))) * normal;
            TexCoord = texCoord;
            LightPos = lightPos;
            
            gl_Position = projection * view * vec4(FragPos, 1.0);
        }
        """
    
    def _create_fragment_shader(self) -> str:
        """Create fragment shader code."""
        return """
        #version 330 core
        out vec4 FragColor;
        
        in vec3 FragPos;
        in vec3 Normal;
        in vec2 TexCoord;
        in vec3 LightPos;
        
        uniform sampler2D texture1;
        uniform vec3 viewPos;
        uniform float shininess;
        uniform float transparency;
        
        void main() {
            vec3 color = texture(texture1, TexCoord).rgb;
            
            // Ambient lighting
            float ambientStrength = 0.3;
            vec3 ambient = ambientStrength * color;
            
            // Diffuse lighting
            vec3 norm = normalize(Normal);
            vec3 lightDir = normalize(LightPos - FragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * color;
            
            // Specular lighting
            float specularStrength = 0.5;
            vec3 viewDir = normalize(viewPos - FragPos);
            vec3 reflectDir = reflect(-lightDir, norm);
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
            vec3 specular = specularStrength * spec * vec3(1.0);
            
            vec3 result = ambient + diffuse + specular;
            FragColor = vec4(result, transparency);
        }
        """
    
    def render_pokemon(self, pokemon: ARPokemon, camera_frame: np.ndarray) -> np.ndarray:
        """Render a 3D Pokemon model onto camera frame."""
        # Create model matrix
        model_matrix = self._create_model_matrix(pokemon)
        
        # Simple 3D mesh rendering (using basic shapes for demo)
        rendered_frame = self._render_basic_pokemon_shape(
            camera_frame, pokemon, model_matrix
        )
        
        return rendered_frame
    
    def _create_model_matrix(self, pokemon: ARPokemon) -> np.ndarray:
        """Create model transformation matrix."""
        # Translation matrix
        translation = np.array([
            [1, 0, 0, pokemon.position[0]],
            [0, 1, 0, pokemon.position[1]],
            [0, 0, 1, pokemon.position[2]],
            [0, 0, 0, 1]
        ])
        
        # Rotation matrices
        rx, ry, rz = pokemon.rotation
        
        rotation_x = np.array([
            [1, 0, 0, 0],
            [0, math.cos(rx), -math.sin(rx), 0],
            [0, math.sin(rx), math.cos(rx), 0],
            [0, 0, 0, 1]
        ])
        
        rotation_y = np.array([
            [math.cos(ry), 0, math.sin(ry), 0],
            [0, 1, 0, 0],
            [-math.sin(ry), 0, math.cos(ry), 0],
            [0, 0, 0, 1]
        ])
        
        rotation_z = np.array([
            [math.cos(rz), -math.sin(rz), 0, 0],
            [math.sin(rz), math.cos(rz), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Scale matrix
        scale_matrix = np.array([
            [pokemon.scale, 0, 0, 0],
            [0, pokemon.scale, 0, 0],
            [0, 0, pokemon.scale, 0],
            [0, 0, 0, 1]
        ])
        
        # Combine transformations
        model = translation @ rotation_z @ rotation_y @ rotation_x @ scale_matrix
        return model
    
    def _render_basic_pokemon_shape(
        self, 
        frame: np.ndarray, 
        pokemon: ARPokemon, 
        model_matrix: np.ndarray
    ) -> np.ndarray:
        """Render a basic 3D shape representing the Pokemon."""
        height, width = frame.shape[:2]
        
        # Project 3D position to 2D screen coordinates
        world_pos = np.array([pokemon.position[0], pokemon.position[1], pokemon.position[2], 1])
        
        # Simple projection (this would use proper camera matrices in real AR)
        screen_x = int(width / 2 + world_pos[0] * 100)
        screen_y = int(height / 2 - world_pos[1] * 100)
        
        # Ensure coordinates are within frame bounds
        if 0 <= screen_x < width and 0 <= screen_y < height:
            # Draw basic Pokemon representation
            self._draw_pokemon_shape(frame, pokemon, screen_x, screen_y)
        
        return frame
    
    def _draw_pokemon_shape(
        self, 
        frame: np.ndarray, 
        pokemon: ARPokemon, 
        x: int, 
        y: int
    ):
        """Draw a simplified Pokemon shape."""
        # Get Pokemon type colors
        type_colors = self._get_type_colors(pokemon.types)
        primary_color = type_colors[0] if type_colors else (255, 255, 255)
        
        # Scale based on Pokemon scale
        size = int(50 * pokemon.scale)
        
        # Draw main body (circle/ellipse)
        cv2.circle(frame, (x, y), size, primary_color, -1)
        
        # Add shiny effect
        if pokemon.is_shiny:
            cv2.circle(frame, (x, y), size + 5, (255, 215, 0), 2)  # Gold outline
        
        # Draw eyes
        eye_offset = size // 3
        cv2.circle(frame, (x - eye_offset, y - eye_offset), 8, (0, 0, 0), -1)
        cv2.circle(frame, (x + eye_offset, y - eye_offset), 8, (0, 0, 0), -1)
        cv2.circle(frame, (x - eye_offset, y - eye_offset), 5, (255, 255, 255), -1)
        cv2.circle(frame, (x + eye_offset, y - eye_offset), 5, (255, 255, 255), -1)
        
        # Animation effects based on state
        self._apply_animation_effects(frame, pokemon, x, y, size)
    
    def _get_type_colors(self, types: List[str]) -> List[Tuple[int, int, int]]:
        """Get BGR colors for Pokemon types."""
        type_color_map = {
            "Normal": (163, 163, 163),
            "Fire": (0, 69, 252),
            "Water": (255, 141, 56),
            "Electric": (0, 215, 255),
            "Grass": (35, 155, 75),
            "Ice": (255, 213, 150),
            "Fighting": (49, 54, 206),
            "Poison": (185, 67, 159),
            "Ground": (91, 123, 230),
            "Flying": (137, 171, 255),
            "Psychic": (140, 105, 251),
            "Bug": (26, 165, 171),
            "Rock": (140, 130, 182),
            "Ghost": (112, 87, 113),
            "Dragon": (111, 53, 252),
            "Dark": (112, 85, 68),
            "Steel": (183, 183, 211),
            "Fairy": (213, 158, 248)
        }
        
        return [type_color_map.get(t, (255, 255, 255)) for t in types]
    
    def _apply_animation_effects(
        self, 
        frame: np.ndarray, 
        pokemon: ARPokemon, 
        x: int, 
        y: int, 
        size: int
    ):
        """Apply visual effects based on Pokemon state."""
        current_time = time.time()
        
        if pokemon.animation_state == PokemonARState.ATTACKING:
            # Red flash effect
            flash_intensity = int(abs(math.sin(current_time * 10)) * 255)
            overlay = frame.copy()
            cv2.circle(overlay, (x, y), size + 10, (0, 0, flash_intensity), -1)
            cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
        
        elif pokemon.animation_state == PokemonARState.CELEBRATING:
            # Sparkle effects
            for i in range(5):
                spark_x = x + random.randint(-size, size)
                spark_y = y + random.randint(-size, size)
                cv2.circle(frame, (spark_x, spark_y), 3, (0, 255, 255), -1)
        
        elif pokemon.animation_state == PokemonARState.WALKING:
            # Slight vertical movement
            bounce = int(math.sin(current_time * 5) * 5)
            cv2.circle(frame, (x, y + bounce), 2, (255, 255, 255), -1)

class ARTracker:
    """AR tracking system for Pokemon placement."""
    
    def __init__(self, mode: ARTrackingMode = ARTrackingMode.MARKER_BASED):
        self.tracking_mode = mode
        self.is_tracking = False
        self.tracked_objects = {}
        
        # Initialize different tracking systems
        if mode == ARTrackingMode.FACE_TRACKING:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        elif mode == ARTrackingMode.MARKER_BASED:
            # ArUco marker detection
            try:
                import cv2.aruco as aruco
                self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
                self.aruco_params = aruco.DetectorParameters_create()
            except:
                print("ArUco markers not available, falling back to basic tracking")
    
    def detect_tracking_points(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect tracking points in the camera frame."""
        tracking_points = []
        
        if self.tracking_mode == ARTrackingMode.FACE_TRACKING:
            tracking_points = self._detect_faces(frame)
        elif self.tracking_mode == ARTrackingMode.MARKER_BASED:
            tracking_points = self._detect_markers(frame)
        elif self.tracking_mode == ARTrackingMode.SURFACE_PLANE:
            tracking_points = self._detect_surfaces(frame)
        else:
            # Free placement mode - return center of frame
            height, width = frame.shape[:2]
            tracking_points = [{
                "position": (width // 2, height // 2),
                "confidence": 1.0,
                "type": "free_placement"
            }]
        
        return tracking_points
    
    def _detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces for AR tracking."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        tracking_points = []
        for (x, y, w, h) in faces:
            center_x = x + w // 2
            center_y = y + h // 2
            
            tracking_points.append({
                "position": (center_x, center_y),
                "confidence": 0.8,
                "type": "face",
                "bounds": (x, y, w, h)
            })
        
        return tracking_points
    
    def _detect_markers(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect ArUco markers for precise AR tracking."""
        tracking_points = []
        
        try:
            import cv2.aruco as aruco
            corners, ids, _ = aruco.detectMarkers(
                frame, self.aruco_dict, parameters=self.aruco_params
            )
            
            if ids is not None:
                for i, corner in enumerate(corners):
                    # Calculate marker center
                    center = corner[0].mean(axis=0)
                    
                    tracking_points.append({
                        "position": (int(center[0]), int(center[1])),
                        "confidence": 0.95,
                        "type": "marker",
                        "marker_id": ids[i][0],
                        "corners": corner[0]
                    })
        except:
            # Fallback to simple corner detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
            
            if corners is not None:
                for corner in corners:
                    x, y = corner.ravel()
                    tracking_points.append({
                        "position": (int(x), int(y)),
                        "confidence": 0.6,
                        "type": "corner"
                    })
        
        return tracking_points
    
    def _detect_surfaces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect flat surfaces for Pokemon placement."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours that could represent surfaces
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        tracking_points = []
        for contour in contours:
            if cv2.contourArea(contour) > 1000:  # Minimum area threshold
                # Approximate the contour
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) >= 4:  # Potential rectangular surface
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        center_x = int(M["m10"] / M["m00"])
                        center_y = int(M["m01"] / M["m00"])
                        
                        tracking_points.append({
                            "position": (center_x, center_y),
                            "confidence": 0.7,
                            "type": "surface",
                            "contour": approx
                        })
        
        return tracking_points


class PokemonARViewer:
    """Main AR Pokemon viewer application."""
    
    def __init__(self):
        self.camera = None
        self.renderer = AR3DRenderer()
        self.tracker = ARTracker(ARTrackingMode.FACE_TRACKING)
        self.pokemon_database = self._initialize_pokemon_database()
        self.active_pokemon = {}
        self.visualization_config = ARVisualization()
        
        # UI elements
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.ui_elements = {}
        
        # Performance tracking
        self.fps_counter = 0
        self.frame_times = []
        
    def _initialize_pokemon_database(self) -> Dict[str, Dict]:
        """Initialize Pokemon database for AR display."""
        return {
            "Pikachu": {
                "types": ["Electric"],
                "stats": {"hp": 35, "attack": 55, "defense": 40, "sp_attack": 50, "sp_defense": 50, "speed": 90},
                "model_scale": 1.0,
                "default_animation": PokemonARState.IDLE,
                "special_effects": ["electric_sparks", "quick_movement"]
            },
            "Charizard": {
                "types": ["Fire", "Flying"],
                "stats": {"hp": 78, "attack": 84, "defense": 78, "sp_attack": 109, "sp_defense": 85, "speed": 100},
                "model_scale": 1.5,
                "default_animation": PokemonARState.IDLE,
                "special_effects": ["fire_breath", "wing_flaps"]
            },
            "Blastoise": {
                "types": ["Water"],
                "stats": {"hp": 79, "attack": 83, "defense": 100, "sp_attack": 85, "sp_defense": 105, "speed": 78},
                "model_scale": 1.3,
                "default_animation": PokemonARState.IDLE,
                "special_effects": ["water_cannons", "shell_defense"]
            }
        }
    
    def start_ar_session(self):
        """Start the AR Pokemon viewing session."""
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")
        
        print("🎥 AR Pokemon Viewer Started!")
        print("Controls:")
        print("  SPACE - Place Pokemon")
        print("  A - Change animation")
        print("  S - Toggle stats display")
        print("  Q - Quit")
        
        running = True
        
        while running:
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to read camera frame")
                break
            
            start_time = time.time()
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect tracking points
            tracking_points = self.tracker.detect_tracking_points(frame)
            
            # Render Pokemon at tracking points
            if tracking_points and self.active_pokemon:
                frame = self._render_pokemon_on_frame(frame, tracking_points)
            
            # Draw UI elements
            frame = self._draw_ui(frame, tracking_points)
            
            # Show the frame
            cv2.imshow('Pokemon AR Viewer', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                running = False
            elif key == ord(' '):  # Space to place Pokemon
                self._place_random_pokemon(tracking_points)
            elif key == ord('a'):  # Change animation
                self._cycle_pokemon_animations()
            elif key == ord('s'):  # Toggle stats
                self.visualization_config.show_stats = not self.visualization_config.show_stats
            elif key == ord('c'):  # Clear all Pokemon
                self.active_pokemon.clear()
            
            # Calculate FPS
            frame_time = time.time() - start_time
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 30:
                self.frame_times.pop(0)
        
        # Cleanup
        self.camera.release()
        cv2.destroyAllWindows()
    
    def _render_pokemon_on_frame(
        self, 
        frame: np.ndarray, 
        tracking_points: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Render all active Pokemon on the camera frame."""
        
        for pokemon_id, pokemon in self.active_pokemon.items():
            # Update Pokemon position based on tracking
            if tracking_points:
                # Use first tracking point for simplicity
                track_point = tracking_points[0]
                screen_x, screen_y = track_point["position"]
                
                # Convert screen coordinates to world coordinates
                pokemon.position = (
                    (screen_x - frame.shape[1] / 2) / 100,
                    (frame.shape[0] / 2 - screen_y) / 100,
                    0
                )
            
            # Render the Pokemon
            frame = self.renderer.render_pokemon(pokemon, frame)
            
            # Add stat overlay if enabled
            if self.visualization_config.show_stats:
                frame = self._draw_pokemon_stats(frame, pokemon)
            
            # Add type effectiveness chart if enabled
            if self.visualization_config.show_type_chart:
                frame = self._draw_type_chart(frame, pokemon)
        
        return frame
    
    def _draw_ui(self, frame: np.ndarray, tracking_points: List[Dict[str, Any]]) -> np.ndarray:
        """Draw UI elements on the frame."""
        height, width = frame.shape[:2]
        
        # Draw tracking indicators
        for point in tracking_points:
            x, y = point["position"]
            confidence = point["confidence"]
            
            # Draw tracking crosshair
            color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
            cv2.drawMarker(frame, (x, y), color, cv2.MARKER_CROSS, 20, 2)
            
            # Show confidence
            cv2.putText(
                frame, f"{confidence:.2f}", 
                (x + 25, y), self.font, 0.5, color, 1
            )
        
        # Draw FPS counter
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            cv2.putText(
                frame, f"FPS: {fps:.1f}", 
                (10, 30), self.font, 0.7, (255, 255, 255), 2
            )
        
        # Draw active Pokemon count
        cv2.putText(
            frame, f"Pokemon: {len(self.active_pokemon)}", 
            (10, 60), self.font, 0.7, (255, 255, 255), 2
        )
        
        # Draw controls help
        help_text = [
            "SPACE: Place Pokemon",
            "A: Change Animation", 
            "S: Toggle Stats",
            "C: Clear All"
        ]
        
        for i, text in enumerate(help_text):
            cv2.putText(
                frame, text, 
                (width - 200, 30 + i * 25), 
                self.font, 0.4, (200, 200, 200), 1
            )
        
        return frame
    
    def _draw_pokemon_stats(self, frame: np.ndarray, pokemon: ARPokemon) -> np.ndarray:
        """Draw Pokemon stats overlay."""
        # Calculate position for stats display
        screen_x = int(frame.shape[1] / 2 + pokemon.position[0] * 100)
        screen_y = int(frame.shape[0] / 2 - pokemon.position[1] * 100)
        
        # Offset stats display
        stats_x = screen_x + 80
        stats_y = screen_y - 100
        
        # Ensure stats are within frame bounds
        if stats_x + 150 > frame.shape[1]:
            stats_x = screen_x - 150
        if stats_y < 50:
            stats_y = screen_y + 150
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (stats_x - 10, stats_y - 30), 
                     (stats_x + 140, stats_y + 130), (0, 0, 0), -1)
        cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
        
        # Draw Pokemon name and level
        cv2.putText(frame, f"{pokemon.name} Lv.{pokemon.level}", 
                   (stats_x, stats_y), self.font, 0.5, (255, 255, 255), 1)
        
        # Draw types
        type_text = " / ".join(pokemon.types)
        cv2.putText(frame, type_text, 
                   (stats_x, stats_y + 20), self.font, 0.4, (200, 200, 200), 1)
        
        # Draw stats bars
        stat_names = ["HP", "ATK", "DEF", "SpA", "SpD", "SPE"]
        stat_keys = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
        
        for i, (name, key) in enumerate(zip(stat_names, stat_keys)):
            stat_value = pokemon.stats.get(key, 0)
            bar_length = int((stat_value / 150) * 100)  # Scale to 100 pixels max
            
            y_pos = stats_y + 40 + i * 15
            
            # Draw stat name
            cv2.putText(frame, name, (stats_x, y_pos), 
                       self.font, 0.3, (255, 255, 255), 1)
            
            # Draw stat bar background
            cv2.rectangle(frame, (stats_x + 30, y_pos - 8), 
                         (stats_x + 130, y_pos - 2), (50, 50, 50), -1)
            
            # Draw stat bar
            bar_color = self._get_stat_color(stat_value)
            cv2.rectangle(frame, (stats_x + 30, y_pos - 8), 
                         (stats_x + 30 + bar_length, y_pos - 2), bar_color, -1)
            
            # Draw stat value
            cv2.putText(frame, str(stat_value), (stats_x + 135, y_pos), 
                       self.font, 0.3, (255, 255, 255), 1)
        
        return frame
    
    def _get_stat_color(self, stat_value: int) -> Tuple[int, int, int]:
        """Get color for stat bar based on value."""
        if stat_value >= 120:
            return (0, 255, 0)      # Green - Excellent
        elif stat_value >= 100:
            return (0, 255, 255)    # Yellow - Great
        elif stat_value >= 80:
            return (0, 165, 255)    # Orange - Good
        elif stat_value >= 60:
            return (0, 100, 255)    # Red-Orange - Average
        else:
            return (0, 0, 255)      # Red - Poor
    
    def _draw_type_chart(self, frame: np.ndarray, pokemon: ARPokemon) -> np.ndarray:
        """Draw type effectiveness chart."""
        # This would show type matchups in a compact visual format
        # For now, just show types with colors
        screen_x = int(frame.shape[1] / 2 + pokemon.position[0] * 100)
        screen_y = int(frame.shape[0] / 2 - pokemon.position[1] * 100)
        
        type_colors = self.renderer._get_type_colors(pokemon.types)
        
        for i, (ptype, color) in enumerate(zip(pokemon.types, type_colors)):
            # Draw type indicator
            type_x = screen_x - 40 + i * 25
            type_y = screen_y - 60
            
            cv2.circle(frame, (type_x, type_y), 10, color, -1)
            cv2.putText(frame, ptype[:3], (type_x - 15, type_y + 25), 
                       self.font, 0.3, color, 1)
        
        return frame
    
    def _place_random_pokemon(self, tracking_points: List[Dict[str, Any]]):
        """Place a random Pokemon at a tracking point."""
        if not tracking_points:
            return
        
        # Select random Pokemon
        pokemon_name = random.choice(list(self.pokemon_database.keys()))
        pokemon_data = self.pokemon_database[pokemon_name]
        
        # Create AR Pokemon instance
        pokemon_id = f"pokemon_{len(self.active_pokemon)}"
        
        ar_pokemon = ARPokemon(
            name=pokemon_name,
            model_path="",  # Would be actual 3D model path
            texture_path="",  # Would be actual texture path
            position=(0, 0, 0),  # Will be updated by tracking
            rotation=(0, 0, 0),
            scale=pokemon_data["model_scale"],
            animation_state=pokemon_data["default_animation"],
            stats=pokemon_data["stats"],
            types=pokemon_data["types"],
            level=random.randint(1, 100),
            is_shiny=random.random() < 0.05  # 5% shiny chance
        )
        
        self.active_pokemon[pokemon_id] = ar_pokemon
        print(f"🎮 Placed {pokemon_name} (Level {ar_pokemon.level})")
        
        if ar_pokemon.is_shiny:
            print("✨ It's shiny!")
    
    def _cycle_pokemon_animations(self):
        """Cycle through Pokemon animation states."""
        animations = list(PokemonARState)
        
        for pokemon in self.active_pokemon.values():
            current_index = animations.index(pokemon.animation_state)
            next_index = (current_index + 1) % len(animations)
            pokemon.animation_state = animations[next_index]
            print(f"🎬 {pokemon.name} is now {pokemon.animation_state.value}")


# Demo and main execution
def demonstrate_ar_system():
    """Demonstrate the AR Pokemon viewer system."""
    print("🎮 Pokemon AR Viewer Demo")
    print("=" * 50)
    
    try:
        # Create AR viewer instance
        ar_viewer = PokemonARViewer()
        
        # Start AR session
        ar_viewer.start_ar_session()
        
    except Exception as e:
        print(f"❌ Error starting AR system: {e}")
        print("Note: AR features require camera access and OpenCV")
        
        # Show system capabilities instead
        print("\n🔍 AR System Capabilities:")
        print("- Real-time 3D Pokemon rendering")
        print("- Multiple tracking modes (Face, Marker, Surface)")
        print("- Interactive stat overlays")
        print("- Animation state management")
        print("- Type effectiveness visualization")
        print("- Performance optimization")

if __name__ == "__main__":
    import random  # Add this import for the random functionality
    demonstrate_ar_system()