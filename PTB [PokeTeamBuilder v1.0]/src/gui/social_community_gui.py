"""
Social Community Hub GUI
Complete interface for social features with login, user profiles, friends,
team sharing, battle replays, tournaments, and community posts.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import Optional, Dict, List, Any
import logging
import os
from datetime import datetime
import hashlib

from src.gui.theme_manager import ThemeManager
from src.features.social_community_hub import (
    CommunityManager, User, UserStatus, PostType, 
    FriendshipStatus, TournamentStatus
)

logger = logging.getLogger(__name__)


class LoginDialog(tk.Toplevel):
    """Login/Registration dialog."""
    
    def __init__(self, parent, community_manager: CommunityManager):
        super().__init__(parent)
        self.community_manager = community_manager
        self.logged_in_user = None
        
        self.title("Pokemon Community Hub - Login")
        self.geometry("450x550")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create login dialog widgets."""
        # Header
        header = tk.Frame(self, bg="#2C3E50", height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="🌟 Pokemon Community Hub",
            font=("Arial", 18, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        title.pack(pady=20)
        
        # Notebook for Login/Register tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Login tab
        self.login_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.login_frame, text="Login")
        self._create_login_tab()
        
        # Register tab
        self.register_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.register_frame, text="Register")
        self._create_register_tab()
    
    def _create_login_tab(self):
        """Create login tab content."""
        container = tk.Frame(self.login_frame, bg="white")
        container.pack(expand=True, pady=30)
        
        # Username
        tk.Label(
            container,
            text="Username or Email:",
            font=("Arial", 11),
            bg="white"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.login_username_var = tk.StringVar()
        self.login_username_entry = tk.Entry(
            container,
            textvariable=self.login_username_var,
            font=("Arial", 11),
            width=30
        )
        self.login_username_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Password
        tk.Label(
            container,
            text="Password:",
            font=("Arial", 11),
            bg="white"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.login_password_var = tk.StringVar()
        self.login_password_entry = tk.Entry(
            container,
            textvariable=self.login_password_var,
            font=("Arial", 11),
            width=30,
            show="●"
        )
        self.login_password_entry.grid(row=3, column=0, pady=(0, 20))
        
        # Login button
        login_btn = tk.Button(
            container,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=25,
            command=self._handle_login
        )
        login_btn.grid(row=4, column=0, pady=10)
        
        # Demo login info
        info_text = "Demo Account:\nUsername: demo_user\nPassword: demo123"
        tk.Label(
            container,
            text=info_text,
            font=("Arial", 9),
            bg="white",
            fg="gray",
            justify=tk.LEFT
        ).grid(row=5, column=0, pady=20)
    
    def _create_register_tab(self):
        """Create registration tab content."""
        container = tk.Frame(self.register_frame, bg="white")
        container.pack(expand=True, pady=20)
        
        # Username
        tk.Label(container, text="Username:", font=("Arial", 10), bg="white").grid(
            row=0, column=0, sticky=tk.W, pady=3
        )
        self.reg_username_var = tk.StringVar()
        self.reg_username_var.trace('w', self._check_username_availability)
        username_entry = tk.Entry(container, textvariable=self.reg_username_var, width=30)
        username_entry.grid(row=0, column=1, pady=3)
        
        # Username validation label
        self.username_status_label = tk.Label(
            container, text="", font=("Arial", 8), bg="white"
        )
        self.username_status_label.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        # Email
        tk.Label(container, text="Email:", font=("Arial", 10), bg="white").grid(
            row=2, column=0, sticky=tk.W, pady=3
        )
        self.reg_email_var = tk.StringVar()
        self.reg_email_var.trace('w', self._check_email_availability)
        email_entry = tk.Entry(container, textvariable=self.reg_email_var, width=30)
        email_entry.grid(row=2, column=1, pady=3)
        
        # Email validation label
        self.email_status_label = tk.Label(
            container, text="", font=("Arial", 8), bg="white"
        )
        self.email_status_label.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        # Display Name
        tk.Label(container, text="Display Name:", font=("Arial", 10), bg="white").grid(
            row=4, column=0, sticky=tk.W, pady=3
        )
        self.reg_display_var = tk.StringVar()
        tk.Entry(container, textvariable=self.reg_display_var, width=30).grid(
            row=4, column=1, pady=3
        )
        
        # Password
        tk.Label(container, text="Password:", font=("Arial", 10), bg="white").grid(
            row=5, column=0, sticky=tk.W, pady=3
        )
        self.reg_password_var = tk.StringVar()
        tk.Entry(container, textvariable=self.reg_password_var, width=30, show="●").grid(
            row=5, column=1, pady=3
        )
        
        # Password strength indicator
        self.password_strength_label = tk.Label(
            container, text="", font=("Arial", 8), bg="white"
        )
        self.password_strength_label.grid(row=6, column=1, sticky=tk.W, pady=(0, 5))
        self.reg_password_var.trace('w', self._check_password_strength)
        
        # Confirm Password
        tk.Label(container, text="Confirm Password:", font=("Arial", 10), bg="white").grid(
            row=7, column=0, sticky=tk.W, pady=3
        )
        self.reg_confirm_var = tk.StringVar()
        tk.Entry(container, textvariable=self.reg_confirm_var, width=30, show="●").grid(
            row=7, column=1, pady=3
        )
        
        # Bio
        tk.Label(container, text="Bio (optional):", font=("Arial", 10), bg="white").grid(
            row=8, column=0, sticky=tk.NW, pady=3
        )
        self.reg_bio_text = tk.Text(container, width=30, height=3, font=("Arial", 9))
        self.reg_bio_text.grid(row=8, column=1, pady=3)
        
        # Username requirements
        requirements = tk.Label(
            container,
            text="Username: 3-20 characters, letters, numbers, underscores only",
            font=("Arial", 8),
            bg="white",
            fg="gray"
        )
        requirements.grid(row=9, column=0, columnspan=2, pady=(10, 5))
        
        # Register button
        self.register_btn = tk.Button(
            container,
            text="Create Account",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=self._handle_register,
            state=tk.DISABLED
        )
        self.register_btn.grid(row=10, column=0, columnspan=2, pady=20)
    
    def _check_username_availability(self, *args):
        """Check if username is available."""
        username = self.reg_username_var.get().strip()
        
        if len(username) < 3:
            self.username_status_label.config(text="", fg="gray")
            self.register_btn.config(state=tk.DISABLED)
            return
        
        # Check format
        import re
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            self.username_status_label.config(
                text="✗ Invalid format (letters, numbers, underscores only)",
                fg="#e74c3c"
            )
            self.register_btn.config(state=tk.DISABLED)
            return
        
        # Check availability
        if self.community_manager.is_username_available(username):
            self.username_status_label.config(
                text="✓ Username available",
                fg="#27ae60"
            )
            self._update_register_button()
        else:
            self.username_status_label.config(
                text="✗ Username already taken",
                fg="#e74c3c"
            )
            self.register_btn.config(state=tk.DISABLED)
    
    def _check_email_availability(self, *args):
        """Check if email is available."""
        email = self.reg_email_var.get().strip()
        
        if len(email) < 3 or "@" not in email:
            self.email_status_label.config(text="", fg="gray")
            self.register_btn.config(state=tk.DISABLED)
            return
        
        # Check availability
        if self.community_manager.is_email_available(email):
            self.email_status_label.config(
                text="✓ Email available",
                fg="#27ae60"
            )
            self._update_register_button()
        else:
            self.email_status_label.config(
                text="✗ Email already registered",
                fg="#e74c3c"
            )
            self.register_btn.config(state=tk.DISABLED)
    
    def _check_password_strength(self, *args):
        """Check password strength."""
        password = self.reg_password_var.get()
        
        if len(password) == 0:
            self.password_strength_label.config(text="", fg="gray")
            return
        
        strength = 0
        feedback = []
        
        if len(password) >= 8:
            strength += 1
        else:
            feedback.append("8+ characters")
        
        if any(c.isupper() for c in password):
            strength += 1
        else:
            feedback.append("uppercase")
        
        if any(c.islower() for c in password):
            strength += 1
        else:
            feedback.append("lowercase")
        
        if any(c.isdigit() for c in password):
            strength += 1
        else:
            feedback.append("number")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            strength += 1
        
        if strength <= 1:
            self.password_strength_label.config(
                text=f"Weak - Add: {', '.join(feedback)}",
                fg="#e74c3c"
            )
        elif strength <= 3:
            self.password_strength_label.config(
                text=f"Medium - Add: {', '.join(feedback)}" if feedback else "Medium strength",
                fg="#f39c12"
            )
        else:
            self.password_strength_label.config(
                text="✓ Strong password",
                fg="#27ae60"
            )
    
    def _update_register_button(self):
        """Update register button state based on all validations."""
        username = self.reg_username_var.get().strip()
        email = self.reg_email_var.get().strip()
        
        if (len(username) >= 3 and 
            self.community_manager.is_username_available(username) and
            "@" in email and 
            self.community_manager.is_email_available(email)):
            self.register_btn.config(state=tk.NORMAL)
        else:
            self.register_btn.config(state=tk.DISABLED)
    
    def _handle_login(self):
        """Handle login attempt."""
        username = self.login_username_var.get().strip()
        password = self.login_password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        # Try to authenticate
        user = self.community_manager.authenticate_user(username, password)
        
        if user:
            self.logged_in_user = user
            self.community_manager.update_user_status(user.user_id, UserStatus.ONLINE)
            messagebox.showinfo("Success", f"Welcome back, {user.display_name}!")
            self.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def _handle_register(self):
        """Handle user registration."""
        username = self.reg_username_var.get().strip()
        email = self.reg_email_var.get().strip()
        display_name = self.reg_display_var.get().strip()
        password = self.reg_password_var.get()
        confirm = self.reg_confirm_var.get()
        bio = self.reg_bio_text.get("1.0", tk.END).strip()
        
        # Validation
        if not all([username, email, display_name, password]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Check username availability one more time
        if not self.community_manager.is_username_available(username):
            messagebox.showerror("Error", "Username is no longer available")
            return
        
        # Check email availability
        if not self.community_manager.is_email_available(email):
            messagebox.showerror("Error", "Email is already registered")
            return
        
        # Try to register
        user_id = self.community_manager.register_user(
            username, email, display_name, password, bio or "Pokemon Trainer"
        )
        
        if user_id:
            # Check if verification email was sent
            verification_file = os.path.join("logs", "email_verifications.txt")
            email_sent_msg = ""
            
            if os.path.exists(verification_file):
                email_sent_msg = (
                    "\n\n📧 A verification email has been sent to your email address.\n"
                    "Please check your email and click the verification link to activate your account.\n\n"
                    "Note: In demo mode, verification links are saved to:\n"
                    f"{verification_file}\n\n"
                    "You can login now, but some features may require email verification."
                )
            
            messagebox.showinfo(
                "Success", 
                f"Account created successfully!\n\n"
                f"Username: {username}\n"
                f"Display Name: {display_name}\n"
                f"{email_sent_msg}\n"
                f"You can now login with your credentials."
            )
            # Switch to login tab
            self.notebook.select(0)
            self.login_username_var.set(username)
        else:
            messagebox.showerror(
                "Error", 
                "Registration failed. Username or email may already be in use, "
                "or there was a validation error."
            )


class SocialCommunityFrame(tk.Frame):
    """Main Social Community Hub interface."""
    
    def __init__(self, parent, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.community_manager = CommunityManager()
        self.current_user = None
        
        self._show_login()
    
    def _show_login(self):
        """Show login dialog."""
        login_dialog = LoginDialog(self, self.community_manager)
        self.wait_window(login_dialog)
        
        if login_dialog.logged_in_user:
            self.current_user = login_dialog.logged_in_user
            self._create_main_interface()
        else:
            # User cancelled login - show placeholder
            self._create_logged_out_interface()
    
    def _create_logged_out_interface(self):
        """Create interface when not logged in."""
        container = tk.Frame(self, bg="white")
        container.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(
            container,
            text="🌟 Pokemon Community Hub",
            font=("Arial", 20, "bold"),
            bg="white"
        ).pack(pady=30)
        
        tk.Label(
            container,
            text="Please login to access community features",
            font=("Arial", 12),
            bg="white",
            fg="gray"
        ).pack(pady=10)
        
        login_btn = tk.Button(
            container,
            text="Login / Register",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            command=self._reshow_login
        )
        login_btn.pack(pady=20)
    
    def _reshow_login(self):
        """Re-show login dialog."""
        for widget in self.winfo_children():
            widget.destroy()
        self._show_login()
    
    def _create_main_interface(self):
        """Create main community interface."""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header with user info
        self._create_header()
        
        # Main content area with tabs
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self._create_profile_tab()
        self._create_friends_tab()
        self._create_teams_tab()
        self._create_replays_tab()
        self._create_tournaments_tab()
        self._create_community_tab()
        self._create_leaderboards_tab()
    
    def _create_header(self):
        """Create header with user info."""
        header = tk.Frame(self, bg="#34495e", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # User info on left
        user_frame = tk.Frame(header, bg="#34495e")
        user_frame.pack(side=tk.LEFT, padx=15, pady=10)
        
        tk.Label(
            user_frame,
            text=f"👤 {self.current_user.display_name}",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(side=tk.LEFT)
        
        tk.Label(
            user_frame,
            text=f"Level {self.current_user.level}",
            font=("Arial", 9),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack(side=tk.LEFT, padx=10)
        
        # Logout button on right
        logout_btn = tk.Button(
            header,
            text="Logout",
            font=("Arial", 9),
            bg="#e74c3c",
            fg="white",
            command=self._handle_logout
        )
        logout_btn.pack(side=tk.RIGHT, padx=15, pady=15)
        
        # Status indicator
        status_colors = {
            UserStatus.ONLINE: "#27ae60",
            UserStatus.AWAY: "#f39c12",
            UserStatus.BUSY: "#e74c3c",
            UserStatus.OFFLINE: "#95a5a6"
        }
        
        status_label = tk.Label(
            header,
            text=f"● {self.current_user.status.value.title()}",
            font=("Arial", 9),
            bg="#34495e",
            fg=status_colors.get(self.current_user.status, "white")
        )
        status_label.pack(side=tk.RIGHT, padx=5)
    
    def _handle_logout(self):
        """Handle user logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            if self.current_user:
                self.community_manager.update_user_status(
                    self.current_user.user_id, 
                    UserStatus.OFFLINE
                )
            self.current_user = None
            
            # Clear and show login
            for widget in self.winfo_children():
                widget.destroy()
            self._show_login()
    
    def _create_profile_tab(self):
        """Create user profile tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="👤 My Profile")
        
        # Scrollable content
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Profile content
        profile_container = tk.Frame(scrollable_frame, bg="white")
        profile_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Avatar section
        avatar_frame = tk.Frame(profile_container, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        avatar_frame.pack(pady=10)
        
        tk.Label(
            avatar_frame,
            text="👤",
            font=("Arial", 48),
            bg="#ecf0f1"
        ).pack(padx=40, pady=40)
        
        # User info
        tk.Label(
            profile_container,
            text=self.current_user.display_name,
            font=("Arial", 20, "bold"),
            bg="white"
        ).pack(pady=5)
        
        tk.Label(
            profile_container,
            text=f"@{self.current_user.username}",
            font=("Arial", 11),
            bg="white",
            fg="gray"
        ).pack()
        
        tk.Label(
            profile_container,
            text=f"📧 {self.current_user.email}",
            font=("Arial", 10),
            bg="white",
            fg="gray"
        ).pack(pady=5)
        
        # Bio
        bio_frame = tk.LabelFrame(
            profile_container,
            text="Bio",
            font=("Arial", 11, "bold"),
            bg="white"
        )
        bio_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            bio_frame,
            text=self.current_user.bio,
            font=("Arial", 10),
            bg="white",
            wraplength=400,
            justify=tk.LEFT
        ).pack(padx=10, pady=10)
        
        # Stats
        stats_frame = tk.LabelFrame(
            profile_container,
            text="Statistics",
            font=("Arial", 11, "bold"),
            bg="white"
        )
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats_grid = tk.Frame(stats_frame, bg="white")
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        stats = [
            ("Level", self.current_user.level),
            ("Experience", self.current_user.experience),
            ("Badges", len(self.current_user.badges)),
            ("Achievements", len(self.current_user.achievements)),
        ]
        
        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(stats_grid, bg="#ecf0f1", relief=tk.RIDGE, bd=1)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            tk.Label(
                stat_frame,
                text=str(value),
                font=("Arial", 18, "bold"),
                bg="#ecf0f1"
            ).pack()
            
            tk.Label(
                stat_frame,
                text=label,
                font=("Arial", 9),
                bg="#ecf0f1",
                fg="gray"
            ).pack()
        
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        
        # Badges
        if self.current_user.badges:
            badges_frame = tk.LabelFrame(
                profile_container,
                text="Badges",
                font=("Arial", 11, "bold"),
                bg="white"
            )
            badges_frame.pack(fill=tk.X, pady=10)
            
            badges_text = ", ".join(self.current_user.badges)
            tk.Label(
                badges_frame,
                text=badges_text,
                font=("Arial", 10),
                bg="white",
                wraplength=400
            ).pack(padx=10, pady=10)
    
    def _create_friends_tab(self):
        """Create friends management tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="👥 Friends")
        
        # Friend search
        search_frame = tk.Frame(tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="Find Friends:", font=("Arial", 10, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        
        self.friend_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.friend_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(
            search_frame,
            text="Search",
            bg="#3498db",
            fg="white",
            command=self._search_friends
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Friends list
        list_frame = tk.LabelFrame(tab, text="My Friends", font=("Arial", 10, "bold"))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable friends list
        friends_canvas = tk.Canvas(list_frame)
        friends_scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=friends_canvas.yview
        )
        self.friends_container = tk.Frame(friends_canvas)
        
        self.friends_container.bind(
            "<Configure>",
            lambda e: friends_canvas.configure(scrollregion=friends_canvas.bbox("all"))
        )
        
        friends_canvas.create_window((0, 0), window=self.friends_container, anchor="nw")
        friends_canvas.configure(yscrollcommand=friends_scrollbar.set)
        
        friends_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        friends_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load friends
        self._load_friends()
    
    def _load_friends(self):
        """Load and display friends list."""
        # Clear existing
        for widget in self.friends_container.winfo_children():
            widget.destroy()
        
        friends = self.community_manager.get_friends(self.current_user.user_id)
        
        if not friends:
            tk.Label(
                self.friends_container,
                text="No friends yet. Use the search to find people!",
                font=("Arial", 10),
                fg="gray"
            ).pack(pady=20)
            return
        
        for friendship in friends:
            # Get friend user info
            friend_id = (
                friendship.recipient_id 
                if friendship.requester_id == self.current_user.user_id 
                else friendship.requester_id
            )
            friend = self.community_manager.get_user(friend_id)
            
            if not friend:
                continue
            
            friend_frame = tk.Frame(
                self.friends_container,
                bg="#ecf0f1",
                relief=tk.RIDGE,
                bd=1
            )
            friend_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Friend info
            info_frame = tk.Frame(friend_frame, bg="#ecf0f1")
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
            
            tk.Label(
                info_frame,
                text=f"👤 {friend.display_name}",
                font=("Arial", 11, "bold"),
                bg="#ecf0f1"
            ).pack(anchor=tk.W)
            
            tk.Label(
                info_frame,
                text=f"@{friend.username} | Level {friend.level}",
                font=("Arial", 9),
                bg="#ecf0f1",
                fg="gray"
            ).pack(anchor=tk.W)
            
            # Status indicator
            status_colors = {
                UserStatus.ONLINE: "#27ae60",
                UserStatus.AWAY: "#f39c12",
                UserStatus.BUSY: "#e74c3c",
                UserStatus.OFFLINE: "#95a5a6"
            }
            
            tk.Label(
                info_frame,
                text=f"● {friend.status.value}",
                font=("Arial", 8),
                bg="#ecf0f1",
                fg=status_colors.get(friend.status, "gray")
            ).pack(anchor=tk.W)
            
            # Action buttons
            btn_frame = tk.Frame(friend_frame, bg="#ecf0f1")
            btn_frame.pack(side=tk.RIGHT, padx=5)
            
            tk.Button(
                btn_frame,
                text="Profile",
                font=("Arial", 8),
                bg="#3498db",
                fg="white",
                command=lambda f=friend: self._view_friend_profile(f)
            ).pack(side=tk.LEFT, padx=2)
            
            tk.Button(
                btn_frame,
                text="Remove",
                font=("Arial", 8),
                bg="#e74c3c",
                fg="white",
                command=lambda fid=friendship.friendship_id: self._remove_friend(fid)
            ).pack(side=tk.LEFT, padx=2)
    
    def _search_friends(self):
        """Search for users to add as friends."""
        search_term = self.friend_search_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a username to search")
            return
        
        # Search for user
        user = self.community_manager.search_users(search_term)
        
        if not user:
            messagebox.showinfo("Not Found", f"No user found with username '{search_term}'")
            return
        
        if user.user_id == self.current_user.user_id:
            messagebox.showinfo("Info", "You cannot add yourself as a friend!")
            return
        
        # Check if already friends
        friends = self.community_manager.get_friends(self.current_user.user_id)
        is_friend = any(
            f.requester_id == user.user_id or f.recipient_id == user.user_id
            for f in friends
        )
        
        if is_friend:
            messagebox.showinfo("Info", f"You are already friends with {user.display_name}")
            return
        
        # Send friend request
        if messagebox.askyesno(
            "Add Friend",
            f"Send friend request to {user.display_name} (@{user.username})?"
        ):
            success = self.community_manager.send_friend_request(
                self.current_user.user_id,
                user.username
            )
            
            if success:
                messagebox.showinfo("Success", "Friend request sent!")
            else:
                messagebox.showerror("Error", "Failed to send friend request")
    
    def _view_friend_profile(self, friend: User):
        """View friend's profile in a dialog."""
        dialog = tk.Toplevel(self)
        dialog.title(f"Profile - {friend.display_name}")
        dialog.geometry("400x500")
        
        # Profile content
        tk.Label(
            dialog,
            text=friend.display_name,
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        tk.Label(
            dialog,
            text=f"@{friend.username}",
            font=("Arial", 11),
            fg="gray"
        ).pack()
        
        tk.Label(
            dialog,
            text=f"Level {friend.level} | {friend.experience} XP",
            font=("Arial", 10)
        ).pack(pady=5)
        
        bio_frame = tk.LabelFrame(dialog, text="Bio", font=("Arial", 10, "bold"))
        bio_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            bio_frame,
            text=friend.bio,
            font=("Arial", 9),
            wraplength=350,
            justify=tk.LEFT
        ).pack(padx=10, pady=10)
        
        if friend.badges:
            badges_frame = tk.LabelFrame(dialog, text="Badges", font=("Arial", 10, "bold"))
            badges_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(
                badges_frame,
                text=", ".join(friend.badges),
                font=("Arial", 9),
                wraplength=350
            ).pack(padx=10, pady=10)
    
    def _remove_friend(self, friendship_id: str):
        """Remove a friend."""
        if messagebox.askyesno("Remove Friend", "Are you sure you want to remove this friend?"):
            # Implementation would call community_manager to remove friendship
            messagebox.showinfo("Info", "Friend removal not fully implemented yet")
    
    def _create_teams_tab(self):
        """Create team sharing tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="📋 Teams")
        
        tk.Label(
            tab,
            text="Team Sharing - Browse and share competitive teams",
            font=("Arial", 12, "bold")
        ).pack(pady=20)
        
        # Share team button
        share_btn = tk.Button(
            tab,
            text="Share My Team",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=self._share_team_dialog
        )
        share_btn.pack(pady=10)
        
        # Popular teams list
        teams_frame = tk.LabelFrame(tab, text="Popular Teams", font=("Arial", 10, "bold"))
        teams_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load popular teams
        popular_teams = self.community_manager.get_popular_teams(limit=10)
        
        if not popular_teams:
            tk.Label(
                teams_frame,
                text="No teams shared yet. Be the first!",
                font=("Arial", 10),
                fg="gray"
            ).pack(pady=20)
        else:
            for team in popular_teams:
                team_item = tk.Frame(teams_frame, bg="#ecf0f1", relief=tk.RIDGE, bd=1)
                team_item.pack(fill=tk.X, padx=5, pady=3)
                
                tk.Label(
                    team_item,
                    text=f"📋 {team.title}",
                    font=("Arial", 11, "bold"),
                    bg="#ecf0f1"
                ).pack(anchor=tk.W, padx=10, pady=5)
                
                tk.Label(
                    team_item,
                    text=f"{team.description[:100]}...",
                    font=("Arial", 9),
                    bg="#ecf0f1",
                    fg="gray"
                ).pack(anchor=tk.W, padx=10)
                
                stats_text = f"⭐ {team.rating:.1f} | 👍 {team.votes} | ⬇ {team.downloads} downloads"
                tk.Label(
                    team_item,
                    text=stats_text,
                    font=("Arial", 8),
                    bg="#ecf0f1"
                ).pack(anchor=tk.W, padx=10, pady=5)
    
    def _share_team_dialog(self):
        """Show dialog to share a team."""
        messagebox.showinfo(
            "Share Team",
            "Team sharing interface would allow you to:\n\n"
            "• Select a team from your saved teams\n"
            "• Add title and description\n"
            "• Choose tags and format\n"
            "• Set visibility (public/private)\n"
            "• Upload team to community"
        )
    
    def _create_replays_tab(self):
        """Create battle replays tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="🎬 Replays")
        
        tk.Label(
            tab,
            text="Battle Replays - Watch and share epic battles",
            font=("Arial", 12, "bold")
        ).pack(pady=20)
        
        tk.Label(
            tab,
            text="Battle replay system coming soon!",
            font=("Arial", 10),
            fg="gray"
        ).pack(pady=10)
    
    def _create_tournaments_tab(self):
        """Create tournaments tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="🏆 Tournaments")
        
        tk.Label(
            tab,
            text="Tournaments - Compete in community events",
            font=("Arial", 12, "bold")
        ).pack(pady=20)
        
        # Tournament list
        tournaments = self.community_manager.get_tournaments()
        
        if not tournaments:
            tk.Label(
                tab,
                text="No active tournaments. Check back later!",
                font=("Arial", 10),
                fg="gray"
            ).pack(pady=10)
        else:
            for tournament in tournaments[:5]:
                tour_frame = tk.Frame(tab, bg="#ecf0f1", relief=tk.RIDGE, bd=2)
                tour_frame.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(
                    tour_frame,
                    text=f"🏆 {tournament.name}",
                    font=("Arial", 12, "bold"),
                    bg="#ecf0f1"
                ).pack(anchor=tk.W, padx=10, pady=5)
                
                tk.Label(
                    tour_frame,
                    text=tournament.description,
                    font=("Arial", 9),
                    bg="#ecf0f1",
                    wraplength=400
                ).pack(anchor=tk.W, padx=10)
                
                info_text = (
                    f"Format: {tournament.format} | "
                    f"Participants: {len(tournament.participants)}/{tournament.max_participants} | "
                    f"Status: {tournament.status.value}"
                )
                tk.Label(
                    tour_frame,
                    text=info_text,
                    font=("Arial", 8),
                    bg="#ecf0f1",
                    fg="gray"
                ).pack(anchor=tk.W, padx=10, pady=5)
    
    def _create_community_tab(self):
        """Create community posts tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="💬 Community")
        
        # Post creation
        create_frame = tk.Frame(tab)
        create_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            create_frame,
            text="+ Create Post",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=self._create_post_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        # Community feed
        feed_frame = tk.LabelFrame(tab, text="Community Feed", font=("Arial", 10, "bold"))
        feed_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Load community posts
        posts = self.community_manager.get_community_feed(limit=20)
        
        if not posts:
            tk.Label(
                feed_frame,
                text="No posts yet. Be the first to post!",
                font=("Arial", 10),
                fg="gray"
            ).pack(pady=20)
        else:
            for post in posts:
                post_frame = tk.Frame(feed_frame, bg="white", relief=tk.RIDGE, bd=1)
                post_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Post header
                header_frame = tk.Frame(post_frame, bg="#f8f9fa")
                header_frame.pack(fill=tk.X)
                
                tk.Label(
                    header_frame,
                    text=f"📝 {post.title}",
                    font=("Arial", 11, "bold"),
                    bg="#f8f9fa"
                ).pack(anchor=tk.W, padx=10, pady=5)
                
                tk.Label(
                    header_frame,
                    text=f"by {post.user_id} | {post.post_type.value}",
                    font=("Arial", 8),
                    bg="#f8f9fa",
                    fg="gray"
                ).pack(anchor=tk.W, padx=10)
                
                # Post content
                tk.Label(
                    post_frame,
                    text=post.content[:200] + ("..." if len(post.content) > 200 else ""),
                    font=("Arial", 9),
                    bg="white",
                    wraplength=500,
                    justify=tk.LEFT
                ).pack(anchor=tk.W, padx=10, pady=10)
                
                # Post stats
                stats_text = f"👍 {post.likes} | 💬 {len(post.comments)} | 👁 {post.views} views"
                tk.Label(
                    post_frame,
                    text=stats_text,
                    font=("Arial", 8),
                    bg="white",
                    fg="gray"
                ).pack(anchor=tk.W, padx=10, pady=5)
    
    def _create_post_dialog(self):
        """Show dialog to create a community post."""
        dialog = tk.Toplevel(self)
        dialog.title("Create Community Post")
        dialog.geometry("500x450")
        
        # Post type
        tk.Label(dialog, text="Post Type:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W, padx=20, pady=(20, 5)
        )
        
        post_type_var = tk.StringVar(value="discussion")
        type_frame = tk.Frame(dialog)
        type_frame.pack(anchor=tk.W, padx=20, pady=5)
        
        for ptype in [PostType.DISCUSSION, PostType.GUIDE, PostType.TEAM_SHARE]:
            tk.Radiobutton(
                type_frame,
                text=ptype.value.replace("_", " ").title(),
                variable=post_type_var,
                value=ptype.value
            ).pack(side=tk.LEFT, padx=5)
        
        # Title
        tk.Label(dialog, text="Title:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W, padx=20, pady=(10, 5)
        )
        title_var = tk.StringVar()
        tk.Entry(dialog, textvariable=title_var, width=50).pack(padx=20, pady=5)
        
        # Content
        tk.Label(dialog, text="Content:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W, padx=20, pady=(10, 5)
        )
        content_text = scrolledtext.ScrolledText(dialog, width=50, height=10)
        content_text.pack(padx=20, pady=5)
        
        # Tags
        tk.Label(dialog, text="Tags (comma-separated):", font=("Arial", 10, "bold")).pack(
            anchor=tk.W, padx=20, pady=(10, 5)
        )
        tags_var = tk.StringVar()
        tk.Entry(dialog, textvariable=tags_var, width=50).pack(padx=20, pady=5)
        
        def submit_post():
            title = title_var.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            tags = [t.strip() for t in tags_var.get().split(",") if t.strip()]
            ptype = PostType(post_type_var.get())
            
            if not title or not content:
                messagebox.showerror("Error", "Please fill in title and content")
                return
            
            post_id = self.community_manager.create_post(
                self.current_user.user_id,
                ptype,
                title,
                content,
                tags
            )
            
            if post_id:
                messagebox.showinfo("Success", "Post created successfully!")
                dialog.destroy()
                # Refresh community tab
            else:
                messagebox.showerror("Error", "Failed to create post")
        
        tk.Button(
            dialog,
            text="Post",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=submit_post
        ).pack(pady=20)
    
    def _create_leaderboards_tab(self):
        """Create leaderboards tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="🏅 Leaderboards")
        
        # Category selector
        cat_frame = tk.Frame(tab)
        cat_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(cat_frame, text="Category:", font=("Arial", 10, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        
        self.leaderboard_cat_var = tk.StringVar(value="ranked_battles")
        categories = ["ranked_battles", "team_shares", "tournaments_won", "community_rep"]
        
        cat_combo = ttk.Combobox(
            cat_frame,
            textvariable=self.leaderboard_cat_var,
            values=categories,
            state="readonly",
            width=20
        )
        cat_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            cat_frame,
            text="Refresh",
            bg="#3498db",
            fg="white",
            command=self._load_leaderboard
        ).pack(side=tk.LEFT, padx=5)
        
        # Leaderboard display
        self.leaderboard_frame = tk.Frame(tab)
        self.leaderboard_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self._load_leaderboard()
    
    def _load_leaderboard(self):
        """Load and display leaderboard."""
        # Clear existing
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()
        
        category = self.leaderboard_cat_var.get()
        entries = self.community_manager.get_leaderboard(category, limit=20)
        
        if not entries:
            tk.Label(
                self.leaderboard_frame,
                text="No leaderboard data available",
                font=("Arial", 10),
                fg="gray"
            ).pack(pady=20)
            return
        
        # Header
        header = tk.Frame(self.leaderboard_frame, bg="#34495e")
        header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            header,
            text=f"🏅 {category.replace('_', ' ').title()} Leaderboard",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(pady=10)
        
        # Entries
        for entry in entries:
            rank_color = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}.get(entry.rank, "#ecf0f1")
            
            entry_frame = tk.Frame(
                self.leaderboard_frame,
                bg=rank_color,
                relief=tk.RIDGE,
                bd=1
            )
            entry_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Rank
            tk.Label(
                entry_frame,
                text=f"#{entry.rank}",
                font=("Arial", 14, "bold"),
                bg=rank_color,
                width=5
            ).pack(side=tk.LEFT, padx=10)
            
            # User info
            info_frame = tk.Frame(entry_frame, bg=rank_color)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
            
            tk.Label(
                info_frame,
                text=entry.username,
                font=("Arial", 11, "bold"),
                bg=rank_color
            ).pack(anchor=tk.W)
            
            tk.Label(
                info_frame,
                text=f"Score: {entry.score:.1f}",
                font=("Arial", 9),
                bg=rank_color,
                fg="gray"
            ).pack(anchor=tk.W)
            
            # Trend indicator
            trend_symbols = {"up": "📈", "down": "📉", "same": "➡"}
            tk.Label(
                entry_frame,
                text=trend_symbols.get(entry.trend, ""),
                font=("Arial", 14),
                bg=rank_color
            ).pack(side=tk.RIGHT, padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pokemon Community Hub - Demo")
    root.geometry("900x700")
    
    app = SocialCommunityFrame(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
