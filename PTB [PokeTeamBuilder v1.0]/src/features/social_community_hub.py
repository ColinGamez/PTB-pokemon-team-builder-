"""
Social Features & Community Hub
Comprehensive social system with friends, leaderboards, tournaments,
team sharing, battle replays, and community-driven content.
"""

import json
import sqlite3
import hashlib
import time
import uuid
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class UserStatus(Enum):
    """User online status."""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"

class FriendshipStatus(Enum):
    """Friendship status between users."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    DECLINED = "declined"

class TournamentStatus(Enum):
    """Tournament status."""
    UPCOMING = "upcoming"
    REGISTRATION = "registration"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PostType(Enum):
    """Community post types."""
    TEAM_SHARE = "team_share"
    BATTLE_REPLAY = "battle_replay"
    GUIDE = "guide"
    DISCUSSION = "discussion"
    ACHIEVEMENT = "achievement"
    ART = "art"

@dataclass
class User:
    """Community user profile."""
    user_id: str
    username: str
    email: str
    display_name: str
    avatar_url: str
    bio: str
    status: UserStatus
    level: int
    experience: int
    join_date: datetime
    last_active: datetime
    badges: List[str]
    achievements: List[str]
    stats: Dict[str, Any]
    preferences: Dict[str, Any]

@dataclass
class Friendship:
    """Friendship relationship between users."""
    friendship_id: str
    requester_id: str
    recipient_id: str
    status: FriendshipStatus
    created_date: datetime
    accepted_date: Optional[datetime] = None
    last_interaction: Optional[datetime] = None

@dataclass
class TeamShare:
    """Shared Pokemon team."""
    share_id: str
    user_id: str
    title: str
    description: str
    team_data: Dict[str, Any]
    tags: List[str]
    format: str
    rating: float
    votes: int
    downloads: int
    created_date: datetime
    updated_date: datetime
    is_featured: bool = False
    is_public: bool = True

@dataclass
class BattleReplay:
    """Battle replay data."""
    replay_id: str
    title: str
    player1_id: str
    player2_id: str
    winner_id: Optional[str]
    battle_format: str
    battle_data: Dict[str, Any]
    duration: int  # seconds
    turns: int
    rating_change: Dict[str, int]
    date: datetime
    views: int
    likes: int
    is_featured: bool = False

@dataclass
class Tournament:
    """Tournament information."""
    tournament_id: str
    name: str
    description: str
    format: str
    max_participants: int
    entry_fee: int
    prize_pool: Dict[str, Any]
    rules: Dict[str, Any]
    status: TournamentStatus
    organizer_id: str
    participants: List[str]
    brackets: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    created_date: datetime

@dataclass
class CommunityPost:
    """Community forum post."""
    post_id: str
    user_id: str
    post_type: PostType
    title: str
    content: str
    attachments: List[str]
    tags: List[str]
    likes: int
    dislikes: int
    comments: List[str]
    views: int
    is_pinned: bool
    is_locked: bool
    created_date: datetime
    updated_date: datetime

@dataclass
class Leaderboard:
    """Leaderboard entry."""
    user_id: str
    username: str
    rank: int
    score: float
    category: str
    season: str
    last_updated: datetime
    trend: str  # "up", "down", "same"

class SocialDatabase:
    """Database manager for social features."""
    
    def __init__(self, db_path: str = "social_features.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the social features database."""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        self._create_tables()
        
        # Insert sample data
        self._insert_sample_data()
    
    def _create_tables(self):
        """Create all necessary database tables."""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                email_verified INTEGER DEFAULT 0,
                verification_token TEXT,
                verification_sent_date TIMESTAMP,
                display_name TEXT NOT NULL,
                avatar_url TEXT,
                bio TEXT,
                status TEXT DEFAULT 'offline',
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                badges TEXT DEFAULT '[]',
                achievements TEXT DEFAULT '[]',
                stats TEXT DEFAULT '{}',
                preferences TEXT DEFAULT '{}'
            )
        """)
        
        # Friendships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friendships (
                friendship_id TEXT PRIMARY KEY,
                requester_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_date TIMESTAMP,
                last_interaction TIMESTAMP,
                FOREIGN KEY (requester_id) REFERENCES users (user_id),
                FOREIGN KEY (recipient_id) REFERENCES users (user_id)
            )
        """)
        
        # Team shares table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_shares (
                share_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                team_data TEXT NOT NULL,
                tags TEXT DEFAULT '[]',
                format TEXT NOT NULL,
                rating REAL DEFAULT 0.0,
                votes INTEGER DEFAULT 0,
                downloads INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_featured BOOLEAN DEFAULT FALSE,
                is_public BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Battle replays table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS battle_replays (
                replay_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                player1_id TEXT NOT NULL,
                player2_id TEXT NOT NULL,
                winner_id TEXT,
                battle_format TEXT NOT NULL,
                battle_data TEXT NOT NULL,
                duration INTEGER NOT NULL,
                turns INTEGER NOT NULL,
                rating_change TEXT DEFAULT '{}',
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (player1_id) REFERENCES users (user_id),
                FOREIGN KEY (player2_id) REFERENCES users (user_id)
            )
        """)
        
        # Tournaments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                tournament_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                format TEXT NOT NULL,
                max_participants INTEGER NOT NULL,
                entry_fee INTEGER DEFAULT 0,
                prize_pool TEXT DEFAULT '{}',
                rules TEXT DEFAULT '{}',
                status TEXT DEFAULT 'upcoming',
                organizer_id TEXT NOT NULL,
                participants TEXT DEFAULT '[]',
                brackets TEXT DEFAULT '{}',
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organizer_id) REFERENCES users (user_id)
            )
        """)
        
        # Community posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_posts (
                post_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                post_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                attachments TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]',
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0,
                comments TEXT DEFAULT '[]',
                views INTEGER DEFAULT 0,
                is_pinned BOOLEAN DEFAULT FALSE,
                is_locked BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Leaderboards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboards (
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                rank INTEGER NOT NULL,
                score REAL NOT NULL,
                category TEXT NOT NULL,
                season TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trend TEXT DEFAULT 'same',
                PRIMARY KEY (user_id, category, season),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        self.connection.commit()
    
    def _insert_sample_data(self):
        """Insert sample data for demonstration."""
        cursor = self.connection.cursor()
        
        # Check if sample data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            return
        
        # Sample users
        sample_users = [
            {
                "user_id": "user_001",
                "username": "PokeMaster_Alex",
                "email": "alex@example.com",
                "display_name": "Alex the Champion",
                "bio": "Competitive Pokemon trainer specializing in OU singles",
                "level": 47,
                "experience": 23560,
                "badges": '["Champion", "Tournament Winner", "Team Builder"]',
                "stats": '{"battles_won": 847, "battles_lost": 203, "teams_created": 45}'
            },
            {
                "user_id": "user_002", 
                "username": "DragonTamer_Sarah",
                "email": "sarah@example.com",
                "display_name": "Sarah Dragon Queen",
                "bio": "Dragon-type specialist and shiny hunter",
                "level": 35,
                "experience": 15400,
                "badges": '["Dragon Master", "Shiny Hunter", "Breeder"]',
                "stats": '{"battles_won": 523, "battles_lost": 187, "shinies_found": 23}'
            },
            {
                "user_id": "user_003",
                "username": "StrategyGuru_Mike",
                "email": "mike@example.com", 
                "display_name": "Mike the Tactician",
                "bio": "VGC doubles expert and team building theorist",
                "level": 52,
                "experience": 31200,
                "badges": '["VGC Champion", "Strategy Master", "Meta Analyst"]',
                "stats": '{"battles_won": 1204, "battles_lost": 356, "guides_written": 15}'
            }
        ]
        
        for user in sample_users:
            cursor.execute("""
                INSERT OR IGNORE INTO users 
                (user_id, username, email, display_name, bio, level, experience, badges, stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user["user_id"], user["username"], user["email"], user["display_name"],
                user["bio"], user["level"], user["experience"], user["badges"], user["stats"]
            ))
        
        self.connection.commit()

class CommunityManager:
    """Main manager for community features."""
    
    def __init__(self):
        self.database = SocialDatabase()
        self.active_users = {}  # user_id -> last_activity_timestamp
        self.notification_callbacks = []
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for community management."""
        # Update user activity status
        threading.Timer(30.0, self._update_user_activity).start()
        
        # Process tournament brackets
        threading.Timer(60.0, self._process_tournaments).start()
    
    def _update_user_activity(self):
        """Update user activity and status."""
        current_time = time.time()
        
        for user_id, last_activity in list(self.active_users.items()):
            # Mark users as away if inactive for 5 minutes
            if current_time - last_activity > 300:
                self.update_user_status(user_id, UserStatus.AWAY)
            
            # Mark users as offline if inactive for 15 minutes
            elif current_time - last_activity > 900:
                self.update_user_status(user_id, UserStatus.OFFLINE)
                del self.active_users[user_id]
        
        # Schedule next update
        threading.Timer(30.0, self._update_user_activity).start()
    
    def _process_tournaments(self):
        """Process tournament status and brackets."""
        cursor = self.database.connection.cursor()
        
        # Find tournaments that should start
        cursor.execute("""
            SELECT * FROM tournaments 
            WHERE status = 'registration' AND start_date <= CURRENT_TIMESTAMP
        """)
        
        for tournament_row in cursor.fetchall():
            tournament_id = tournament_row["tournament_id"]
            self._start_tournament(tournament_id)
        
        # Schedule next check
        threading.Timer(60.0, self._process_tournaments).start()
    
    # User Management
    def create_user(self, username: str, email: str, display_name: str) -> str:
        """Create a new user account."""
        user_id = str(uuid.uuid4())
        
        cursor = self.database.connection.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, username, email, display_name)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, email, display_name))
        
        self.database.connection.commit()
        return user_id
    
    def register_user(self, username: str, email: str, display_name: str, password: str, bio: str = "") -> Optional[str]:
        """Register a new user with password hashing."""
        import hashlib
        
        # Check if username is already taken
        if not self.is_username_available(username):
            logger.warning(f"Username '{username}' is already taken")
            return None
        
        # Check if email is already registered
        if not self.is_email_available(email):
            logger.warning(f"Email '{email}' is already registered")
            return None
        
        # Validate username format (alphanumeric, underscores, 3-20 chars)
        if not self._validate_username(username):
            logger.warning(f"Username '{username}' is invalid")
            return None
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Generate email verification token
        verification_token = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()
        
        cursor = self.database.connection.cursor()
        
        try:
            # Create user
            user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (
                    user_id, username, email, email_verified, verification_token,
                    verification_sent_date, display_name, bio, status, 
                    level, experience, badges, achievements, stats, preferences
                )
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, username, email, 0, verification_token, 
                display_name, bio, UserStatus.ONLINE.value,
                1, 0, json.dumps([]), json.dumps([]), 
                json.dumps({"password_hash": password_hash}),
                json.dumps({})
            ))
            
            self.database.connection.commit()
            
            # Send verification email
            self._send_verification_email(email, username, verification_token)
            
            logger.info(f"User '{username}' registered successfully with ID: {user_id}")
            return user_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Registration error - integrity constraint: {e}")
            return None
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return None
    
    def is_username_available(self, username: str) -> bool:
        """Check if a username is available."""
        cursor = self.database.connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        return cursor.fetchone() is None
    
    def is_email_available(self, email: str) -> bool:
        """Check if an email is available."""
        cursor = self.database.connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        return cursor.fetchone() is None
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        import re
        # Username must be 3-20 characters, alphanumeric with underscores
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
    
    def _send_verification_email(self, email: str, username: str, token: str):
        """Send email verification link to user."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Email configuration (you'll need to set these)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "pokemonteambuilder@gmail.com"  # Configure this
            sender_password = ""  # Configure this in environment variable
            
            # For demo purposes, just log the verification link
            verification_link = f"http://localhost:5000/verify-email?token={token}"
            
            logger.info(f"Email verification link for {username}: {verification_link}")
            
            # If SMTP credentials are configured, send actual email
            if sender_password:
                message = MIMEMultipart("alternative")
                message["Subject"] = "Pokemon Team Builder - Verify Your Email"
                message["From"] = sender_email
                message["To"] = email
                
                html_content = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h1 style="color: #2C3E50; text-align: center;">🎮 Pokemon Team Builder</h1>
                            <h2 style="color: #3498db;">Welcome, {username}!</h2>
                            
                            <p style="font-size: 16px; color: #555;">
                                Thank you for joining the Pokemon Team Builder community! To complete your registration 
                                and verify your email address, please click the button below:
                            </p>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{verification_link}" 
                                   style="background-color: #3498db; color: white; padding: 15px 30px; 
                                          text-decoration: none; border-radius: 5px; font-weight: bold; 
                                          display: inline-block;">
                                    Verify Email Address
                                </a>
                            </div>
                            
                            <p style="font-size: 14px; color: #777;">
                                Or copy and paste this link into your browser:<br>
                                <a href="{verification_link}" style="color: #3498db;">{verification_link}</a>
                            </p>
                            
                            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                            
                            <p style="font-size: 12px; color: #999;">
                                If you didn't create an account, please ignore this email.
                            </p>
                            
                            <p style="font-size: 12px; color: #999; text-align: center;">
                                © 2025 Pokemon Team Builder. All rights reserved.
                            </p>
                        </div>
                    </body>
                </html>
                """
                
                text_content = f"""
                Pokemon Team Builder - Email Verification
                
                Welcome, {username}!
                
                Thank you for joining the Pokemon Team Builder community! To complete your registration 
                and verify your email address, please visit this link:
                
                {verification_link}
                
                If you didn't create an account, please ignore this email.
                
                © 2025 Pokemon Team Builder. All rights reserved.
                """
                
                part1 = MIMEText(text_content, "plain")
                part2 = MIMEText(html_content, "html")
                
                message.attach(part1)
                message.attach(part2)
                
                # Send email
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, email, message.as_string())
                
                logger.info(f"Verification email sent to {email}")
            else:
                # Demo mode - save to file
                verification_file = os.path.join("logs", "email_verifications.txt")
                os.makedirs("logs", exist_ok=True)
                
                with open(verification_file, "a") as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"Date: {datetime.now()}\n")
                    f.write(f"Username: {username}\n")
                    f.write(f"Email: {email}\n")
                    f.write(f"Verification Link: {verification_link}\n")
                    f.write(f"{'='*60}\n")
                
                logger.info(f"Verification link saved to {verification_file}")
                
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            # Don't fail registration if email sending fails
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with token."""
        cursor = self.database.connection.cursor()
        
        try:
            # Find user with this token
            cursor.execute("""
                SELECT user_id, verification_sent_date FROM users 
                WHERE verification_token = ? AND email_verified = 0
            """, (token,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Invalid or expired verification token")
                return False
            
            user_id = row["user_id"]
            sent_date = datetime.fromisoformat(row["verification_sent_date"])
            
            # Check if token is still valid (24 hours)
            if (datetime.now() - sent_date).total_seconds() > 86400:
                logger.warning(f"Verification token expired for user {user_id}")
                return False
            
            # Mark email as verified
            cursor.execute("""
                UPDATE users 
                SET email_verified = 1, verification_token = NULL 
                WHERE user_id = ?
            """, (user_id,))
            
            self.database.connection.commit()
            
            logger.info(f"Email verified for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            return False
    
    def resend_verification_email(self, email: str) -> bool:
        """Resend verification email to user."""
        cursor = self.database.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT user_id, username, email_verified FROM users 
                WHERE email = ?
            """, (email,))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            if row["email_verified"]:
                logger.info(f"Email already verified for {email}")
                return False
            
            # Generate new token
            verification_token = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()
            
            cursor.execute("""
                UPDATE users 
                SET verification_token = ?, verification_sent_date = CURRENT_TIMESTAMP 
                WHERE email = ?
            """, (verification_token, email))
            
            self.database.connection.commit()
            
            # Send email
            self._send_verification_email(email, row["username"], verification_token)
            
            logger.info(f"Verification email resent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error resending verification email: {e}")
            return False
    
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        import hashlib
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT * FROM users 
            WHERE (username = ? OR email = ?) 
        """, (username_or_email, username_or_email))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check password
        stats = json.loads(row["stats"])
        stored_hash = stats.get("password_hash", "")
        
        if stored_hash != password_hash:
            return None
        
        # Return user object
        return User(
            user_id=row["user_id"],
            username=row["username"],
            email=row["email"],
            display_name=row["display_name"],
            avatar_url=row["avatar_url"] or "",
            bio=row["bio"] or "",
            status=UserStatus(row["status"]),
            level=row["level"],
            experience=row["experience"],
            join_date=datetime.fromisoformat(row["join_date"]),
            last_active=datetime.fromisoformat(row["last_active"]),
            badges=json.loads(row["badges"]),
            achievements=json.loads(row["achievements"]),
            stats=json.loads(row["stats"]),
            preferences=json.loads(row["preferences"])
        )
    
    def search_users(self, search_term: str) -> Optional[User]:
        """Search for a user by username."""
        cursor = self.database.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (search_term,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return User(
            user_id=row["user_id"],
            username=row["username"],
            email=row["email"],
            display_name=row["display_name"],
            avatar_url=row["avatar_url"] or "",
            bio=row["bio"] or "",
            status=UserStatus(row["status"]),
            level=row["level"],
            experience=row["experience"],
            join_date=datetime.fromisoformat(row["join_date"]),
            last_active=datetime.fromisoformat(row["last_active"]),
            badges=json.loads(row["badges"]),
            achievements=json.loads(row["achievements"]),
            stats=json.loads(row["stats"]),
            preferences=json.loads(row["preferences"])
        )
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        cursor = self.database.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return User(
            user_id=row["user_id"],
            username=row["username"],
            email=row["email"],
            display_name=row["display_name"],
            avatar_url=row["avatar_url"] or "",
            bio=row["bio"] or "",
            status=UserStatus(row["status"]),
            level=row["level"],
            experience=row["experience"],
            join_date=datetime.fromisoformat(row["join_date"]),
            last_active=datetime.fromisoformat(row["last_active"]),
            badges=json.loads(row["badges"]),
            achievements=json.loads(row["achievements"]),
            stats=json.loads(row["stats"]),
            preferences=json.loads(row["preferences"])
        )
    
    def update_user_status(self, user_id: str, status: UserStatus):
        """Update user online status."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            UPDATE users SET status = ?, last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        """, (status.value, user_id))
        
        self.database.connection.commit()
        
        # Update active users tracking
        if status in [UserStatus.ONLINE, UserStatus.BUSY]:
            self.active_users[user_id] = time.time()
    
    # Friend System
    def send_friend_request(self, requester_id: str, recipient_username: str) -> bool:
        """Send a friend request."""
        # Get recipient ID
        cursor = self.database.connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (recipient_username,))
        recipient_row = cursor.fetchone()
        
        if not recipient_row:
            return False
        
        recipient_id = recipient_row["user_id"]
        
        # Check if friendship already exists
        cursor.execute("""
            SELECT * FROM friendships 
            WHERE (requester_id = ? AND recipient_id = ?) 
            OR (requester_id = ? AND recipient_id = ?)
        """, (requester_id, recipient_id, recipient_id, requester_id))
        
        if cursor.fetchone():
            return False  # Friendship already exists
        
        # Create friend request
        friendship_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO friendships (friendship_id, requester_id, recipient_id, status)
            VALUES (?, ?, ?, 'pending')
        """, (friendship_id, requester_id, recipient_id))
        
        self.database.connection.commit()
        
        # Send notification
        self._send_notification(recipient_id, "friend_request", {
            "requester_id": requester_id,
            "friendship_id": friendship_id
        })
        
        return True
    
    def respond_to_friend_request(self, friendship_id: str, accept: bool) -> bool:
        """Respond to a friend request."""
        cursor = self.database.connection.cursor()
        
        status = "accepted" if accept else "declined"
        accepted_date = datetime.now() if accept else None
        
        cursor.execute("""
            UPDATE friendships 
            SET status = ?, accepted_date = ?
            WHERE friendship_id = ? AND status = 'pending'
        """, (status, accepted_date, friendship_id))
        
        if cursor.rowcount > 0:
            self.database.connection.commit()
            return True
        
        return False
    
    def get_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's friends list."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT u.user_id, u.username, u.display_name, u.status, u.level,
                   f.last_interaction, f.accepted_date
            FROM friendships f
            JOIN users u ON (
                CASE 
                    WHEN f.requester_id = ? THEN u.user_id = f.recipient_id
                    ELSE u.user_id = f.requester_id
                END
            )
            WHERE (f.requester_id = ? OR f.recipient_id = ?) 
            AND f.status = 'accepted'
            ORDER BY u.status DESC, f.last_interaction DESC
        """, (user_id, user_id, user_id))
        
        friends = []
        for row in cursor.fetchall():
            friends.append({
                "user_id": row["user_id"],
                "username": row["username"],
                "display_name": row["display_name"],
                "status": row["status"],
                "level": row["level"],
                "last_interaction": row["last_interaction"],
                "friends_since": row["accepted_date"]
            })
        
        return friends
    
    # Team Sharing System
    def share_team(
        self, 
        user_id: str, 
        title: str, 
        team_data: Dict[str, Any], 
        description: str = "",
        tags: List[str] = None,
        format: str = "OU"
    ) -> str:
        """Share a Pokemon team with the community."""
        share_id = str(uuid.uuid4())
        tags = tags or []
        
        cursor = self.database.connection.cursor()
        cursor.execute("""
            INSERT INTO team_shares 
            (share_id, user_id, title, description, team_data, tags, format)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            share_id, user_id, title, description, 
            json.dumps(team_data), json.dumps(tags), format
        ))
        
        self.database.connection.commit()
        
        # Award experience for sharing
        self._award_experience(user_id, 50, "team_share")
        
        return share_id
    
    def get_popular_teams(self, format: str = None, limit: int = 20) -> List[TeamShare]:
        """Get popular shared teams."""
        cursor = self.database.connection.cursor()
        
        if format:
            cursor.execute("""
                SELECT ts.*, u.username, u.display_name
                FROM team_shares ts
                JOIN users u ON ts.user_id = u.user_id
                WHERE ts.format = ? AND ts.is_public = TRUE
                ORDER BY (ts.rating * 0.7 + ts.downloads * 0.3) DESC
                LIMIT ?
            """, (format, limit))
        else:
            cursor.execute("""
                SELECT ts.*, u.username, u.display_name
                FROM team_shares ts
                JOIN users u ON ts.user_id = u.user_id
                WHERE ts.is_public = TRUE
                ORDER BY (ts.rating * 0.7 + ts.downloads * 0.3) DESC
                LIMIT ?
            """, (limit,))
        
        teams = []
        for row in cursor.fetchall():
            team = TeamShare(
                share_id=row["share_id"],
                user_id=row["user_id"],
                title=row["title"],
                description=row["description"],
                team_data=json.loads(row["team_data"]),
                tags=json.loads(row["tags"]),
                format=row["format"],
                rating=row["rating"],
                votes=row["votes"],
                downloads=row["downloads"],
                created_date=datetime.fromisoformat(row["created_date"]),
                updated_date=datetime.fromisoformat(row["updated_date"]),
                is_featured=bool(row["is_featured"]),
                is_public=bool(row["is_public"])
            )
            teams.append(team)
        
        return teams
    
    def rate_team(self, user_id: str, share_id: str, rating: float) -> bool:
        """Rate a shared team (1-5 stars)."""
        if not 1 <= rating <= 5:
            return False
        
        # This would typically check if user already rated and update accordingly
        # For simplicity, we'll just update the average rating
        cursor = self.database.connection.cursor()
        cursor.execute("""
            UPDATE team_shares 
            SET rating = ((rating * votes) + ?) / (votes + 1),
                votes = votes + 1
            WHERE share_id = ?
        """, (rating, share_id))
        
        if cursor.rowcount > 0:
            self.database.connection.commit()
            return True
        
        return False
    
    def download_team(self, user_id: str, share_id: str) -> Optional[Dict[str, Any]]:
        """Download a shared team."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT team_data FROM team_shares 
            WHERE share_id = ? AND is_public = TRUE
        """, (share_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Increment download counter
        cursor.execute("""
            UPDATE team_shares SET downloads = downloads + 1 
            WHERE share_id = ?
        """, (share_id,))
        
        self.database.connection.commit()
        
        return json.loads(row["team_data"])
    
    # Tournament System
    def create_tournament(
        self,
        organizer_id: str,
        name: str,
        format: str,
        max_participants: int,
        start_date: datetime,
        end_date: datetime,
        entry_fee: int = 0,
        description: str = ""
    ) -> str:
        """Create a new tournament."""
        tournament_id = str(uuid.uuid4())
        
        cursor = self.database.connection.cursor()
        cursor.execute("""
            INSERT INTO tournaments 
            (tournament_id, name, description, format, max_participants, 
             entry_fee, organizer_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'registration')
        """, (
            tournament_id, name, description, format, max_participants,
            entry_fee, organizer_id, start_date.isoformat(), end_date.isoformat()
        ))
        
        self.database.connection.commit()
        return tournament_id
    
    def join_tournament(self, user_id: str, tournament_id: str) -> bool:
        """Join a tournament."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT participants, max_participants, status FROM tournaments 
            WHERE tournament_id = ?
        """, (tournament_id,))
        
        row = cursor.fetchone()
        if not row or row["status"] != "registration":
            return False
        
        participants = json.loads(row["participants"])
        
        if user_id in participants:
            return False  # Already joined
        
        if len(participants) >= row["max_participants"]:
            return False  # Tournament full
        
        participants.append(user_id)
        
        cursor.execute("""
            UPDATE tournaments SET participants = ? WHERE tournament_id = ?
        """, (json.dumps(participants), tournament_id))
        
        self.database.connection.commit()
        return True
    
    def _start_tournament(self, tournament_id: str):
        """Start a tournament and generate brackets."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT participants FROM tournaments WHERE tournament_id = ?
        """, (tournament_id,))
        
        row = cursor.fetchone()
        if not row:
            return
        
        participants = json.loads(row["participants"])
        brackets = self._generate_tournament_brackets(participants)
        
        cursor.execute("""
            UPDATE tournaments 
            SET status = 'in_progress', brackets = ?
            WHERE tournament_id = ?
        """, (json.dumps(brackets), tournament_id))
        
        self.database.connection.commit()
        
        # Notify participants
        for participant_id in participants:
            self._send_notification(participant_id, "tournament_started", {
                "tournament_id": tournament_id
            })
    
    def _generate_tournament_brackets(self, participants: List[str]) -> Dict[str, Any]:
        """Generate tournament brackets."""
        import random
        random.shuffle(participants)
        
        # Simple single elimination bracket
        rounds = []
        current_round = participants.copy()
        
        round_num = 1
        while len(current_round) > 1:
            next_round = []
            matches = []
            
            # Pair up participants
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    match = {
                        "match_id": str(uuid.uuid4()),
                        "player1": current_round[i],
                        "player2": current_round[i + 1],
                        "winner": None,
                        "status": "pending"
                    }
                    matches.append(match)
                    next_round.append(None)  # Placeholder for winner
                else:
                    # Odd number of players, this one gets a bye
                    next_round.append(current_round[i])
            
            rounds.append({
                "round": round_num,
                "matches": matches
            })
            
            current_round = next_round
            round_num += 1
        
        return {"rounds": rounds, "champion": None}
    
    # Leaderboard System
    def update_leaderboard(
        self, 
        user_id: str, 
        category: str, 
        score: float, 
        season: str = "current"
    ):
        """Update user's leaderboard ranking."""
        cursor = self.database.connection.cursor()
        
        # Get username
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        username_row = cursor.fetchone()
        if not username_row:
            return
        
        username = username_row["username"]
        
        # Insert or update leaderboard entry
        cursor.execute("""
            INSERT OR REPLACE INTO leaderboards 
            (user_id, username, rank, score, category, season, trend)
            VALUES (?, ?, 0, ?, ?, ?, 'same')
        """, (user_id, username, score, category, season))
        
        # Recalculate ranks for this category and season
        cursor.execute("""
            UPDATE leaderboards 
            SET rank = (
                SELECT COUNT(*) + 1 
                FROM leaderboards l2 
                WHERE l2.category = leaderboards.category 
                AND l2.season = leaderboards.season 
                AND l2.score > leaderboards.score
            )
            WHERE category = ? AND season = ?
        """, (category, season))
        
        self.database.connection.commit()
    
    def get_leaderboard(
        self, 
        category: str, 
        season: str = "current", 
        limit: int = 50
    ) -> List[Leaderboard]:
        """Get leaderboard rankings."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT * FROM leaderboards 
            WHERE category = ? AND season = ?
            ORDER BY rank ASC
            LIMIT ?
        """, (category, season, limit))
        
        leaderboard = []
        for row in cursor.fetchall():
            entry = Leaderboard(
                user_id=row["user_id"],
                username=row["username"],
                rank=row["rank"],
                score=row["score"],
                category=row["category"],
                season=row["season"],
                last_updated=datetime.fromisoformat(row["last_updated"]),
                trend=row["trend"]
            )
            leaderboard.append(entry)
        
        return leaderboard
    
    # Community Posts
    def create_post(
        self,
        user_id: str,
        post_type: PostType,
        title: str,
        content: str,
        tags: List[str] = None,
        attachments: List[str] = None
    ) -> str:
        """Create a community post."""
        post_id = str(uuid.uuid4())
        tags = tags or []
        attachments = attachments or []
        
        cursor = self.database.connection.cursor()
        cursor.execute("""
            INSERT INTO community_posts 
            (post_id, user_id, post_type, title, content, tags, attachments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id, user_id, post_type.value, title, content,
            json.dumps(tags), json.dumps(attachments)
        ))
        
        self.database.connection.commit()
        
        # Award experience for posting
        self._award_experience(user_id, 25, "community_post")
        
        return post_id
    
    def get_community_feed(
        self, 
        user_id: str = None, 
        post_type: PostType = None,
        limit: int = 50
    ) -> List[CommunityPost]:
        """Get community feed."""
        cursor = self.database.connection.cursor()
        
        query = """
            SELECT cp.*, u.username, u.display_name
            FROM community_posts cp
            JOIN users u ON cp.user_id = u.user_id
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND cp.user_id = ?"
            params.append(user_id)
        
        if post_type:
            query += " AND cp.post_type = ?"
            params.append(post_type.value)
        
        query += " ORDER BY cp.created_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        posts = []
        for row in cursor.fetchall():
            post = CommunityPost(
                post_id=row["post_id"],
                user_id=row["user_id"],
                post_type=PostType(row["post_type"]),
                title=row["title"],
                content=row["content"],
                attachments=json.loads(row["attachments"]),
                tags=json.loads(row["tags"]),
                likes=row["likes"],
                dislikes=row["dislikes"],
                comments=json.loads(row["comments"]),
                views=row["views"],
                is_pinned=bool(row["is_pinned"]),
                is_locked=bool(row["is_locked"]),
                created_date=datetime.fromisoformat(row["created_date"]),
                updated_date=datetime.fromisoformat(row["updated_date"])
            )
            posts.append(post)
        
        return posts
    
    def like_post(self, user_id: str, post_id: str, is_like: bool = True) -> bool:
        """Like or dislike a post."""
        cursor = self.database.connection.cursor()
        
        if is_like:
            cursor.execute("""
                UPDATE community_posts SET likes = likes + 1 
                WHERE post_id = ?
            """, (post_id,))
        else:
            cursor.execute("""
                UPDATE community_posts SET dislikes = dislikes + 1 
                WHERE post_id = ?
            """, (post_id,))
        
        if cursor.rowcount > 0:
            self.database.connection.commit()
            return True
        
        return False
    
    # Utility Methods
    def _award_experience(self, user_id: str, amount: int, reason: str):
        """Award experience points to a user."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            UPDATE users 
            SET experience = experience + ?
            WHERE user_id = ?
        """, (amount, user_id))
        
        # Check for level up
        cursor.execute("""
            SELECT level, experience FROM users WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if row:
            new_level = row["experience"] // 1000 + 1  # Simple level calculation
            if new_level > row["level"]:
                cursor.execute("""
                    UPDATE users SET level = ? WHERE user_id = ?
                """, (new_level, user_id))
                
                # Send level up notification
                self._send_notification(user_id, "level_up", {
                    "new_level": new_level
                })
        
        self.database.connection.commit()
    
    def _send_notification(self, user_id: str, notification_type: str, data: Dict[str, Any]):
        """Send notification to user."""
        notification = {
            "user_id": user_id,
            "type": notification_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Call registered notification callbacks
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                print(f"Notification callback error: {e}")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        cursor = self.database.connection.cursor()
        
        # User basic info
        user = self.get_user(user_id)
        if not user:
            return {}
        
        # Friends count
        cursor.execute("""
            SELECT COUNT(*) as friend_count FROM friendships 
            WHERE (requester_id = ? OR recipient_id = ?) AND status = 'accepted'
        """, (user_id, user_id))
        friend_count = cursor.fetchone()["friend_count"]
        
        # Teams shared
        cursor.execute("""
            SELECT COUNT(*) as teams_shared FROM team_shares WHERE user_id = ?
        """, (user_id,))
        teams_shared = cursor.fetchone()["teams_shared"]
        
        # Tournament participation
        cursor.execute("""
            SELECT COUNT(*) as tournaments_joined FROM tournaments 
            WHERE participants LIKE '%' || ? || '%'
        """, (user_id,))
        tournaments_joined = cursor.fetchone()["tournaments_joined"]
        
        # Community posts
        cursor.execute("""
            SELECT COUNT(*) as posts_created FROM community_posts WHERE user_id = ?
        """, (user_id,))
        posts_created = cursor.fetchone()["posts_created"]
        
        return {
            "user": asdict(user),
            "social_stats": {
                "friends": friend_count,
                "teams_shared": teams_shared,
                "tournaments_joined": tournaments_joined,
                "community_posts": posts_created
            }
        }


# Demo function
def demonstrate_social_system():
    """Demonstrate the social features system."""
    print("🌟 Pokemon Community Hub Demo")
    print("=" * 50)
    
    # Initialize community manager
    community = CommunityManager()
    
    # Get sample users
    users = ["user_001", "user_002", "user_003"]
    
    print("\n👥 User Profiles:")
    print("-" * 30)
    for user_id in users:
        user = community.get_user(user_id)
        if user:
            print(f"🏆 {user.display_name} (@{user.username})")
            print(f"   Level {user.level} | {user.experience} XP")
            print(f"   Bio: {user.bio}")
            print(f"   Badges: {', '.join(user.badges)}")
    
    # Demonstrate friend system
    print(f"\n🤝 Friend System:")
    print("-" * 30)
    community.send_friend_request(users[0], "DragonTamer_Sarah")
    friends = community.get_friends(users[0])
    print(f"Friends for {users[0]}: {len(friends)} friends")
    
    # Demonstrate team sharing
    print(f"\n📋 Team Sharing:")
    print("-" * 30)
    sample_team = {
        "pokemon": [
            {"name": "Garchomp", "level": 50, "moves": ["Earthquake", "Dragon Claw"]},
            {"name": "Rotom-Wash", "level": 50, "moves": ["Hydro Pump", "Thunderbolt"]}
        ]
    }
    share_id = community.share_team(
        users[0], "My Championship Team", sample_team, 
        "This team won me the regional tournament!", ["competitive", "OU"]
    )
    print(f"Team shared with ID: {share_id}")
    
    # Show popular teams
    popular_teams = community.get_popular_teams(limit=3)
    print(f"Popular teams: {len(popular_teams)} found")
    
    # Demonstrate leaderboards
    print(f"\n🏅 Leaderboards:")
    print("-" * 30)
    community.update_leaderboard(users[0], "ranked_battles", 1850.5)
    community.update_leaderboard(users[1], "ranked_battles", 1720.0)
    community.update_leaderboard(users[2], "ranked_battles", 1950.2)
    
    leaderboard = community.get_leaderboard("ranked_battles", limit=10)
    for entry in leaderboard:
        print(f"#{entry.rank}: {entry.username} - {entry.score} points")
    
    # Demonstrate community posts
    print(f"\n💬 Community Posts:")
    print("-" * 30)
    post_id = community.create_post(
        users[0], PostType.GUIDE,
        "How to Build a Balanced Team",
        "Here's my guide on creating competitive teams...",
        ["guide", "teambuilding", "competitive"]
    )
    
    feed = community.get_community_feed(limit=5)
    for post in feed:
        print(f"📝 {post.title} by {post.user_id}")
        print(f"   {post.post_type.value} | {post.likes} likes")
    
    # Show user statistics
    print(f"\n📊 User Statistics:")
    print("-" * 30)
    stats = community.get_user_stats(users[0])
    if stats:
        social_stats = stats["social_stats"]
        print(f"Friends: {social_stats['friends']}")
        print(f"Teams Shared: {social_stats['teams_shared']}")
        print(f"Tournament Participation: {social_stats['tournaments_joined']}")
        print(f"Community Posts: {social_stats['community_posts']}")

if __name__ == "__main__":
    demonstrate_social_system()