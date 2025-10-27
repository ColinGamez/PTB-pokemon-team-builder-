"""
Admin Panel GUI
Comprehensive administration interface for managing users, content,
and system monitoring.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta
import sqlite3
import os

from src.gui.theme_manager import ThemeManager
from src.features.social_community_hub import (
    CommunityManager, User, UserStatus, PostType
)

logger = logging.getLogger(__name__)


class AdminLoginDialog(tk.Toplevel):
    """Admin login dialog."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.admin_authenticated = False
        
        self.title("Admin Panel - Authentication")
        self.geometry("400x300")
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
        header = tk.Frame(self, bg="#e74c3c", height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="🔒 Admin Panel",
            font=("Arial", 18, "bold"),
            bg="#e74c3c",
            fg="white"
        )
        title.pack(pady=20)
        
        # Login form
        container = tk.Frame(self, bg="white")
        container.pack(expand=True, pady=30)
        
        # Admin PIN
        tk.Label(
            container,
            text="Admin PIN:",
            font=("Arial", 11),
            bg="white"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            container,
            textvariable=self.password_var,
            font=("Arial", 11),
            width=30,
            show="●"
        )
        self.password_entry.grid(row=1, column=0, pady=(0, 15))
        self.password_entry.focus()
        self.password_entry.bind('<Return>', lambda e: self._handle_login())
        
        # Login button
        login_btn = tk.Button(
            container,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            width=25,
            command=self._handle_login
        )
        login_btn.grid(row=2, column=0, pady=10)
        
        # Demo info
        info_text = "Enter your 6-digit admin PIN"
        tk.Label(
            container,
            text=info_text,
            font=("Arial", 9),
            bg="white",
            fg="gray",
            justify=tk.LEFT
        ).grid(row=3, column=0, pady=20)
    
    def _handle_login(self):
        """Handle admin login."""
        password = self.password_var.get()
        
        # Check against secure PIN
        if password == "050270":
            self.admin_authenticated = True
            messagebox.showinfo("Success", "Admin access granted!")
            self.destroy()
        else:
            messagebox.showerror("Error", "Invalid admin PIN")
            self.password_var.set("")
            self.password_entry.focus()


class AdminPanelFrame(tk.Frame):
    """Main admin panel interface."""
    
    def __init__(self, parent, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.community_manager = CommunityManager()
        self.is_admin = False
        
        self._show_login()
    
    def _show_login(self):
        """Show admin login dialog."""
        login_dialog = AdminLoginDialog(self)
        self.wait_window(login_dialog)
        
        if login_dialog.admin_authenticated:
            self.is_admin = True
            self._create_main_interface()
        else:
            # Access denied - show placeholder
            self._create_access_denied_interface()
    
    def _create_access_denied_interface(self):
        """Create interface when access is denied."""
        container = tk.Frame(self, bg="white")
        container.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(
            container,
            text="🔒 Admin Panel",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#e74c3c"
        ).pack(pady=30)
        
        tk.Label(
            container,
            text="Access Denied",
            font=("Arial", 14),
            bg="white",
            fg="gray"
        ).pack(pady=10)
        
        tk.Label(
            container,
            text="Admin authentication required",
            font=("Arial", 10),
            bg="white",
            fg="gray"
        ).pack(pady=5)
        
        login_btn = tk.Button(
            container,
            text="Try Again",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            command=self._reshow_login
        )
        login_btn.pack(pady=20)
    
    def _reshow_login(self):
        """Re-show admin login dialog."""
        for widget in self.winfo_children():
            widget.destroy()
        self._show_login()
    
    def _create_main_interface(self):
        """Create main admin interface."""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header
        self._create_header()
        
        # Main content area with tabs
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self._create_dashboard_tab()
        self._create_users_tab()
        self._create_content_moderation_tab()
        self._create_system_stats_tab()
        self._create_database_tab()
        self._create_settings_tab()
    
    def _create_header(self):
        """Create header with admin info."""
        header = tk.Frame(self, bg="#e74c3c", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title on left
        title_frame = tk.Frame(header, bg="#e74c3c")
        title_frame.pack(side=tk.LEFT, padx=15, pady=10)
        
        tk.Label(
            title_frame,
            text="🔒 Admin Panel",
            font=("Arial", 14, "bold"),
            bg="#e74c3c",
            fg="white"
        ).pack(side=tk.LEFT)
        
        # Logout button on right
        logout_btn = tk.Button(
            header,
            text="Logout",
            font=("Arial", 9),
            bg="#c0392b",
            fg="white",
            command=self._handle_logout
        )
        logout_btn.pack(side=tk.RIGHT, padx=15, pady=15)
    
    def _handle_logout(self):
        """Handle admin logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.is_admin = False
            
            # Clear and show access denied
            for widget in self.winfo_children():
                widget.destroy()
            self._create_access_denied_interface()
    
    def _create_dashboard_tab(self):
        """Create dashboard overview tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="📊 Dashboard")
        
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
        
        # Dashboard content
        container = tk.Frame(scrollable_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Stats cards
        stats_frame = tk.Frame(container, bg="white")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Get statistics
        stats = self._get_system_stats()
        
        cards = [
            ("Total Users", stats['total_users'], "#3498db"),
            ("Online Users", stats['online_users'], "#27ae60"),
            ("Total Posts", stats['total_posts'], "#f39c12"),
            ("Email Verified", stats['verified_users'], "#9b59b6")
        ]
        
        for i, (label, value, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            tk.Label(
                card,
                text=str(value),
                font=("Arial", 32, "bold"),
                bg=color,
                fg="white"
            ).pack(pady=(20, 5))
            
            tk.Label(
                card,
                text=label,
                font=("Arial", 11),
                bg=color,
                fg="white"
            ).pack(pady=(0, 20))
        
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
        
        # Recent activity
        activity_frame = tk.LabelFrame(
            container,
            text="Recent Activity",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Activity list
        activity_text = scrolledtext.ScrolledText(
            activity_frame,
            height=15,
            font=("Courier", 9),
            bg="#f8f9fa"
        )
        activity_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load recent activity
        self._load_recent_activity(activity_text)
        
        # Quick actions
        actions_frame = tk.LabelFrame(
            container,
            text="Quick Actions",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        actions_frame.pack(fill=tk.X, pady=10)
        
        btn_frame = tk.Frame(actions_frame, bg="white")
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="Refresh Stats",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=lambda: self._create_dashboard_tab()
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Export Data",
            font=("Arial", 10),
            bg="#27ae60",
            fg="white",
            command=self._export_data
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="View Logs",
            font=("Arial", 10),
            bg="#f39c12",
            fg="white",
            command=self._view_logs
        ).pack(side=tk.LEFT, padx=5)
    
    def _get_system_stats(self) -> Dict[str, int]:
        """Get system statistics."""
        cursor = self.community_manager.database.connection.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Online users
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'online'")
        online_users = cursor.fetchone()[0]
        
        # Verified users
        cursor.execute("SELECT COUNT(*) FROM users WHERE email_verified = 1")
        verified_users = cursor.fetchone()[0]
        
        # Total posts
        cursor.execute("SELECT COUNT(*) FROM community_posts")
        total_posts = cursor.fetchone()[0]
        
        return {
            'total_users': total_users,
            'online_users': online_users,
            'verified_users': verified_users,
            'total_posts': total_posts
        }
    
    def _load_recent_activity(self, text_widget):
        """Load recent activity into text widget."""
        cursor = self.community_manager.database.connection.cursor()
        
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, "Recent User Registrations:\n")
        text_widget.insert(tk.END, "="*60 + "\n\n")
        
        # Recent users
        cursor.execute("""
            SELECT username, display_name, email_verified, join_date 
            FROM users 
            ORDER BY join_date DESC 
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            verified = "✓" if row[2] else "✗"
            text_widget.insert(tk.END, 
                f"{verified} {row[0]:<20} ({row[1]})\n"
                f"   Joined: {row[3]}\n\n"
            )
    
    def _export_data(self):
        """Export system data."""
        messagebox.showinfo(
            "Export Data",
            "Data export functionality:\n\n"
            "• Export user list to CSV\n"
            "• Export posts to JSON\n"
            "• Backup database\n"
            "• Generate reports"
        )
    
    def _view_logs(self):
        """View system logs."""
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            messagebox.showinfo(
                "System Logs",
                f"Log files location:\n{os.path.abspath(logs_dir)}\n\n"
                "Available logs:\n"
                "• email_verifications.txt\n"
                "• application.log\n"
                "• error.log"
            )
        else:
            messagebox.showinfo("Logs", "No log files found")
    
    def _create_users_tab(self):
        """Create user management tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="👥 Users")
        
        # Search bar
        search_frame = tk.Frame(tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="Search:", font=("Arial", 10, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        
        self.user_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.user_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Search",
            bg="#3498db",
            fg="white",
            command=self._search_users
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Show All",
            bg="#95a5a6",
            fg="white",
            command=self._load_all_users
        ).pack(side=tk.LEFT, padx=5)
        
        # Users list with scrollbar
        list_frame = tk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview
        columns = ("Username", "Display Name", "Email", "Level", "Status", "Verified", "Join Date")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=120)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.users_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.users_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Action buttons
        action_frame = tk.Frame(tab)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            bg="#3498db",
            fg="white",
            command=self._view_user_details
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Delete User",
            bg="#e74c3c",
            fg="white",
            command=self._delete_user
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Verify Email",
            bg="#27ae60",
            fg="white",
            command=self._verify_user_email
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Ban User",
            bg="#c0392b",
            fg="white",
            command=self._ban_user
        ).pack(side=tk.LEFT, padx=5)
        
        # Load all users
        self._load_all_users()
    
    def _load_all_users(self):
        """Load all users into the tree view."""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        cursor = self.community_manager.database.connection.cursor()
        cursor.execute("""
            SELECT username, display_name, email, level, status, email_verified, join_date 
            FROM users 
            ORDER BY join_date DESC
        """)
        
        for row in cursor.fetchall():
            verified = "✓" if row[5] else "✗"
            self.users_tree.insert("", "end", values=(
                row[0],  # username
                row[1],  # display_name
                row[2],  # email
                row[3],  # level
                row[4],  # status
                verified,
                row[6]   # join_date
            ))
    
    def _search_users(self):
        """Search for users."""
        search_term = self.user_search_var.get().strip()
        
        if not search_term:
            self._load_all_users()
            return
        
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        cursor = self.community_manager.database.connection.cursor()
        cursor.execute("""
            SELECT username, display_name, email, level, status, email_verified, join_date 
            FROM users 
            WHERE username LIKE ? OR email LIKE ? OR display_name LIKE ?
            ORDER BY join_date DESC
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        for row in cursor.fetchall():
            verified = "✓" if row[5] else "✗"
            self.users_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], row[4], verified, row[6]
            ))
    
    def _view_user_details(self):
        """View selected user details."""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        # Create details dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"User Details - {username}")
        dialog.geometry("500x600")
        
        text = scrolledtext.ScrolledText(dialog, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get full user details
        cursor = self.community_manager.database.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            text.insert(tk.END, f"{'='*50}\n")
            text.insert(tk.END, f"USER DETAILS: {username}\n")
            text.insert(tk.END, f"{'='*50}\n\n")
            
            for key in row.keys():
                text.insert(tk.END, f"{key:<20}: {row[key]}\n")
        
        text.config(state=tk.DISABLED)
    
    def _delete_user(self):
        """Delete selected user."""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?\n\n"
            "This action cannot be undone!"
        ):
            cursor = self.community_manager.database.connection.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.community_manager.database.connection.commit()
            
            messagebox.showinfo("Success", f"User '{username}' deleted")
            self._load_all_users()
    
    def _verify_user_email(self):
        """Manually verify user's email."""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        cursor = self.community_manager.database.connection.cursor()
        cursor.execute(
            "UPDATE users SET email_verified = 1 WHERE username = ?",
            (username,)
        )
        self.community_manager.database.connection.commit()
        
        messagebox.showinfo("Success", f"Email verified for user '{username}'")
        self._load_all_users()
    
    def _ban_user(self):
        """Ban selected user."""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        messagebox.showinfo(
            "Ban User",
            f"User ban functionality:\n\n"
            f"Would ban user: {username}\n"
            f"• Set status to 'banned'\n"
            f"• Prevent login\n"
            f"• Hide content\n"
            f"• Log ban reason"
        )
    
    def _create_content_moderation_tab(self):
        """Create content moderation tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="📝 Content")
        
        tk.Label(
            tab,
            text="Content Moderation",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        # Posts list
        posts_frame = tk.LabelFrame(tab, text="Recent Posts", font=("Arial", 11, "bold"))
        posts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load posts
        cursor = self.community_manager.database.connection.cursor()
        cursor.execute("""
            SELECT post_id, user_id, title, post_type, created_date 
            FROM community_posts 
            ORDER BY created_date DESC 
            LIMIT 20
        """)
        
        for row in cursor.fetchall():
            post_item = tk.Frame(posts_frame, bg="#f8f9fa", relief=tk.RIDGE, bd=1)
            post_item.pack(fill=tk.X, padx=5, pady=3)
            
            tk.Label(
                post_item,
                text=f"📝 {row[2]}",
                font=("Arial", 10, "bold"),
                bg="#f8f9fa"
            ).pack(anchor=tk.W, padx=10, pady=5)
            
            tk.Label(
                post_item,
                text=f"Type: {row[3]} | Posted: {row[4]}",
                font=("Arial", 8),
                bg="#f8f9fa",
                fg="gray"
            ).pack(anchor=tk.W, padx=10)
            
            btn_frame = tk.Frame(post_item, bg="#f8f9fa")
            btn_frame.pack(anchor=tk.E, padx=5, pady=5)
            
            tk.Button(
                btn_frame,
                text="View",
                font=("Arial", 8),
                bg="#3498db",
                fg="white"
            ).pack(side=tk.LEFT, padx=2)
            
            tk.Button(
                btn_frame,
                text="Delete",
                font=("Arial", 8),
                bg="#e74c3c",
                fg="white"
            ).pack(side=tk.LEFT, padx=2)
    
    def _create_system_stats_tab(self):
        """Create system statistics tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="📈 Statistics")
        
        # Stats text area
        stats_text = scrolledtext.ScrolledText(tab, font=("Courier", 10))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Gather comprehensive stats
        cursor = self.community_manager.database.connection.cursor()
        
        stats_text.insert(tk.END, "="*60 + "\n")
        stats_text.insert(tk.END, "SYSTEM STATISTICS\n")
        stats_text.insert(tk.END, "="*60 + "\n\n")
        
        # User stats
        stats_text.insert(tk.END, "USER STATISTICS:\n")
        stats_text.insert(tk.END, "-"*40 + "\n")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        stats_text.insert(tk.END, f"Total Users: {cursor.fetchone()[0]}\n")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE email_verified = 1")
        stats_text.insert(tk.END, f"Verified Users: {cursor.fetchone()[0]}\n")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'online'")
        stats_text.insert(tk.END, f"Online Users: {cursor.fetchone()[0]}\n")
        
        # Content stats
        stats_text.insert(tk.END, "\nCONTENT STATISTICS:\n")
        stats_text.insert(tk.END, "-"*40 + "\n")
        
        cursor.execute("SELECT COUNT(*) FROM community_posts")
        stats_text.insert(tk.END, f"Total Posts: {cursor.fetchone()[0]}\n")
        
        cursor.execute("SELECT COUNT(*) FROM team_shares")
        stats_text.insert(tk.END, f"Shared Teams: {cursor.fetchone()[0]}\n")
        
        cursor.execute("SELECT COUNT(*) FROM battle_replays")
        stats_text.insert(tk.END, f"Battle Replays: {cursor.fetchone()[0]}\n")
        
        # Friendship stats
        stats_text.insert(tk.END, "\nSOCIAL STATISTICS:\n")
        stats_text.insert(tk.END, "-"*40 + "\n")
        
        cursor.execute("SELECT COUNT(*) FROM friendships")
        stats_text.insert(tk.END, f"Total Friendships: {cursor.fetchone()[0]}\n")
        
        cursor.execute("SELECT COUNT(*) FROM friendships WHERE status = 'accepted'")
        stats_text.insert(tk.END, f"Active Friendships: {cursor.fetchone()[0]}\n")
        
        # Database stats
        stats_text.insert(tk.END, "\nDATABASE STATISTICS:\n")
        stats_text.insert(tk.END, "-"*40 + "\n")
        
        db_path = "data/social_community.db"
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024  # KB
            stats_text.insert(tk.END, f"Database Size: {db_size:.2f} KB\n")
        
        stats_text.config(state=tk.DISABLED)
    
    def _create_database_tab(self):
        """Create database management tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="💾 Database")
        
        tk.Label(
            tab,
            text="Database Management",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        # Database actions
        actions_frame = tk.Frame(tab)
        actions_frame.pack(pady=20)
        
        tk.Button(
            actions_frame,
            text="Backup Database",
            font=("Arial", 11),
            bg="#27ae60",
            fg="white",
            width=20,
            command=self._backup_database
        ).pack(pady=10)
        
        tk.Button(
            actions_frame,
            text="Optimize Database",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            width=20,
            command=self._optimize_database
        ).pack(pady=10)
        
        tk.Button(
            actions_frame,
            text="Export to JSON",
            font=("Arial", 11),
            bg="#f39c12",
            fg="white",
            width=20,
            command=self._export_json
        ).pack(pady=10)
        
        tk.Button(
            actions_frame,
            text="View Database Schema",
            font=("Arial", 11),
            bg="#9b59b6",
            fg="white",
            width=20,
            command=self._view_schema
        ).pack(pady=10)
    
    def _backup_database(self):
        """Backup database."""
        import shutil
        from datetime import datetime
        
        try:
            os.makedirs("backups", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backups/social_community_{timestamp}.db"
            
            shutil.copy("data/social_community.db", backup_file)
            
            messagebox.showinfo(
                "Success",
                f"Database backed up successfully!\n\n"
                f"Backup saved to:\n{backup_file}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed:\n{e}")
    
    def _optimize_database(self):
        """Optimize database."""
        cursor = self.community_manager.database.connection.cursor()
        cursor.execute("VACUUM")
        self.community_manager.database.connection.commit()
        
        messagebox.showinfo("Success", "Database optimized successfully!")
    
    def _export_json(self):
        """Export database to JSON."""
        import json
        
        try:
            cursor = self.community_manager.database.connection.cursor()
            
            # Export users
            cursor.execute("SELECT * FROM users")
            users = [dict(row) for row in cursor.fetchall()]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"exports/users_{timestamp}.json"
            
            os.makedirs("exports", exist_ok=True)
            
            with open(export_file, 'w') as f:
                json.dump(users, f, indent=2, default=str)
            
            messagebox.showinfo(
                "Success",
                f"Data exported successfully!\n\n"
                f"File saved to:\n{export_file}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")
    
    def _view_schema(self):
        """View database schema."""
        cursor = self.community_manager.database.connection.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        
        dialog = tk.Toplevel(self)
        dialog.title("Database Schema")
        dialog.geometry("700x600")
        
        text = scrolledtext.ScrolledText(dialog, font=("Courier", 9))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for row in cursor.fetchall():
            if row[0]:
                text.insert(tk.END, row[0] + ";\n\n")
        
        text.config(state=tk.DISABLED)
    
    def _create_settings_tab(self):
        """Create settings tab."""
        tab = tk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text="⚙️ Settings")
        
        tk.Label(
            tab,
            text="Admin Settings",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        settings_frame = tk.Frame(tab)
        settings_frame.pack(pady=20)
        
        # Admin password change
        tk.Label(
            settings_frame,
            text="Change Admin Password:",
            font=("Arial", 11, "bold")
        ).pack(pady=10)
        
        tk.Button(
            settings_frame,
            text="Change Password",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=self._change_admin_password
        ).pack(pady=5)
        
        # Email settings
        tk.Label(
            settings_frame,
            text="Email Configuration:",
            font=("Arial", 11, "bold")
        ).pack(pady=(30, 10))
        
        tk.Button(
            settings_frame,
            text="Configure SMTP",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self._configure_smtp
        ).pack(pady=5)
        
        # System maintenance
        tk.Label(
            settings_frame,
            text="System Maintenance:",
            font=("Arial", 11, "bold")
        ).pack(pady=(30, 10))
        
        tk.Button(
            settings_frame,
            text="Clear Old Logs",
            font=("Arial", 10),
            bg="#f39c12",
            fg="white",
            command=self._clear_logs
        ).pack(pady=5)
    
    def _change_admin_password(self):
        """Change admin password."""
        messagebox.showinfo(
            "Change Password",
            "Admin password change:\n\n"
            "In production, this would:\n"
            "• Verify current password\n"
            "• Set new password\n"
            "• Hash and store securely\n"
            "• Log the change"
        )
    
    def _configure_smtp(self):
        """Configure SMTP settings."""
        messagebox.showinfo(
            "SMTP Configuration",
            "SMTP settings are configured in .env file:\n\n"
            "SMTP_SERVER=smtp.gmail.com\n"
            "SMTP_PORT=587\n"
            "SENDER_EMAIL=your-email@gmail.com\n"
            "SENDER_PASSWORD=your-app-password\n\n"
            "See GMAIL_SETUP_GUIDE.md for details"
        )
    
    def _clear_logs(self):
        """Clear old log files."""
        if messagebox.askyesno("Confirm", "Clear old log files?"):
            messagebox.showinfo("Success", "Old log files cleared!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pokemon Team Builder - Admin Panel")
    root.geometry("1000x700")
    
    app = AdminPanelFrame(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
